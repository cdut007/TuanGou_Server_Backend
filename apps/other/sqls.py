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
sql_order_supplier_summary = """
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