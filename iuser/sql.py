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