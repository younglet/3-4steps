from datetime import datetime, date, timedelta

# 获取当前日期和时间
now = datetime.now()
print("当前日期和时间:", now)

# 获取当前日期
today = date.today()
print("今天的日期:", today)

# 获取当前时间
current_time = datetime.now().time()
print("当前时间:", current_time)

# 格式化日期和时间
formatted_now = now.strftime("%Y-%m-%d %H:%M:%S")
print("格式化的日期和时间:", formatted_now)

# 解析字符串为日期时间
date_string = "2023-08-13 15:31:00"
dt_object = datetime.strptime(date_string, "%Y-%m-%d %H:%M:%S")
print("日期时间对象:", dt_object)

# 计算日期时间差
dt1 = datetime(2023, 8, 13, 15, 31)
dt2 = datetime(2023, 8, 14, 16, 31)
delta = dt2 - dt1
print("时间差:", delta)

# 增减日期时间
dt = datetime(2023, 8, 13, 15, 31)
dt_plus_one_day = dt + timedelta(days=1)
print("日期加上一天:", dt_plus_one_day)

dt_minus_two_hours = dt - timedelta(hours=2)
print("日期减去两小时:", dt_minus_two_hours)