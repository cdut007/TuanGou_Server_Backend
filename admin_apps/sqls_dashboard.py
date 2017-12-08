# _*_ coding:utf-8 _*_
sql_group_buying_doing = """
SELECT
    a.id AS group_buying_id,
	b.`name`,
	CONCAT('{_image_prefix}', b.icon) AS icon,	
	CONCAT('{_image_prefix}', b.image) AS image,
	a.eyu,
	DATE_FORMAT(a.end_time, '%Y-%m-%d %H:%i:%s') AS end_time,
	'5' AS purchased_user
FROM
	market_groupbuy AS a
LEFT JOIN market_goodsclassify AS b ON a.goods_classify_id=b.id
WHERE
	end_time > NOW()
AND on_sale = 1
"""