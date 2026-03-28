#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试市场统计数据的各种接口
寻找获取涨跌个股数的方法
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

print("🔍 寻找获取涨跌个股数的方法...")

# 获取今天的日期
today = datetime.now().strftime('%Y%m%d')
print(f"今天日期: {today}")

# 方法1: 使用通用行情接口pro_bar（可能需要复权参数）
print("\n1. 测试pro_bar接口...")
try:
    # 尝试获取上证指数成分股的涨跌幅
    # 先获取上证指数成分股列表
    print("获取上证指数成分股...")
    
    # 尝试获取指数成分股（可能需要特定权限）
    try:
        # 先测试pro_bar获取单个股票
        test_stock = pro.bar(ts_code='000001.SH', freq='D', start_date=today, end_date=today)
        print(f"pro_bar测试: {len(test_stock) if test_stock is not None else 0}条记录")
        if test_stock is not None and not test_stock.empty:
            print(f"字段: {list(test_stock.columns)}")
    except Exception as e:
        print(f"pro_bar失败: {e}")
    
    # 尝试使用通用行情接口
    try:
        # 测试通用行情接口
        general_data = pro.daily(ts_code='000001.SH', trade_date=today)
        print(f"daily接口: {len(general_data) if general_data is not None else 0}条记录")
        if general_data is not None and not general_data.empty:
            print(f"字段: {list(general_data.columns)}")
            if 'pct_chg' in general_data.columns:
                print(f"✅ 找到pct_chg字段: {general_data.iloc[0]['pct_chg']}")
    except Exception as e:
        print(f"daily接口失败: {e}")
        
except Exception as e:
    print(f"❌ pro_bar测试失败: {e}")

# 方法2: 使用指数数据接口获取市场整体统计
print("\n2. 测试指数市场统计接口...")

# 尝试获取市场概况数据
try:
    # 尝试使用index_daily获取主要指数
    major_indices = ['000001.SH', '399001.SZ', '399006.SZ', '000300.SH']
    for idx in major_indices:
        idx_data = pro.index_daily(ts_code=idx, trade_date=today)
        if not idx_data.empty:
            print(f"{idx}: {len(idx_data)}条记录")
            # 检查是否有市场统计字段
            print(f"  字段: {list(idx_data.columns)}")
        else:
            # 获取最近数据
            idx_recent = pro.index_daily(ts_code=idx, limit=1)
            if not idx_recent.empty:
                print(f"{idx}最近: {idx_recent.iloc[0]['trade_date']}, 涨跌: {idx_recent.iloc[0].get('pct_chg', 'N/A')}")
except Exception as e:
    print(f"指数接口失败: {e}")

# 方法3: 尝试从其他数据源获取
print("\n3. 探索替代数据源方案...")

# 检查是否有其他市场统计接口
try:
    # 尝试moneyflow接口
    moneyflow = pro.moneyflow(trade_date=today, limit=10)
    if not moneyflow.empty:
        print(f"moneyflow接口: {len(moneyflow)}条记录")
        print(f"字段: {list(moneyflow.columns)}")
    else:
        print("moneyflow数据为空")
except Exception as e:
    print(f"moneyflow失败: {e}")

# 方法4: 网页爬虫降级方案测试
print("\n4. 网页爬虫可行性测试...")
print("方案: 使用公开网站获取市场涨跌统计")
print("  目标网站: 东方财富网市场概况")
print("  URL示例: http://quote.eastmoney.com/center/gridlist.html")
print("  技术: requests + BeautifulSoup")

# 方法5: 使用估算逻辑改进
print("\n5. 当前估算逻辑分析...")
print("当前使用: 上涨1200, 下跌2800 (总计4000)")
print("实际市场: 上海A股1703 + 深圳A股? ≈ 3000-4000只")
print("问题: 需要更准确的估算方法")

# 检查是否有深圳市场数据
try:
    sz_data = pro.daily_info(exchange='SZSE', trade_date=today)
    if not sz_data.empty:
        print(f"\n深圳市场数据:")
        for idx, row in sz_data.iterrows():
            if 'A股' in row['ts_name']:
                print(f"  {row['ts_name']}: {row['com_count']}只股票")
except Exception as e:
    print(f"深圳数据获取失败: {e}")

# 计算更合理的估算值
print("\n6. 改进估算方法...")
try:
    # 获取上海和深圳A股数量
    sh_a = pro.daily_info(ts_code='SH_A', trade_date=today)
    sz_a = pro.daily_info(ts_code='SZ_A', trade_date=today) if 'SZ_A' in pro.daily_info(trade_date=today)['ts_code'].values else None
    
    total_a = 0
    if not sh_a.empty:
        sh_count = sh_a.iloc[0]['com_count']
        total_a += sh_count
        print(f"上海A股: {sh_count}只")
    
    if sz_a is not None and not sz_a.empty:
        sz_count = sz_a.iloc[0]['com_count']
        total_a += sz_count
        print(f"深圳A股: {sz_count}只")
    else:
        # 估算深圳A股数量
        sz_estimate = 2300  # 典型值
        total_a += sz_estimate
        print(f"深圳A股(估算): {sz_estimate}只")
    
    print(f"总计A股: {total_a}只")
    
    # 根据市场情绪估算涨跌比例
    # 获取主要指数涨跌幅
    sh_index = pro.index_daily(ts_code='000001.SH', trade_date=today)
    if not sh_index.empty:
        sh_pct = sh_index.iloc[0]['pct_chg']
        print(f"上证指数涨跌: {sh_pct}%")
        
        # 简单估算：指数下跌时，下跌个股更多
        if sh_pct < -1.0:
            # 大跌日，下跌个股可能占70-80%
            down_ratio = 0.75
        elif sh_pct < -0.5:
            # 小跌日，下跌个股可能占60-70%
            down_ratio = 0.65
        elif sh_pct > 1.0:
            # 大涨日，上涨个股可能占70-80%
            down_ratio = 0.25
        elif sh_pct > 0.5:
            # 小涨日，上涨个股可能占60-70%
            down_ratio = 0.35
        else:
            # 震荡日，各占一半
            down_ratio = 0.5
        
        down_count = int(total_a * down_ratio)
        up_count = total_a - down_count
        
        print(f"基于指数涨跌的估算:")
        print(f"  上涨: {up_count}只 ({up_count/total_a*100:.1f}%)")
        print(f"  下跌: {down_count}只 ({down_count/total_a*100:.1f}%)")
        
except Exception as e:
    print(f"改进估算失败: {e}")
    import traceback
    traceback.print_exc()

print("\n✅ 测试完成")