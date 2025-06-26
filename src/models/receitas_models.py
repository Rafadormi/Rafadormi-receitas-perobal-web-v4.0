from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Paciente(db.Model):
    __tablename__ = 'pacientes'
    
    id = db.Column(db.Integer, primary_key=True)
    nome_completo = db.Column(db.String(200), nullable=False)
    cpf = db.Column(db.String(14), unique=True, nullable=True)
    data_nascimento = db.Column(db.Date, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'nome_completo': self.nome_completo,
            'cpf': self.cpf,
            'data_nascimento': self.data_nascimento.isoformat() if self.data_nascimento else None,
            'created_at': self.created_at.isoformat()
        }

class Medicamento(db.Model):
    __tablename__ = 'medicamentos'
    
    id = db.Column(db.Integer, primary_key=True)
    denominacao_generica = db.Column(db.String(200), nullable=False)
    concentracao = db.Column(db.String(100), nullable=True)
    apresentacao = db.Column(db.String(100), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'denominacao_generica': self.denominacao_generica,
            'concentracao': self.concentracao,
            'apresentacao': self.apresentacao,
            'created_at': self.created_at.isoformat()
        }

class Receita(db.Model):
    __tablename__ = 'receitas'
    
    id = db.Column(db.Integer, primary_key=True)
    paciente_id = db.Column(db.Integer, db.ForeignKey('pacientes.id'), nullable=False)
    data_inicial = db.Column(db.Date, nullable=False)
    num_receitas = db.Column(db.Integer, nullable=False, default=1)
    observacoes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relacionamentos
    paciente = db.relationship('Paciente', backref='receitas')
    medicamentos = db.relationship('ReceitaMedicamento', backref='receita', cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'paciente_id': self.paciente_id,
            'paciente': self.paciente.to_dict() if self.paciente else None,
            'data_inicial': self.data_inicial.isoformat(),
            'num_receitas': self.num_receitas,
            'observacoes': self.observacoes,
            'medicamentos': [med.to_dict() for med in self.medicamentos],
            'created_at': self.created_at.isoformat()
        }

class ReceitaMedicamento(db.Model):
    __tablename__ = 'receita_medicamentos'
    
    id = db.Column(db.Integer, primary_key=True)
    receita_id = db.Column(db.Integer, db.ForeignKey('receitas.id'), nullable=False)
    medicamento_id = db.Column(db.Integer, db.ForeignKey('medicamentos.id'), nullable=False)
    posologia = db.Column(db.String(200), nullable=True)
    instrucoes = db.Column(db.Text, nullable=True)
    
    # Relacionamentos
    medicamento = db.relationship('Medicamento')
    
    def to_dict(self):
        return {
            'id': self.id,
            'receita_id': self.receita_id,
            'medicamento_id': self.medicamento_id,
            'medicamento': self.medicamento.to_dict() if self.medicamento else None,
            'posologia': self.posologia,
            'instrucoes': self.instrucoes
        }

