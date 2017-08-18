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