sql_goods_list = """
SELECT
	a.id AS goods_id,
	a.name, 
	CONCAT(
	'{_image_prefix}', 
	SUBSTRING_INDEX(b.image, '.', 1),
	'_thumbnail.',
	SUBSTRING_INDEX(b.image, '.', -1)
	) AS image
FROM
	market_goods AS a
LEFT JOIN market_goodsgallery AS b ON a.id = b.goods_id AND b.is_primary=1
{_where}
{_order_by}
{_limit}
"""

sql_goods_detail = """
SELECT
	a.id AS goods_id,
	a.`desc`,
	a.name,
	CONCAT(
		'[',
		GROUP_CONCAT(
			CONCAT(
				'{\"url\": \"%(image_prefix)s',
				b.image,
				'\", ',
				'\"id\": "',
				b.id,
				'\"}'
			)
		),
		']'
	) AS images
FROM
	market_goods AS a
LEFT JOIN market_goodsgallery AS b ON a.id = b.goods_id
WHERE
	a.id = %(goods_id)s
GROUP BY
	a.id
"""

sql_insert_goods_gallery = """
INSERT INTO market_goodsgallery (
	image,
	is_primary,
	add_time,
	goods_id
)
VALUES
{values}
"""

sql_delete_goods_gallery = """
DELETE
FROM
	market_goodsgallery
WHERE
	id IN ({detImg})
"""

sql_update_gallery_primary = """
UPDATE market_goodsgallery
SET is_primary = 1
WHERE
	goods_id = {goods_id}
ORDER BY
	id
LIMIT 1
"""

sql_product_search = """
SELECT
	a.id,
	a.`name`,
	CONCAT(
	'{_image_prefix}', 
	SUBSTRING_INDEX(b.image, '.', 1),
	'_thumbnail.',
	SUBSTRING_INDEX(b.image, '.', -1)
	) AS image
FROM
	market_goods AS a
LEFT JOIN market_goodsgallery AS b ON a.id=b.goods_id AND b.is_primary=1
WHERE
	a.`name` LIKE '%{_keyword}%'
"""

sql_group_buying_list = """
SELECT
	a.id,
	a.end_time,
	a.title,
	DATE_FORMAT(a.ship_time, '%d  %b  %y') AS ship_time,
	a.on_sale,
	b.`name` AS classify
FROM
	market_groupbuy AS a
INNER JOIN market_goodsclassify AS b ON a.goods_classify_id = b.id
{_where}
{_order_by}
{_limit}
"""

sql_group_buying_detail = """
SELECT
	a.id,
	a.end_time,
	a.ship_time,
	a.title,
	a.on_sale,
	b.id AS classify
FROM
	market_groupbuy AS a
LEFT JOIN market_goodsclassify AS b ON a.goods_classify_id=b.id
WHERE
	a.id = {id}
"""

sql_group_buying_products = """
SELECT
	a.id,
	a.price,
	a.brief_dec,
	a.stock,
	c.`name`,
	d.image
FROM
	market_groupbuygoods AS a
INNER JOIN market_groupbuy AS b ON a.group_buy_id = b.id AND a.group_buy_id={id}
LEFT JOIN market_goods AS c ON a.goods_id=c.id
LEFT JOIN market_goodsgallery AS d ON c.id=d.goods_id AND d.is_primary=1

"""

sql_classify_list = """
SELECT * FROM market_goodsclassify
"""