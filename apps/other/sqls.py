# _*_ coding:utf-8 _*_

# 判断订单是否为空
sql_is_order_empty = """
SELECT
	COUNT(a.id) AS count
FROM
	iuser_genericorder AS a
LEFT JOIN market_groupbuygoods AS b ON a.goods_id=b.id
WHERE
	a.agent_code = '{_merchant_code}' AND b.group_buy_id={_group_buying_id}
"""

#'团员订单详情'
sql_order_consumer_detail = """
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
				'\"money\": \"',
				temp.amount,
				'\"}'
			)
		),
		']'
	) AS goods_list,
	a.nickname,
	a.phone_num,
	SUM(temp.quantity) AS total_quantity,
	SUM(temp.amount) AS total_money
FROM
	(
		SELECT
			a.user_id,
			b.price,
			b.price * a.quantity AS amount,
			CONCAT(c.`name`, ' $', b.price, ' ', b.brief_dec) AS NAME,
			a.quantity
		FROM
			iuser_genericorder AS a
		LEFT JOIN market_groupbuygoods AS b ON a.goods_id = b.id
		LEFT JOIN market_goods AS c ON b.goods_id = c.id
		WHERE
			a.agent_code = '%(agent_code)s'
		AND a.`status` = 1
		AND b.group_buy_id =  %(group_buy_id)s
	) AS temp
INNER JOIN iuser_userprofile AS a on temp.user_id=a.id
GROUP BY
	temp.user_id
"""

#'仓库发货清单'
sql_order_supplier_summary = """
SELECT
	sum(a.quantity) AS quantity,
	CONCAT('$', CONVERT((SUM(a.quantity) * b.price),decimal)) AS m_amount,
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