import sqlite3
from pathlib import Path

from classes import Usuario, Tarefa, DIAS, HORARIOS


# Caminho do banco de dados
CAMINHO_BANCO = Path(__file__).resolve().parent / "agenda.db"


# CONEXÃO

from contextlib import contextmanager


@contextmanager
def conectar():
    # abre o banco, grava (commit) se der certo, desfaz (rollback) se der erro e sempre fecha
    conexao = sqlite3.connect(CAMINHO_BANCO)
    conexao.row_factory = sqlite3.Row
    conexao.execute("PRAGMA foreign_keys = ON")

    try:
        yield conexao
        conexao.commit()
    except Exception:
        conexao.rollback()
        raise
    finally:
        conexao.close()

# CRIAÇÃO DAS TABELAS

def inicializar_banco():
    # cria as tabelas do banco, se elas ainda não existirem
    with conectar() as conexao:

        # Usuários
        conexao.execute("""
            CREATE TABLE IF NOT EXISTS usuario (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                email TEXT NOT NULL,
                senha TEXT NOT NULL
            )
        """)

        # Tarefas
        conexao.execute("""
            CREATE TABLE IF NOT EXISTS tarefa (
                id_tarefa INTEGER PRIMARY KEY AUTOINCREMENT,
                id_usuario INTEGER NOT NULL,
                nome TEXT NOT NULL,
                data TEXT NOT NULL,
                prioridade TEXT NOT NULL,
                disciplina TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'Pendente',

                FOREIGN KEY (id_usuario)
                    REFERENCES usuario(id)
                    ON DELETE CASCADE
            )
        """)

        # Grade de horários
        conexao.execute("""
            CREATE TABLE IF NOT EXISTS horario_grade (
                id_horario INTEGER PRIMARY KEY AUTOINCREMENT,
                id_usuario INTEGER NOT NULL,
                dia TEXT NOT NULL,
                horario TEXT NOT NULL,
                disciplina TEXT NOT NULL DEFAULT '-',

                FOREIGN KEY (id_usuario)
                    REFERENCES usuario(id)
                    ON DELETE CASCADE,

                UNIQUE (id_usuario, dia, horario)
            )
        """)


# USUÁRIOS

def cadastrar_usuario(nome, email, senha):
    # grava um usuário novo, se o nome e o e-mail ainda não existirem
    with conectar() as conexao:

        # Verifica se o nome ou o e-mail já está cadastrado
        existente = conexao.execute("""
            SELECT id
            FROM usuario
            WHERE email = ? OR nome = ?
            """,
        (email, nome)).fetchone()

        if existente:
            raise ValueError("Este nome ou e-mail já está cadastrado!")

        cursor = conexao.execute("""
            INSERT INTO usuario (nome, email, senha)
            VALUES (?, ?, ?)
        """, (nome, email, senha))

        return cursor.lastrowid


def autenticar_usuario(nome, senha):
    # confere nome e senha e devolve o usuário com tarefas e grade (ou None se não bater)
    with conectar() as conexao:

        usuario = conexao.execute("""
            SELECT *
            FROM usuario
            WHERE nome = ? AND senha = ?
        """, (nome, senha)).fetchone()

    if usuario is None:
        return None

    objeto_usuario = Usuario(
        usuario["nome"],
        usuario["email"],
        usuario["senha"],
        id=usuario["id"]
    )

    carregar_dados_usuario(objeto_usuario)

    return objeto_usuario


def buscar_usuario_email(email):
    # procura o usuário pelo e-mail (usado na recuperação de senha)
    with conectar() as conexao:

        usuario = conexao.execute("""
            SELECT *
            FROM usuario
            WHERE email = ?
        """, (email,)).fetchone()

    if usuario is None:
        return None

    objeto_usuario = Usuario(
        usuario["nome"],
        usuario["email"],
        usuario["senha"],
        id=usuario["id"]
    )

    carregar_dados_usuario(objeto_usuario)

    return objeto_usuario


def atualizar_senha(id_usuario, nova_senha):
    # troca a senha do usuário no banco
    with conectar() as conexao:

        cursor = conexao.execute("""
            UPDATE usuario
            SET senha = ?
            WHERE id = ?
        """, (nova_senha, id_usuario))

        return cursor.rowcount > 0


# TAREFAS

def carregar_tarefas(usuario):
    # lê do banco as tarefas do usuário e coloca na lista dele
    with conectar() as conexao:

        registros = conexao.execute("""
            SELECT *
            FROM tarefa
            WHERE id_usuario = ?
            ORDER BY id_tarefa
        """, (usuario.id,)).fetchall()

    usuario.tarefas.clear()

    for registro in registros:

        tarefa = Tarefa(
            nome=registro["nome"],
            data=registro["data"],
            prioridade=registro["prioridade"],
            disciplina=registro["disciplina"],
            id=registro["id_tarefa"]
        )

        tarefa.status = registro["status"]

        usuario.adicionar_tarefa(tarefa)


def salvar_tarefa(id_usuario, tarefa):
    # grava uma tarefa nova no banco e guarda nela o ID gerado
    with conectar() as conexao:

        cursor = conexao.execute("""
            INSERT INTO tarefa (
                id_usuario,
                nome,
                data,
                prioridade,
                disciplina,
                status
            )
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            id_usuario,
            tarefa.nome,
            tarefa.data,
            tarefa.prioridade,
            tarefa.disciplina,
            tarefa.status
        ))

        # Guarda o ID real gerado pelo SQLite no objeto
        tarefa.id = cursor.lastrowid

        return tarefa.id


def atualizar_tarefa(id_usuario, tarefa):
    # atualiza no banco todos os dados da tarefa editada
    with conectar() as conexao:

        cursor = conexao.execute("""
            UPDATE tarefa
            SET nome = ?,
                data = ?,
                prioridade = ?,
                disciplina = ?,
                status = ?
            WHERE id_tarefa = ?
              AND id_usuario = ?
        """, (
            tarefa.nome,
            tarefa.data,
            tarefa.prioridade,
            tarefa.disciplina,
            tarefa.status,
            tarefa.id,
            id_usuario
        ))

        return cursor.rowcount > 0


def atualizar_status_tarefa(id_usuario, tarefa):
    # atualiza no banco só o status da tarefa (Pendente ou Concluída)
    with conectar() as conexao:

        cursor = conexao.execute("""
            UPDATE tarefa
            SET status = ?
            WHERE id_tarefa = ?
              AND id_usuario = ?
        """, (
            tarefa.status,
            tarefa.id,
            id_usuario
        ))

        return cursor.rowcount > 0


def excluir_tarefa(id_usuario, id_tarefa):
    # apaga a tarefa do banco
    with conectar() as conexao:

        cursor = conexao.execute("""
            DELETE FROM tarefa
            WHERE id_tarefa = ?
              AND id_usuario = ?
        """, (id_tarefa, id_usuario))

        return cursor.rowcount > 0


# GRADE DE ESTUDOS

def carregar_grade(usuario):
    # lê do banco os horários da grade do usuário
    # A grade já começa preenchida com "-" pela classe Usuario.
    with conectar() as conexao:

        registros = conexao.execute("""
            SELECT dia, horario, disciplina
            FROM horario_grade
            WHERE id_usuario = ?
        """, (usuario.id,)).fetchall()

    for registro in registros:

        dia = registro["dia"]
        horario = registro["horario"]

        if dia in DIAS and horario in HORARIOS:
            usuario.grade[horario][dia] = registro["disciplina"]


def salvar_grade(id_usuario, grade):
    # grava no banco todos os horários da grade (atualiza os que já existem)
    with conectar() as conexao:

        for horario in HORARIOS:
            for dia in DIAS:

                disciplina = grade[horario][dia].strip() or "-"

                conexao.execute("""
                    INSERT INTO horario_grade (
                        id_usuario,
                        dia,
                        horario,
                        disciplina
                    )
                    VALUES (?, ?, ?, ?)

                    ON CONFLICT (id_usuario, dia, horario)
                    DO UPDATE SET
                        disciplina = excluded.disciplina
                """, (
                    id_usuario,
                    dia,
                    horario,
                    disciplina
                ))


# CARREGAMENTO COMPLETO DO USUÁRIO

def carregar_dados_usuario(usuario):
    # carrega as tarefas e a grade do usuário, de uma vez
    carregar_tarefas(usuario)
    carregar_grade(usuario)