from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from datetime import datetime
import os

# ===================== CONFIGURAÇÃO DO APP =====================
app = Flask(__name__)
CORS(app)  # Permite o site conectar na API

# Configuração do Banco (SQLite para desenvolvimento)
# Para produção, use: 'postgresql://usuario:senha@localhost/nome_bd'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ===================== MODELOS DO BANCO =====================

class Usuario(db.Model):
    __tablename__ = 'usuarios'
    
    id_usuario = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    numero_telefone = db.Column(db.String(20))
    senha = db.Column(db.String(255), nullable=False)
    
    # Relacionamentos
    arquivos = db.relationship('Arquivo', backref='dono', lazy=True)
    regras = db.relationship('RegraOrganizacao', backref='dono', lazy=True)
    pastas = db.relationship('Pasta', backref='dono', lazy=True)
    processos = db.relationship('ProcessoOrganizacao', backref='dono', lazy=True)


class Arquivo(db.Model):
    __tablename__ = 'arquivos'
    
    id_arquivo = db.Column(db.Integer, primary_key=True)
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuarios.id_usuario'), nullable=False)
    id_pasta = db.Column(db.Integer, db.ForeignKey('pastas.id_pasta'))
    nome_arquivo = db.Column(db.String(255), nullable=False)
    extensao = db.Column(db.String(10))
    tamanho = db.Column(db.BigInteger)
    data_criacao = db.Column(db.DateTime)
    data_modificacao = db.Column(db.DateTime)
    caminho_original = db.Column(db.Text, nullable=False)
    caminho_destino = db.Column(db.Text)
    tipo_arquivo = db.Column(db.String(50))
    
    # Relacionamentos
    metadado = db.relationship('Metadado', backref='arquivo', uselist=False)


class Metadado(db.Model):
    __tablename__ = 'metadados'
    
    id_metadado = db.Column(db.Integer, primary_key=True)
    id_arquivo = db.Column(db.Integer, db.ForeignKey('arquivos.id_arquivo'), unique=True)
    autor = db.Column(db.String(255))
    data_captura = db.Column(db.DateTime)
    resolucao = db.Column(db.String(50))
    categoria = db.Column(db.String(100))
    palavra_chave = db.Column(db.Text)  # Armazene como texto separado por vírgulas


class RegraOrganizacao(db.Model):
    __tablename__ = 'regras_organizacao'
    
    id_regra = db.Column(db.Integer, primary_key=True)
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuarios.id_usuario'), nullable=False)
    nome_regra = db.Column(db.String(255), nullable=False)
    criterio_organizacao = db.Column(db.Text)
    ordem_classificacao = db.Column(db.Integer)
    formato_destino = db.Column(db.String(50))
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)


class Pasta(db.Model):
    __tablename__ = 'pastas'
    
    id_pasta = db.Column(db.Integer, primary_key=True)
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuarios.id_usuario'), nullable=False)
    nome_pasta = db.Column(db.String(255), nullable=False)
    caminho_pasta = db.Column(db.Text, nullable=False)
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)


class ProcessoOrganizacao(db.Model):
    __tablename__ = 'processos_organizacao'
    
    id_processo = db.Column(db.Integer, primary_key=True)
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuarios.id_usuario'), nullable=False)
    id_regra = db.Column(db.Integer, db.ForeignKey('regras_organizacao.id_regra'), nullable=False)
    data_execucao = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(50), default='Pendente')
    quantidade_arquivos = db.Column(db.Integer)
    tempo_execucao = db.Column(db.Integer)

# ===================== ROTAS DA API =====================

# Inicializa o banco (rode uma vez)
with app.app_context():
    db.create_all()
    print("✅ Banco de dados criado com sucesso!")

# --- ROTAS DE USUÁRIO ---

@app.route('/api/cadastro', methods=['POST'])
def cadastrar_usuario():
    dados = request.json
    
    novo_usuario = Usuario(
        nome=dados['nome'],
        email=dados['email'],
        numero_telefone=dados.get('numero_telefone'),
        senha=dados['senha']  # Em produção, use hash (bcrypt)!
    )
    
    db.session.add(novo_usuario)
    db.session.commit()
    
    return jsonify({'mensagem': 'Usuário cadastrado!', 'id': novo_usuario.id_usuario}), 201


@app.route('/api/login', methods=['POST'])
def login():
    dados = request.json
    usuario = Usuario.query.filter_by(email=dados['email'], senha=dados['senha']).first()
    
    if usuario:
        return jsonify({'mensagem': 'Login okay!', 'id_usuario': usuario.id_usuario}), 200
    return jsonify({'erro': 'Credenciais inválidas'}), 401


# --- ROTAS DE ARQUIVO ---

@app.route('/api/upload', methods=['POST'])
def upload_arquivo():
    dados = request.json
    
    novo_arquivo = Arquivo(
        id_usuario=dados['id_usuario'],
        nome_arquivo=dados['nome_arquivo'],
        extensao=dados.get('extensao'),
        tamanho=dados.get('tamanho'),
        caminho_original=dados['caminho_original'],
        tipo_arquivo=dados.get('tipo_arquivo'),
        data_criacao=datetime.utcnow(),
        data_modificacao=datetime.utcnow()
    )
    
    db.session.add(novo_arquivo)
    db.session.commit()
    
    return jsonify({'mensagem': 'Arquivo upado!', 'id': novo_arquivo.id_arquivo}), 201


@app.route('/api/arquivos/<int:id_usuario>', methods=['GET'])
def listar_arquivos(id_usuario):
    arquivos = Arquivo.query.filter_by(id_usuario=id_usuario).all()
    
    lista = []
    for arq in arquivos:
        lista.append({
            'id': arq.id_arquivo,
            'nome': arq.nome_arquivo,
            'extensao': arq.extensao,
            'tamanho': arq.tamanho,
            'caminho_original': arq.caminho_original,
            'caminho_destino': arq.caminho_destino
        })
    
    return jsonify(lista), 200


# --- ROTAS DE ORGANIZAÇÃO ---

@app.route('/api/criar-regra', methods=['POST'])
def criar_regra():
    dados = request.json
    
    nova_regra = RegraOrganizacao(
        id_usuario=dados['id_usuario'],
        nome_regra=dados['nome_regra'],
        criterio_organizacao=dados.get('criterio_organizacao'),
        ordem_classificacao=dados.get('ordem_classificacao'),
        formato_destino=dados.get('formato_destino')
    )
    
    db.session.add(nova_regra)
    db.session.commit()
    
    return jsonify({'mensagem': 'Regra criada!', 'id': nova_regra.id_regra}), 201


@app.route('/api/executar-organizacao', methods=['POST'])
def executar_organizacao():
    dados = request.json
    
    # Cria o processo
    novo_processo = ProcessoOrganizacao(
        id_usuario=dados['id_usuario'],
        id_regra=dados['id_regra'],
        status='Em Andamento',
        quantidade_arquivos=dados.get('quantidade_arquivos', 0)
    )
    
    db.session.add(novo_processo)
    db.session.commit()
    
    # Aqui você adiciona a lógica de mover os arquivos según a regra!
    # Exemplo: atualiza o caminho_destino dos arquivos
    
    return jsonify({'mensagem': 'Processo iniciado!', 'id_processo': novo_processo.id_processo}), 201


# ===================== INICIAR API =====================
if __name__ == '__main__':
    app.run(debug=True, port=5000)