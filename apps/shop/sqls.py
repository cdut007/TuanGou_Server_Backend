sql_app_index_page = """
SELECT
	CONCAT('{image_prefix}', b.image) AS image,
	b.id AS classify_id,
	b.`name`,
	CONCAT('{image_prefix}', b.icon) AS icon
FROM
	market_groupbuy AS a
LEFT JOIN market_goodsclassify AS b ON a.goods_classify_id = b.id
WHERE
	a.end_time > NOW()
AND a.on_sale = 1 AND LEFT(a.created_by, 5)='admin'
GROUP BY a.goods_classify_id
ORDER BY a.add_time DESC
"""

sql_web_index_page = """
SELECT
	CONCAT('{image_prefix}', c.image) AS image,
	c.id AS classify_id,
	c.`name`,
	CONCAT('{image_prefix}', c.icon) AS icon
FROM
	iuser_agentorder AS a
LEFT JOIN market_groupbuy AS b ON a.group_buy_id = b.id
LEFT JOIN market_goodsclassify AS c ON c.id = b.goods_classify_id
WHERE
	b.end_time > NOW()
AND b.on_sale = 1
AND a.user_id = {user_id}
GROUP BY b.goods_classify_id
ORDER BY b.add_time DESC
"""

sql_web_index_page_old = """
SELECT
	CONVERT(CONCAT(
			'\{"id\": \"',
			e.id,
			'\", ',
			'\"name\": \"',
			e.`name`,
			'\", ',
			'\"desc\": \"',
			e.`desc`,
			'\", ',
			'\"icon\": \"',
			e.icon,
			'\", ',
			'\"image\": \"',
			e.image,
			'\"}'
	) USING utf8)  AS classify,
	CONCAT(
		'[',
		GROUP_CONCAT(
			'\{"goods_id\": \"',
			c.id,
			'\", ',
			'\"image\": \"',
			d.image,
			'\"}'
		),
		']'
	) AS goods_list
FROM
	iuser_agentorder AS a
LEFT JOIN market_groupbuy AS b ON a.group_buy_id = b.id
LEFT JOIN market_groupbuygoods AS c ON FIND_IN_SET(c.id, a.goods_ids)
LEFT JOIN market_goodsgallery AS d ON c.goods_id=d.goods_id AND d.is_primary=1
LEFT JOIN market_goodsclassify AS e ON e.id=b.goods_classify_id
WHERE
	user_id = 172
AND b.end_time > NOW()
AND a.mc_end = 0
GROUP BY
	a.group_buy_id
"""

sql_goods_detail = """
SELECT
	a.id AS goods_id,
	a.price,
	a.stock,
	a.brief_dec,
	b.`name`,
	b.desc,
	d.ship_time,
	CONCAT(
		'[',
		GROUP_CONCAT(CONCAT('"', '%(image_prefix)s', c.image, '"')),
		']'
	) AS images,
	CONCAT(
        '{\"group_buying_id\": \"',
        d.id,
        '\", ',
        '\"user_remark\": \"',
        IFNULL(e.remark, ''),
        '\"} '
	) AS  group_buying
FROM
	market_groupbuygoods AS a
LEFT JOIN market_goods AS b ON a.goods_id = b.id
LEFT JOIN market_goodsgallery AS c ON b.id = c.goods_id
LEFT JOIN market_groupbuy AS d ON a.group_buy_id=d.id
LEFT JOIN lg_consumer_order_remarks AS e ON e.group_buying_id=d.id AND e.user_id=%(access_user)s AND e.merchant_code='%(merchant_code)s'
WHERE
	a.id = %(goods_id)s
GROUP BY
	a.id
"""

sql_goods_purchased_user = """
(
SELECT
	b.nickname,
	b.headimgurl,
	0 AS count
FROM
	iuser_genericorder AS a
LEFT JOIN iuser_userprofile AS b ON a.user_id = b.id
WHERE
	a.goods_id = {goods_id} AND a.`status` = 1
GROUP BY
	a.user_id
ORDER BY a.add_time DESC
{_limit}
)
UNION
(
SELECT
	'' AS nickname,
	'' AS headimgurl,
	COUNT(DISTINCT user_id) AS count
FROM
	iuser_genericorder
WHERE
	goods_id = {goods_id}
)
"""

sql_goods_classify = """
SELECT
    c.id AS classify_id,
	c.`name`,
	CONCAT('{image_prefix}', c.icon) AS icon,
	a.group_buy_id
FROM
	market_groupbuygoods AS a
LEFT JOIN market_groupbuy AS b ON a.group_buy_id = b.id
LEFT JOIN market_goodsclassify AS c ON c.id = b.goods_classify_id
WHERE
	a.id = {goods_id}
"""

sql_goods_detail_related = """
SELECT
	a.id AS goods_id,
	a.price,
	b.`name`,
	CONCAT(
		'{image_prefix}',
		SUBSTRING_INDEX(c.image, '.', 1),
		'_thumbnail.',
		SUBSTRING_INDEX(c.image, '.', -1)
	) AS image
FROM
	market_groupbuygoods AS a
INNER JOIN market_goods AS b ON a.goods_id = b.id
INNER JOIN market_goodsgallery AS c ON b.id = c.goods_id
AND c.is_primary = 1
WHERE
	a.group_buy_id = (
		SELECT
			group_buy_id
		FROM
			market_groupbuygoods
		WHERE
			id = {goods_id}
	)
AND a.id != {goods_id}
"""

sql_merchant_goods_detail_related = """
SELECT
	a.id AS goods_id,
	a.price,
	b.`name`,
	CONCAT(
		'{image_prefix}',
		SUBSTRING_INDEX(c.image, '.', 1),
		'_thumbnail.',
		SUBSTRING_INDEX(c.image, '.', - 1)
	) AS image
FROM
	market_groupbuygoods AS a
INNER JOIN market_goods AS b ON a.goods_id = b.id
INNER JOIN market_goodsgallery AS c ON b.id = c.goods_id
INNER JOIN iuser_agentorder AS d ON FIND_IN_SET(a.id,d.goods_ids)
INNER JOIN iuser_userprofile AS e ON d.user_id=e.id
AND c.is_primary = 1
WHERE
	a.group_buy_id = (
		SELECT
			group_buy_id
		FROM
			market_groupbuygoods
		WHERE
			id = {goods_id}
	)
AND a.id != {goods_id}
AND e.merchant_code='{merchant_code}'
"""

sql_classify_info = """
SELECT CONCAT('{image_prefix}', image) AS image, `desc`, name FROM market_goodsclassify WHERE id = {classify_id}
"""

sql_goods_detail_app = """
SELECT
	a.price,
	a.stock,
	a.brief_dec AS unit,
	b.`name`,
	b.`desc`,
	CONCAT('[', GROUP_CONCAT(CONCAT('\"{image_prefix}', c.image, '\"')), ']') AS images
FROM
	market_groupbuygoods AS a
LEFT JOIN market_goods AS b ON a.goods_id=b.id
LEFT JOIN market_goodsgallery AS c ON c.goods_id=b.id AND c.is_primary=1
WHERE
	a.id = {goods_id}
"""

sql_goods_related_app = """
SELECT
    a.id as goods_id,
	a.price,
	b.`name`,
    CONCAT(
        '{image_prefix}',
        SUBSTRING_INDEX(c.image, '.', 1),
        '_thumbnail.',
        SUBSTRING_INDEX(c.image, '.', - 1)
    ) AS image
FROM
	market_groupbuygoods AS a
LEFT JOIN market_goods AS b ON a.goods_id=b.id
LEFT JOIN market_goodsgallery AS c ON c.goods_id=b.id AND c.is_primary=1
WHERE
	a.group_buy_id=(SELECT group_buy_id FROM market_groupbuygoods WHERE id={goods_id})
AND a.id!= {goods_id}
"""

sql_classify_group_buy_list_with_all_goods = """
SELECT
	CONCAT(
		'[',
		GROUP_CONCAT(
			'{\"goods_id\": \"',
			a.id,
			'\", ',
			'\"unit\": \"',
			a.brief_dec,
			'\", ',
			'\"price\": \"',
			a.price,
			'\", ',
			'\"stock\": \"',
			a.stock,
			'\", ',
			'\"name\": \"',
			d.`name`,
			'\", ',
			'\"image\": \"',
			CONCAT(
				'%(image_prefix)s',
				SUBSTRING_INDEX(c.image, '.', 1),
				'_thumbnail.',
				SUBSTRING_INDEX(c.image, '.', - 1)
			),
			'\"}'
		),
		']'
	) AS goods_list,
	a.group_buy_id,
	DATE_FORMAT(b.end_time,'%%Y-%%m-%%d %%H:%%i:%%s') AS end_time,
	b.ship_time,
	b.eyu
FROM
	market_groupbuygoods AS a
LEFT JOIN market_groupbuy AS b ON a.group_buy_id=b.id
LEFT JOIN market_goodsgallery AS c ON a.goods_id=c.goods_id AND c.is_primary=1
LEFT JOIN market_goods AS d ON d.id=a.goods_id
WHERE b.goods_classify_id = %(classify_id)s
AND b.end_time > NOW() 
AND b.on_sale=1
AND LEFT(b.created_by, 5)='admin'
GROUP BY a.group_buy_id
"""

sql_merchant_classify_group_buy_list_with_all_goods_v2 = """
SELECT
	a.id AS group_buy_id,
	a.ship_time,
	a.eyu,
	IFNULL(e.remark,'') AS user_remark,
	DATE_FORMAT(a.end_time,'%%Y-%%m-%%d %%H:%%i:%%s') AS end_time,
	CONCAT(
		'[',
		GROUP_CONCAT(
			CONCAT(
				'{\"goods_id\": \"',
				b.goods_id,
				'\", ',
				'\"purchased_user\": \"',
				IFNULL(b.purchased_user, '[]'),
				'\", ',
				'\"price\": \"',
				b.price,
				'\", ',
				'\"stock\": \"',
				b.stock,
				'\", ',
				'\"brief_dec\": \"',
				b.brief_dec,
				'\", ',
				'\"name\": \"',
				b.`name`,
				'\", ',
				'\"image\": \"',
				b.image,
				'\"}'
			)
		),
		']'
	) AS goods_list
FROM
	market_groupbuy AS a
LEFT JOIN (
	SELECT
		a.group_buy_id,
		a.id AS goods_id,
		a.price,
		a.stock,
		a.brief_dec,
		b.`name`,
		CONCAT(
			'%(image_prefix)s',
			SUBSTRING_INDEX(c.image, '.', 1),
			'_thumbnail.',
			SUBSTRING_INDEX(c.image, '.', - 1)
		) AS image,
		CONCAT(
			'{\"users\": [',
			SUBSTRING_INDEX(GROUP_CONCAT(CONCAT(
				'{\"nickname\": \"',
				e.nickname,
				'\", ',
				'\"headimgurl\": \"',
				e.headimgurl,
				'\"}'
			)), ',{', 5),
			'], ',
			'\"count\": \"',
			COUNT(e.nickname),
			'\"}'
		) AS purchased_user
	FROM
		market_groupbuygoods AS a
	LEFT JOIN market_goods AS b ON a.goods_id = b.id
	LEFT JOIN market_goodsgallery AS c ON b.id = c.goods_id AND c.is_primary = 1
	LEFT JOIN (
		SELECT
			DISTINCT ig1.goods_id,
			iu2.nickname,
			iu2.headimgurl
		FROM
			iuser_genericorder AS ig1
		LEFT JOIN iuser_userprofile AS iu2 ON ig1.user_id = iu2.id
		ORDER BY ig1.add_time DESC
	) AS e ON e.goods_id=a.id
	GROUP BY
		a.id
) AS b ON a.id = b.group_buy_id
INNER JOIN iuser_agentorder AS c ON b.group_buy_id = c.group_buy_id AND FIND_IN_SET(b.goods_id, c.goods_ids)
INNER JOIN iuser_userprofile AS d ON c.user_id = d.id
LEFT JOIN lg_consumer_order_remarks AS e ON e.user_id=%(access_user)s AND e.group_buying_id=b.group_buy_id AND e.merchant_code='%(merchant_code)s'
WHERE
	a.goods_classify_id = %(classify_id)s
AND a.on_sale = 1
AND a.end_time >= NOW()
AND d.merchant_code = '%(merchant_code)s'
GROUP BY
	a.id
"""



# abandon
sql_goods_list = """
SELECT
	a.id AS goods_id,
	a.price,
	a.stock,
	a.brief_dec,
	b.`name`,
	CONCAT(
		'{image_prefix}',
		SUBSTRING_INDEX(c.image, '.', 1),
		'_thumbnail.',
		SUBSTRING_INDEX(c.image, '.', -1)
	) AS image
FROM
	market_groupbuygoods AS a
INNER JOIN market_goods AS b ON a.goods_id = b.id
INNER JOIN market_goodsgallery AS c ON b.id = c.goods_id AND c.is_primary = 1
WHERE
	group_buy_id = {group_buy_id}
"""

sql_classify_group_buy_list = """
SELECT
	id AS group_buy_id, 
	ship_time,
	DATE_FORMAT(end_time,'%Y-%m-%d %H:%i:%s') AS end_time
FROM
	market_groupbuy AS a
WHERE
	goods_classify_id = {classify_id}
AND on_sale = 1
AND end_time >= NOW()
"""

sql_merchant_classify_group_buy_list_with_all_goods = """
SELECT
	a.id AS group_buy_id,
	a.ship_time,
	IFNULL(e.remark,'') AS user_remark,
	DATE_FORMAT(
		a.end_time,
		'%%Y-%%m-%%d %%H:%%i:%%s'
	) AS end_time,
	CONCAT(
		'[',
		GROUP_CONCAT(
			CONCAT(
				'{\"goods_id\": \"',
				b.goods_id,
				'\", ',
				'\"price\": \"',
				b.price,
				'\", ',
				'\"stock\": \"',
				b.stock,
				'\", ',
				'\"brief_dec\": \"',
				b.brief_dec,
				'\", ',
				'\"name\": \"',
				b.`name`,
				'\", ',
				'\"image\": \"',
				b.image,
				'\"}'
			)
		),
		']'
	) AS goods_list
FROM
	market_groupbuy AS a
LEFT JOIN (
	SELECT
		a.group_buy_id,
		a.id AS goods_id,
		a.price,
		a.stock,
		a.brief_dec,
		b.`name`,
		CONCAT(
			'%(image_prefix)s',
			SUBSTRING_INDEX(c.image, '.', 1),
			'_thumbnail.',
			SUBSTRING_INDEX(c.image, '.', - 1)
		) AS image
	FROM
		market_groupbuygoods AS a
	LEFT JOIN market_goods AS b ON a.goods_id = b.id
	LEFT JOIN market_goodsgallery AS c ON b.id = c.goods_id
	AND c.is_primary = 1
) AS b ON a.id = b.group_buy_id
INNER JOIN iuser_agentorder AS c ON b.group_buy_id = c.group_buy_id
AND FIND_IN_SET(b.goods_id, c.goods_ids)
INNER JOIN iuser_userprofile AS d ON c.user_id = d.id
LEFT JOIN lg_consumer_order_remarks AS e ON e.user_id=%(access_user)s AND e.group_buying_id=b.group_buy_id AND e.merchant_code='%(merchant_code)s'
WHERE
	a.goods_classify_id = %(classify_id)s
AND a.on_sale = 1
AND a.end_time >= NOW()
AND d.merchant_code = '%(merchant_code)s'
GROUP BY
	a.id
"""

