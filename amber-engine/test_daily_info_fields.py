#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试daily_info接口字段，特别是涨跌个股数
"""

import os
import sys
import tushare as ts
import pandas as pd
from datetime import datetime, timedelta

# 设置token
os.environ['TUSHARE_TOKEN'] = "9e32ef28eac05c5fbb11e6f02a50da903def70f94b3018e93340568b"
token = os.getenv('TUSHARE_TOKEN')
pro = ts.pro_api(token)

print("🔧 测试daily_info接口字段...")

# 获取今天的日期
today = datetime.now().strftime('%Y%m%d')
print(f"今天日期: {today}")

# 测试daily_info接口
print("\n1. 测试daily_info接口...")
try:
    market_data = pro.daily_info(trade_date=today)
    if not market_data.empty:
        print(f"✅ daily_info数据获取成功，共{len(market_data)}条记录")
        print(f"数据列名: {list(market_data.columns)}")
        print(f"\n数据预览:")
        print(market_data.head())
        
        # 检查每个字段
        print(f"\n字段详情:")
        for col in market_data.columns:
            sample_value = market_data[col].iloc[0] if not market_data[col].empty else "N/A"
            print(f"  {col}: {sample_value} (类型: {type(sample_value).__name__})")
        
        # 特别关注可能的涨跌计数字段
        print(f"\n🔍 搜索涨跌相关字段:")
        for col in market_data.columns:
            col_lower = col.lower()
            if any(keyword in col_lower for keyword in ['up', 'down', '涨', '跌', 'count']):
                print(f"  ⭐ {col}: {market_data[col].iloc[0]}")
                
    else:
        print("⚠️  今日daily_info数据为空，尝试获取最近交易日...")
        # 获取最近5个交易日数据
        market_data_recent = pro.daily_info(limit=5)
        if not market_data_recent.empty:
            print(f"最近交易日: {market_data_recent.iloc[0]['trade_date']}")
            print(f"数据列名: {list(market_data_recent.columns)}")
            print("\n数据预览:")
            print(market_data_recent.head())
            
except Exception as e:
    print(f"❌ daily_info接口失败: {e}")

# 2. 测试其他可能包含涨跌个股数的接口
print("\n" + "="*60)
print("2. 测试其他可能接口...")

# 测试index_dailybasic接口
print("\n测试index_dailybasic接口...")
try:
    index_basic = pro.index_dailybasic(ts_code='000001.SH', trade_date=today)
    if not index_basic.empty:
        print(f"✅ index_dailybasic数据获取成功")
        print(f"字段: {list(index_basic.columns)}")
        print(index_basic.head())
    else:
        print("⚠️  今日index_dailybasic数据为空")
except Exception as e:
    print(f"❌ index_dailybasic接口失败: {e}")

# 测试daily_basic接口（虽然之前pct_chg字段有问题，但可能有其他字段）
print("\n测试daily_basic接口字段...")
try:
    # 只获取少量数据检查字段
    basic_sample = pro.daily_basic(trade_date=today, limit=10)
    if not basic_sample.empty:
        print(f"✅ daily_basic数据获取成功，共{len(basic_sample)}条记录")
        print(f"字段: {list(basic_sample.columns)}")
        
        # 检查是否有pct_chg字段
        if 'pct_chg' in basic_sample.columns:
            print(f"✅ 找到pct_chg字段，可以计算涨跌个股数")
            # 计算涨跌数量
            up_count = (basic_sample['pct_chg'] > 0).sum()
            down_count = (basic_sample['pct_chg'] < 0).sum()
            print(f"  样本中: 上涨 {up_count}, 下跌 {down_count}")
        else:
            print(f"❌ 没有pct_chg字段，可用字段: {list(basic_sample.columns)}")
    else:
        print("⚠️  今日daily_basic数据为空")
except Exception as e:
    print(f"❌ daily_basic接口失败: {e}")

# 3. 查看Tushare官方文档字段说明（通过实际调用了解）
print("\n" + "="*60)
print("3. 检查字段详细说明...")

# 尝试获取不同交易所的数据
exchanges = ['SSE', 'SZSE']
for exchange in exchanges:
    print(f"\n检查{exchange}交易所数据...")
    try:
        # 尝试获取交易日历了解可用字段
        if exchange == 'SSE':
            cal_data = pro.trade_cal(exchange='SSE', start_date='20260101', end_date='20260110')
            print(f"SSE交易日历字段: {list(cal_data.columns) if not cal_data.empty else '空'}")
    except Exception as e:
        print(f"  {exchange}检查失败: {e}")

print("\n✅ 测试完成")