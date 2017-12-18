# _*_ coding:utf-8 _*_

sql_rp_one_detail = """
SELECT
	b.nickname AS unpack_user,
	a.money,
	DATE_FORMAT(a.unpack_time,'%m月%d号 %H:%i') AS unpack_time
FROM
	lg_unpack_red_packets_log AS a
LEFT JOIN iuser_userprofile AS b ON a.unpack_user=b.id
WHERE
	group_buying_id = 103
AND receiver = 78
"""