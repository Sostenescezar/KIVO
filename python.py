import urllib.request, json
dados = json.dumps({"nome": "João Silva", "email": "joao@email.com", "numero_telefone": "11999999999", "senha": "123456"})
req = urllib.request.Request("http://localhost:5000/api/cadastro", data=dados.encode("utf-8"), headers={"Content-Type": "application/json"}, method="POST")
print(urllib.request.urlopen(req).read().decode("utf-8"))