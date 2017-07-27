# _*_ coding:utf-8 _*_

#'团员订单详情'
sql1 = """
SELECT
	d.nickname AS user_name,
	d.address,
	a.quantity,
	(b.price * a.quantity) AS m_amount,
	CONCAT(c.`name`,' ',b.price,' ',b.brief_dec) AS goods
FROM
	iuser_genericorder AS a
INNER JOIN market_groupbuygoods AS b ON a.goods_id = b.goods_id
INNER JOIN market_goods AS c ON b.goods_id = c.id
INNER JOIN iuser_userprofile AS d ON a.user_id = d.id
WHERE
	a.agent_code = 'oANa5v4DA46AKU8iyA303UJBLYmo'
AND b.group_buy_id = 5
"""

#'团员订购清单'
sql2 = """
SELECT
	a.goods_id,
	sum(a.quantity) AS m_amount,
    CONCAT(c.`name`,' ',b.price,' ',b.brief_dec) AS goods
FROM
	iuser_genericorder AS a
INNER JOIN market_groupbuygoods AS b ON a.goods_id = b.goods_id
INNER JOIN market_goods AS c ON b.goods_id = c.id
WHERE
	a.agent_code = 'ocsmexGwV4BzMOQMFN_IzHwgkj3I'
AND b.group_buy_id = 3
GROUP BY
	a.goods_id
"""