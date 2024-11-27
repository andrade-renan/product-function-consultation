from flask import jsonify, Response, send_file
import pandas as pd
from tkinter import Tk
from tkinter.filedialog import asksaveasfilename
import xlsxwriter
import io
import json
import os
import threading

from product_info.product_info import doGet_productInfo

class doGet_groupIngredients:
    def __init__(self):
        self.getpath_product_info = doGet_productInfo()
        

    def _get_product_info(self, ean):
        return self.getpath_product_info.process_product_info(ean)
    
    def comparison_spreadsheet(self, ean_list):
        # Dicionário para armazenar dados com ingredientes únicos
        ingredients_dict = {}
        
        # Primeiro, recuperar as informações dos produtos para formar a primeira linha
        product_compositions = {}
        for ean in ean_list:
            infos = self._get_product_info(ean).get_json()
            product_name = infos['name']
            product_compositions[product_name] = ', '.join(infos['composition'])

            # Iterar sobre cada ingrediente e funções associadas
            for ingredient, description in infos['descriptionPerComposition'].items():
                if ingredient not in ingredients_dict:
                    ingredients_dict[ingredient] = {
                        'Descrição': set(),
                        'Funções': set(infos['functionsPerComposition'].get(ingredient, []))
                    }

                ingredients_dict[ingredient][product_name] = ', '.join(infos['functionsPerComposition'].get(ingredient, []))
                ingredients_dict[ingredient]['Descrição'].add(description)
                ingredients_dict[ingredient]['Funções'].update(infos['functionsPerComposition'].get(ingredient, []))

        # Estrutura tabular para os dados
        data = [{'Ingrediente': 'Composition', **product_compositions}]
        
        # Adicionando dados dos ingredientes
        for ingredient, info in ingredients_dict.items():
            row = {
                'Ingrediente': ingredient,
                'Descrição': ', '.join(info['Descrição']),
            }
            for product_name in product_compositions.keys():
                row[product_name] = info.get(product_name, '-')
            
            data.append(row)

        # Criação do DataFrame
        df = pd.DataFrame(data)

        # Salvar o DataFrame em um buffer de memória
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name='Ingredientes')

        buffer.seek(0)  # Move o ponteiro para o início do buffer

        return buffer
        
        