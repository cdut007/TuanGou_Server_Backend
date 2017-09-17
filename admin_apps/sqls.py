sql_goods_list = """
SELECT
	a.id AS goods_id,
	a.name, 
	CONCAT('{_image_prefix}', b.image) AS image
FROM
	market_goods AS a
LEFT JOIN market_goodsgallery AS b ON a.id = b.goods_id AND b.is_primary=1
{_where}
{_order_by}
{_limit}
"""