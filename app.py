from flask import Flask, jsonify, request
import pandas as pd
import re

db_products = pd.read_csv('.\data\db_products.csv', delimiter=';', encoding='utf-8-sig')
db_cosing = pd.read_csv('.\data\db_cosing.csv', delimiter=';', encoding='utf-8-sig')

db_products['Código de Barras'] = [db_products['Código de Barras'][i].replace('"', '') for i,row in db_products.iterrows()]

def get_product_function(ean):

    functions = {}

    for i, row in db_products.iterrows():
        if row['Código de Barras'] == ean:
            compositions = row['Composição']
            compositions = compositions.split(sep=',')
            # print(compositions)

            for composition in compositions:
                composition = composition.strip()

                for j, cosing_row in db_cosing.iterrows():
                    # print(cosing_row['INCI name'].strip())
                    if composition.upper() == cosing_row['INCI name'].strip():
                        print('achei!')
                        functions[composition] = cosing_row['Function PT'].split(sep=',')
                    
                if composition not in functions.keys():
                    functions[composition]: 'Não encontrado'

    all_composition = []
    for composition in functions.keys():
        all_composition += functions[composition]



    # print(all_composition)

    print(functions)
                    
            
        
get_product_function('7898305625775')
     
'''
def get_db_connection():
    try:
        server = 'DANIELKUNIHIRO\MSSQLSERVER01'  # Ou 'localhost\\SQLEXPRESS'
        database = 'db_product-inci'
        conn = pyodbc.connect(f'DRIVER={{SQL Server}};SERVER={server};DATABASE={database};Trusted_Connection=yes', timeout=5)
        return conn
    except Exception as e:
        print(f"Erro ao conectar ao banco de dados: {e}")
        return None  # Retorna None para indicar falha


# Criar a aplicação em Flask
app = Flask(__name__)

def get_products():
    # Função para retornar uma lista de produtos ou as informações de um produto específicado
    conn = get_db_connection()
    cursor = conn.cursor()

    # Recuperando o código de barras da URL se fornecido
    barcode = request.args.get('ean', default=None)

    # Modificar a consulta SQL com base na presença do códigto de barras
    if barcode:
        cursor.execute("EXEC function_info_by_productEan @ean = ?", (barcode,))
        # cursor.execute('SELECT * FROM db_products WHERE código_de_barras = ?', (barcode,))
    else: 
        cursor.execute('SELECT * FROM db_products')
    
    products = cursor.fetchall()
    cursor.close()
    conn.close()

    # Conveter os resultados em uma lista de dicionários para jsonify
    # products_list = [{'ref': product[0],'brand': product[1] ,'name': product[2], 'cateogory': product[3], 'price': product[4], 'description': product[5],'ean': barcode ,'use_mode': product[7], 'composition': product[8]} for product in products]
    products_list = [{'function': product[0], 'qtd': product[1]} for product in products]
    return jsonify(products_list)



    
@app.route('/product-info', methods=['GET'])
def get_product_info():
    barcode = request.args.get('ean', default=None)
    if not barcode:
        return jsonify({'error': 'EAN code is required'}), 400
    
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        sql = 'SET NOCOUNT ON; EXEC function_info_by_productEan @ean=?'
        values = (barcode)
        cursor.execute(sql, (values))
        # cursor.execute("EXEC function_info_by_productEan(?)", (barcode,))
        results = cursor.fetchall()
        # Assumindo que a função retorna colunas específicas, ajuste conforme necessário
        product_info = [{'function': row[0], 'qtd': row[1]} for row in results]
        return jsonify(product_info)
    except Exception as e:
        return jsonify({'error': 'Failed to fetch data', 'message': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

if __name__ == '__main__':
    app.run()


'''