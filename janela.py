import random
import smtplib
import ssl
import banco
from datetime import datetime
from email.message import EmailMessage
from tkinter import *
from tkinter.font import Font
from tkinter.messagebox import *
from tkinter.ttk import Combobox, Treeview

from classes import Usuario, Tarefa, DIAS, HORARIOS


# E-mail que vai enviar os códigos de recuperação 
EMAIL_REMETENTE = "programamns@gmail.com"
SENHA_APP = "axmqwoiagbegyvon"

# Inicialização do banco de dados
banco.inicializar_banco()

print("Banco de dados preparado com sucesso!")

# CLASSE DA INTERFACE

class ProgramaMNS(Frame):
    def __init__(self):
        # monta a janela de cadastro e guarda o estado do programa
        Frame.__init__(self)

        self.usuarios = []
        self.usuarioRecuperacao = None
        self.codigoRecuperacao = None
        self.usuarioLogado = None

        
        self.janelaEntrar = None
        self.janelaMenu = None
        self.janelaTarefas = None
        self.janelaGrade = None

        self.master.title("Programa - MNS")
        self.master.geometry("423x350")
        self.master.configure(bg="lightblue") 
        self.configure(bg="lightblue")
        self.grid()

        fonte2 = Font(family="Verdana", size=14, weight="bold")
        fonte3 = Font(family="Times New Roman", size=23)

        # PRIMEIRA LEGENDA
        self.lblTexto1 = Label(self)
        self.lblTexto1["font"] = fonte3
        self.lblTexto1["text"] = "  Gerenciador de Tarefas - MNS  \n"
        self.lblTexto1["bg"] = "SteelBlue"

        self.lblTexto1.grid(row=0, column=0, columnspan=3, pady=10)

        # SEGUNDA LEGENDA
        self.lblTexto2 = Label(self)
        self.lblTexto2["font"] = fonte2
        self.lblTexto2["text"] = "Cadastro de Dados"
        self.lblTexto2["bg"] = "lightblue"
        self.lblTexto2.grid(row=1, column=0, columnspan=5, pady=10)

        # LABEL PARA O NOME DO USUÁRIO
        self.lblNome = Label(self)
        self.lblNome["text"] = "Nome de usuário:"
        self.lblNome["bg"] = "LightPink"
        self.lblNome.grid(row=2, column=0, padx=5, pady=5)

        self.nome = Entry(self)
        self.nome.grid(row=2, column=1, padx=5, pady=5)

        # LABEL PARA O E-MAIL
        self.lblEmail = Label(self)
        self.lblEmail["text"] = "Digite seu Email:"
        self.lblEmail["bg"] = "LightPink"
        self.lblEmail.grid(row=3, column=0, padx=5, pady=5)

        self.email = Entry(self)
        self.email.grid(row=3, column=1, padx=5, pady=5)

        # LABEL PARA A SENHA
        self.lblSenha = Label(self)
        self.lblSenha["text"] = "Digite sua senha:"
        self.lblSenha["bg"] = "LightPink"
        self.lblSenha.grid(row=4, column=0, padx=5, pady=5)

        self.senha = Entry(self, show="*")
        self.senha.grid(row=4, column=1, padx=5, pady=5)

        # BOTÃO PARA CADASTRAR
        self.btnCadastrar = Button(self)
        self.btnCadastrar["text"] = "Cadastrar"
        self.btnCadastrar["bg"] = "SteelBlue"
        self.btnCadastrar["command"] = self.cadastrar
        self.btnCadastrar.grid(row=5, column=0, columnspan=2, pady=10)

        # BOTÃO PARA ENTRAR
        self.btnEntrar = Button(self)
        self.btnEntrar["text"] = "Entrar"
        self.btnEntrar["bg"] = "SteelBlue"
        self.btnEntrar["command"] = self.entrar
        self.btnEntrar.grid(row=5, column=1, padx=1, pady=10)


 
    # FUNÇÃO DO BOTÃO CADASTRAR
   
    def cadastrar(self):
        # lê os campos, valida e cadastra o usuário
        try:
            nome = self.nome.get().strip()
            email = self.email.get().strip()
            senha = self.senha.get()

            if not nome or not email or not senha:
                raise ValueError("Preencha todos os campos.")

            partes = email.split("@")

            if len(partes) != 2 or not partes[0] or "." not in partes[1] or partes[1].endswith(".") or " " in email:
                raise ValueError("Digite um e-mail válido (ex: nome@gmail.com).")

            # Cadastra diretamente no banco
            banco.cadastrar_usuario(nome, email, senha)

            showinfo("Sucesso", "Usuário cadastrado com sucesso!", parent=self)

            self.nome.delete(0, END)
            self.email.delete(0, END)
            self.senha.delete(0, END)

        except ValueError as erro:
            showerror("Erro no cadastro", str(erro), parent=self)

    # FUNÇÃO DO BOTÃO ENTRAR (LOGIN)

    def entrar(self):
        # abre a janela de login com nome e senha

        # evita abrir várias janelas de login
        if self.janelaEntrar is not None and self.janelaEntrar.winfo_exists():
            self.janelaEntrar.lift()
            return

        self.janelaEntrar = Toplevel(self.master)
        self.janelaEntrar.title("ENTRAR COM SUA CONTA")
        self.janelaEntrar.geometry("450x300")
        self.janelaEntrar.configure(bg="lightblue") 

        self.lblFiltro = Label(
            self.janelaEntrar,
            text="Entre com seus dados para acessar sua conta",
            font=("Verdana", 12, "bold"),
            bg="SteelBlue"
        )
        self.lblFiltro.grid(row=0, column=0, columnspan=2, padx=20, pady=20)

        self.lblLoginNome = Label(self.janelaEntrar, text="Nome de usuário:")
        self.lblLoginNome["bg"] = "LightPink"
        self.lblLoginNome.grid(row=1, column=0, padx=5, pady=5, sticky="e")

        self.loginNome = Entry(self.janelaEntrar, width=30)
        self.loginNome.grid(row=1, column=1, padx=5, pady=5)

        self.lblLoginSenha = Label(self.janelaEntrar, text="Senha:")
        self.lblLoginSenha["bg"] = "LightPink"
        self.lblLoginSenha.grid(row=2, column=0, padx=5, pady=5, sticky="e")

        self.loginSenha = Entry(self.janelaEntrar, width=30, show="*")
        self.loginSenha.grid(row=2, column=1, padx=5, pady=5)

        self.btnAcessar = Button(
            self.janelaEntrar,
            text="Acessar",
            bg="SteelBlue",
            command=self.fazerAcesso
        )
        self.btnAcessar.grid(row=3, column=0, columnspan=2, pady=15)

        fonteLink = Font(family="Verdana", size=9, underline=True)
        self.lblEsqueceu = Label(
            self.janelaEntrar,
            text="Esqueceu a senha?",
            fg="blue",
            bg="lightblue",
            cursor="hand2",
            font=fonteLink
        )
        self.lblEsqueceu.bind("<Button-1>", self.esqueceuSenha)
        self.lblEsqueceu.grid(row=4, column=0, columnspan=2, pady=5)
        self.lblEsqueceu.grid_remove()   # só aparece depois de um erro

        self.janelaEntrar.bind("<Return>", lambda event: self.fazerAcesso())

    def fazerAcesso(self):
        # confere nome e senha no banco e abre o menu se estiverem certos
        nome = self.loginNome.get().strip()
        senha = self.loginSenha.get()

        if not nome or not senha:
            showwarning("Atenção", "Preencha nome e senha.", parent=self.janelaEntrar)
            return

        # Consulta o usuário no banco e carrega seus dados
        usuario = banco.autenticar_usuario(nome, senha)

        if usuario is not None:
            self.usuarioLogado = usuario

            self.janelaEntrar.destroy()
            self.abrirMenu()
            return

        showerror(
            "Erro",
            "Nome de usuário ou senha incorretos",
            parent=self.janelaEntrar
        )

        self.lblEsqueceu.grid()

    # FUNÇÃO DO LINK "ESQUECEU A SENHA"

    def esqueceuSenha(self, event):
        # abre a janela para digitar o e-mail da conta
        self.janelaEntrar.destroy()

        self.janelaEmail = Toplevel(self.master)
        self.janelaEmail.title("RECUPERAR SENHA")
        self.janelaEmail.geometry("400x230")
        self.janelaEmail.configure(bg="lightblue") 
        self.janelaEmail.grab_set()

        Label(
            self.janelaEmail,
            text="Digite o e-mail cadastrado na sua conta",
            font=("Verdana", 11, "italic"),
            bg="SteelBlue"
        ).grid(row=0, column=0, columnspan=2, padx=20, pady=20)

        self.lbljanelaEmail = Label(self.janelaEmail, text="E-mail:")
        self.lbljanelaEmail["bg"] = "LightPink"
        self.lbljanelaEmail.grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.recEmail = Entry(self.janelaEmail, width=30)
        self.recEmail.grid(row=1, column=1, padx=5, pady=5)

        self.btnconfirmarEmail = Button(self.janelaEmail, text="Confirmar", bg="SteelBlue", command=self.confirmarEmail)
        
        self.btnconfirmarEmail.grid(row=2, column=0, columnspan=2, pady=15)

    def confirmarEmail(self):
        # procura o e-mail no banco e envia o código de recuperação
        email = self.recEmail.get().strip()

        usuario = banco.buscar_usuario_email(email)

        if usuario is None:
            showerror("Erro", "E-mail não encontrado.", parent=self.janelaEmail)
            return

        try:
            self.usuarioRecuperacao = usuario
            self.codigoRecuperacao = f"{random.randint(0, 999999):06d}"

            self.enviarCodigo(usuario.email, self.codigoRecuperacao)

            self.janelaEmail.destroy()
            self.abrirCodigo()

        except smtplib.SMTPAuthenticationError:
            showerror(
                "Erro",
                "As credenciais do remetente estão incorretas. Confira as configurações do e-mail.",
                parent=self.janelaEmail
            )

        except (smtplib.SMTPException, OSError):
            showerror(
                "Erro",
                "Não foi possível enviar o código. Verifique a conexão e as configurações do e-mail.",
                parent=self.janelaEmail
            )

    def enviarCodigo(self, destino, codigo):
        # monta o e-mail e envia o código pelo Gmail
        mensagem = EmailMessage()
        mensagem["Subject"] = "Código de recuperação de senha - MNS"
        mensagem["From"] = EMAIL_REMETENTE
        mensagem["To"] = destino
        mensagem.set_content(
            f"Olá!\n\nSeu código de recuperação de senha é: {codigo}\n\n"
            "Se não foi você quem pediu, ignore esta mensagem."
        )

        with smtplib.SMTP("smtp.gmail.com", 587, timeout=15) as servidor:
            servidor.starttls(context=ssl.create_default_context())
            servidor.login(EMAIL_REMETENTE, SENHA_APP)
            servidor.send_message(mensagem)

    def abrirCodigo(self):
        # abre a janela para digitar o código recebido por e-mail
        self.janelaCodigo = Toplevel(self.master)
        self.janelaCodigo.title("CÓDIGO DE VERIFICAÇÃO")
        self.janelaCodigo.geometry("400x230")
        self.janelaCodigo.configure(bg="lightblue")
        self.janelaCodigo.grab_set()

        Label(
            self.janelaCodigo,
            text="Digite o código enviado para o seu e-mail",
            font=("Verdana", 11, "italic"),
            bg="SteelBlue"
        ).grid(row=0, column=0, columnspan=2, padx=20, pady=20)

        Label(
            self.janelaCodigo,
            text="Dica: pode estar na caixa de SPAM.",
            font=("Verdana", 8, "italic"),
            bg="lightblue"
        ).grid(row=len(HORARIOS) + 2, column=0, columnspan=len(DIAS) + 1)

        self.lblCodigo = Label(self.janelaCodigo, text="Código:")
        self.lblCodigo["bg"] = "LightPink"
        self.lblCodigo.grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.recCodigo = Entry(self.janelaCodigo, width=30)
        self.recCodigo.grid(row=1, column=1, padx=5, pady=5)

        self.btnConfirmarCodigo = Button(self.janelaCodigo, text="Confirmar", bg="SteelBlue", command=self.confirmarCodigo)
        self.btnConfirmarCodigo.grid(row=2, column=0, columnspan=2, pady=15)

    def confirmarCodigo(self):
        # confere se o código digitado é o mesmo que foi enviado
        codigo = self.recCodigo.get().strip()

        if codigo == self.codigoRecuperacao:
            self.codigoRecuperacao = None
            self.janelaCodigo.destroy()
            self.abrirNovaSenha()
        else:
            showerror("Erro", "Código incorreto.", parent=self.janelaCodigo)

    def abrirNovaSenha(self):
        # abre a janela para digitar a nova senha
        self.janelaNovaSenha = Toplevel(self.master)
        self.janelaNovaSenha.title("NOVA SENHA")
        self.janelaNovaSenha.geometry("500x280")
        self.janelaNovaSenha.configure(bg="lightblue")
        self.janelaNovaSenha.grab_set()

        Label(
            self.janelaNovaSenha,
            text="Digite sua nova senha",
            font=("Verdana", 11, "italic"),
            bg="SteelBlue"
        ).grid(row=0, column=0, columnspan=2, padx=20, pady=20)

        self.lblNovaSenha = Label(self.janelaNovaSenha, text="Nova senha:")
        self.lblNovaSenha["bg"] = "LightPink"
        self.lblNovaSenha.grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.novaSenha = Entry(self.janelaNovaSenha, width=30, show="*")
        self.novaSenha.grid(row=1, column=1, padx=5, pady=5)

        self.lblConfirmaSenha = Label(self.janelaNovaSenha, text="Confirmar senha:")
        self.lblConfirmaSenha["bg"] = "LightPink"
        self.lblConfirmaSenha.grid(row=2, column=0, padx=5, pady=5, sticky="e")
        self.confirmaSenha = Entry(self.janelaNovaSenha, width=30, show="*")
        self.confirmaSenha.grid(row=2, column=1, padx=5, pady=5)

        self.btnConfirmarNovaSenha = Button(self.janelaNovaSenha, text="Confirmar", bg="SteelBlue", command=self.salvarNovaSenha)
        self.btnConfirmarNovaSenha.grid(row=3, column=0, columnspan=2, pady=15)

    def salvarNovaSenha(self):
        # confere as duas senhas digitadas e salva a nova senha
        nova = self.novaSenha.get()
        confirma = self.confirmaSenha.get()

        if not nova or not confirma:
            showwarning("Atenção", "Preencha os dois campos.",
                        parent=self.janelaNovaSenha)
            return

        if nova != confirma:
            showerror("Erro", "As senhas não são iguais.",
                      parent=self.janelaNovaSenha)
            return

        # Atualiza a senha no objeto e no banco de dados
        self.usuarioRecuperacao.senha = nova

        banco.atualizar_senha(
            self.usuarioRecuperacao.id,
            nova
        )
        showinfo("Sucesso", "Senha alterada com sucesso!",
                 parent=self.janelaNovaSenha)

        self.janelaNovaSenha.destroy()
        self.usuarioRecuperacao = None
        self.entrar()   # volta para o login


   
    # MENU PRINCIPAL DO PROGRAMA (SÓ APARECE DEPOIS DO LOGIN)

    def abrirMenu(self):
        # cria o menu com um botão para cada função do programa
        self.master.withdraw()   # esconde a janela de cadastro

        self.janelaMenu = Toplevel(self.master)
        self.janelaMenu.title("MENU")
        self.janelaMenu.geometry("400x420")
        self.janelaMenu.configure(bg="lightblue")
        # fechar pelo X faz o mesmo que o botão Sair
        self.janelaMenu.protocol("WM_DELETE_WINDOW", self.sair)

        Label(
            self.janelaMenu,
            text=f"Olá, {self.usuarioLogado.nome}!",
            font=("Verdana", 14, "italic"),
            bg="LightPink"
        ).grid(row=0, column=0, padx=80, pady=20)

        botoes = [
            ("Adicionar tarefa", self.adicionarTarefa),
            ("Listar tarefas", self.listarTarefas),
            ("Total e porcentagem", self.mostrarEstatisticas),
            ("Grade de estudos", self.abrirGrade),
            ("Sair", self.sair),
        ]
        for i, (texto, comando) in enumerate(botoes, start=1):
            Button(self.janelaMenu, text=texto, width=28, bg="SteelBlue", command=comando).grid(
                row=i, column=0, pady=8)

    def sair(self):
        # fecha o menu e volta para a janela de cadastro
        self.janelaMenu.destroy()   # fecha também as janelas filhas
        self.usuarioLogado = None
        self.master.deiconify()     # mostra o cadastro de novo



    # FUNÇÃO DO BOTÃO "ADICIONAR / EDITAR TAREFA"
    
    def adicionarTarefa(self):
        # abre o formulário vazio para cadastrar uma nova tarefa
        self.abrirFormulario()

    def abrirFormulario(self, tarefa=None):
        # cria o formulário da tarefa (vazio para adicionar, preenchido para editar)

        # a janela do formulário abre "em cima" da tabela, se ela estiver aberta
        pai = self.janelaMenu
        if self.janelaTarefas is not None and self.janelaTarefas.winfo_exists():
            pai = self.janelaTarefas

        janela = Toplevel(pai)
        janela.title("EDITAR TAREFA" if tarefa else "ADICIONAR TAREFA")
        janela.geometry("430x300")
        janela.configure(bg="lightblue")
        janela.grab_set()

        Label(
            janela,
            text="Editar tarefa" if tarefa else "Nova tarefa",
            font=("Verdana", 12, "italic"),
            bg="SteelBlue"
        ).grid(row=0, column=0, columnspan=2, padx=20, pady=15)

        rotulos = ["Tarefa:", "Data (dd/mm/aaaa):", "Prioridade:", "Disciplina:"]
        for i, rotulo in enumerate(rotulos, start=1):
            Label(janela, text=rotulo, bg="LightPink").grid(row=i, column=0, padx=5, pady=5, sticky="e")

        entNome = Entry(janela, width=30)
        entNome.grid(row=1, column=1, padx=5, pady=5)

        entData = Entry(janela, width=30)
        entData.grid(row=2, column=1, padx=5, pady=5)

        cmbPrioridade = Combobox(janela, values=["alta", "média", "baixa"],
                                 state="readonly", width=27)
        cmbPrioridade.grid(row=3, column=1, padx=5, pady=5)

        entDisciplina = Entry(janela, width=30)
        entDisciplina.grid(row=4, column=1, padx=5, pady=5)

        if tarefa:   # edição: preenche com os dados atuais
            entNome.insert(0, tarefa.nome)
            entData.insert(0, tarefa.data)
            cmbPrioridade.set(tarefa.prioridade)
            entDisciplina.insert(0, tarefa.disciplina)
        else:
            cmbPrioridade.set("média")

        Button(
            janela,
            text="Salvar",
            bg="SteelBlue",
            command=lambda: self.salvarFormulario(
                janela, tarefa, entNome, entData, cmbPrioridade, entDisciplina)
        ).grid(row=5, column=0, columnspan=2, pady=15)

    def salvarFormulario(self, janela, tarefa, entNome, entData, cmbPrioridade, entDisciplina):
        # valida os campos e salva a tarefa (nova ou editada)
        try:
            nome = entNome.get().strip()
            data = entData.get().strip()
            prioridade = cmbPrioridade.get().strip()
            disciplina = entDisciplina.get().strip()

            if not nome or not data or not prioridade or not disciplina:
                raise ValueError("Preencha todos os campos.")

            try:
                datetime.strptime(data, "%d/%m/%Y")
            except ValueError:
                raise ValueError("Data inválida. Use o formato dd/mm/aaaa (ex: 25/12/2026).")

            if tarefa is None:
                nova_tarefa = Tarefa(nome, data, prioridade, disciplina)

                # Salva no banco e recebe o ID gerado pelo SQLite
                banco.salvar_tarefa(
                    self.usuarioLogado.id,
                    nova_tarefa
                )

                # Adiciona o objeto à lista do usuário
                self.usuarioLogado.adicionar_tarefa(nova_tarefa)

                showinfo("Sucesso", "Tarefa adicionada com sucesso!", parent=janela)

            else:
                tarefa.editar(nome, data, prioridade, disciplina)

                # Atualiza a tarefa no banco
                banco.atualizar_tarefa(
                    self.usuarioLogado.id,
                    tarefa
                )

                showinfo("Sucesso", "Tarefa editada com sucesso!", parent=janela)

            janela.destroy()
            self.atualizarTabela()

        except ValueError as erro:
            showerror("Erro", str(erro), parent=janela)



    # LISTAR TAREFAS (concluir, editar, remover, buscar)

    def listarTarefas(self):
        # abre a janela com a tabela de tarefas e os botões de ação
        if self.janelaTarefas is not None and self.janelaTarefas.winfo_exists():
            self.janelaTarefas.lift()
            return

        self.janelaTarefas = Toplevel(self.janelaMenu)
        self.janelaTarefas.title("MINHAS TAREFAS")
        self.janelaTarefas.geometry("700x460")
        self.janelaTarefas.configure(bg="lightblue")

        # busca 
        Label(self.janelaTarefas, text="Buscar:", bg="LightPink").grid(row=0, column=0, padx=5, pady=10, sticky="e")
        self.entBusca = Entry(self.janelaTarefas, width=35)
        self.entBusca.grid(row=0, column=1, columnspan=2, padx=5, pady=10, sticky="w")
        self.entBusca.bind("<KeyRelease>", lambda event: self.atualizarTabela())
        Button(self.janelaTarefas, text="Limpar", bg="SteelBlue", command=self.limparBusca).grid(
            row=0, column=3, padx=5, pady=10, sticky="w")

        #  tabela 
        colunas = ("id", "nome", "disciplina", "data", "prioridade", "status")
        titulos = {"id": "ID", "nome": "Tarefa", "disciplina": "Disciplina",
                   "data": "Data", "prioridade": "Prioridade", "status": "Status"}
        larguras = {"id": 40, "nome": 200, "disciplina": 120,
                    "data": 90, "prioridade": 80, "status": 90}

        self.tabela = Treeview(self.janelaTarefas, columns=colunas,
                               show="headings", selectmode="browse", height=12)
        for coluna in colunas:
            self.tabela.heading(coluna, text=titulos[coluna])
            self.tabela.column(coluna, width=larguras[coluna],
                               anchor="w" if coluna == "nome" else "center")
        self.tabela.tag_configure("concluida", foreground="gray")
        self.tabela.grid(row=1, column=0, columnspan=4, padx=(10, 0), sticky="nsew")

        barra = Scrollbar(self.janelaTarefas, orient=VERTICAL, command=self.tabela.yview)
        self.tabela.configure(yscrollcommand=barra.set)
        barra.grid(row=1, column=4, sticky="ns", padx=(0, 10))

        # botões
        frameBotoes = Frame(self.janelaTarefas, bg="lightblue")
        frameBotoes.grid(row=2, column=0, columnspan=4, pady=10)
        Button(frameBotoes, text="Adicionar", width=12, bg="SteelBlue", command=self.adicionarTarefa).grid(row=0, column=0, padx=5)
        Button(frameBotoes, text="Concluir", width=12, bg="SteelBlue", command=self.concluirTarefa).grid(row=0, column=1, padx=5)
        Button(frameBotoes, text="Editar", width=12, bg="SteelBlue", command=self.editarTarefa).grid(row=0, column=2, padx=5)
        Button(frameBotoes, text="Remover", width=12, bg="SteelBlue", command=self.removerTarefa).grid(row=0, column=3, padx=5)

        # resumo (total e porcentagem) 
        self.lblResumo = Label(self.janelaTarefas, text="", font=("Verdana", 10, "italic"), bg="lightblue")
        self.lblResumo.grid(row=3, column=0, columnspan=4, pady=5)

        self.atualizarTabela()

    def limparBusca(self):
        # apaga o texto da busca e mostra todas as tarefas de novo
        self.entBusca.delete(0, END)
        self.atualizarTabela()

    def atualizarTabela(self):
        # refaz a tabela com as tarefas e atualiza o resumo (total e porcentagem)

        # só atualiza se a janela de tarefas estiver aberta
        if self.janelaTarefas is not None and self.janelaTarefas.winfo_exists():
            self.tabela.delete(*self.tabela.get_children())

            for i, t in self.usuarioLogado.buscar_tarefas(self.entBusca.get()):
                tags = ("concluida",) if t.status == "Concluída" else ()
                self.tabela.insert("", END,
                                   values=(i, t.nome, t.disciplina, t.data, t.prioridade, t.status),
                                   tags=tags)

            usuario = self.usuarioLogado
            self.lblResumo["text"] = (
                f"Total: {len(usuario.tarefas)}   |   "
                f"Concluídas: {usuario.total_concluidas()}   |   "
                f"{usuario.porcentagem_concluidas():.2f}% concluídas"
            )

    def tarefaSelecionada(self):
        # Devolve a tarefa da linha selecionada
        selecao = self.tabela.selection()
        if not selecao:
            raise IndexError("Selecione uma tarefa na tabela.")

        numero = int(self.tabela.item(selecao[0], "values")[0])
        return self.usuarioLogado.encontrar_tarefa(numero)

    def concluirTarefa(self):
        # marca a tarefa selecionada como concluída
        try:
            tarefa = self.tarefaSelecionada()

            if tarefa.status == "Concluída":
                showinfo("Atenção", "Essa tarefa já está concluída!", parent=self.janelaTarefas)
            else:
                tarefa.concluir()

                # Atualiza o status no banco
                banco.atualizar_status_tarefa(
                    self.usuarioLogado.id,
                    tarefa
                )

                self.atualizarTabela()
                
        except IndexError as erro:
            showwarning("Atenção", str(erro), parent=self.janelaTarefas)

    def editarTarefa(self):
        # abre o formulário já preenchido com a tarefa selecionada
        try:
            tarefa = self.tarefaSelecionada()
            self.abrirFormulario(tarefa)

        except IndexError as erro:
            showwarning("Atenção", str(erro), parent=self.janelaTarefas)

    def removerTarefa(self):
        # remove a tarefa selecionada, depois de pedir confirmação
        try:
            tarefa = self.tarefaSelecionada()

            if askyesno("Confirmar", f"Deseja remover a tarefa '{tarefa.nome}'?",
                        parent=self.janelaTarefas):
                # Remove primeiro do banco
                banco.excluir_tarefa(
                    self.usuarioLogado.id,
                    tarefa.id
                )

                # Depois remove da lista em memória
                self.usuarioLogado.remover_tarefa(tarefa)

                self.atualizarTabela()

        except IndexError as erro:
            showwarning("Atenção", str(erro), parent=self.janelaTarefas)

    
    # TOTAL E PORCENTAGEM
   

    def mostrarEstatisticas(self):
        # mostra o total de tarefas, as concluídas e a porcentagem
        usuario = self.usuarioLogado

        if len(usuario.tarefas) == 0:
            showinfo("Estatísticas",
                     "A lista de tarefas está vazia! Adicione uma tarefa primeiro.",
                     parent=self.janelaMenu)
        else:
            showinfo(
                "Estatísticas",
                f"Total de tarefas: {len(usuario.tarefas)}\n"
                f"Concluídas: {usuario.total_concluidas()}\n"
                f"Porcentagem concluída: {usuario.porcentagem_concluidas():.2f}%",
                parent=self.janelaMenu
            )



    # GRADE DE ESTUDOS
 
    def abrirGrade(self):
        # abre a janela da grade de estudos com o formulário para alterar
        if self.janelaGrade is not None and self.janelaGrade.winfo_exists():
            self.janelaGrade.lift()
            return

        self.janelaGrade = Toplevel(self.janelaMenu)
        self.janelaGrade.title("GRADE DE ESTUDOS")
        self.janelaGrade.geometry("720x400")
        self.janelaGrade.configure(bg="lightblue")

        # cabeçalho
        Label(self.janelaGrade, text="Horário", width=10, relief="solid",
              borderwidth=1, font=("Verdana", 9, "bold"), bg="SteelBlue").grid(row=0, column=0)
        for j, dia in enumerate(DIAS, start=1):
            Label(self.janelaGrade, text=dia, width=14, relief="solid",
                  borderwidth=1, font=("Verdana", 9, "bold"), bg="SteelBlue").grid(row=0, column=j)

        # células (guardadas para poder atualizar depois)
        self.labelsGrade = {}
        for i, horario in enumerate(HORARIOS, start=1):
            Label(self.janelaGrade, text=horario, width=10, relief="solid",
                  borderwidth=1, bg="SteelBlue").grid(row=i, column=0)
            for j, dia in enumerate(DIAS, start=1):
                lbl = Label(self.janelaGrade, text="-", width=14, relief="solid", borderwidth=1, bg="lightblue")
                lbl.grid(row=i, column=j)
                self.labelsGrade[(horario, dia)] = lbl

        # formulário para alterar
        frame = Frame(self.janelaGrade, bg="lightblue")
        frame.grid(row=len(HORARIOS) + 1, column=0, columnspan=len(DIAS) + 1, pady=20)

        Label(frame, text="Dia:", bg="LightPink").grid(row=0, column=0, padx=3)
        self.cmbDia = Combobox(frame, values=DIAS, state="readonly", width=10)
        self.cmbDia.grid(row=0, column=1, padx=3)

        Label(frame, text="Horário:", bg="LightPink").grid(row=0, column=2, padx=3)
        self.cmbHorario = Combobox(frame, values=HORARIOS, state="readonly", width=8)
        self.cmbHorario.grid(row=0, column=3, padx=3)

        Label(frame, text="Disciplina:", bg="LightPink").grid(row=0, column=4, padx=3)
        self.entGradeDisciplina = Entry(frame, width=15)
        self.entGradeDisciplina.grid(row=0, column=5, padx=3)

        Button(frame, text="Atualizar", bg="SteelBlue", command=self.salvarGrade).grid(row=0, column=6, padx=8)

        Label(self.janelaGrade, text="Dica: deixe a disciplina vazia para limpar o horário.",
              font=("Verdana", 8, "italic"), bg="lightblue").grid(row=len(HORARIOS) + 2, column=0,
                                                  columnspan=len(DIAS) + 1)

        self.atualizarGrade()

    def atualizarGrade(self):
        # escreve na tela o que está guardado na grade do usuário
        for (horario, dia), lbl in self.labelsGrade.items():
            lbl["text"] = self.usuarioLogado.grade[horario][dia]

    def salvarGrade(self):
        # altera um horário da grade e salva no banco
        try:
            dia = self.cmbDia.get()
            horario = self.cmbHorario.get()

            if not dia or not horario:
                raise ValueError("Escolha o dia e o horário.")

            self.usuarioLogado.definir_grade(
                horario,
                dia,
                self.entGradeDisciplina.get()
            )

            # Salva a grade completa do usuário
            banco.salvar_grade(
                self.usuarioLogado.id,
                self.usuarioLogado.grade
            )

            self.entGradeDisciplina.delete(0, END)
            self.atualizarGrade()

        except ValueError as erro:
            showwarning("Atenção", str(erro), parent=self.janelaGrade)


# FUNÇÃO PRINCIPAL
def main():
    # abre o programa na janela de cadastro
    ProgramaMNS().mainloop()


if __name__ == "__main__":
    main()
