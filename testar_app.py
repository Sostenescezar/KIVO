import urllib.request
import json

# 1. Cadastrar Usuário
dados = {
    "nome": "João Silva",
    "email": "joao@email.com",
    "numero_telefone": "11999999999",
    "senha": "123456"
}

req = urllib.request.Request(
    "http://localhost:5000/api/cadastro",
    data=json.dumps(dados).encode("utf-8"),
    headers={"Content-Type": "application/json"},
    method="POST"
)

resposta = urllib.request.urlopen(req).read().decode("utf-8")
print("Cadastro:", resposta)

# 2. Login (para testar)
dados_login = {"email": "joao@email.com", "senha": "123456"}
req = urllib.request.Request(
    "http://localhost:5000/api/login",
    data=json.dumps(dados_login).encode("utf-8"),
    headers={"Content-Type": "application/json"},
    method="POST"
)
resposta = urllib.request.urlopen(req).read().decode("utf-8")
print("Login:", resposta)

# 3. Upload de Arquivo (id_usuario = 1)
dados_arquivo = {
    "id_usuario": 1,
    "nome_arquivo": "relatorio.pdf",
    "extensao": "pdf",
    "tamanho": 2048000,
    "caminho_original": "C:/uploads/relatorio.pdf",
    "tipo_arquivo": "documento"
}

req = urllib.request.Request(
    "http://localhost:5000/api/upload",
    data=json.dumps(dados_arquivo).encode("utf-8"),
    headers={"Content-Type": "application/json"},
    method="POST"
)
resposta = urllib.request.urlopen(req).read().decode("utf-8")
print("Upload:", resposta)