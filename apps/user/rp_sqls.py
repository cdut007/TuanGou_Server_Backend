# _*_ coding:utf-8 _*_

sql_rp_one_entries = """
SELECT
	b.nickname AS unpack_user,
	a.money,
	DATE_FORMAT(a.unpack_time,'%m月%d号 %H:%i') AS unpack_time
FROM
	lg_unpack_red_packets_log AS a
LEFT JOIN iuser_userprofile AS b ON a.unpack_user=b.id
WHERE
	group_buying_id = {_group_buying_id}
AND receiver = {_receiver}
"""

sql_unopened_rp = """
SELECT
	group_buying_id,
	COUNT(a.id) AS unopened_rp,
	c.`name` AS  title
FROM
	lg_unpack_red_packets_log AS a
LEFT JOIN market_groupbuy AS b ON a.group_buying_id=b.id
LEFT JOIN market_goodsclassify AS c ON c.id=b.goods_classify_id
LEFT JOIN iuser_agentorder AS d ON d.group_buy_id=a.group_buying_id AND a.get_from=d.user_id
WHERE receiver={_receiver} AND d.mc_end=0 AND unpack_user is NULL 
GROUP BY group_buying_id
"""

sql_opened_rp = """
SELECT
	group_buying_id,
	SUM(a.money) AS money,
	c.`name` AS title
FROM
	lg_unpack_red_packets_log AS a
LEFT JOIN market_groupbuy AS b ON a.group_buying_id=b.id
LEFT JOIN market_goodsclassify AS c ON c.id=b.goods_classify_id
LEFT JOIN iuser_agentorder AS d ON d.group_buy_id=a.group_buying_id AND a.get_from=d.user_id
WHERE receiver={_receiver} AND unpack_user is NOT NULL AND d.mc_end=0
GROUP BY group_buying_id
"""

sql_failed_rp = """
SELECT
	group_buying_id,
  COUNT(a.id) AS failure_rp,
	c.`name` AS title,
	CASE is_failure 
	WHEN 1 THEN 'unopened'
	WHEN 2 THEN 'cancel order'
	WHEN 3 THEN 'your merchant unreached order amount'
	END AS failure_reason
FROM
	lg_unpack_red_packets_log AS a
LEFT JOIN market_groupbuy AS b ON a.group_buying_id=b.id
LEFT JOIN market_goodsclassify AS c ON c.id=b.goods_classify_id
WHERE receiver={_receiver} AND is_failure!=0 
GROUP BY group_buying_id
"""

sql_send_rp = """
SELECT
	a.receiver,
    SUM(a.money) AS money,
	b.openid_web
FROM
	lg_unpack_red_packets_log AS a
LEFT JOIN iuser_userprofile AS b ON a.receiver=b.id
WHERE
	a.get_from = {_get_from}
AND a.group_buying_id = {_group_buying_id}
AND a.is_failure=0
AND a.send_id IS NULL
GROUP BY a.receiver
"""

sql_rp_logs = """
SELECT
	money,
	DATE_FORMAT(send_time, '%Y-%m-%d %H:%s:%i') AS send_time
FROM
	lg_wei_xin_rp_send_log AS a
LEFT JOIN iuser_userprofile AS b ON a.openid=b.openid_web
WHERE a.result_code='SUCCESS' AND b.id={_user_id}
"""

sql_rp_amount = """
SELECT
	SUM(money) AS amount
FROM
	lg_wei_xin_rp_send_log AS a
LEFT JOIN iuser_userprofile AS b ON a.openid=b.openid_web
WHERE a.result_code='SUCCESS' AND b.id={_user_id}
"""

sql_unopened_and_opened_rp_count = """
SELECT
 	SUM(IF(a.unpack_user, 1, 0)) AS opened_rp,
	SUM(IF(a.unpack_user IS NULL, 1, 0)) AS unopened_rp
FROM
	lg_unpack_red_packets_log AS a
LEFT JOIN iuser_agentorder AS b ON a.group_buying_id=b.group_buy_id AND a.get_from=b.user_id
LEFT JOIN market_groupbuy AS c ON a.group_buying_id=c.id
WHERE a.receiver={_user_id} AND b.mc_end=0 AND c.end_time > NOW() AND a.is_failure=0
"""

sql_failed_rp_count = """
SELECT COUNT(id) AS failed_rp FROM lg_unpack_red_packets_log WHERE receiver={_user_id} AND is_failure!='0'
"""