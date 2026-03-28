#!/usr/bin/env python3
"""
简单的tushare测试脚本
"""

import sys
import os

# 添加tushare-data skill路径
skill_path = "/home/luckyelite/.openclaw/workspace/skills/tushare-data"
if skill_path not in sys.path:
    sys.path.insert(0, skill_path)

# 设置token
os.environ['TUSHARE_TOKEN'] = "9e32ef28eac05c5fbb11e6f02a50da903def70f94b3018e93340568b"

print("🔧 测试tushare-data skill...")
print(f"Token: {os.environ['TUSHARE_TOKEN'][:10]}...")

# 尝试导入tushare
try:
    import tushare as ts
    print("✅ tushare库导入成功")
    
    # 测试连接
    pro = ts.pro_api(os.environ['TUSHARE_TOKEN'])
    print("✅ tushare pro接口初始化成功")
    
    # 简单测试 - 获取交易日历
    try:
        data = pro.trade_cal(exchange='SSE', start_date='20240101', end_date='20240110')
        if data is not None:
            print(f"✅ 数据获取成功，返回 {len(data)} 条记录")
            print("示例数据:")
            print(data.head())
        else:
            print("❌ 数据获取失败")
    except Exception as e:
        print(f"❌ 数据获取失败: {e}")
        
except ImportError as e:
    print(f"❌ tushare库导入失败: {e}")
    print("\n💡 安装建议:")
    print("1. 使用系统包管理器: sudo apt install python3-tushare")
    print("2. 或使用pip安装: pip install tushare --break-system-packages")
    print("3. 或创建虚拟环境: python3 -m venv venv && source venv/bin/activate && pip install tushare")

print("\n🎯 中国人寿测试计划:")
print("股票代码: 601628.SH (A股)")
print("测试项目:")
print("1. 基本信息查询")
print("2. 日线行情数据")
print("3. 财务指标分析")
print("4. 公司信息查询")
print("5. 概念板块分析")