sql_goods_list = """
SELECT
	a.id AS goods_id,
	a.name,
	a.default_price,
	a.default_stock,
	a.default_unit,
	a.set,
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
	a.default_price,
	a.default_stock,
	a.default_unit,
	a.set,
	a.brief_desc,
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
    'NULL' AS goods_id,
	a.id AS org_goods_id,
	a.`name`,
	a.default_price AS price,
	a.default_stock AS stock,
	a.default_unit AS unit,
	CONCAT(
	'{_image_prefix}', 
	SUBSTRING_INDEX(b.image, '.', 1),
	'_thumbnail.',
	SUBSTRING_INDEX(b.image, '.', -1)
	) AS image
FROM
	market_goods AS a
LEFT JOIN market_goodsgallery AS b ON a.id=b.goods_id AND b.is_primary=1
{_where}
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

sql_merchant_group_buying_list = """
SELECT
	a.id AS group_buy_id,
	DATE_FORMAT(a.end_time, '%Y-%m-%d %H:%i:%s') AS end_time,
	b.`name`,
	CONCAT('{_image_prefix}', d.image) AS image
FROM
	market_groupbuy AS a
LEFT JOIN market_goodsclassify AS b ON a.goods_classify_id=b.id
LEFT JOIN market_groupbuygoods AS c ON c.group_buy_id=a.id
LEFT JOIN market_goodsgallery AS d ON d.goods_id=c.goods_id AND d.is_primary=1
WHERE
	a.created_by = '{_owner}'
GROUP BY a.id
ORDER BY a.id DESC
{_limit}
"""

sql_group_buying_detail = """
SELECT
  a.id,
  DATE_FORMAT(a.ship_time, '%Y-%m-%d') AS ship_time,
  DATE_FORMAT(a.end_time, '%Y/%m/%d %H:%i:%s') AS end_time,
  a.title,
  a.on_sale,
  a.eyu,
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
  CONCAT('{image_prefix}', d.image) AS image
FROM
  market_groupbuygoods AS a
INNER JOIN market_groupbuy AS b ON a.group_buy_id = b.id AND a.group_buy_id={id}
LEFT JOIN market_goods AS c ON a.goods_id=c.id
LEFT JOIN market_goodsgallery AS d ON c.id=d.goods_id AND d.is_primary=1
"""

sql_classify_list = """
SELECT
	id,
	`name`,
	`desc`,
	CONCAT('{_image_prefix}', icon) AS icon,
	CONCAT('{_image_prefix}', image) AS image
FROM
	market_goodsclassify
WHERE created_by='{_owner}'
"""

sql_group_buying_orders = """
SELECT
  a.id AS user_id,
  a.merchant_code AS merchant_code,
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
  ) AS hgh,
  SUM(temp1.money) AS total_money,
  SUM(temp1.quantity) AS total_quantity
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
LEFT JOIN iuser_userprofile AS a ON temp1.agent_code=a.merchant_code
GROUP BY
  temp1.agent_code
"""

sql_group_buying_orders_v2 = """
SELECT
    temp1.merchant_id,
    temp1.merchant_code,
	CONVERT(CONCAT(temp1.merchant_id, '  ', c.nickname) USING utf8) AS merchant_name,
	SUM(temp2.quantity) AS total_quantity,
	SUM(a.price*temp2.quantity) AS total_money,
	CONCAT(
	'[',
	GROUP_CONCAT(
		'{\"name\": \"',
		CONCAT(b.`name`, ' $', a.price, ' ', a.brief_dec),
		'\", ',
		'\"quantity\": \"',
		temp2.quantity,
		'\", ',
		'\"money\": \"',
		ROUND(a.price*temp2.quantity, 2),
		'\"}'
	),
	']'
	) AS goods_list
FROM
	(
		SELECT
			a.id AS aorder_id,
			a.group_buy_id,
			a.user_id AS merchant_id,
			b.merchant_code AS merchant_code
		FROM
			iuser_agentorder AS a
		LEFT JOIN iuser_userprofile AS b ON a.user_id = b.id
		WHERE
			group_buy_id = %(group_buy_id)s
	) AS temp1
LEFT JOIN (
	SELECT
		a.user_id AS consumer_id,
		a.agent_code,
		SUM(a.quantity) AS quantity,
		a.goods_id,
		b.group_buy_id
	FROM
		iuser_genericorder AS a
	LEFT JOIN market_groupbuygoods AS b ON a.goods_id = b.id
	WHERE
		b.group_buy_id = %(group_buy_id)s
	GROUP BY a.agent_code, a.goods_id
) AS temp2 ON temp1.group_buy_id=temp2.group_buy_id AND temp1.merchant_code=temp2.agent_code
LEFT JOIN market_groupbuygoods AS a ON temp2.goods_id=a.id
LEFT JOIN market_goods AS b ON b.id=a.goods_id
LEFT JOIN iuser_userprofile AS c ON temp1.merchant_id=c.id
GROUP BY temp1.merchant_id
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
    id,
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
DELETE FROM market_groupbuygoods WHERE id IN ({goods_id})
"""

sql_user_list = """
SELECT
	id AS user_id,
	nickname,
	country,
	address,
	phone_num,
	is_agent,
	headimgurl,
    IF (is_agent, merchant_code, '') AS merchant_code
FROM
	iuser_userprofile
{_where}
{_order_by}
{_limit}
"""

sql_merchant_order_detail = """
SELECT
	CONCAT(
		'[',
		GROUP_CONCAT(
			CONCAT(
				'\"',
				temp.`name`,
				' -- ',
				temp.quantity,
				'\"'
			)
		),
		']'
	) AS goods_list,
	a.nickname
FROM
	(
		SELECT
			a.user_id,
			b.price,
			b.price * a.quantity AS amount,
			CONCAT(c.`name`, ' (', b.brief_dec, ')') AS NAME,
			a.quantity,
			DATE_FORMAT(a.add_time,'%%Y-%%m-%%d %%H:%%i') AS time
		FROM
			iuser_genericorder AS a
		LEFT JOIN market_groupbuygoods AS b ON a.goods_id = b.id
		LEFT JOIN market_goods AS c ON b.goods_id = c.id
		WHERE
			a.agent_code = '{merchant_code}'
		AND a.`status` = 1
		AND b.group_buy_id = {group_buying_id}
	) AS temp
INNER JOIN iuser_userprofile AS a on temp.user_id=a.id
GROUP BY
	temp.user_id
"""

sql_merchant_order_summary = """
SELECT
	temp2.group_buy_id,
	d.title,
	SUM(temp2.quantity) AS total_quantity,
	SUM(b.price*temp2.quantity) AS total_money,
	CONCAT(
		'[',
		GROUP_CONCAT(
		'{\"name\": \"',
		CONCAT(c.`name`, ' $', b.price, ' ', b.brief_dec), 
		'\", ',
		'\"quantity\": \"',	
		temp2.quantity,
		'\", ',
		'\"money\": \"',	
		b.price*temp2.quantity,
		'\"}'
		),
		']'
	) AS order_goods
FROM
	(
		SELECT
			temp1.morder_id,
			temp1.group_buy_id,
			a.goods_id,
			SUM(a.quantity) AS quantity,
			temp1.add_time
		FROM
			(
				SELECT
					id AS morder_id,
					goods_ids,
					group_buy_id,
					add_time
				FROM
					iuser_agentorder
				WHERE
					user_id = %(user_id)s
				ORDER BY
					add_time DESC
				LIMIT %(start)s, 5
			) AS temp1
		LEFT JOIN iuser_genericorder AS a ON FIND_IN_SET(a.goods_id, temp1.goods_ids) AND a.agent_code='%(merchant_code)s'                                         
		GROUP BY
			temp1.morder_id,
			a.goods_id
	) AS temp2
LEFT JOIN market_groupbuygoods AS b ON b.id = temp2.goods_id
LEFT JOIN market_goods AS c ON b.goods_id = c.id
LEFT JOIN market_groupbuy AS d ON temp2.group_buy_id=d.id
GROUP BY
	temp2.morder_id
ORDER BY
	temp2.add_time DESC
"""

sql_product_set_update = """
UPDATE market_goods SET `set`='{new_set}' WHERE `set`='{old_set}'
"""

sql_product_set_list = """
SELECT
	a.`set`,
	IFNULL(
        CONCAT(
        '{_image_prefix}', 
        SUBSTRING_INDEX(b.image, '.', 1),
        '_thumbnail.',
        SUBSTRING_INDEX(b.image, '.', -1)
        ), 
        ''
	) AS image,
	COUNT(DISTINCT a.id) AS count
FROM
	market_goods AS a
LEFT JOIN market_goodsgallery AS b ON a.id=b.goods_id AND is_primary=1
WHERE
	a.created_by = '{_owner}'
GROUP BY a.`set`
{_limit}
"""

sql_product_set_goods = """
SELECT
	a.id,
	a.`name`,
	a.default_price,
	a.default_stock,
	a.default_unit,
	IFNULL(
        CONCAT(
        '{_image_prefix}', 
        SUBSTRING_INDEX(b.image, '.', 1),
        '_thumbnail.',
        SUBSTRING_INDEX(b.image, '.', -1)
        ), 
        ''
	) AS image
FROM
	market_goods AS a 
LEFT JOIN market_goodsgallery AS b ON a.id=b.goods_id AND is_primary=1
WHERE
	a.created_by = '{_owner}'
AND a.`set` = '{_set}'
"""


