sql_get_consumer_order = """
SELECT
	e.ship_time,
	f.`name`,
	CONCAT('[', GROUP_CONCAT(
		CONCAT(
		'{\"goods_id\": \"',
		temp.goods_id,
		'\", ',
		'\"order_id\": \"',
		temp.order_id,
		'\", ',
		'\"price\": \"',
		temp.price,
		'\", ',
		'\"stock\": \"',
		temp.stock,
		'\", ',
		'\"purchased\": \"',
		temp.quantity,
		'\", ',
		'\"goods_name\": \"',
		temp.goods_name,
		'\", ',
		'\"image\": \"%(image_prefix)s',
		temp.image,
		'\", ',
		'\"brief_desc\": \"',
		temp.brief_dec,
		'\"}'
		)), ']') AS `goods_list`
FROM
	(
		SELECT
			a.id as order_id,
			a.goods_id,
			a.`quantity`,
			c.`name` AS goods_name,
			d.image,
			b.brief_dec,
			b.price,
			b.stock,
			b.group_buy_id
		FROM
			iuser_genericorder AS a
		LEFT JOIN market_groupbuygoods AS b ON a.goods_id = b.id
		LEFT JOIN market_goods AS c ON b.goods_id = c.id
		LEFT JOIN market_goodsgallery AS d ON c.id = d.goods_id
		AND d.is_primary = 1
		WHERE
			a.user_id = %(consumer_id)s
		AND a.agent_code = '%(merchant_code)s'
	) AS temp
LEFT JOIN market_groupbuy AS e ON temp.group_buy_id=e.id
LEFT JOIN market_goodsclassify AS f ON e.goods_classify_id=f.id
WHERE 
	e.on_sale = 1 AND e.end_time %(group_buy_is_over)s NOW()
GROUP BY 
	temp.group_buy_id
"""

sql_create_consumer_order = """
INSERT INTO iuser_genericorder (
	agent_code,
	add_time,
	user_id,
	goods_id,
	quantity,
	status
)
VALUES
%(values)s
ON DUPLICATE KEY UPDATE quantity = quantity + VALUES(quantity);
"""

sql_clear_cart = """
DELETE
FROM
	iuser_shoppingcart
WHERE
	user_id = %(consumer_id)s
AND agent_code = '%(merchant_code)s'
AND goods_id IN (%(goods_ids)s)
"""

sql_done_consumer_order_update_stock = """UPDATE market_groupbuygoods SET stock = stock - {0} WHERE id = {1};"""