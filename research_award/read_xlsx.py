import pandas as pd

# อ่านไฟล์ Excel
df = pd.read_excel('2026-04-26 ตัวแปรงานรางวัลตีพิมพ์ 2551-2566.xlsx')

# ลบบรรทัดที่ทุกคอลัมน์เป็น NaN
df = df.dropna(how='all')

print(df)