#!/usr/bin/env python3
"""
测试ETF净值数据获取
"""

import tushare as ts
import pandas as pd

# 设置Tushare Token
TOKEN = "9e32ef28eac05c5fbb11e6f02a50da903def70f94b3018e93340568b"
ts.set_token(TOKEN)
pro = ts.pro_api()

# 测试几个ETF
test_etfs = [
    {"code": "512480.SH", "name": "半导体芯片ETF"},
    {"code": "515070.SH", "name": "人工智能ETF"},
    {"code": "515030.SH", "name": "新能源车ETF"},
]

dates = ["20260227", "20260320"]

for etf in test_etfs:
    print(f"\n🔍 测试 {etf['name']} ({etf['code']})...")
    
    for date in dates:
        try:
            # 获取净值数据
            df = pro.fund_nav(ts_code=etf['code'], end_date=date)
            print(f"  {date}: 返回 {len(df)} 行数据")
            
            if len(df) > 0:
                # 查找指定日期
                df_date = df[df['nav_date'] == date]
                if len(df_date) > 0:
                    data = df_date.iloc[0]
                    print(f"    nav_date: {data['nav_date']}")
                    print(f"    unit_nav: {data['unit_nav']}")
                    print(f"    total_netasset: {data['total_netasset']}")
                    print(f"    net_asset: {data['net_asset']}")
                else:
                    print(f"    ❌ 没有 {date} 的精确数据")
                    # 显示最近的数据
                    recent = df.iloc[0]
                    print(f"    最近数据: nav_date={recent['nav_date']}, unit_nav={recent['unit_nav']}")
            else:
                print(f"    ❌ 没有数据")
                
        except Exception as e:
            print(f"    ❌ 错误: {e}")