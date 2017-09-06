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