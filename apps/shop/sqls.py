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