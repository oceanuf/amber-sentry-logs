#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试获取市场成交数据
"""

import os
import sys
import tushare as ts
import pandas as pd
from datetime import datetime, timedelta

# 设置token
os.environ['TUSHARE_TOKEN'] = "9e32ef28eac05c5fbb11e6f02a50da903def70f94b3018e93340568b"

# 初始化pro接口
token = os.getenv('TUSHARE_TOKEN')
pro = ts.pro_api(token)

print("🔧 测试市场数据获取...")

# 获取今天的日期 (北京时间)
now = datetime.now()
today = now.strftime('%Y%m%d')
print(f"今天日期: {today}")

# 1. 获取上证指数数据 (000001.SH)
print("\n1. 获取上证指数数据...")
try:
    sh_data = pro.index_daily(ts_code='000001.SH', trade_date=today)
    if not sh_data.empty:
        print(f"上证指数数据: {sh_data.iloc[0]}")
        sh_close = sh_data.iloc[0]['close']
        sh_pct_chg = sh_data.iloc[0]['pct_chg']  # 涨跌幅 %
        sh_amount = sh_data.iloc[0]['amount']  # 成交额(千元)
        sh_high = sh_data.iloc[0]['high']
        sh_low = sh_data.iloc[0]['low']
        sh_amplitude = ((sh_high - sh_low) / sh_close) * 100  # 振幅%
        
        print(f"收盘: {sh_close}, 涨跌幅: {sh_pct_chg}%, 成交额: {sh_amount/100000:.2f}亿, 振幅: {sh_amplitude:.2f}%")
    else:
        print("⚠️  今日上证指数数据为空，尝试获取最近交易日...")
        # 获取最近5个交易日数据
        sh_data_recent = pro.index_daily(ts_code='000001.SH', limit=5)
        if not sh_data_recent.empty:
            latest = sh_data_recent.iloc[0]
            print(f"最近交易日: {latest['trade_date']}, 收盘: {latest['close']}, 涨跌幅: {latest['pct_chg']}%")
except Exception as e:
    print(f"❌ 获取上证指数数据失败: {e}")

# 2. 获取深证成指数据 (399001.SZ)
print("\n2. 获取深证成指数据...")
try:
    sz_data = pro.index_daily(ts_code='399001.SZ', trade_date=today)
    if not sz_data.empty:
        print(f"深证成指数据: {sz_data.iloc[0]}")
        sz_close = sz_data.iloc[0]['close']
        sz_pct_chg = sz_data.iloc[0]['pct_chg']
        sz_amount = sz_data.iloc[0]['amount']
        sz_high = sz_data.iloc[0]['high']
        sz_low = sz_data.iloc[0]['low']
        sz_amplitude = ((sz_high - sz_low) / sz_close) * 100
        
        print(f"收盘: {sz_close}, 涨跌幅: {sz_pct_chg}%, 成交额: {sz_amount/100000:.2f}亿, 振幅: {sz_amplitude:.2f}%")
    else:
        print("⚠️  今日深证成指数据为空，尝试获取最近交易日...")
        sz_data_recent = pro.index_daily(ts_code='399001.SZ', limit=5)
        if not sz_data_recent.empty:
            latest = sz_data_recent.iloc[0]
            print(f"最近交易日: {latest['trade_date']}, 收盘: {latest['close']}, 涨跌幅: {latest['pct_chg']}%")
except Exception as e:
    print(f"❌ 获取深证成指数据失败: {e}")

# 3. 获取市场总体数据 (daily_info)
print("\n3. 获取市场总体数据 (daily_info)...")
try:
    market_data = pro.daily_info(trade_date=today)
    if not market_data.empty:
        print(f"市场总体数据: {market_data.iloc[0]}")
        # 解析字段
        total_amount = market_data.iloc[0]['total_amount']  # 总成交额(百万元)
        up_count = market_data.iloc[0]['up_count']  # 上涨家数
        down_count = market_data.iloc[0]['down_count']  # 下跌家数
        
        print(f"总成交额: {total_amount/100:.2f}亿, 上涨家数: {up_count}, 下跌家数: {down_count}")
    else:
        print("⚠️  今日市场总体数据为空，尝试获取最近交易日...")
        market_data_recent = pro.daily_info(limit=5)
        if not market_data_recent.empty:
            latest = market_data_recent.iloc[0]
            print(f"最近交易日: {latest['trade_date']}, 总成交额: {latest['total_amount']/100:.2f}亿")
except Exception as e:
    print(f"❌ 获取市场总体数据失败: {e}")
    
    # 尝试备用方法: 使用 daily_basic
    print("尝试使用daily_basic接口...")
    try:
        # 获取所有股票的daily_basic数据并汇总
        basic_data = pro.daily_basic(trade_date=today)
        if not basic_data.empty:
            total_volume = basic_data['total_vol'].sum()  # 总成交量(手)
            total_amount = basic_data['total_amount'].sum()  # 总成交额(千元)
            up_count = (basic_data['pct_chg'] > 0).sum()
            down_count = (basic_data['pct_chg'] < 0).sum()
            
            print(f"通过daily_basic汇总: 总成交额: {total_amount/100000:.2f}亿, 上涨: {up_count}, 下跌: {down_count}")
    except Exception as e2:
        print(f"❌ daily_basic也失败: {e2}")

print("\n✅ 测试完成")