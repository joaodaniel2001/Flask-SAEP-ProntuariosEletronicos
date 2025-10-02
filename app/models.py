from . import db
from flask_login import UserMixin
from datetime import datetime

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    sobrenome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    senha = db.Column(db.String(200), nullable=False)
    tipo_profissional = db.Column(db.String(50), default='Medico', nullable=False)
    registros_prontuario = db.relationship('Prontuario', backref='profissional', lazy=True)

class Paciente(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(150), nullable=False)
    cpf = db.Column(db.String(14), unique=True, nullable=False)
    data_nascimento = db.Column(db.Date, nullable=False)
    alergias = db.Column(db.Text, default='Nenhuma')
    medicamentos_uso = db.Column(db.Text, default='Nenhum')
    data_cadastro = db.Column(db.DateTime, default=datetime.utcnow)
    prontuarios = db.relationship('Prontuario', backref='paciente', lazy=True)

class Prontuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data_registro = db.Column(db.DateTime, default=datetime.utcnow)
    tipo_registro = db.Column(db.String(50), nullable=False)
    descricao = db.Column(db.Text, nullable=False)
    paciente_id = db.Column(db.Integer, db.ForeignKey('paciente.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
