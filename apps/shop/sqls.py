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
		GROUP_CONCAT(CONCAT('"', '{image_prefix}', c.image, '"')),
		']'
	) AS images
FROM
	market_groupbuygoods AS a
LEFT JOIN market_goods AS b ON a.goods_id = b.id
LEFT JOIN market_goodsgallery AS c ON b.id = c.goods_id
LEFT JOIN market_groupbuy AS d ON a.group_buy_id=d.id
WHERE
	a.id = {goods_id}
GROUP BY
	a.id
"""

sql_goods_classify = """
SELECT
	c.`name`,
	CONCAT('{image_prefix}', c.icon) AS icon
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
AND e.openid='{merchant_code}'
"""

sql_classify_info = """
SELECT CONCAT('{image_prefix}', image) AS image, `desc`, name FROM market_goodsclassify WHERE id = {classify_id}
"""

sql_classify_group_buy_list_with_all_goods = """
SELECT
	a.id AS group_buy_id,
	a.ship_time,
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
			'{image_prefix}',
			SUBSTRING_INDEX(c.image, '.', 1),
			'_thumbnail.',
			SUBSTRING_INDEX(c.image, '.', - 1)
		) AS image
	FROM
		market_groupbuygoods AS a
	INNER JOIN market_goods AS b ON a.goods_id = b.id
	INNER JOIN market_goodsgallery AS c ON b.id = c.goods_id
	AND c.is_primary = 1
) AS b ON a.id = b.group_buy_id
WHERE
	a.goods_classify_id = %(classify_id)s
AND a.on_sale = 1
AND a.end_time >= NOW()
GROUP BY
	a.id
"""

sql_merchant_classify_group_buy_list_with_all_goods = """
SELECT
	a.id AS group_buy_id,
	a.ship_time,
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
WHERE
	a.goods_classify_id = %(classify_id)s
AND a.on_sale = 1
AND a.end_time >= NOW()
AND d.openid = '%(merchant_code)s'
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

