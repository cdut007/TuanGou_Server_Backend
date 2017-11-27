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
LEFT JOIN iuser_agentorder AS agent_order ON agent_order.group_buy_id = e.id AND agent_order.user_id=%(merchant_id)s
LEFT JOIN market_goodsclassify AS f ON e.goods_classify_id=f.id
LEFT JOIN lg_consumer_order_remarks AS g ON temp.group_buy_id=g.group_buying_id AND g.user_id=%(consumer_id)s AND g.merchant_code='%(merchant_code)s'
WHERE 
	e.on_sale = 1 %(_is_end)s
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

sql_user_group_buying = """
SELECT
    a.group_buy_id,
	DATE_FORMAT(b.end_time,'%Y-%m-%d %H:%i:%s') AS end_time,
	b.ship_time,
	b.title AS `desc`,
	IFNULL(
		CONCAT(
		  '[', 
          GROUP_CONCAT(
            '\"{image_prefix}', 
            SUBSTRING_INDEX(e.image, '.', 1),
            '_thumbnail.',
            SUBSTRING_INDEX(e.image, '.', -1), 
            '\"'
          ), 
		  ']'
		),
		'[]'
	) AS images,
	IF(f.id, 1, 0) AS notice_pushed 
FROM
	iuser_agentorder AS a 
LEFT JOIN market_groupbuy AS b ON a.group_buy_id=b.id
LEFT JOIN market_goodsclassify AS c ON c.id=b.goods_classify_id
LEFT JOIN market_groupbuygoods AS d ON FIND_IN_SET(d.id, SUBSTRING_INDEX(a.goods_ids, ',', 10))
LEFT JOIN market_goodsgallery AS e ON e.goods_id=d.goods_id AND is_primary=1
LEFT JOIN lg_merchant_push_log AS f ON f.group_buying_id=a.group_buy_id AND merchant_id={user_id} AND is_send_take_goods_notification=1
WHERE
	user_id = {user_id}
AND b.end_time < NOW()
GROUP BY a.group_buy_id
ORDER BY b.ship_time DESC
{_limit}
"""

sql_merchant_notice_consumer_take_goods = """
SELECT
	b.openid,
	b.nickname,
	CONCAT(GROUP_CONCAT(d.`name`)) AS goods
FROM
	iuser_genericorder AS a
LEFT JOIN iuser_userprofile AS b ON a.user_id=b.id
LEFT JOIN market_groupbuygoods AS c ON c.id=a.goods_id
LEFT JOIN market_goods AS d ON d.id=c.goods_id
WHERE
	a.agent_code = (
		SELECT
			openid
		FROM
			iuser_userprofile
		WHERE
			id = {user_id}
	)
AND FIND_IN_SET(
	a.goods_id,
	(
		SELECT
			goods_ids
		FROM
			iuser_agentorder
		WHERE
			user_id = {user_id}
		AND group_buy_id = {group_buying_id}
	)
)
GROUP BY b.openid
"""

sql_merchant_share_jie_long = """
SELECT
    a.group_buy_id,
	b.ship_time,
	c.`name` AS classify_name,
	CONCAT('{_image_prefix}', e.image) AS goods_image
FROM
	iuser_agentorder AS a
LEFT JOIN market_groupbuy AS b ON a.group_buy_id=b.id
LEFT JOIN market_goodsclassify AS c ON b.goods_classify_id=c.id
LEFT JOIN market_groupbuygoods AS d ON SUBSTRING_INDEX(a.goods_ids,',',1)=d.id
LEFT JOIN market_goodsgallery AS e ON d.goods_id=e.goods_id
WHERE
	a.user_id = {_user_id}
AND a.mc_end = 0
AND b.end_time > NOW()
GROUP BY a.group_buy_id
ORDER BY
	a.add_time DESC
{_limit}
"""

sql_merchant_check_jie_long = """
SELECT
	a.group_buy_id,
	c.`name` AS classify_name,
	CONCAT('%(_image_prefix)s', c.icon) AS icon,
	COUNT(temp1.headimgurl) AS purchased_count,
	CONCAT('[', SUBSTRING_INDEX(GROUP_CONCAT('\"', temp1.headimgurl, '\"'),',',10), ']') AS headimages
FROM
	iuser_agentorder AS a
LEFT JOIN market_groupbuy AS b ON a.group_buy_id = b.id
LEFT JOIN market_goodsclassify AS c ON b.goods_classify_id = c.id
LEFT JOIN (
	SELECT
		b.group_buy_id,
		c.headimgurl
	FROM
		iuser_genericorder AS a
	LEFT JOIN market_groupbuygoods AS b ON a.goods_id = b.id
	LEFT JOIN iuser_userprofile AS c ON a.user_id=c.id
	WHERE agent_code = '%(_merchant_code)s'
	GROUP BY a.user_id
	ORDER BY a.add_time DESC
) AS temp1 ON a.group_buy_id=temp1.group_buy_id
WHERE
	a.user_id = %(_merchant_id)s
AND a.mc_end = 0
AND b.end_time > NOW()
GROUP BY a.group_buy_id
ORDER BY
	a.add_time DESC
"""