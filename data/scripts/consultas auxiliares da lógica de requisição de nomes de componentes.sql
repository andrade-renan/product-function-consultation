select * from db_cosing

SELECT
	c.INCI_name as nome_original,
    c.INCI_name_PT as nome_pt, 
	c.function_pt
FROM
    db_cosing c
where c.INCI_name in (
		SELECT value FROM STRING_SPLIT(
            (
                SELECT composição
                FROM db_products 
                WHERE código_de_barras = '7898305623627'
            ), ','
        )
)


SELECT value FROM STRING_SPLIT(
    (
        SELECT composição
        FROM db_products 
        WHERE código_de_barras = '7898305623627'
    ), ','
) ORDER BY VALUE ASC





select * from db_cosing where INCI_Name LIKE '%Cocamide DEA%'

select Composição from db_products where Composição LIKE '%Disodium Edetate%'

SELECT *
FROM db_products
WHERE Composição LIKE '%' + LEFT(LIKE '%.%', LEN(@busca) - 1) + '%';