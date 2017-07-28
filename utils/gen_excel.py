# _*_ coding:utf-8 _*_
import xlwt
import os

test_data = {
    'agent_info': {'time': u'2017/6/13', 'address': u'地址', 'phone': u'12345678', 'wx': u'87654321'},
    'ship_list': [
        {'goods': u'巨峰葡萄 $6/500克/盒', u'quantity': '5', 'm_amount': u'$30.00'},
        {'goods': u'巨峰葡萄 $6/500克/盒', u'quantity': '5', 'm_amount': u'$30.00'},
        {'goods': u'巨峰葡萄 $6/500克/盒', u'quantity': '5', 'm_amount': u'$30.00'},
        {'goods': u' ', u'quantity': u'总数量：15', 'm_amount': u'总金额：$90.00'}
    ],
    'order_list': [
        {'user_wx': u'jenifer', 'phone': u'12345678', 'goods': u'巨峰葡萄 $6/500克/盒', 'quantity': u'5', 'm_amount': u'$15.00'},
        {'user_wx': u'jenifer', 'phone': u'12345678', 'goods': u'巨峰葡萄 $6/500克/盒', 'quantity': u'5', 'm_amount': u'$15.00'},
        {'user_wx': u'jenifer', 'phone': u'12345678', 'goods': u'巨峰葡萄 $6/500克/盒', 'quantity': u'5', 'm_amount': u'$15.00'},
        {'user_wx': u'jenifer', 'phone': u'12345678', 'goods': u'巨峰葡萄 $6/500克/盒', 'quantity': u'5', 'm_amount': u'$15.00'},
    ]
}

style_title = xlwt.easyxf(
    'font: height 280, name Arial, colour_index black,  bold on; '
    'align: wrap on, vert centre, horiz centre; '
    'pattern: pattern solid, fore_colour gray25;'
)
style_content = xlwt.easyxf(
    'font: height 240, name Arial, colour_index black, bold off, italic off; '
    'align: wrap on, vert centre, horiz centre;',
)

content_height = 384
title_height = 640

def order_excel(data):
    work_book = xlwt.Workbook(encoding='utf-8')
    sheet1 = work_book.add_sheet(u'sheet1',cell_overwrite_ok=False)

    sheet1.col(0).width = 256 * 20
    sheet1.col(1).width = 256 * 60
    sheet1.col(2).width = 256 * 30
    sheet1.col(3).width = 256 * 30

    #仓库发货清单
    sheet1.row(0).height_mismatch = True
    sheet1.row(0).height = title_height
    sheet1.write_merge(0, 0, 0, 3,u'仓库发货清单', style_title)

    for i in range(1,5):
        sheet1.row(i).height_mismatch = True
        sheet1.row(i).height = content_height

    sheet1.write(1,0, u'发货时间', style_content)
    sheet1.write(1,1, u'发货地点', style_content)
    sheet1.write(1,2, u'团长电话', style_content)
    sheet1.write(1,3, u'团长微信名', style_content)

    sheet1.write(2,0, data['agent_info']['time'], style_content)
    sheet1.write(2,1, data['agent_info']['address'], style_content)
    sheet1.write(2,2, data['agent_info']['phone'], style_content)
    sheet1.write(2,3, data['agent_info']['wx'], style_content)

    sheet1.write_merge(4, 4, 0, 1, u'商品名', style_content)
    sheet1.write(4, 2, u'数量', style_content)
    sheet1.write(4, 3, u'金额', style_content)

    cur_row1 = 5
    for item in data['ship_list']:
        sheet1.row(cur_row1).height_mismatch = True
        sheet1.row(cur_row1).height = content_height
        sheet1.write_merge(cur_row1, cur_row1, 0, 1, item['goods'], style_content)
        sheet1.write(cur_row1, 2, item['quantity'], style_content)
        sheet1.write(cur_row1, 3, item['m_amount'], style_content)
        cur_row1 += 1

    #团员购买清单
    sheet2 = work_book.add_sheet(u'sheet2', cell_overwrite_ok=False)

    sheet2.col(0).width = 256 * 20
    sheet2.col(1).width = 256 * 20
    sheet2.col(2).width = 256 * 50
    sheet2.col(3).width = 256 * 20
    sheet2.col(4).width = 256 * 20

    sheet2.row(0).height_mismatch = True
    sheet2.row(0).height = title_height
    sheet2.write_merge(0, 0, 0, 4,u'团员订购清单', style_title)

    sheet2.row(1).height_mismatch = True
    sheet2.row(1).height = content_height
    sheet2.write(1,0, u'团员微信号', style_content)
    sheet2.write(1,1, u'手机号', style_content)
    sheet2.write(1,2, u'商品号', style_content)
    sheet2.write(1,3, u'数量', style_content)
    sheet2.write(1,4, u'价格', style_content)

    cur_row2 = 2
    for item in data['order_list']:
        sheet2.row(cur_row2).height_mismatch = True
        sheet2.row(cur_row2).height = content_height
        sheet2.write(cur_row2, 0, item['user_wx'], style_content)
        sheet2.write(cur_row2, 1, item['phone'], style_content)
        sheet2.write(cur_row2, 2, item['goods'], style_content)
        sheet2.write(cur_row2, 3, item['quantity'], style_content)
        sheet2.write(cur_row2, 4, item['m_amount'], style_content)
        cur_row2 += 1

    work_book.save(data['file_path'])

if __name__ == '__main__':
    order_excel(test_data)
