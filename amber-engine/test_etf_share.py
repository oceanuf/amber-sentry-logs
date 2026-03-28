#!/usr/bin/env python3
"""
测试ETF份额数据获取
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
]

dates = ["20260227", "20260320"]

for etf in test_etfs:
    print(f"\n🔍 测试 {etf['name']} ({etf['code']})...")
    
    for date in dates:
        try:
            # 获取份额数据
            df = pro.fund_share(ts_code=etf['code'], trade_date=date)
            print(f"  {date}: 返回 {len(df)} 行数据")
            
            if len(df) > 0:
                data = df.iloc[0]
                print(f"    trade_date: {data['trade_date']}")
                print(f"    fd_share: {data['fd_share']} 万份")
                print(f"    market: {data['market']}")
                
                # 获取同日的净值
                df_nav = pro.fund_nav(ts_code=etf['code'], end_date=date)
                if len(df_nav) > 0:
                    df_nav_date = df_nav[df_nav['nav_date'] == date]
                    if len(df_nav_date) > 0:
                        nav_data = df_nav_date.iloc[0]
                        unit_nav = nav_data['unit_nav']
                        print(f"    unit_nav: {unit_nav} 元")
                        
                        # 计算市值
                        market_cap = data['fd_share'] * unit_nav
                        print(f"    计算市值: {data['fd_share']}万份 × {unit_nav}元 = {market_cap:.2f} 亿元")
            else:
                print(f"    ❌ 没有份额数据")
                
        except Exception as e:
            print(f"    ❌ 错误: {e}")