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
        
        # Iterar sobre cada EAN para obter as informações do produto
        for ean in ean_list:
            infos = self._get_product_info(ean).get_json()
            product_name = infos['name']
            # Itera sobre cada ingrediente e funções associadas

            for ingredient, description in infos['descriptionPerComposition'].items():
                # Se o ingrediente não está no dicionário, adiciona-o com um conjunto de funções e presença de produtos
                if ingredient not in ingredients_dict:
                    ingredients_dict[ingredient] = {
                        'Descrição': set(),
                        'Funções': set(infos['functionsPerComposition'].get(ingredient, []))
                    }
                

                # Adiciona o produto à entrada do ingrediente, com a funççao caso haja presença
                ingredients_dict[ingredient][product_name] = ', '.join(infos['functionsPerComposition'].get(ingredient, []))

                # Atualiza as funções do ingrediente, mantendo-as únicas
                ingredients_dict[ingredient]['Descrição'].add(description)
                ingredients_dict[ingredient]['Funções'].update(infos['functionsPerComposition'].get(ingredient, []))
            


            # Converte o dicionário para uma estrutura tabular
            data = []
            for ingredient, info in ingredients_dict.items():
                # Cria uma linha com ingrediente, funções unidas por vírgulas, e presença de cada produto
                row = {
                    'Ingrediente': ingredient,
                    'Descrição': ', '.join(info['Descrição']),  # Converte o conjunto para string
                } 
                # Adiciona a presença do produto como "Sim" ou "Não" para cada produto
                for ean in ean_list:
                    product_name = self._get_product_info(ean).get_json()['name']
                    row[product_name] = info.get(product_name, '-') 
                
                data.append(row)

        # Cria o DataFrame final
        df = pd.DataFrame(data)

        # Salvar o DataFrame em um buffer de memória
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name='Ingredientes')

        buffer.seek(0) # Move o ponteiro para o início do buffer

        return buffer
        
        