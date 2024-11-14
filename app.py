from product_info.product_info import doGet_productInfo
from group_ingredients.group_ingredients import doGet_groupIngredients
from flask import Flask, request


# Criar a aplicação em Flask
app = Flask(__name__)

getPath_product_info = doGet_productInfo()
getPath_groupIngredients = doGet_groupIngredients()
    
@app.route('/product-info', methods=['GET'])
def get_product_info():
    barcode = request.args.get('ean', default=None)
    return getPath_product_info.process_product_info(barcode)

@app.route('/group-ingredients', methods=['GET'])
def group_products_ingredients():
    barcodes_str = request.args.get('eans', default=None)
    barcode_list = barcodes_str.split(',')
    getPath_groupIngredients.comparison_spreadsheet(barcode_list)
    return barcode_list

"""
Essa chamada agrupa os produtos em Ingrediente, Produto 1, Produto 2, etc. em colunas onde:
Ingrediente: Nome do Ingrediente
Produtos: Funções daquele ingredientes relativa ao produto
"""

if __name__ == '__main__':
    app.run(debug=True)