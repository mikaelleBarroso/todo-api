# API de Lista de Tarefas (To-Do)

Atividade prática de **Programação para Internet II** — API REST para gerenciamento
de uma lista de tarefas, construída com **FastAPI**.

## Como executar

```bash
uv sync
uv run fastapi dev main.py
```

A aplicação sobe em `http://127.0.0.1:8000` e a documentação interativa em
`http://127.0.0.1:8000/docs`.

## Estrutura

- `main.py` — endpoints da API (rotas, filtros, ordenação, paginação).
- `schemas.py` — modelos Pydantic usados para validar entrada e formatar saída.
- Os dados são mantidos **em memória** (uma lista Python), apenas para fins didáticos.
  Reiniciar a aplicação apaga as tarefas cadastradas.

## Modelo de tarefa

```json
{
  "id": 1,
  "titulo": "Estudar FastAPI",
  "descricao": "Revisar criação de APIs REST",
  "concluida": false,
  "tags": ["python", "fastapi", "backend"],
  "data_criacao": "2026-09-09T08:30:00",
  "data_atualizacao": "2026-09-09T08:30:00"
}
```

`id`, `data_criacao` e `data_atualizacao` são preenchidos automaticamente pela
aplicação.

## Endpoints

| Método | Rota           | Descrição                          |
|--------|----------------|-------------------------------------|
| POST   | `/tarefas`      | Cria uma nova tarefa                |
| GET    | `/tarefas`      | Lista tarefas (com filtros, ordenação e paginação) |
| GET    | `/tarefas/{id}` | Consulta uma tarefa específica      |
| PUT    | `/tarefas/{id}` | Atualiza uma tarefa                 |
| DELETE | `/tarefas/{id}` | Exclui uma tarefa                   |

### Query parameters de `GET /tarefas`

| Parâmetro     | Tipo | Descrição                                                        |
|---------------|------|-------------------------------------------------------------------|
| `concluida`   | bool | Filtra por tarefas concluídas (`true`) ou pendentes (`false`)     |
| `tag`         | str  | Filtra tarefas que possuem a tag informada                        |
| `titulo`      | str  | Filtra tarefas cujo título contenha o texto (case-insensitive)    |
| `data_inicio` | date | Data inicial do período de criação (`YYYY-MM-DD`)                 |
| `data_fim`    | date | Data final do período de criação (`YYYY-MM-DD`)                   |
| `ordenar_por` | enum | `id`, `titulo`, `data_criacao` ou `data_atualizacao` (padrão: `data_criacao`) |
| `ordem`       | enum | `asc` ou `desc` (padrão: `asc`)                                    |
| `pagina`      | int  | Página desejada (padrão: `1`)                                     |
| `limite`      | int  | Tarefas por página, entre 1 e 100 (padrão: `10`)                  |

Todos os filtros podem ser combinados livremente, por exemplo:

```
GET /tarefas?concluida=false&tag=python&ordenar_por=data_criacao&ordem=desc
```

### Exemplo de resposta paginada

```json
{
  "pagina": 2,
  "limite": 10,
  "total": 35,
  "tarefas": []
}
```

## Testes

Um script de verificação manual (`test_manual.py`) exercita todos os endpoints e
regras da atividade (CRUD, filtros, ordenação, paginação, período e validação):

```bash
uv run python test_manual.py
```
