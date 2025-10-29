from flask import Flask, jsonify, request
import requests
from models import get_db, Atividade, Nota
from datetime import datetime

app = Flask(__name__)
GERENCIAMENTO_URL = "http://gerenciamento:5000"

# --- ROTAS AUXILIARES ---
def model_to_dict(model):
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

# --- ROTAS DE ATIVIDADES (CRUD + Validação Síncrona Dupla) ---
@app.route('/atividades', methods=['POST'])
def criar_atividade():
    data = request.json
    turma_id = data.get('turma_id')
    professor_id = data.get('professor_id')

    # 1. VALIDAÇÃO SÍNCRONA: Professor
    valido, erro_msg = validar_entidade_externa('professores', professor_id)
    if not valido:
        status_code = 404 if "não encontrado" in erro_msg else 503
        return jsonify({"erro": erro_msg}), status_code

    # 2. VALIDAÇÃO SÍNCRONA: Turma
    valido, erro_msg = validar_entidade_externa('turmas', turma_id)
    if not valido:
        status_code = 404 if "não encontrado" in erro_msg else 503
        return jsonify({"erro": erro_msg}), status_code
    
    # 3. CRIAÇÃO da Atividade
    db = next(get_db())
    nova_atividade = Atividade(
        nome=data['nome'], 
        peso=data['peso'], 
        turma_id=turma_id,
        professor_id=professor_id
    )
    db.add(nova_atividade)
    db.commit()
    db.close()

    return jsonify({"mensagem": "Atividade criada com sucesso.", "atividade": model_to_dict(nova_atividade)}), 201

# --- ROTAS DE NOTAS (Validação do Aluno + Atividade local) ---
@app.route('/notas', methods=['POST'])
def criar_nota():
    data = request.json
    aluno_id = data.get('aluno_id')
    atividade_id = data.get('atividade_id')

   
    db = next(get_db())
    atividade = db.query(Atividade).filter(Atividade.id == atividade_id).first()
    if not atividade:
        db.close()
        return jsonify({"erro": f"Atividade com ID {atividade_id} não encontrada neste serviço."}), 404
    
    
    valido, erro_msg = validar_entidade_externa('alunos', aluno_id)
    if not valido:
        status_code = 404 if "não encontrado" in erro_msg else 503
        return jsonify({"erro": erro_msg}), status_code


    nova_nota = Nota(
        nota=data['nota'],
        aluno_id=aluno_id,
        atividade_id=atividade_id
    )
    db.add(nova_nota)
    db.commit()
    db.close()

    return jsonify({"mensagem": "Nota criada com sucesso.", "nota": model_to_dict(nova_nota)}), 201


if __name__ == '__main__':
    app.run(port=5002, debug=True)