from flask import Flask, jsonify, request
from sqlalchemy.exc import IntegrityError
from models import get_db, Professor, Turma, Aluno

app = Flask(__name__)


def model_to_dict(model):
    """Converte um objeto SQLAlchemy em um dicionário."""
    return {c.name: getattr(model, c.name) for c in model.__table__.columns}


@app.route('/professores', methods=['POST'])
def criar_professor():
    data = request.json
    db = next(get_db())
    try:
        novo_professor = Professor(nome=data['nome'], materia=data['materia'])
        db.add(novo_professor)
        db.commit()
        return jsonify(model_to_dict(novo_professor)), 201
    except Exception as e:
        db.rollback()
        return jsonify({"erro": f"Erro ao criar professor: {str(e)}"}), 500
    finally:
        db.close()

@app.route('/professores/<int:professor_id>', methods=['GET'])
def obter_professor(professor_id):
    """Endpoint crucial para validação síncrona."""
    db = next(get_db())
    professor = db.query(Professor).filter(Professor.id == professor_id).first()
    db.close()
    if not professor:
        return jsonify({"erro": "Professor não encontrado"}), 404
    return jsonify(model_to_dict(professor)), 200

@app.route('/turmas', methods=['POST'])
def criar_turma():
    data = request.json
    db = next(get_db())
    
    professor = db.query(Professor).filter(Professor.id == data['professor_id']).first()
    if not professor:
        db.close()
        return jsonify({"erro": "Professor ID inválido para a turma"}), 400

    nova_turma = Turma(descricao=data['descricao'], professor_id=data['professor_id'])
    db.add(nova_turma)
    db.commit()
    db.close()
    return jsonify(model_to_dict(nova_turma)), 201

@app.route('/turmas/<int:turma_id>', methods=['GET'])
def obter_turma(turma_id):
    """Endpoint crucial para validação síncrona."""
    db = next(get_db())
    turma = db.query(Turma).filter(Turma.id == turma_id).first()
    db.close()
    if not turma:
        return jsonify({"erro": "Turma não encontrada"}), 404
    return jsonify(model_to_dict(turma)), 200


@app.route('/alunos/<int:aluno_id>', methods=['GET'])
def obter_aluno(aluno_id):
    """Endpoint crucial para validação síncrona."""
    db = next(get_db())
    aluno = db.query(Aluno).filter(Aluno.id == aluno_id).first()
    db.close()
    if not aluno:
        return jsonify({"erro": "Aluno não encontrado"}), 404
    return jsonify(model_to_dict(aluno)), 200

if __name__ == '__main__':
    app.run(port=5000, debug=True)