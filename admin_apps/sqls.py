sql_goods_list = """
SELECT
	a.id AS goods_id,
	a.name, 
	CONCAT(
	'{_image_prefix}', 
	SUBSTRING_INDEX(b.image, '.', 1),
	'_thumbnail.',
	SUBSTRING_INDEX(b.image, '.', -1)
	) AS image
FROM
	market_goods AS a
LEFT JOIN market_goodsgallery AS b ON a.id = b.goods_id AND b.is_primary=1
{_where}
{_order_by}
{_limit}
"""

sql_goods_detail = """
SELECT
	a.id AS goods_id,
	a.`desc`,
	a.name,
	CONCAT(
		'[',
		GROUP_CONCAT(
			CONCAT(
				'{\"url\": \"%(image_prefix)s',
				b.image,
				'\", ',
				'\"id\": "',
				b.id,
				'\"}'
			)
		),
		']'
	) AS images
FROM
	market_goods AS a
LEFT JOIN market_goodsgallery AS b ON a.id = b.goods_id
WHERE
	a.id = %(goods_id)s
GROUP BY
	a.id
"""

sql_insert_goods_gallery = """
INSERT INTO market_goodsgallery (
	image,
	is_primary,
	add_time,
	goods_id
)
VALUES
{values}
"""

sql_delete_goods_gallery = """
DELETE
FROM
	market_goodsgallery
WHERE
	id IN ({detImg})
"""

sql_update_gallery_primary = """
UPDATE market_goodsgallery
SET is_primary = 1
WHERE
	goods_id = {goods_id}
ORDER BY
	id
LIMIT 1
"""

sql_product_search = """
SELECT
	a.id AS org_goods_id,
	a.`name`,
	CONCAT(
	'{_image_prefix}', 
	SUBSTRING_INDEX(b.image, '.', 1),
	'_thumbnail.',
	SUBSTRING_INDEX(b.image, '.', -1)
	) AS image
FROM
	market_goods AS a
LEFT JOIN market_goodsgallery AS b ON a.id=b.goods_id AND b.is_primary=1
WHERE
	a.`name` LIKE '%{_keyword}%'
"""

sql_group_buying_list = """
SELECT
  a.id,
  a.end_time,
  a.title,
  DATE_FORMAT(a.ship_time, '%d  %b  %y') AS ship_time,
  a.on_sale,
  b.`name` AS classify
FROM
  market_groupbuy AS a
INNER JOIN market_goodsclassify AS b ON a.goods_classify_id = b.id
{_where}
{_order_by}
{_limit}
"""

sql_group_buying_detail = """
SELECT
  a.id,
  DATE_FORMAT(a.ship_time, '%Y-%m-%d') AS ship_time,
  DATE_FORMAT(a.end_time, '%Y-%m-%d %h:%i:%s') AS end_time,
  a.title,
  a.on_sale,
  b.id AS classify
FROM
  market_groupbuy AS a
LEFT JOIN market_goodsclassify AS b ON a.goods_classify_id=b.id
WHERE
  a.id = {id}
"""

sql_group_buying_products = """
SELECT
  a.id AS goods_id,
  a.price,
  a.brief_dec AS unit,
  a.stock,
  c.id AS org_goods_id,
  c.`name`,
  d.image
FROM
  market_groupbuygoods AS a
INNER JOIN market_groupbuy AS b ON a.group_buy_id = b.id AND a.group_buy_id={id}
LEFT JOIN market_goods AS c ON a.goods_id=c.id
LEFT JOIN market_goodsgallery AS d ON c.id=d.goods_id AND d.is_primary=1
"""

sql_classify_list = """SELECT * FROM market_goodsclassify"""

sql_merchant_order_summary = """
SELECT
  a.id AS user_id,
  a.nickname,
  CONCAT(
    '[',
    GROUP_CONCAT(
      '{\"goods\": \"',
      temp1.goods,
      '\", ',
      '\"money\": \"',
      temp1.money,
      '\", ',
      '\"quantity\": \"',
      temp1.quantity,
      '\"}'
    ),
    ']'
  ) AS hgh
FROM
  (
    SELECT
      a.agent_code,
      SUM(a.quantity) AS quantity,
      CONCAT(c.`name`, ' $', b.price, ' ', b.brief_dec) AS goods,
      SUM(a.quantity) * b.price AS money
    FROM
      iuser_genericorder AS a
    INNER JOIN market_groupbuygoods AS b ON a.goods_id = b.id
    INNER JOIN market_goods AS c ON b.goods_id = c.id
    AND a. STATUS = 1
    AND b.group_buy_id = %(group_buy_id)s
    GROUP BY
      a.agent_code,
      a.goods_id
  ) AS temp1
LEFT JOIN iuser_userprofile AS a ON temp1.agent_code=a.openid
GROUP BY
  temp1.agent_code
"""

sql_group_buying_sell_summary = """
SELECT
	CONCAT(b.`name`,' $', a.price,' ', a.brief_dec) AS goods,
	IFNULL(SUM(c.quantity), 0) AS quantity,
	IFNULL(CONVERT(SUM(c.quantity)*a.price, DECIMAL(10, 2)), 0) AS money
FROM
	market_groupbuygoods AS a
LEFT JOIN market_goods AS b ON a.goods_id = b.id
LEFT JOIN iuser_genericorder AS c ON c.goods_id = a.id
WHERE
	a.group_buy_id = {group_buy_id}
group BY a.id
"""

sql_group_buying_goods_create = """
INSERT INTO market_groupbuygoods (
	price,
	stock,
	brief_dec,
	goods_id,
	group_buy_id
)
VALUES
%(values)s
"""

sql_group_buying_goods_update = """
REPLACE INTO market_groupbuygoods (
	price,
	stock,
	brief_dec,
	goods_id,
	group_buy_id
)
VALUES
%(values)s
"""

sql_group_buying_goods_delete = """
DELETE FROM market_groupbuygoods WHERE group_buy_id={group_buy_id} AND goods_id IN ({org_goods_id})
"""

sql_user_list = """
SELECT
	id,
	nickname,
	country,
	address,
	phone_num,
	is_agent,
    IF (is_agent, openid, '') AS merchant_code
FROM
	iuser_userprofile
ORDER BY id DESC
"""
