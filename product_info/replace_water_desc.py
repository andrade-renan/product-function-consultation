import json

# Caminho do arquivo JSON
caminho_arquivo = 'product_info\product_cache.json'

# Carregar os dados do arquivo JSON
with open(caminho_arquivo, 'r', encoding='utf-8') as file:
    data = json.load(file)

# Substituir todas as descrições de composição de "Água" por um novo valor
novo_valor = 'Aqua (EU),Deionized Water,Distilled Water,Micromatrix Fractile AN,Onsen-Sui (JPN),Purified Water'
for product_key, product_info in data.items():
    if 'descriptionPerComposition' in product_info and 'Water' in product_info['descriptionPerComposition']:
        product_info['descriptionPerComposition']['Water'] = novo_valor

# Salvar as alterações de volta para o arquivo JSON
with open(caminho_arquivo, 'w', encoding='utf-8') as file:
    json.dump(data, file, ensure_ascii=False, indent=4)

print('Substituição completa.')
