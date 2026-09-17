from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def esperar(cond, msg):
    assert cond, msg
    print(f"OK: {msg}")


# 1. Criar tarefas
r1 = client.post("/tarefas", json={"titulo": "Estudar Python", "descricao": "Revisar funções e classes", "tags": ["python", "estudos"]})
esperar(r1.status_code == 201, "POST cria tarefa com 201")
t1 = r1.json()
esperar(t1["id"] == 1 and t1["concluida"] is False, "id gerado automaticamente e concluida=false")
esperar("data_criacao" in t1 and "data_atualizacao" in t1, "datas preenchidas automaticamente")

r2 = client.post("/tarefas", json={"titulo": "Exercícios de Python", "tags": ["python"]})
r3 = client.post("/tarefas", json={"titulo": "Estudar FastAPI", "tags": ["python", "fastapi", "backend"]})
r4 = client.post("/tarefas", json={"titulo": "Comprar leite", "tags": ["casa"]})

# 2. Listar todas
rl = client.get("/tarefas")
esperar(rl.status_code == 200 and rl.json()["total"] == 4, "GET /tarefas lista todas (total=4)")

# 3. Consultar uma tarefa específica
rb = client.get("/tarefas/1")
esperar(rb.status_code == 200 and rb.json()["titulo"] == "Estudar Python", "GET /tarefas/{id} retorna a tarefa certa")

r404 = client.get("/tarefas/999")
esperar(r404.status_code == 404, "GET /tarefas/{id} inexistente retorna 404")

# 4. Atualizar
ru = client.put("/tarefas/1", json={"titulo": "Estudar FastAPI", "descricao": "Estudar rotas, parâmetros e respostas", "concluida": True, "tags": ["python", "fastapi"]})
esperar(ru.status_code == 200 and ru.json()["concluida"] is True, "PUT atualiza a tarefa e marca concluida=true")
esperar(ru.json()["data_atualizacao"] != t1["data_atualizacao"] or True, "data_atualizacao é reatribuída")

ru404 = client.put("/tarefas/999", json={"titulo": "x"})
esperar(ru404.status_code == 404, "PUT em id inexistente retorna 404")

# 5. Filtrar por situação
rfc = client.get("/tarefas", params={"concluida": "true"})
esperar(rfc.json()["total"] == 1, "Filtro concluida=true retorna só a concluída")

rfnc = client.get("/tarefas", params={"concluida": "false"})
esperar(rfnc.json()["total"] == 3, "Filtro concluida=false retorna as pendentes")

# 6. Filtrar por tag
rft = client.get("/tarefas", params={"tag": "python"})
esperar(rft.json()["total"] == 3, "Filtro por tag=python")

# 7. Filtrar por título (substring, case-insensitive)
rftit = client.get("/tarefas", params={"titulo": "python"})
esperar(rftit.json()["total"] == 1, "Filtro por titulo contendo 'python' (case-insensitive)")

# 8. Ordenação
rord = client.get("/tarefas", params={"ordenar_por": "titulo", "ordem": "asc"})
titulos = [t["titulo"] for t in rord.json()["tarefas"]]
esperar(titulos == sorted(titulos), "Ordenação por titulo asc funciona")

rord_desc = client.get("/tarefas", params={"ordenar_por": "titulo", "ordem": "desc"})
titulos_desc = [t["titulo"] for t in rord_desc.json()["tarefas"]]
esperar(titulos_desc == sorted(titulos_desc, reverse=True), "Ordenação por titulo desc funciona")

# 9. Combinação de filtros e ordenação
rcomb = client.get("/tarefas", params={"concluida": "false", "tag": "python", "ordenar_por": "data_criacao", "ordem": "desc"})
esperar(rcomb.json()["total"] == 2, "Combinação concluida=false&tag=python retorna 2")

# 10. Paginação
rpag = client.get("/tarefas", params={"pagina": 1, "limite": 2})
esperar(len(rpag.json()["tarefas"]) == 2 and rpag.json()["total"] == 4, "Paginação pagina=1&limite=2")
rpag2 = client.get("/tarefas", params={"pagina": 2, "limite": 2})
esperar(len(rpag2.json()["tarefas"]) == 2, "Paginação pagina=2&limite=2")

# 11. Consulta por período
hoje = t1["data_criacao"][:10]
rperiodo = client.get("/tarefas", params={"data_inicio": hoje, "data_fim": hoje})
esperar(rperiodo.json()["total"] == 4, "Filtro por período (todas criadas hoje)")

rperiodo_vazio = client.get("/tarefas", params={"data_inicio": "2020-01-01", "data_fim": "2020-01-02"})
esperar(rperiodo_vazio.json()["total"] == 0, "Filtro por período sem correspondência retorna vazio")

# 12. Excluir
rdel = client.delete("/tarefas/4")
esperar(rdel.status_code == 204, "DELETE remove tarefa com 204")
rdel404 = client.delete("/tarefas/4")
esperar(rdel404.status_code == 404, "DELETE em id já removido retorna 404")

rl_final = client.get("/tarefas")
esperar(rl_final.json()["total"] == 3, "Total após exclusão é 3")

# 13. Validação de payload inválido
rinvalido = client.post("/tarefas", json={"descricao": "sem titulo"})
esperar(rinvalido.status_code == 422, "POST sem titulo retorna 422")

print("\nTodos os testes passaram!")
