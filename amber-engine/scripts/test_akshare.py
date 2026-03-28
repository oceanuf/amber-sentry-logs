#!/usr/bin/env python3
"""
测试AkShare是否可用
"""

import sys
import os

# 添加虚拟环境路径
venv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "venv")
if os.path.exists(venv_path):
    sys.path.insert(0, os.path.join(venv_path, "lib", "python3.12", "site-packages"))

try:
    import akshare as ak
    print("✅ AkShare导入成功")
    
    # 测试获取沪深300数据
    print("测试获取沪深300数据...")
    try:
        df = ak.stock_zh_index_daily_em(symbol="sh000300")
        print(f"✅ 数据获取成功，数据形状: {df.shape}")
        print(f"最新数据:")
        print(df.tail(3))
    except Exception as e:
        print(f"❌ 数据获取失败: {e}")
        
except ImportError as e:
    print(f"❌ AkShare导入失败: {e}")
    print("请运行: python3 -m venv venv && source venv/bin/activate && pip install akshare pandas")