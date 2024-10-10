from abc import ABC, abstractmethod
from datetime import datetime
import textwrap

class Transacao(ABC):
    @property
    @abstractmethod
    def valor(self):
        pass

    @abstractmethod
    def registrar_transacao(self, conta):
        pass

class Deposito(Transacao):
    def __init__(self, valor):
        self._valor = valor

    @property
    def valor(self):
        return self._valor

    def registrar_transacao(self, conta):
        conta._saldo += self._valor

class Saque(Transacao):
    def __init__(self, valor):
        self._valor = valor

    @property
    def valor(self):
        return self._valor

    def registrar_transacao(self, conta):
        if conta._saldo >= self._valor:
            conta._saldo -= self._valor
            print("Saque realizado com sucesso.")
        else:
            print("Saldo insuficiente para o saque.")

class Historico:
    def __init__(self):
        self._transacoes = []

    @property
    def transacoes(self):
        return self._transacoes
    
    def adicionar_transacao(self, transacao):
        self._transacoes.append(
            {
                'tipo': transacao.__class__.__name__,
                'valor': transacao.valor,
                'data': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }
        )

class Cliente:
    def __init__(self, endereco):
        self.endereco = endereco
        self.contas = []

    def registrar_transacao(self, conta, transacao):
        transacao.registrar_transacao(conta)
        conta.historico.adicionar_transacao(transacao)
    
    def adicionar_conta(self, conta):
        self.contas.append(conta)

class PessoaFisica(Cliente):
    def __init__(self, nome, data_nascimento, cpf, endereco):
        super().__init__(endereco)
        self.nome = nome
        self.data_nascimento = data_nascimento
        self.cpf = cpf

class Conta:
    def __init__(self, numero, cliente):
        self._saldo = 0
        self._numero = numero
        self._agencia = "0001"
        self._cliente = cliente
        self._historico = Historico()
        cliente.adicionar_conta(self)
    
    @classmethod
    def nova_conta(cls, cliente, numero):
        return cls(numero, cliente)

    @property
    def saldo(self):
        return self._saldo
    
    @property
    def numero(self):
        return self._numero
    
    @property
    def agencia(self):
        return self._agencia
    
    @property
    def cliente(self):
        return self._cliente
    
    @property
    def historico(self):
        return self._historico

    def sacar(self, valor):
        if valor > self._saldo:
            print("Você não tem saldo suficiente.")
            return False
        elif valor > 0:
            self._saldo -= valor
            print("Saque realizado com sucesso.")
            return True
        else:
            print("Valor informado é inválido.")
            return False
    
    def depositar(self, valor):
        if valor > 0:
            self._saldo += valor
            print("Depósito realizado com sucesso.")
            return True
        else:
            print("Valor informado é inválido.")
            return False

class ContaCorrente(Conta):
    def __init__(self, numero, cliente, limite=500, limite_saques=3):
        super().__init__(numero, cliente)
        self.limite = limite
        self.limite_saques = limite_saques

    def sacar(self, valor):
        numero_saques = len(
            [transacao for transacao in self.historico.transacoes if transacao["tipo"] == Saque.__name__]
        )
        excedeu_limite = valor > self.limite
        excedeu_saques = numero_saques >= self.limite_saques

        if excedeu_limite:
            print("Saque excede o limite.")
            return False
        elif excedeu_saques:
            print("Número máximo de saques excedido.")
            return False
        else:
            return super().sacar(valor)
    
    def __str__(self):      
        return f"""\
            Agência:\t{self.agencia}
            C/C:\t\t{self.numero}
            Titular:\t{self.cliente.nome}
        """

def menu():
    menu = """\n
    ================ MENU ================
    [d]\tDepositar
    [s]\tSacar
    [e]\tExtrato
    [nc]\tNova conta
    [lc]\tListar contas
    [nu]\tNovo usuário
    [q]\tSair
    => """
    return input(textwrap.dedent(menu))

def depositar(contas):
    cpf = input("Informe o CPF do usuário: ")
    valor = float(input("Informe o valor do depósito: "))
    conta = filtrar_conta_por_cpf(cpf, contas)
    if conta:
        conta.depositar(valor)
    else:
        print("\n@@@ Conta não encontrada. @@@")

def sacar(contas):
    cpf = input("Informe o CPF do usuário: ")
    valor = float(input("Informe o valor do saque: "))
    conta = filtrar_conta_por_cpf(cpf, contas)
    if conta:
        conta.sacar(valor)
    else:
        print("\n@@@ Conta não encontrada. @@@")

def exibir_extrato(contas):
    cpf = input("Informe o CPF do usuário: ")
    conta = filtrar_conta_por_cpf(cpf, contas)
    if conta:
        print("\n================ EXTRATO ================")
        for transacao in conta.historico.transacoes:
            print(f"Transação: {transacao['tipo']}, Valor: {transacao['valor']}, Data: {transacao['data']}")
        print(f"\nSaldo:\t\tR$ {conta.saldo:.2f}")
        print("==========================================")
    else:
        print("\n@@@ Conta não encontrada. @@@")

def criar_usuario(usuarios):
    cpf = input("Informe o CPF (somente número): ")
    usuario = filtrar_usuario(cpf, usuarios)

    if usuario:
        print("\n@@@ Já existe usuário com esse CPF! @@@")
        return

    nome = input("Informe o nome completo: ")
    data_nascimento = input("Informe a data de nascimento (dd-mm-aaaa): ")
    endereco = input("Informe o endereço (logradouro, nro - bairro - cidade/sigla estado): ")

    usuarios.append(PessoaFisica(nome, data_nascimento, cpf, endereco))

    print("=== Usuário criado com sucesso! ===")

def filtrar_usuario(cpf, usuarios):
    usuarios_filtrados = [usuario for usuario in usuarios if usuario.cpf == cpf]
    return usuarios_filtrados[0] if usuarios_filtrados else None

def criar_conta(numero_conta, usuarios, contas):
    cpf = input("Informe o CPF do usuário: ")
    usuario = filtrar_usuario(cpf, usuarios)

    if usuario:
        conta = ContaCorrente.nova_conta(usuario, numero_conta)
        contas.append(conta)
        print("\n=== Conta criada com sucesso! ===")
    else:
        print("\n@@@ Usuário não encontrado, fluxo de criação de conta encerrado! @@@")

def listar_contas(contas):
    for conta in contas:
        print("=" * 100)
        print(conta)

def filtrar_conta_por_cpf(cpf, contas):
    for conta in contas:
        if conta.cliente.cpf == cpf:
            return conta
    return None

def main():
    usuarios = []
    contas = []

    while True:
        opcao = menu()

        if opcao == "d":
            depositar(contas)

        elif opcao == "s":
            sacar(contas)

        elif opcao == "e":
            exibir_extrato(contas)

        elif opcao == "nu":
            criar_usuario(usuarios)

        elif opcao == "nc":
            numero_conta = len(contas) + 1
            criar_conta(numero_conta, usuarios, contas)

        elif opcao == "lc":
            listar_contas(contas)

        elif opcao == "q":
            break

        else:
            print("Operação inválida, por favor selecione novamente a operação desejada.")

main()