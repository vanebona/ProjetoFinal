import sqlite3
import pygal


class DadosFornecedor:
    db = 'database/banco_dados.db'

    def __init__(self, email):
        self.email = email

    # Método para visualizar dados de um fornecedor
    def visualizar_dados(self):
        with sqlite3.connect(self.db) as con:
            cursor = con.cursor()
            # Busca os dados de um fornecedor específico
            query = "SELECT nome,telefone,endereco,NIF,email FROM fornecedora where email=?"
            parametro = ([self.email])
            resultado = cursor.execute(query, parametro)
            lista_dic = []
        for dado in resultado:
            resultado_dic = dict()
            resultado_dic['nome'] = dado[0]
            resultado_dic['telefone'] = dado[1]
            resultado_dic['endereco'] = dado[2]
            resultado_dic['NIF'] = dado[3]
            resultado_dic['email'] = dado[4]
            lista_dic.append(resultado_dic)
        return lista_dic

    # Método utilizado para mostrar todos os fornecedores
    def fornecedores(self):
        with sqlite3.connect(self.db) as con:
            cursor = con.cursor()
            # Busca todos os fornecedores
            query = "SELECT nome,email FROM fornecedora"
            resultado = cursor.execute(query)
            lista_dic = []
        for dado in resultado:
            resultado_dic = dict()
            resultado_dic['nome'] = dado[0]
            resultado_dic['email'] = dado[1]
            lista_dic.append(resultado_dic)
        return lista_dic


class ProdutosFornecedor:
    db = 'database/banco_dados.db'

    def __init__(self, email):
        self.email = email

    # Método para mostrar todos os produtos de um determinado fornecedor
    def visualizar_produtos_fornecedor(self):
        with sqlite3.connect(self.db) as con:
            cursor = con.cursor()
            # Busca todos os produtos de um fornecedor especifico
            query = "SELECT produtos.imagem, produtos.nome,produtos.descricao,produtos.cor,produtos.referencia," \
                    "produto_fornecedor.preco_fornecedor,produto_fornecedor.porcentagem,produto_fornecedor.iva FROM " \
                    "produtos JOIN produto_fornecedor ON produtos.referencia=produto_fornecedor.referencia WHERE " \
                    "produtos.fornecedor=? "
            parametro = ([self.email])
            resultado = cursor.execute(query, parametro)
            lista_dic = []
        for dado in resultado:
            resultado_dic = dict()
            resultado_dic['imagem'] = dado[0]
            resultado_dic['nome'] = dado[1]
            resultado_dic['descricao'] = dado[2]
            resultado_dic['cor'] = dado[3].split(";")
            resultado_dic['referencia'] = dado[4]
            resultado_dic['preco_fornecedor'] = dado[5]
            resultado_dic['porcentagem'] = dado[6]
            resultado_dic['iva'] = dado[7]
            lista_dic.append(resultado_dic)
        return lista_dic

    # Método para gerar um gráfico, informando ao fornecedor a quantidade de produtos que foram fornecidos
    def gerar_grafico(self):
        with sqlite3.connect(self.db) as con:
            cursor = con.cursor()
            # Busca todos os produtos fornecidos e suas quantidades
            query = "SELECT produto_fornecedor.referencia,produto_fornecedor.quantidade_fornecido,produtos.nome, " \
                    "produto_fornecedor.preco_fornecedor FROM produto_fornecedor JOIN produtos ON " \
                    "produtos.referencia=produto_fornecedor.referencia WHERE produtos.fornecedor=? "
            parametro = ([self.email])
            resultado = cursor.execute(query, parametro)
            lista_dic = []
        for dado in resultado:
            resultado_dic = dict()
            resultado_dic['referencia'] = dado[0]
            resultado_dic['quantidade_fornecido'] = dado[1]
            resultado_dic['nome'] = dado[2]
            resultado_dic['preco_fornecedor'] = dado[3]
            lista_dic.append(resultado_dic)

        # Inicializa o objeto do gráfico
        chart = pygal.Bar()
        # Gera uma lista com os dados que fazem parte do eixo Y
        quant_list = [x['quantidade_fornecido'] for x in lista_dic]
        # Gera uma lista com os dados que fazem parte do eixo X
        nome_list = [x['nome'] for x in lista_dic]
        # Adiciona os dados do eixo Y ao gráfico
        chart.add('Produto', quant_list)
        # Adiciona os dados do eixo X ao gráfico
        chart.x_labels = nome_list
        # Renderiza o gráfico e salva em um ficheiro
        chart.render_to_file('static/fornecedor_venda_produto.svg')

    # Método para gerar um gráfico, informando ao fornecedor o lucro total por produto fornecido
    def gerar_grafico_soma(self):
        with sqlite3.connect(self.db) as con:
            cursor = con.cursor()
            # Busca todos os produtos fornecidos e seus valores de venda
            query = "SELECT produto_fornecedor.referencia,produto_fornecedor.quantidade_fornecido,produtos.nome, " \
                    "produto_fornecedor.preco_fornecedor," \
                    "produto_fornecedor.preco_fornecedor*produto_fornecedor.quantidade_fornecido AS " \
                    "preco_total_produto FROM produto_fornecedor JOIN produtos ON " \
                    "produtos.referencia=produto_fornecedor.referencia WHERE produtos.fornecedor=? "
            parametro = ([self.email])
            resultado = cursor.execute(query, parametro)
            lista_dic = []
        for dado in resultado:
            resultado_dic = dict()
            resultado_dic['referencia'] = dado[0]
            resultado_dic['quantidade_fornecido'] = dado[1]
            resultado_dic['nome'] = dado[2]
            resultado_dic['preco_fornecedor'] = dado[3]
            resultado_dic['preco_total_produto'] = dado[4]
            lista_dic.append(resultado_dic)

        # Inicializa o objeto do gráfico
        chart = pygal.Bar()
        # Gera uma lista com os dados que fazem parte do eixo Y
        preco_list = [x['preco_total_produto'] for x in lista_dic]
        # Gera uma lista com os dados que fazem parte do eixo X
        nome_list = [x['nome'] for x in lista_dic]
        # Adiciona os dados do eixo Y ao gráfico
        chart.add('Produto', preco_list)
        # Adiciona os dados do eixo X ao gráfico
        chart.x_labels = nome_list
        # Renderiza o gráfico e salva em um ficheiro
        chart.render_to_file('static/fornecedor_venda_produto2.svg')
