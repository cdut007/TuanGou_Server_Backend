# _*_ coding:utf-8 _*_

sql_rp_one_entries = """
SELECT
    b.id AS user_id,
	b.nickname AS unpack_user,
	b.headimgurl,
	a.money,
	DATE_FORMAT(a.unpack_time,'%Y-%m-%d %H:%i:%s') AS unpack_time,
	is_failure
FROM
	lg_unpack_red_packets_log AS a
LEFT JOIN iuser_userprofile AS b ON a.unpack_user=b.id
WHERE
	group_buying_id = {_group_buying_id}
AND receiver = {_receiver}
ORDER BY a.unpack_time DESC 
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
WHERE receiver={_receiver} AND a.is_failure=0 AND d.mc_end=0 AND b.end_time>NOW() AND unpack_user is NULL 
GROUP BY group_buying_id
"""

sql_opened_rp = """
SELECT
	group_buying_id,
	SUM(a.money) AS money,
	COUNT(a.id) AS opened_rp,
	c.`name` AS title,
	DATE_FORMAT(a.unpack_time,'%Y-%m-%d %H:%s:%i') AS unpack_time
FROM
	lg_unpack_red_packets_log AS a
LEFT JOIN market_groupbuy AS b ON a.group_buying_id=b.id
LEFT JOIN market_goodsclassify AS c ON c.id=b.goods_classify_id
LEFT JOIN iuser_agentorder AS d ON d.group_buy_id=a.group_buying_id AND a.get_from=d.user_id
WHERE receiver={_receiver} AND a.is_failure=0 AND unpack_user is NOT NULL AND d.mc_end=0 AND b.end_time>NOW()
GROUP BY group_buying_id
"""

sql_failed_rp = """
SELECT
	group_buying_id,
  COUNT(a.id) AS failure_rp,
	c.`name` AS title,
	CASE is_failure 
	WHEN 1 THEN '很遗憾！你的接龙红包在截团前未拆完！'
	WHEN 2 THEN '很遗憾！由于订单取消导致红包失效！'
	WHEN 3 THEN '很遗憾！该接龙在截团时不满足送货条件！'
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