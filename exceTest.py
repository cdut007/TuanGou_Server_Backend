# _*_ coding:utf-8 _*_
import xlwt

style0 = xlwt.easyxf(
    'font: '
        'name Times New Roman, '
        'color-index black, '
        'bold off, ',
        # 'align: wrap yes',
    num_format_str='#,##0.00'
)

work_book = xlwt.Workbook()
sheet1 = work_book.add_sheet(u'sheet1',cell_overwrite_ok=False)
sheet1.write_merge(0, 0, 0, 3,u'仓库发货清单', style0)
work_book.col(0).width = 256 * 20  # around 220 pixels

sheet1.write(1,0, u'发货时间', style0)
sheet1.write(1,1, u'发货地点', style0)
sheet1.write(1,2, u'团长电话', style0)
sheet1.write(1,3, u'团长微信', style0)

sheet1.write(2,0, u'2017/6/13', style0)
sheet1.write(2,1, u'武极甘柏', style0)
sheet1.write(2,2, u'97735567', style0)
sheet1.write(2,3, u'12027710528', style0)

sheet1.write_merge(4,4,0,1, u'商品名', style0)
sheet1.write(4,2, u'数量', style0)
sheet1.write(4,3, u'金额', style0)

sheet1.write_merge(5,5,0,1, u'巨峰葡萄 $6/500克/盒', style0)
sheet1.write(5,2, u'5', style0)
sheet1.write(5,3, u'$30.00', style0)

sheet1.write_merge(6,6,0,1, u'巨峰葡萄 $6/500克/盒', style0)
sheet1.write(6,2, u'3', style0)
sheet1.write(6,3, u'$30.00', style0)

sheet1.write_merge(7,7,0,1, u'', style0)
sheet1.write(7,2, u'总数量：32', style0)
sheet1.write(7,3, u'总金额：$538.00', style0)

work_book.save('demo2.xlsx')
