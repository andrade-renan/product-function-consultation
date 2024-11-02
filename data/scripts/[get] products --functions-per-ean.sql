/*
SELECT value FROM STRING_SPLIT(
    (
        SELECT composição
        FROM db_products 
        WHERE código_de_barras = '7898305623627'
    ), ','
)
*/

WITH ProductComponents AS (
    SELECT value FROM STRING_SPLIT(
        (SELECT composição FROM db_products WHERE código_de_barras = '7898305623627'), ','
    ) AS components
),
RankedMatches AS (
    SELECT
        pc.value AS Component,
        c.INCI_name AS nome_original,
        c.INCI_name_PT AS nome_pt,
        c.function_pt,
        CHARINDEX(LTRIM(RTRIM(pc.value)), c.INCI_name) AS MatchIndex
    FROM
        db_cosing c
    CROSS JOIN
        ProductComponents pc
    WHERE
        c.INCI_name LIKE '%' + LTRIM(RTRIM(pc.value)) + '%'
)
SELECT
    Component,
    nome_original,
    nome_pt,
    function_pt
FROM (
    SELECT *,
        ROW_NUMBER() OVER (PARTITION BY Component ORDER BY MatchIndex ASC, LEN(nome_original) ASC) AS rn
    FROM RankedMatches
    WHERE MatchIndex > 0
) AS Matches
WHERE rn = 1

