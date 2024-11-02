# IDEIAS DE ENDPOINTS

## [get] Product Functions

_params_:
`ean`: Código de barras do produto

_descrição_:
Faz uma chamada GET pelo código de barras do produto e retorna as seguintes informações:

1. Código de Barras do Produto
2. Código de Referência
3. Marca do produto
4. Nome do Produto
5. Linha do produto
6. Composição do Produto
7. Funções por ordem de ocorrência na composição
8. Funções por número de ocorrências na composição
9. Funções por pontuação (número de ocorrência/ordem de ocorrência)

## [get] Product has function

_params_:
`ean`: Código de barras do produto
`function`: Função desejada do produto

_descrição_: Faz uma chamada GET pelo código de barras do produto e retorna as seguintes informações:

1. Código de barras do produto
2. Código de referência
3. Marca do produto
4. Nome do produto
5. Linha do produto
6. Composição do produto
7. Ingredientes naquele produto que tenha a função especificada e localização dentro da composição
8. Pontuação por função
