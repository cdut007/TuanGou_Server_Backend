sql_goods_detail = """
SELECT
	a.id AS goods_id,
	a.price,
	a.stock,
	a.brief_dec,
	b.`name`,
	b.desc,
	CONCAT(
		'[',
		GROUP_CONCAT(CONCAT('"', '{image_prefix}', c.image, '"')),
		']'
	) AS images
FROM
	market_groupbuygoods AS a
LEFT JOIN market_goods AS b ON a.goods_id = b.id
LEFT JOIN market_goodsgallery AS c ON b.id = c.goods_id
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

sql_classify_group_buy_list = """
SELECT
	id AS group_buy_id, 
	ship_time,
	end_time
FROM
	market_groupbuy AS a
WHERE
	goods_classify_id = {classify_id}
AND on_sale = 1
AND end_time >= NOW()
"""

sql_classify_info = """
SELECT CONCAT('{image_prefix}', image) AS image, `desc` FROM market_goodsclassify WHERE id = {classify_id}
"""

sql_classify_group_buy_first = """
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
INNER JOIN market_goodsgallery AS c ON b.id = c.goods_id
WHERE
	group_buy_id = (
		SELECT
			id
		FROM
			market_groupbuy AS a
		WHERE
			goods_classify_id = {classify_id}
		AND on_sale = 1
        AND end_time >= NOW()
		ORDER BY
			ship_time DESC
		LIMIT 1
	)
"""