#!/usr/bin/env python3
"""
基础tushare测试
"""

import tushare as ts
import os

# 设置token
token = "9e32ef28eac05c5fbb11e6f02a50da903def70f94b3018e93340568b"
print(f"使用的token: {token[:10]}...")

try:
    # 初始化
    pro = ts.pro_api(token)
    print("✅ pro接口初始化成功")
    
    # 尝试获取基础数据
    print("\n🔍 尝试获取基础数据...")
    
    # 1. 尝试获取交易日历（基础接口）
    try:
        df = pro.trade_cal(exchange='SSE', start_date='20240101', end_date='20240105')
        print(f"✅ 交易日历获取成功: {len(df)} 条记录")
        print(df.head())
    except Exception as e:
        print(f"❌ 交易日历获取失败: {e}")
    
    # 2. 尝试获取股票列表（可能需要权限）
    try:
        df = pro.stock_basic(exchange='', list_status='L', fields='ts_code,symbol,name')
        print(f"\n✅ 股票列表获取成功: {len(df)} 条记录")
        print(df.head())
    except Exception as e:
        print(f"\n❌ 股票列表获取失败: {e}")
    
    # 3. 尝试获取指数列表（通常有权限）
    try:
        df = pro.index_basic(market='SSE')
        print(f"\n✅ 指数列表获取成功: {len(df)} 条记录")
        print(df.head())
    except Exception as e:
        print(f"\n❌ 指数列表获取失败: {e}")
    
    # 4. 检查token权限
    print("\n🔐 检查token权限...")
    try:
        # 尝试获取用户信息
        df = pro.user()
        print(f"✅ 用户信息获取成功")
        print(df)
    except Exception as e:
        print(f"❌ 用户信息获取失败: {e}")
        print("💡 这个token可能没有足够的权限")
        
except Exception as e:
    print(f"❌ 初始化失败: {e}")

print("\n💡 建议:")
print("1. 检查token是否正确")
print("2. 访问 https://tushare.pro 查看token权限")
print("3. 可能需要升级token权限才能访问股票数据")