from datetime import date, datetime
from http import HTTPStatus
from typing import Annotated

from fastapi import FastAPI, HTTPException, Path, Query

from schemas import (
    CampoOrdenacao,
    DirecaoOrdenacao,
    Mensagem,
    TarefaAtualizarSchema,
    TarefaBD,
    TarefaPublic,
    TarefaSchema,
    TarefasPaginadas,
)

app = FastAPI(
    title="API de Lista de Tarefas (To-Do)",
    description="Atividade prática de Programação para Internet II",
)

# "Banco de dados" em memória, apenas para fins didáticos.
banco: list[TarefaBD] = []
proximo_id = 1


@app.get("/", response_model=Mensagem)
def home():
    return {"mensagem": "API de Tarefas no ar!"}


def buscar_indice_ou_404(id: int) -> int:
    for indice, tarefa in enumerate(banco):
        if tarefa.id == id:
            return indice
    raise HTTPException(
        status_code=HTTPStatus.NOT_FOUND, detail="Tarefa não encontrada"
    )


@app.post("/tarefas", response_model=TarefaPublic, status_code=HTTPStatus.CREATED)
def criar_tarefa(tarefa: TarefaSchema):
    global proximo_id

    agora = datetime.now()
    nova_tarefa = TarefaBD(
        id=proximo_id,
        concluida=False,
        data_criacao=agora,
        data_atualizacao=agora,
        **tarefa.model_dump(),
    )
    banco.append(nova_tarefa)
    proximo_id += 1

    return nova_tarefa


@app.get("/tarefas", response_model=TarefasPaginadas)
def listar_tarefas(
    concluida: Annotated[
        bool | None, Query(description="Filtra por tarefas concluídas ou não")
    ] = None,
    tag: Annotated[
        str | None, Query(description="Filtra tarefas que possuem a tag informada")
    ] = None,
    titulo: Annotated[
        str | None,
        Query(description="Filtra tarefas cujo título contenha o texto informado"),
    ] = None,
    data_inicio: Annotated[
        date | None, Query(description="Data inicial do período de criação")
    ] = None,
    data_fim: Annotated[
        date | None, Query(description="Data final do período de criação")
    ] = None,
    ordenar_por: Annotated[
        CampoOrdenacao, Query(description="Campo usado para ordenação")
    ] = "data_criacao",
    ordem: Annotated[
        DirecaoOrdenacao, Query(description="asc (crescente) ou desc (decrescente)")
    ] = "asc",
    pagina: Annotated[int, Query(ge=1, description="Página desejada")] = 1,
    limite: Annotated[
        int, Query(ge=1, le=100, description="Quantidade máxima de tarefas por página")
    ] = 10,
):
    resultado = list(banco)

    if concluida is not None:
        resultado = [t for t in resultado if t.concluida == concluida]

    if tag is not None:
        resultado = [t for t in resultado if tag in t.tags]

    if titulo is not None:
        titulo_lower = titulo.lower()
        resultado = [t for t in resultado if titulo_lower in t.titulo.lower()]

    if data_inicio is not None:
        resultado = [t for t in resultado if t.data_criacao.date() >= data_inicio]

    if data_fim is not None:
        resultado = [t for t in resultado if t.data_criacao.date() <= data_fim]

    resultado.sort(
        key=lambda t: getattr(t, ordenar_por),
        reverse=(ordem == "desc"),
    )

    total = len(resultado)
    inicio = (pagina - 1) * limite
    fim = inicio + limite
    tarefas_da_pagina = [
        TarefaPublic(**t.model_dump()) for t in resultado[inicio:fim]
    ]

    return TarefasPaginadas(
        pagina=pagina,
        limite=limite,
        total=total,
        tarefas=tarefas_da_pagina,
    )


@app.get("/tarefas/{id}", response_model=TarefaPublic)
def buscar_tarefa(id: Annotated[int, Path(ge=1)]):
    indice = buscar_indice_ou_404(id)
    return banco[indice]


@app.put("/tarefas/{id}", response_model=TarefaPublic)
def atualizar_tarefa(id: Annotated[int, Path(ge=1)], tarefa: TarefaAtualizarSchema):
    indice = buscar_indice_ou_404(id)
    atual = banco[indice]

    tarefa_atualizada = TarefaBD(
        id=atual.id,
        data_criacao=atual.data_criacao,
        data_atualizacao=datetime.now(),
        **tarefa.model_dump(),
    )
    banco[indice] = tarefa_atualizada

    return tarefa_atualizada


@app.delete("/tarefas/{id}", status_code=HTTPStatus.NO_CONTENT)
def excluir_tarefa(id: Annotated[int, Path(ge=1)]):
    indice = buscar_indice_ou_404(id)
    del banco[indice]
