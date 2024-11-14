from flask import jsonify, Response, send_file
import pandas as pd
import io
import json
import os

from product_info.product_info import doGet_productInfo

class doGet_groupIngredients:
    def __init__(self):
        self.getpath_product_info = doGet_productInfo()
        

    def get_product_info(self, ean):
        return self.getpath_product_info.process_product_info(ean)
    
    def comparison_spreadsheet(self, ean_list):
        
        for ean in ean_list:
            infos = self.get_product_info(ean).get_json()
            print(f"Nome do produto: {infos['name']}")
            print(infos['functionsPerComposition']['Water'])
            
            for composition in infos['functionsPerComposition']:
                print(f'---------- {composition} ----------')
                for function in infos['functionsPerComposition'][composition]:
                    print(function)

    

        