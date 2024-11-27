from flask import jsonify, Response
import pandas as pd
import re
import json
import os

class doGet_productInfo:
    def __init__(self):

        # Caminho absoluto para o diretório do script
        base_dir = os.path.dirname(os.path.abspath(__file__))
        
        product_path = os.path.join(base_dir, '..', 'data', 'db_products.csv')
        cosing_path = os.path.join(base_dir, '..', 'data', 'db_cosing.csv')

        self.db_products = pd.read_csv(product_path, delimiter=';', encoding='utf-8-sig')

        self.db_cosing = pd.read_csv(cosing_path, delimiter=';', encoding='utf-8-sig')
        self.db_products['Código de Barras'] = [self.db_products['Código de Barras'][i].replace('"', '') for i,row in self.db_products.iterrows()]
        self.cache = self.load_cache()

        self.populate_cache()
        # self.att_descriptionPerComposition()

    def load_cache(self):
        if os.path.exists('.\\product_info\\product_cache.json'):
            with open('.\\product_info\\product_cache.json', 'r', encoding='utf-8') as f:  # Especifique utf-8 aqui
                try:
                    return {str(k): v for k, v in json.load(f).items()}  # Garantir que as chaves sejam strings
                except json.JSONDecodeError:
                    print("Erro ao decodificar JSON. Inicializando cache vazio.")
                    return {}
        else:
            return {}

    
    def save_cache(self):
        """Salva o cache atual no arquivo JSON, garantindo a correta codificação."""
        try:
            # Abre o arquivo com a codificação UTF-8 explícita para leitura
            with open('.\product_info\product_cache.json', 'r', encoding='utf-8') as f:
                existing_cache = json.load(f)
        except FileNotFoundError:
            existing_cache = {}
        except json.JSONDecodeError:
            print("Erro ao decodificar o arquivo JSON. Verifique se o conteúdo é válido.")
            existing_cache = {}
        except UnicodeDecodeError:
            print("Erro de decodificação Unicode. O arquivo pode não estar em UTF-8.")
            existing_cache = {}

        # Atualiza o cache existente com as novas informações do cache na memória
        existing_cache.update(self.cache)

        # Abre o arquivo para escrita com a codificação UTF-8
        with open('.\product_info\product_cache.json', 'w', encoding='utf-8') as f:
            json.dump(existing_cache, f, indent=4, ensure_ascii=False)

    
    def find_closest_inci_name(self, component, inci_names):
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
    
    def get_product_function(self, ean):

        product_infos = {
            'functionsPerComposition': {},
            'functionOccurrences': {},   # Guarda a primeira ocorrência da composição e a ordem geral de cada função
            'functionPerOcurrenceNumber': {},  # Contagem de ocorrências para cada função
        }

        composition_count = 0
        all_functions = []

        for i, row in self.db_products.iterrows():
            
            if row['Código de Barras'] == ean:

               

                # Verifica se 'Composição' é uma string e não um NaN
                if pd.notna(row['Composição']):

                    product_infos['composition'] = [composition.strip() for composition in row['Composição'].split(sep=',')]
                    product_infos['ref'] = row['REF']
                    product_infos['brand'] = row['Marca']
                    product_infos['name'] = row['Nome do Produto']
                    product_infos['ean'] = ean

                    compositions = [comp.strip() for comp in row['Composição'].split(',')]
                    for composition in compositions:
                        composition_count += 1
                        inci_names = [cosing_row['INCI name'] for cosing_index, cosing_row in self.db_cosing.iterrows()]
                        closest_inci = self.find_closest_inci_name(composition, inci_names)
                        
                        # Após encontrar o INCI mais próximo, obtenha as funções relacionadas
                        if closest_inci:
                            matched_row = self.db_cosing[self.db_cosing['INCI name'].str.contains(re.escape(closest_inci), case=False, regex=True)]
                            if not matched_row.empty:
                                function_list = [func.strip() for func in matched_row.iloc[0]['Function PT'].split(',')]
                                product_infos['functionsPerComposition'][composition] = [func.lower() for func in function_list]
                                if 'descriptionPerComposition' in product_infos:
                                    product_infos['descriptionPerComposition'][composition] = matched_row.iloc[0]['Chem/IUPAC Name / Description']
                                else:
                                    # Se a chave não existir, inicialize-a com um dicionário vazio ou com o valor adequado
                                    product_infos['descriptionPerComposition'] = {composition: matched_row.iloc[0]['Chem/IUPAC Name / Description']}
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
                else:
                    # Trate o caso onde 'Composição' é NaN
                    product_infos['ref'] = row['REF']
                    product_infos['brand'] = row['Marca']
                    product_infos['name'] = row['Nome do Produto'] 
                    product_infos['ean'] = ean
                    product_infos['composition'] = []
        
        return product_infos
    
    def calculate_function_score(self, product_infos):
        # Verificar se há dados para processar
        if not product_infos['functionPerOcurrenceNumber']:
            return {}

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
    
    def populate_cache(self):
        cache_updated = False
        for ean in self.db_products['Código de Barras'].unique():
            ean_str = str(ean)  # Garantir que o EAN é uma string
            if ean_str not in self.cache:
                print(f'Adicionando {ean_str} ao cache.')
                product_info = self.get_product_function(ean_str)
                product_info['functionScores'] = self.calculate_function_score(product_info)
                self.cache[ean_str] = product_info
                cache_updated = True
            else:
                print(f'{ean_str} já está no cache.')

        if cache_updated:
            self.save_cache()


    def att_descriptionPerComposition(self):
        for ean, product_info in self.cache.items():
            # Verifica se 'descriptionPerComposition' já está no cache, caso contrário, inicializa
            if 'descriptionPerComposition' not in product_info:
                product_info['descriptionPerComposition'] = {}

            for composition in product_info.get('composition', []):
                # Converte a composição para minúsculas
                composition_lower = composition.lower()
                
                # Busca correspondência em `db_cosing` com índice em minúsculas
                match = self.db_cosing[self.db_cosing['INCI name'].str.lower() == composition_lower]

                if not match.empty:
                    # Atribui o valor da coluna 'Chem/IUPAC Name / Description' da primeira correspondência
                    description = match['Chem/IUPAC Name / Description'].iloc[0]
                    product_info['descriptionPerComposition'][composition] = description
                else:
                    # Define uma descrição padrão caso não encontre correspondência
                    product_info['descriptionPerComposition'][composition] = "Descrição não encontrada"

            # Atualiza o cache com a nova descrição
            self.cache[ean] = product_info
        
            # Salva o cache atualizado
            self.save_cache()



        

    def process_product_info(self,ean):
        """ Processa e retorna as informações do produto em JSON"""

        if not ean:
            return jsonify({'error': 'EAN code is required'}), 400
        
        if ean in self.cache:
            json_response = json.dumps(self.cache[ean], ensure_ascii=False)

            return Response(json_response, content_type='application/json; charset=utf-8')
        
        product_info = self.get_product_function(ean)
        if not product_info:
            return jsonify({'error': 'Product not found'}), 404
        
        product_info['functionScores'] = self.calculate_function_score(product_info)
        self.cache[ean] = product_info
        self.save_cache()

        json_response = json.dumps(product_info, ensure_ascii=False)

        

        return Response(json_response, content_type='application/json; charset=utf-8')
    
