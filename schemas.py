from datetime import datetime
from typing import Annotated, Literal

from pydantic import BaseModel, Field


class Mensagem(BaseModel):
    mensagem: str


class TarefaSchema(BaseModel):
    """Dados aceitos na criação de uma tarefa (POST /tarefas)."""

    titulo: Annotated[
        str,
        Field(min_length=1, max_length=200, examples=["Estudar FastAPI"]),
    ]
    descricao: Annotated[
        str,
        Field(max_length=2000, examples=["Revisar criação de APIs REST"]),
    ] = ""
    tags: Annotated[
        list[str],
        Field(examples=[["python", "fastapi", "backend"]]),
    ] = []


class TarefaAtualizarSchema(BaseModel):
    """Dados aceitos na atualização de uma tarefa (PUT /tarefas/{id})."""

    titulo: Annotated[str, Field(min_length=1, max_length=200)]
    descricao: Annotated[str, Field(max_length=2000)] = ""
    concluida: bool = False
    tags: Annotated[list[str], Field()] = []


class TarefaBD(TarefaSchema):
    """Representação completa da tarefa, como fica armazenada em memória."""

    id: int
    concluida: bool = False
    data_criacao: datetime
    data_atualizacao: datetime


class TarefaPublic(BaseModel):
    """Formato retornado pela API para cada tarefa."""

    id: int
    titulo: str
    descricao: str
    concluida: bool
    tags: list[str]
    data_criacao: datetime
    data_atualizacao: datetime


class TarefasPaginadas(BaseModel):
    """Envelope de resposta da listagem, com metadados de paginação."""

    pagina: int
    limite: int
    total: int
    tarefas: list[TarefaPublic]


CampoOrdenacao = Literal["id", "titulo", "data_criacao", "data_atualizacao"]
DirecaoOrdenacao = Literal["asc", "desc"]
