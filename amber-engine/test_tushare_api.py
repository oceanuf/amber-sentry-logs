#!/usr/bin/env python3
"""
测试Tushare Pro API接口
"""

import tushare as ts
import pandas as pd

# 设置Tushare Token
TOKEN = "9e32ef28eac05c5fbb11e6f02a50da903def70f94b3018e93340568b"
ts.set_token(TOKEN)
pro = ts.pro_api()

# 测试一个ETF
test_ts_code = "512480.SH"  # 半导体芯片ETF
test_date = "20260227"

print("🔍 测试Tushare Pro API接口...")
print(f"测试ETF: {test_ts_code}")
print(f"测试日期: {test_date}")
print("=" * 50)

# 测试fund_share接口
print("\n1. 测试fund_share接口:")
try:
    df_share = pro.fund_share(ts_code=test_ts_code, trade_date=test_date)
    print(f"返回数据行数: {len(df_share)}")
    if len(df_share) > 0:
        print("字段列表:", list(df_share.columns))
        print("第一行数据:")
        print(df_share.iloc[0])
        print("\n完整数据:")
        print(df_share)
except Exception as e:
    print(f"fund_share接口错误: {e}")

# 测试fund_nav接口
print("\n2. 测试fund_nav接口:")
try:
    df_nav = pro.fund_nav(ts_code=test_ts_code, end_date=test_date)
    print(f"返回数据行数: {len(df_nav)}")
    if len(df_nav) > 0:
        print("字段列表:", list(df_nav.columns))
        print("第一行数据:")
        print(df_nav.iloc[0])
except Exception as e:
    print(f"fund_nav接口错误: {e}")

# 测试fund_daily接口
print("\n3. 测试fund_daily接口:")
try:
    df_daily = pro.fund_daily(ts_code=test_ts_code, start_date=test_date, end_date=test_date)
    print(f"返回数据行数: {len(df_daily)}")
    if len(df_daily) > 0:
        print("字段列表:", list(df_daily.columns))
        print("第一行数据:")
        print(df_daily.iloc[0])
except Exception as e:
    print(f"fund_daily接口错误: {e}")

# 测试fund_basic接口
print("\n4. 测试fund_basic接口:")
try:
    df_basic = pro.fund_basic(ts_code=test_ts_code)
    print(f"返回数据行数: {len(df_basic)}")
    if len(df_basic) > 0:
        print("字段列表:", list(df_basic.columns))
        print("第一行数据:")
        print(df_basic.iloc[0])
except Exception as e:
    print(f"fund_basic接口错误: {e}")

print("\n" + "=" * 50)
print("测试完成")