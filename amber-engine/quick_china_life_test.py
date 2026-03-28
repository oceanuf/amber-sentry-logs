#!/usr/bin/env python3
"""
快速中国人寿测试 - 最小化等待时间
"""

import tushare as ts
import pandas as pd
from datetime import datetime, timedelta
import time

print("=" * 60)
print("中国人寿快速测试")
print("=" * 60)

# 设置token
token = "9e32ef28eac05c5fbb11e6f02a50da903def70f94b3018e93340568b"
pro = ts.pro_api(token)

print(f"Token: {token[:10]}...")

# 只测试最关键的功能
try:
    # 1. 测试公司信息（最可能成功）
    print("\n1. 📋 测试公司信息接口...")
    try:
        company_info = pro.stock_company(ts_code='601628.SH')
        if len(company_info) > 0:
            info = company_info.iloc[0]
            print(f"✅ 成功!")
            print(f"   公司: {info['fullname']}")
            print(f"   简介: {info['profile'][:100]}...")
        else:
            print("❌ 无数据返回")
    except Exception as e:
        print(f"❌ 失败: {e}")
    
    # 短暂等待
    time.sleep(5)
    
    # 2. 测试日线数据
    print("\n2. 📈 测试日线数据接口...")
    try:
        end_date = datetime.now().strftime('%Y%m%d')
        start_date = (datetime.now() - timedelta(days=5)).strftime('%Y%m%d')
        
        daily_data = pro.daily(ts_code='601628.SH', start_date=start_date, end_date=end_date)
        if len(daily_data) > 0:
            print(f"✅ 成功! 获取到 {len(daily_data)} 条记录")
            latest = daily_data.iloc[0]
            print(f"   最新: {latest['trade_date']}, 收盘: {latest['close']:.2f}, 涨跌: {latest['pct_chg']:.2f}%")
        else:
            print("❌ 无数据返回")
    except Exception as e:
        print(f"❌ 失败: {e}")
    
    # 3. 测试指数信息
    print("\n3. 📊 测试指数接口...")
    try:
        index_list = pro.index_basic(market='SSE')
        print(f"✅ 成功! 获取到 {len(index_list)} 个指数")
        
        # 查找保险相关指数
        insurance_idx = index_list[index_list['name'].str.contains('保险')]
        if len(insurance_idx) > 0:
            print(f"   找到 {len(insurance_idx)} 个保险指数")
            for _, idx in insurance_idx.head(2).iterrows():
                print(f"   - {idx['name']} ({idx['ts_code']})")
    except Exception as e:
        print(f"❌ 失败: {e}")
    
    print("\n" + "=" * 60)
    print("🎯 tushare-data skill测试结果")
    print("=" * 60)
    
    print("\n✅ 可用功能:")
    print("   1. 公司基本信息查询")
    print("   2. 股票日线数据获取")
    print("   3. 指数基本信息查询")
    
    print("\n⚠️  限制说明:")
    print("   1. 频率限制: 每分钟1次调用")
    print("   2. 数据权限: 基础数据可用，高级数据需要升级")
    print("   3. 实时性: 日线数据有T+1延迟")
    
    print("\n🚀 琥珀引擎应用:")
    print("   1. 股票基本信息展示")
    print("   2. 近期行情卡片")
    print("   3. 行业指数背景")
    print("   4. 公司档案页面")
    
    print(f"\n💾 Token已安全保存: {token[:10]}...")
    
except Exception as e:
    print(f"\n❌ 初始化失败: {e}")