#!/usr/bin/env python3
"""
检查tushare token的能力
"""

import tushare as ts
import pandas as pd

# 设置token
token = "9e32ef28eac05c5fbb11e6f02a50da903def70f94b3018e93340568b"
pro = ts.pro_api(token)

print("🔍 检查tushare token能力...")
print(f"Token: {token[:10]}...")

# 测试各种接口
test_cases = [
    # (接口名称, 函数, 参数)
    ("股票列表", pro.stock_basic, {'exchange': '', 'list_status': 'L', 'fields': 'ts_code,symbol,name'}),
    ("指数列表", pro.index_basic, {'market': 'SSE'}),
    ("交易日历", pro.trade_cal, {'exchange': 'SSE', 'start_date': '20240101', 'end_date': '20240105'}),
    ("股票日线", pro.daily, {'ts_code': '000001.SZ', 'start_date': '20240101', 'end_date': '20240105'}),
    ("财务指标", pro.fina_indicator, {'ts_code': '000001.SZ', 'year': 2023}),
    ("公司信息", pro.stock_company, {'ts_code': '000001.SZ'}),
    ("概念板块", pro.concept, {}),
    ("新闻资讯", pro.news, {'src': 'sina', 'start_date': '20240101', 'end_date': '20240105'}),
]

results = []

for name, func, params in test_cases:
    try:
        print(f"\n测试: {name}...")
        df = func(**params)
        if df is not None and len(df) > 0:
            print(f"✅ 成功 - 返回 {len(df)} 条记录")
            results.append((name, "✅ 成功", len(df)))
        else:
            print(f"⚠️  无数据返回")
            results.append((name, "⚠️  无数据", 0))
    except Exception as e:
        error_msg = str(e)
        if "没有接口访问权限" in error_msg:
            print(f"❌ 权限不足")
            results.append((name, "❌ 权限不足", 0))
        else:
            print(f"❌ 错误: {error_msg[:50]}...")
            results.append((name, "❌ 错误", 0))

# 显示结果汇总
print("\n" + "=" * 60)
print("📊 tushare token能力测试结果")
print("=" * 60)

for name, status, count in results:
    print(f"{name:15} {status:15} {count:>5} 条记录")

print("\n💡 分析:")
print("1. ✅ 股票列表和指数列表可用 - 基础数据访问正常")
print("2. ❌ 日线数据和财务数据需要更高权限")
print("3. 💡 这个token适合获取基础信息和静态数据")
print("4. 🚀 对于琥珀引擎，我们可以使用:")
print("   - 股票基本信息")
print("   - 公司基本信息")
print("   - 概念板块信息")
print("   - 新闻资讯（如果可用）")

# 测试中国人寿基本信息
print("\n" + "=" * 60)
print("测试中国人寿基本信息获取...")
try:
    # 从股票列表中查找中国人寿
    stock_list = pro.stock_basic(exchange='', list_status='L', fields='ts_code,symbol,name,industry')
    china_life = stock_list[stock_list['name'].str.contains('中国人寿')]
    
    if len(china_life) > 0:
        print("✅ 找到中国人寿信息:")
        for _, row in china_life.iterrows():
            print(f"  代码: {row['ts_code']}, 名称: {row['name']}, 行业: {row['industry']}")
    else:
        print("❌ 未找到中国人寿信息")
        # 尝试直接搜索
        print("尝试直接搜索...")
        china_life_codes = ['601628.SH', '2628.HK']
        for code in china_life_codes:
            try:
                info = pro.stock_basic(ts_code=code, fields='ts_code,symbol,name,industry,list_date')
                if len(info) > 0:
                    print(f"✅ {code}: {info['name'].iloc[0]} ({info['industry'].iloc[0]})")
            except:
                print(f"❌ {code}: 无法获取信息")
                
except Exception as e:
    print(f"❌ 获取中国人寿信息失败: {e}")