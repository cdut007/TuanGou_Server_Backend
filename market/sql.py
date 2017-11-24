sql_copy_group_buy = """
INSERT INTO market_groupbuy (
	end_time,
	goods_classify_id,
	add_time,
	title,
	ship_time,
	on_sale
) SELECT
	end_time,
	goods_classify_id,
	NOW(),
	title,
	ship_time,
	0
FROM
	market_groupbuy
WHERE
	id = {};
"""

sql_copy_group_buy_goods = """
INSERT INTO market_groupbuygoods (
	price,
	goods_id,
	group_buy_id,
	stock,
	brief_dec
) SELECT
	price,
	goods_id,
	{0},
	stock,
	brief_dec
FROM
	market_groupbuygoods
WHERE
	group_buy_id = {1} 
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
			CONCAT('%(image_prefix)s', e.icon)
			'\", ',
			'\"image\": \"',
			CONCAT('%(image_prefix)s', e.image)
			'\"}'
	) USING utf8)  AS classify,
	CONCAT(
		'[',
		GROUP_CONCAT(
			'\{"goods_id\": \"',
			c.id,
			'\", ',
			'\"image\": \"',
			CONCAT(
				'%(image_prefix)s',
				SUBSTRING_INDEX(d.image, '.', 1),
				'_thumbnail.',
				SUBSTRING_INDEX(d.image, '.', - 1)
			),
			'\"}'
		),
		']'
	) AS goods
FROM
	iuser_agentorder AS a
LEFT JOIN market_groupbuy AS b ON a.group_buy_id = b.id
LEFT JOIN market_groupbuygoods AS c ON FIND_IN_SET(c.id, a.goods_ids)
LEFT JOIN market_goodsgallery AS d ON c.goods_id=d.goods_id AND d.is_primary=1
LEFT JOIN market_goodsclassify AS e ON e.id=b.goods_classify_id
WHERE
	user_id = %(user_id)s
AND b.end_time > NOW()
AND a.mc_end = 0
GROUP BY
	a.group_buy_id
"""