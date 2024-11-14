import json
import os

# Carrega os dados do arquivo JSON, se existir
if os.path.exists('.\\product_info\\product_cache.json'):
    with open('.\\product_info\\product_cache.json', 'r', encoding='utf-8') as f:
        DADOS = json.load(f)

# Exemplo de serialização com ensure_ascii=True (para exibir no terminal, se necessário)
json_string = json.dumps(DADOS, ensure_ascii=True)
print(json_string)

# Salva as alterações no arquivo JSON com `ensure_ascii=True` (para exibir caracteres especiais como Unicode)
with open('.\\product_info\\product_cache.json', 'w', encoding='utf-8') as f:
    json.dump(DADOS, f, ensure_ascii=True, indent=4)
