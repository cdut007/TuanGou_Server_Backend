sql_get_consumer_order = """
SELECT
	e.ship_time,
	IFNULL(g.remark,'') AS remark,
	e.id AS group_buy_id,
	CONCAT('%(image_prefix)s', f.icon) AS classify_icon,
	f.`name`,
	DATE_FORMAT(
		temp.add_time,
		'%%Y-%%m-%%d %%H:%%i:%%s'
	) AS add_time,
	SUM(temp.quantity) AS total_quantity,
	SUM(temp.money) AS total_money,
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
			a.add_time,
			c.`name` AS goods_name,
			d.image,
			b.brief_dec,
			b.price,
			b.stock,
			b.group_buy_id,
			a.quantity * b.price AS money
		FROM
			iuser_genericorder AS a
		LEFT JOIN market_groupbuygoods AS b ON a.goods_id = b.id
		LEFT JOIN market_goods AS c ON b.goods_id = c.id
		LEFT JOIN market_goodsgallery AS d ON c.id = d.goods_id
		AND d.is_primary = 1
		WHERE
			a.user_id = %(consumer_id)s
		AND a.status = 1
		AND a.agent_code = '%(merchant_code)s'
	) AS temp
LEFT JOIN market_groupbuy AS e ON temp.group_buy_id=e.id
LEFT JOIN market_goodsclassify AS f ON e.goods_classify_id=f.id
LEFT JOIN lg_consumer_order_remarks AS g ON temp.group_buy_id=g.group_buying_id AND g.user_id=%(consumer_id)s AND g.merchant_code='%(merchant_code)s'
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

sql_create_consumer_order_remarks = """
INSERT INTO lg_consumer_order_remarks (
	group_buying_id,
	user_id,
	merchant_code,
	remark,
	add_time
)
VALUES
%(values)s
ON DUPLICATE KEY UPDATE remark=VALUES(remark), add_time=VALUES(add_time) ;
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

sql_merchant_order_detail = """
SELECT
	CONCAT(
		'[',
		GROUP_CONCAT(
			CONCAT(
				'{\"name\": \"',
				temp.`name`,
				'\", ',
				'\"quantity\": \"',
				temp.quantity,
				'\", ',
				'\"price\": \"',
				temp.price,
				'\", ',
				'\"amount\": \"',
				temp.amount,
				'\"}'
			)
		),
		']'
	) AS goods_list,
	temp.time,
	COUNT(temp.user_id) AS total_quantity,
	SUM(temp.amount) AS total_amount,
	a.nickname,
	a.headimgurl,
	IFNULL(b.remark,'') AS remark
FROM
	(
		SELECT
			a.user_id,
			b.price,
			b.price * a.quantity AS amount,
			CONCAT(c.`name`, ' (', b.brief_dec, ')') AS NAME,
			a.quantity,
			DATE_FORMAT(a.add_time,'%%Y-%%m-%%d %%H:%%i') AS time
		FROM
			iuser_genericorder AS a
		LEFT JOIN market_groupbuygoods AS b ON a.goods_id = b.id
		LEFT JOIN market_goods AS c ON b.goods_id = c.id
		WHERE
			a.agent_code = '%(merchant_code)s'
		AND a.`status` = 1
		AND b.group_buy_id = %(group_buy_id)s
	) AS temp
INNER JOIN iuser_userprofile AS a on temp.user_id=a.id
LEFT JOIN lg_consumer_order_remarks AS b ON a.id=b.user_id AND b.group_buying_id=%(group_buy_id)s AND b.merchant_code='%(merchant_code)s'
GROUP BY
	temp.user_id
"""

sql_share_latest_groupbuying = """
SELECT
	c.`name`,
	c.`desc`,
	CONCAT('{image_prefix}', c.icon) AS icon,
	CONCAT('{image_prefix}', c.image) AS image
FROM
	iuser_agentorder AS a
LEFT JOIN market_groupbuy AS b ON a.group_buy_id=b.id
LEFT JOIN market_goodsclassify AS c ON c.id=b.goods_classify_id
WHERE
	a.user_id = {user_id}
ORDER BY
	a.add_time DESC
LIMIT 1
"""