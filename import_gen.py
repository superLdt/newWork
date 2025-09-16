from openpyxl import Workbook
from pathlib import Path

wb = Workbook()
ws = wb.active
ws.title = 'Sheet1'
# 列头按后端模板假设：车牌号, 车厢号, 容积
ws.append(['车牌号','车厢号','容积'])
# 两条样例：一条完整、一条无车牌以测试规则
ws.append(['皖B88888','GXA-01', 35])
ws.append(['', 'GXB-02', 52])

out = Path('import_test.xlsx').resolve()
wb.save(out)
print('generated', str(out))