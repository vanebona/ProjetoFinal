import sqlite3
import pygal


class Estoque:
    db = 'database/banco_dados.db'

    # Método para visualizar todos os produtos que estão disponíveis
    def visualizar_produtos(self):
        with sqlite3.connect(self.db) as con:
            cursor = con.cursor()
            # Busca todos os produtos na base de dados
            query = "SELECT imagem,nome,descricao,cor,referencia,preco FROM produtos"
            resultado = cursor.execute(query)
            print(resultado)
            lista_dic = []
        for produto in resultado:
            resultado_dic = dict()
            resultado_dic['imagem'] = produto[0]
            resultado_dic['nome'] = produto[1]
            resultado_dic['descricao'] = produto[2]
            resultado_dic['cor'] = produto[3].split(";")
            resultado_dic['referencia'] = produto[4]
            resultado_dic['preco'] = produto[5]
            lista_dic.append(resultado_dic)
        return lista_dic


class Venda:
    db = 'database/banco_dados.db'

    # Métodos para inserir produtos no carrinho
    def adicionar_carrinho(self, email, referencia, quantidade_carrinho, cor):
        with sqlite3.connect(self.db) as con:
            cursor = con.cursor()
            # Insere um produto no carrinho
            query = "INSERT INTO carrinho (email,referencia,quantidade_carrinho,cor) VALUES (?,?,?,?)"
            parametros = (email, referencia, quantidade_carrinho, cor)
            resultado = cursor.execute(query, parametros)
            return resultado

    # Método para mostrar todos os produtos que estão no carrinho do utilizador
    def itens_carrinho(self, email):
        with sqlite3.connect(self.db) as con:
            cursor = con.cursor()
            # Busca todos os produtos existentes no carrinho de um utilizador
            query = "SELECT produtos.imagem, produtos.nome, produtos.referencia, carrinho.cor," \
                    "carrinho.quantidade_carrinho, carrinho.quantidade_carrinho*produto_fornecedor.preco_fornecedor " \
                    "as preco_total_fornecedor, carrinho.quantidade_carrinho*produtos.preco as preco_total FROM " \
                    "carrinho JOIN produtos ON produtos.referencia=carrinho.referencia JOIN produto_fornecedor ON " \
                    "produto_fornecedor.referencia=carrinho.referencia WHERE carrinho.email=? "
            parametros = ([email])
            resultado = cursor.execute(query, parametros)
            lista_dic = []
            for produto in resultado:
                resultado_dic = dict()
                resultado_dic['imagem'] = produto[0]
                resultado_dic['nome'] = produto[1]
                resultado_dic['referencia'] = produto[2]
                resultado_dic['cor'] = produto[3]
                resultado_dic['quantidade_carrinho'] = produto[4]
                resultado_dic['preco_total_fornecedor'] = produto[5]
                resultado_dic['preco_total'] = produto[6]
                lista_dic.append(resultado_dic)
            return lista_dic

    # Método para fazer a soma de todos os produtos que estão no carrinho
    def total(self, email):
        with sqlite3.connect(self.db) as con:
            cursor = con.cursor()
            # Calcula preço total e quantidade total do carrinho de um utilizador
            query = "SELECT SUM(carrinho.quantidade_carrinho) as quant_total, " \
                    "SUM(carrinho.quantidade_carrinho*produtos.preco) as preco_total FROM carrinho JOIN produtos ON " \
                    "produtos.referencia=carrinho.referencia WHERE carrinho.email=? "
            parametros = ([email])
            resultado = cursor.execute(query, parametros)
            resultado_dic = dict()
            for produto in resultado:
                resultado_dic['quant_total'] = produto[0]
                resultado_dic['preco_total'] = produto[1]
            return resultado_dic

    # Método que é chamado ao finalizar a compra
    def finalizar_compra(self, email):
        itens_carrinho = self.itens_carrinho(email)
        with sqlite3.connect(self.db) as con:
            for produto in itens_carrinho:
                cursor = con.cursor()
                # Atualiza o estoque de um produto após a venda
                query = "UPDATE produtos SET quantidade_estoque=quantidade_estoque-? WHERE referencia=?"
                parametros = (produto['quantidade_carrinho'], produto['referencia'])
                cursor.execute(query, parametros)
                # Cria uma venda
                query = "INSERT INTO vendas (referencia, quantidade_venda, preco, " \
                        "preco_fornecedor,lucro, email) VALUES (?,?,?,?,?,?) "
                parametros = (produto['referencia'], produto['quantidade_carrinho'], produto['preco_total'],
                              produto['preco_total_fornecedor'],
                              produto['preco_total'] - produto['preco_total_fornecedor'], email)
                cursor.execute(query, parametros)
                # Remove o item do carrinho
                query = "DELETE FROM carrinho WHERE email=?"
                parametros = ([email])
                cursor.execute(query, parametros)

    # Método para gerar um gráfico, informando ao cliente a quantidade de produtos foi vendido
    def gerar_grafico(self, email):
        with sqlite3.connect(self.db) as con:
            cursor = con.cursor()
            # Busca todas as vendas, agrupadas por produto e suas quantidades para um utilizador
            query = "SELECT vendas.referencia, sum(vendas.quantidade_venda) as quantidade_venda_total, produtos.nome "\
                    "FROM vendas JOIN produtos ON produtos.referencia=vendas.referencia WHERE vendas.email=? GROUP BY "\
                    "vendas.referencia "
            parametro = ([email])
            resultado = cursor.execute(query, parametro)
            lista_dic = []
        for dado in resultado:
            resultado_dic = dict()
            resultado_dic['referencia'] = dado[0]
            resultado_dic['quantidade_venda_total'] = dado[1]
            resultado_dic['nome'] = dado[2]
            lista_dic.append(resultado_dic)

        # Inicializa o objeto do gráfico
        chart = pygal.Bar()
        # Gera uma lista com os dados que fazem parte do eixo Y
        quant_list = [x['quantidade_venda_total'] for x in lista_dic]
        # Gera uma lista com os dados que fazem parte do eixo X
        nome_list = [x['nome'] for x in lista_dic]
        # Adiciona os dados do eixo Y ao gráfico
        chart.add('Produto', quant_list)
        # Adiciona os dados do eixo X ao gráfico
        chart.x_labels = nome_list
        # Renderiza o gráfico e salva em um ficheiro
        chart.render_to_file('static/cliente_quantidade_venda.svg')
