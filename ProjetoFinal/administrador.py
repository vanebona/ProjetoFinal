import sqlite3
import pygal


class Inventario:
    db = 'database/banco_dados.db'

    # Método para visualizar todos os produtos em estoque
    def visualizar_todos_produtos(self):
        with sqlite3.connect(self.db) as con:
            cursor = con.cursor()
            # Busca todos os produtos
            query = "SELECT imagem,nome,descricao,fornecedor,referencia,quantidade_estoque,local_armazem," \
                    "preco, notificacao_estoque FROM produtos"
            resultado = cursor.execute(query)
            lista_dic = []
        for produto in resultado:
            resultado_dic = dict()
            resultado_dic['imagem'] = produto[0]
            resultado_dic['nome'] = produto[1]
            resultado_dic['descricao'] = produto[2]
            resultado_dic['fornecedor'] = produto[3]
            resultado_dic['referencia'] = produto[4]
            resultado_dic['quantidade_estoque'] = produto[5]
            resultado_dic['local_armazem'] = produto[6]
            resultado_dic['preco'] = produto[7]
            resultado_dic['notificacao_estoque'] = produto[8]
            lista_dic.append(resultado_dic)
        return lista_dic

    # Método para gerar gráfico que informam ao administrador a quantidade de venda por produto e o lucro total
    def gerar_graficos(self):
        with sqlite3.connect(self.db) as con:
            cursor = con.cursor()
            # Busca todas as vendas, agrupadas por produto e suas quantidades e os lucros
            query = "SELECT vendas.referencia, sum(vendas.quantidade_venda) as quantidade_venda_total, produtos.nome," \
                    "sum(vendas.lucro) as lucro_total  FROM vendas JOIN produtos ON " \
                    "produtos.referencia=vendas.referencia GROUP BY vendas.referencia "
            resultado = cursor.execute(query)
            lista_dic = []
        for dado in resultado:
            resultado_dic = dict()
            resultado_dic['referencia'] = dado[0]
            resultado_dic['quantidade_venda_total'] = dado[1]
            resultado_dic['nome'] = dado[2]
            resultado_dic['lucro_total'] = dado[3]
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
        chart.render_to_file('static/admin_quantidade_venda.svg')

        # Inicializa o objeto do gráfico
        chart = pygal.Bar()
        # Gera uma lista com os dados que fazem parte do eixo Y
        quant_list = [x['lucro_total'] for x in lista_dic]
        # Gera uma lista com os dados que fazem parte do eixo X
        nome_list = [x['nome'] for x in lista_dic]
        # Adiciona os dados do eixo Y ao gráfico
        chart.add('Produto', quant_list)
        # Adiciona os dados do eixo X ao gráfico
        chart.x_labels = nome_list
        # Renderiza o gráfico e salva em um ficheiro
        chart.render_to_file('static/admin_lucro_total.svg')
