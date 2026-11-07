# Constantes usadas pelo terminal principal.py
DIAS = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta"]
HORARIOS = ["07:00", "08:40", "10:30", "12:30", "14:20", "16:00"]


class Tarefa:
    def __init__(self, nome, data, prioridade, disciplina, id=None):
        # guarda os dados da tarefa (ela começa como Pendente)
        self.id = id    # id da tarefa no banco 
        self.nome = nome
        self.data = data
        self.prioridade = prioridade
        self.disciplina = disciplina
        self.status = "Pendente"

    def concluir(self):
        # marca a tarefa como concluída
        self.status = "Concluída"

    def editar(self, novo_nome, novo_data, novo_prioridade, novo_disciplina):
        # troca os dados da tarefa pelos novos
        self.nome = novo_nome
        self.data = novo_data
        self.prioridade = novo_prioridade
        self.disciplina = novo_disciplina


class Usuario:
    def __init__(self, nome, email, senha, id=None):
        # guarda os dados do usuário, a lista de tarefas e a grade
        self.id = id    # id do usuário no banco 
        self.nome = nome
        self.email = email
        self.senha = senha
        self.tarefas = []
        self.grade = {}
        self.criar_grade()

    # TAREFAS 
    def adicionar_tarefa(self, tarefa):
        # coloca a tarefa na lista do usuário
        self.tarefas.append(tarefa)

    def remover_tarefa(self, tarefa):
        # tira a tarefa da lista do usuário
        self.tarefas.remove(tarefa)

    def encontrar_tarefa(self, numero):
        # devolve a tarefa pelo número (ID) que aparece na tabela
        # Se o ID não existir, dá mensagem de erro 
        if numero < 1 or numero > len(self.tarefas):
            raise IndexError("Tarefa não encontrada!")
        return self.tarefas[numero - 1]

    def buscar_tarefas(self, texto=""):
        # Devolve uma lista de pares (id, tarefa). Texto vazio devolve todas.
        texto = texto.strip().lower()
        resultado = []
        for i, tarefa in enumerate(self.tarefas, start=1):
            campos = [tarefa.nome, tarefa.disciplina, tarefa.prioridade,
                      tarefa.data, tarefa.status]
            if not texto or any(texto in campo.lower() for campo in campos):
                resultado.append((i, tarefa))
        return resultado

    def total_concluidas(self):
        # conta quantas tarefas estão concluídas
        return sum(1 for t in self.tarefas if t.status == "Concluída")

    def porcentagem_concluidas(self):
        # calcula a porcentagem de tarefas concluídas (0 se não houver tarefas)
        if len(self.tarefas) == 0:
            return 0.0
        return (self.total_concluidas() / len(self.tarefas)) * 100

    # GRADE 
    def criar_grade(self):
        # monta a grade vazia, com "-" em todos os horários
        self.grade = {}
        for horario in HORARIOS:
            self.grade[horario] = {}
            for dia in DIAS:
                self.grade[horario][dia] = "-"

    def definir_grade(self, horario, dia, disciplina):
        # Texto vazio volta para "-". Dia/horário inexistente lança erro.
        if horario not in self.grade or dia not in DIAS:
            raise ValueError("Dia ou horário inválido!")
        self.grade[horario][dia] = disciplina.strip() or "-"

    # LISTAR TAREFAS E GRADE
    def listar_tarefas(self):
        # mostra todas as tarefas no terminal
        print("\n*********************** Suas Tarefas ***********************")
        for i, tarefa in enumerate(self.tarefas, start=1):
            print(f"\nID: {i}")
            print(f"Tarefa: {tarefa.nome}")
            print(f"Disciplina: {tarefa.disciplina}")
            print(f"Data: {tarefa.data}")
            print(f"Prioridade: {tarefa.prioridade}")
            print(f"Status: {tarefa.status}")
        print("**************************************************************")

    def mostrar_grade(self):
        # mostra a grade de estudos no terminal, em forma de tabela
        print("\n" + " Grade de Estudos ".center(85, "*"))
        print(f"{'Horário':<10}", end="")
        for dia in DIAS:
            print(f"{dia:<15}", end="")
        print()
        print("-" * 85)

        for horario in HORARIOS:
            print(f"{horario:<10}", end="")
            for dia in DIAS:
                print(f"{self.grade[horario][dia]:<15}", end="")
            print()
        print("*" * 85)

#ALTERAR GRADE

    def alterar_grade(self):
        # pergunta o dia, o horário e a disciplina no terminal e altera a grade
        print("\nDias disponíveis:")
        for i, dia in enumerate(DIAS, start=1):
            print(f"{i} - {dia}")

        try:
            escolha_dia = int(input("Escolha o dia: "))
            if escolha_dia < 1 or escolha_dia > len(DIAS):
                raise ValueError("Dia inválido!")
            dia = DIAS[escolha_dia - 1]

            print("\nHorários disponíveis:")
            for i, horario in enumerate(HORARIOS, start=1):
                print(f"{i} - {horario}")

            escolha_horario = int(input("Escolha o horário: "))
            if escolha_horario < 1 or escolha_horario > len(HORARIOS):
                raise ValueError("Horário inválido!")
            horario = HORARIOS[escolha_horario - 1]

            disciplina = input("Qual disciplina será estudada? ")
            self.definir_grade(horario, dia, disciplina)

            print("\nGrade atualizada com sucesso!")
            self.mostrar_grade()
        except ValueError:
            print("\nEscolha uma opção válida (apenas números da lista)!")