from flask import Flask, jsonify, request
import pandas as pd
import re

db_products = pd.read_csv('.\data\db_products.csv', delimiter=';', encoding='utf-8-sig')
db_cosing = pd.read_csv('.\data\db_cosing.csv', delimiter=';', encoding='utf-8-sig')

db_products['Código de Barras'] = [db_products['Código de Barras'][i].replace('"', '') for i,row in db_products.iterrows()]

def find_closest_inci_name(component, inci_names):
    """ Encontra o nome INCI mais próximo baseado na regex. """
    # Escapa caracteres especiais em componentes para uso em regex
    pattern = re.escape(component.strip().lower())
    best_match = None
    best_score = 0

    for inci_name in inci_names:
        # Verifica quantas palavras em `component` aparecem em `inci_name`
        matches = re.findall(pattern, inci_name.lower())
        score = len(matches)
        if score > best_score:
            best_score = score
            best_match = inci_name

    return best_match


def get_product_function(ean):
    product_infos = {
        'functionsPerComposition': {},
        'functionOccurrences': {},   # Guarda a primeira ocorrência da composição e a ordem geral de cada função
        'functionPerOcurrenceNumber': {},  # Contagem de ocorrências para cada função
    }
    

    composition_count = 0
    all_functions = []

    for i, row in db_products.iterrows():
        if row['Código de Barras'] == ean:

            product_infos['ref'] = row['REF']
            product_infos['brand'] = row['Marca']
            product_infos['name'] = row['Nome do Produto']
            product_infos['ean'] = ean
            product_infos['composition'] = [composition.strip() for composition in row['Composição'].split(sep=',')]

            compositions = [comp.strip() for comp in row['Composição'].split(',')]
            for composition in compositions:
                composition_count += 1
                inci_names = [cosing_row['INCI name'] for cosing_index, cosing_row in db_cosing.iterrows()]
                closest_inci = find_closest_inci_name(composition, inci_names)
                
                # Após encontrar o INCI mais próximo, obtenha as funções relacionadas
                if closest_inci:
                    matched_row = db_cosing[db_cosing['INCI name'].str.contains(re.escape(closest_inci), case=False, regex=True)]
                    if not matched_row.empty:
                        function_list = [func.strip() for func in matched_row.iloc[0]['Function PT'].split(',')]
                        product_infos['functionsPerComposition'][composition] = [func.lower() for func in function_list]
                        for function in function_list:
                            function_lower = function.lower()
                            if function_lower not in product_infos['functionOccurrences']:
                                all_functions.append(function_lower)
                                product_infos['functionOccurrences'][function_lower] = [composition_count, len(all_functions)]
                            
                            # Adiciona ou incrementa a contagem de ocorrências de cada função
                            if function_lower in product_infos['functionPerOcurrenceNumber']:
                                product_infos['functionPerOcurrenceNumber'][function_lower] += 1
                            else:
                                product_infos['functionPerOcurrenceNumber'][function_lower] = 1

    return product_infos


def calculate_function_score(product_infos):
    # Pesos: Suponha que a frequência é duas vezes mais importante que a posição
    peso_frequencia = 2.0
    peso_posicao = 1.0

    max_occurrence = max(product_infos['functionPerOcurrenceNumber'].values())  # Máximo de ocorrências para normalização
    min_position = min(val[0] for val in product_infos['functionOccurrences'].values())  # Mínima posição para normalização

    function_scores = {}

    for function, details in product_infos['functionOccurrences'].items():
        # Normalizando valores
        normalized_occurrence = product_infos['functionPerOcurrenceNumber'][function] / max_occurrence
        normalized_position = (min_position / details[0])  # Inverte para que menor posição tenha maior score

        # Cálculo do score
        score = (peso_frequencia * normalized_occurrence) + (peso_posicao * normalized_position)
        function_scores[function] = float(f"{score:.2f}")

    return function_scores

# Criar a aplicação em Flask
app = Flask(__name__)
    
@app.route('/product-info', methods=['GET'])
def get_product_info():
    barcode = request.args.get('ean', default=None)
    if not barcode:
        return jsonify({'error': 'EAN code is required'}), 400
    product_info = get_product_function(barcode)
    product_info['functionScores'] = {}
    product_info['functionScores'] = calculate_function_score(product_info)
    
    return jsonify(product_info)

@app.route('/product-has-function', methods=['GET'])
def get_product_functions():
    pass

if __name__ == '__main__':
    app.run()