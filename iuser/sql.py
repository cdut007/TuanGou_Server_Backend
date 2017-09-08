# _*_ coding:utf-8 _*_

#'团员订单详情'
sql1_desc = [u'团员微信号', u'手机号', u'数量', u'价格', u'商品号']
sql1 = """
SELECT
	d.nickname AS user_wx,
	d.phone_num AS phone,
	a.quantity,
	CONCAT('$', ROUND((b.price * a.quantity), 2)) AS m_amount,
	CONCAT(c.`name`,' $',b.price,' ',b.brief_dec) AS goods
FROM
	iuser_genericorder AS a
INNER JOIN market_groupbuygoods AS b ON a.goods_id = b.id
INNER JOIN market_goods AS c ON b.goods_id = c.id
INNER JOIN iuser_userprofile AS d ON a.user_id = d.id
WHERE
	a.agent_code = '%(agent_code)s'
AND a.status = 1
AND b.group_buy_id = %(group_buy_id)s
"""


#'仓库发货清单'
sql2_desc = [u'数量', u'价格', u'商品号']
sql2 = """
SELECT
	sum(a.quantity) AS quantity,
	CONCAT('$', ROUND((quantity * b.price), 2)) AS m_amount,
    CONCAT(c.`name`,' $',b.price,' ',b.brief_dec) AS goods
FROM
	iuser_genericorder AS a
INNER JOIN market_groupbuygoods AS b ON a.goods_id = b.id
INNER JOIN market_goods AS c ON b.goods_id = c.id
WHERE
	a.agent_code = '%(agent_code)s'
AND a.status = 1
AND b.group_buy_id = %(group_buy_id)s
GROUP BY
	a.goods_id
"""

#'团购信息'
sql3 = """
SELECT
	b.title AS '团购标题',
	b.end_time AS '团购结束时间',
	b.ship_time AS '团购发货时间',
	c.nickname AS '团长昵称',
	c.address AS '团长地址',
	c.phone_num AS '团长手机号'
FROM
	iuser_agentorder AS a
INNER JOIN market_groupbuy AS b ON a.group_buy_id = b.id
INNER JOIN iuser_userprofile AS c ON a.user_id = c.id
WHERE
	a.id = %(agent_order_id)s
"""

#'clear shopping cart'
sql4 = """
DELETE
FROM
	iuser_shoppingcart
WHERE
	user_id = %(user_id)s
AND agent_code = '%(agent_code)s'
AND goods_id IN (%(goods_ids)s)
"""

sql_insert_generic_order = """
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

sql_add_to_cart = """
INSERT INTO iuser_shoppingcart (
	agent_code,
	add_time,
	user_id,
	goods_id,
	quantity
)
VALUES
%(values)s
ON DUPLICATE KEY UPDATE quantity = quantity + VALUES(quantity);
"""

sql_get_shopping_cart = """
SELECT
	e.ship_time,
	f.`name`,
	CONCAT('[', GROUP_CONCAT(
		CONCAT(
		'{\"goods_id\": \"',
		temp.goods_id,
		'\", ',
		'\"cart_id\": \"',
		temp.cart_id,
		'\", ',
		'\"price\": \"',
		temp.price,
		'\", ',
		'\"stock\": \"',
		temp.stock,
		'\", ',
		'\"quantity\": \"',
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
		    a.id AS cart_id,
			a.goods_id,
			a.`quantity`,
			c.`name` AS goods_name,
			d.image,
			b.brief_dec,
			b.price,
			b.stock,
			b.group_buy_id
		FROM
			iuser_shoppingcart AS a
		LEFT JOIN market_groupbuygoods AS b ON a.goods_id = b.id
		LEFT JOIN market_goods AS c ON b.goods_id = c.id
		LEFT JOIN market_goodsgallery AS d ON c.id = d.goods_id
		AND d.is_primary = 1
		WHERE
			a.user_id = %(user_id)s
		AND a.agent_code = '%(agent_code)s'
	) AS temp
LEFT JOIN market_groupbuy AS e ON temp.group_buy_id=e.id
LEFT JOIN market_goodsclassify AS f ON e.goods_classify_id=f.id
WHERE 
	e.on_sale = 1 AND e.end_time >= NOW()
GROUP BY 
	temp.group_buy_id
"""

sql_get_gengeric_order = """
SELECT
	e.ship_time,
	f.`name`,
	CONCAT('[', GROUP_CONCAT(
		CONCAT(
		'{\"goods_id\": \"',
		temp.goods_id,
		'\", ',
		'{\"order_id\": \"',
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
			a.user_id = %(user_id)s
		AND a.agent_code = '%(agent_code)s'
	) AS temp
LEFT JOIN market_groupbuy AS e ON temp.group_buy_id=e.id
LEFT JOIN market_goodsclassify AS f ON e.goods_classify_id=f.id
WHERE 
	e.on_sale = 1 AND e.end_time %(status_opt)s NOW()
GROUP BY 
	temp.group_buy_id
"""

sql_goods_clasify = """
SELECT
	c.id AS classify_id,
	c.`name`,
	c.`desc`
FROM
	market_groupbuygoods AS a
LEFT JOIN market_groupbuy AS b ON a.group_buy_id = b.id
LEFT JOIN market_goodsclassify AS c ON b.goods_classify_id=c.id
WHERE
	a.id = %(goods_id)s
"""

sql_group_buy_classify = """
SELECT
	a.title AS group_buy_title,
	b.`name` AS classify_name,
	b.`desc` AS classify_desc
FROM
	market_groupbuy AS a
LEFT JOIN market_goodsclassify AS b ON a.goods_classify_id = b.id
WHERE
	a.id = %(group_buy_id)s
"""
