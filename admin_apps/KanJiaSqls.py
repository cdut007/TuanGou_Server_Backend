sql_kan_jia_list = """
SELECT activity_id, title, activity_description, CONCAT('{_image_prefix}', goods_image) AS goods_image FROM kj_activity ORDER BY activity_id DESC {_limit}
"""

sql_kan_jia_detail = """
SELECT * FROM kj_activity WHERE activity_id={activity_id}
"""