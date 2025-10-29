from flask import Flask, jsonify, request
import requests
from sqlalchemy.exc import IntegrityError
from models import get_db, Reserva, get_db
from datetime import datetime

app = Flask(__name__)

GERENCIAMENTO_URL = "http://gerenciamento:5000"

def model_to_dict(model):
    """Converte um objeto SQLAlchemy em um dicionário."""
    data = {c.name: getattr(model, c.name) for c in model.__table__.columns}
    
    for key, value in data.items():
        if isinstance(value, datetime) or isinstance(value, datetime.date):
            data[key] = value.isoformat()
    return data

def validar_entidade_externa(entity_name, entity_id):
    """Função genérica de validação síncrona."""
    try:
        url = f'{GERENCIAMENTO_URL}/{entity_name}/{entity_id}'
        response = requests.get(url)
        
        if response.status_code == 404:
            return False, f"{entity_name.capitalize()} com ID {entity_id} não encontrado(a)."
        
        if response.status_code != 200:
            return False, f"Erro ao consultar o serviço Gerenciamento. Status: {response.status_code}"

        return True, None
    except requests.exceptions.ConnectionError:
        return False, "Serviço Gerenciamento indisponível (503)."

@app.route('/reservas', methods=['POST'])
def criar_reserva():
    data = request.json
    turma_id = data.get('turma_id')

    valido, erro_msg = validar_entidade_externa('turmas', turma_id)
    if not valido:
        status_code = 404 if "não encontrado" in erro_msg else 503
        return jsonify({"erro": erro_msg}), status_code


    db = next(get_db())
    data_reserva = datetime.strptime(data['data_reserva'], '%Y-%m-%d').date()
    
    nova_reserva = Reserva(
        num_sala=data['num_sala'], 
        data_reserva=data_reserva, 
        turma_id=turma_id
    )
    db.add(nova_reserva)
    db.commit()
    db.close()

    return jsonify({"mensagem": "Reserva criada com sucesso.", "reserva": model_to_dict(nova_reserva)}), 201

@app.route('/reservas/<int:reserva_id>', methods=['GET'])
def obter_reserva(reserva_id):
    db = next(get_db())
    reserva = db.query(Reserva).filter(Reserva.id == reserva_id).first()
    db.close()
    if not reserva:
        return jsonify({"erro": "Reserva não encontrada"}), 404
    return jsonify(model_to_dict(reserva)), 200

if __name__ == '__main__':
    app.run(port=5001, debug=True)