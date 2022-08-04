from flask import Flask, render_template, request, redirect, url_for
import sqlite3

from cliente import Estoque, Venda
from fornecedor import DadosFornecedor, ProdutosFornecedor
from administrador import Inventario

app = Flask(__name__)


class Login:
    db = 'database/banco_dados.db'

    def __init__(self, email, senha):
        self.email = email
        self.senha = senha

    # Método para verificação de 'login', consultando a base de dados
    def verificar_login(self):
        with sqlite3.connect(self.db) as con:
            cursor = con.cursor()
            query = "SELECT * FROM login where email=? AND senha=?"
            parametros = (self.email, self.senha)
            resultado = cursor.execute(query, parametros)
            lista_dic = []
            # Convertendo a lista em dicionário
            for utilizador in resultado:
                resultado_dic = dict()
                resultado_dic['email'] = utilizador[0]
                resultado_dic['tipo'] = utilizador[2]
                lista_dic.append(resultado_dic)
            return lista_dic


@app.route('/')
def home():
    return render_template("index.html")


@app.route('/logout')
def logout():
    return home()


@app.route('/cliente')
def cliente():
    email = request.args.get('email')
    estoque = Estoque()
    lista_produtos = estoque.visualizar_produtos()
    venda = Venda()
    venda.gerar_grafico(email)
    return render_template("cliente.html", listaProdutos=lista_produtos, email=email)


@app.route('/carrinho', methods=['POST'])
def carrinho():
    email = request.args.get('email')
    itens_carrinho = Venda()
    lista_produtos = itens_carrinho.itens_carrinho(email)
    total = itens_carrinho.total(email)
    return render_template("carrinho.html", listaProdutos=lista_produtos, total=total, email=email)


@app.route('/fornecedor')
def fornecedor():
    email = request.args.get('email')
    dados_fornecedor = DadosFornecedor(email)
    lista_dados = dados_fornecedor.visualizar_dados()
    produtos_fornecedor = ProdutosFornecedor(email)
    lista_produtos_fornecedor = produtos_fornecedor.visualizar_produtos_fornecedor()
    produtos_fornecedor.gerar_grafico()
    produtos_fornecedor.gerar_grafico_soma()
    return render_template("fornecedor.html", listaDados=lista_dados, listaProdutosFornecedor=lista_produtos_fornecedor)


@app.route('/administrador')
def administrador():
    inventario = Inventario()
    dados_fornecedor = DadosFornecedor("")
    lista_todos_produtos = inventario.visualizar_todos_produtos()
    fornecedores = dados_fornecedor.fornecedores()
    inventario.gerar_graficos()
    return render_template("administrador.html", listaTodosProdutos=lista_todos_produtos, fornecedores=fornecedores)


@app.route('/login', methods=['POST'])
# Método usado para verificação de 'login'
def login():
    conta = Login(request.form['email'], request.form['senha'])
    resposta = conta.verificar_login()
    login_valido = False
    tipo_login = ''
    email = ''
    # Filtrando pelo 'tipo' de utilizador que está fazendo o login
    for utilizador in resposta:
        login_valido = True
        tipo_login = utilizador['tipo']
        email = utilizador['email']

    # Redireciona para o respectivo ecrã (Cliente, Fornecedor ou Administrador)
    if login_valido:
        if tipo_login == 'cliente':
            return redirect(url_for('cliente', email=email))
        if tipo_login == 'fornecedor':
            return redirect(url_for('fornecedor', email=email))

        if tipo_login == 'administrador':
            return redirect(url_for('administrador'))
    # Caso o e-mail e senha sejam digitados errados irá aparecer a mensagem de erro
    else:
        return render_template("index.html", loginErro=True)


@app.route('/adicionar_carrinho', methods=['POST'])
def adicionar_carrinho():
    venda = Venda()
    venda.adicionar_carrinho(request.args['email'], request.args['referencia'], request.form['quant'],
                             request.form['cor'])
    return cliente()


@app.route('/finalizar_compra', methods=['POST'])
def finalizar_compra():
    venda = Venda()
    venda.finalizar_compra(request.args['email'])
    return cliente()


if __name__ == '__main__':
    app.run(debug=True)
