sql_activity_detail = """
SELECT
	title,
	original_price,
	activity_price,
	exchange_price,
	DATE_FORMAT(end_time,'%Y-%m-%d %H:%i:%s') AS end_time,
	quantity,
	CONCAT('{_image_prefix}', goods_image) AS goods_image,
	activity_description,
	activity_introduction,
	goods_description,
	purchase_limitation,
	need_subscribe
FROM
	kj_activity
WHERE
	activity_id = {activity_id}
"""

sql_activity_ranking = """
SELECT
	a.current_price,
	b.nickname
FROM
	kj_activity_join AS a
LEFT JOIN iuser_userprofile AS b ON a.`owner` = b.id
WHERE a.activity_id ={activity_id}
ORDER BY a.current_price
"""

sql_activity_user_info = """
SELECT
	a.current_price,
	b.nickname,
	b.headimgurl,
	b.sharing_code,
	c.wx_result_code,
	c.pickup_code
FROM
	kj_activity_join AS a
LEFT JOIN iuser_userprofile AS b ON a.`owner`=b.id
LEFT JOIN kj_order AS c ON c.activity_id=a.activity_id AND c.`owner`={owner} AND c.wx_result_code='SUCCESS'
WHERE 
a.activity_id={activity_id} AND a.`owner`={owner} 
"""

sql_activity_kan_jia_logs = """
SELECT
	b.nickname,
	money, 
	current_price
FROM
	kj_activity_log AS a
LEFT JOIN iuser_userprofile as b ON a.kj_user=b.id
WHERE
	`owner` = {owner}
AND activity_id = {activity_id}
ORDER BY a.kjl_id DESC
"""