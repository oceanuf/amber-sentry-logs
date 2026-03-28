#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
琥珀引擎青铜法典数据采集脚本 (Tushare Pro修复版本)
修复fund_nav接口字段名问题
"""

import tushare as ts
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import os
import time
import sys

print("="*60)
print("🚀 琥珀引擎青铜法典数据采集任务启动 (Tushare Pro修复版)")
print("="*60)

# 设置Tushare Token
TOKEN = "9e32ef28eac05c5fbb11e6f02a50da903def70f94b3018e93340568b"
ts.set_token(TOKEN)
pro = ts.pro_api()

# 简化ETF列表，先测试5支
TEST_ETFS = [
    {"ts_code": "510300.SH", "name": "沪深300ETF"},
    {"ts_code": "512480.SH", "name": "半导体ETF"},
    {"ts_code": "512880.SH", "name": "证券ETF"},
    {"ts_code": "518880.SH", "name": "黄金ETF"},
    {"ts_code": "159915.SZ", "name": "创业板ETF"},
]

def fetch_etf_nav_simple(ts_code, days=30):
    """简化版ETF净值数据获取"""
    print(f"\n🔍 采集ETF数据: {ts_code}")
    
    try:
        # 直接使用fund_daily接口获取日线数据
        end_date = datetime.now().strftime("%Y%m%d")
        start_date = (datetime.now() - timedelta(days=days*2)).strftime("%Y%m%d")
        
        print(f"   日期范围: {start_date} 至 {end_date}")
        
        # 获取日线数据
        df = pro.fund_daily(ts_code=ts_code, start_date=start_date, end_date=end_date)
        
        if df.empty:
            print(f"   ❌ 无日线数据")
            return None
        
        # 按日期排序
        df = df.sort_values('trade_date', ascending=False)
        
        nav_data = []
        for i, row in df.iterrows():
            if len(nav_data) >= days:
                break
                
            nav_data.append({
                "date": row['trade_date'],
                "nav": float(row['close']),
                "change": float(row['pct_chg']) if not pd.isna(row['pct_chg']) else 0.0
            })
        
        print(f"   ✅ 获取成功: {len(nav_data)}条记录")
        print(f"     最新净值: {nav_data[0]['nav']} ({nav_data[0]['change']}%)")
        
        return nav_data
        
    except Exception as e:
        print(f"   ❌ 数据采集失败: {e}")
        return None

def main():
    """主函数 - 测试5支ETF"""
    print(f"\n📊 测试采集5支ETF数据")
    
    success_count = 0
    
    for i, etf in enumerate(TEST_ETFS):
        print(f"\n[{i+1}/5] {etf['name']} ({etf['ts_code']})")
        
        nav_data = fetch_etf_nav_simple(etf['ts_code'], days=30)
        
        if nav_data:
            # 保存数据
            code = etf['ts_code'].split('.')[0]
            output_path = f"data/nav_history/{code}.json"
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(nav_data, f, ensure_ascii=False, indent=2)
            
            print(f"   💾 已保存: {output_path}")
            success_count += 1
        else:
            print(f"   ❌ 采集失败")
        
        time.sleep(1)
    
    print(f"\n🎯 测试完成: {success_count}/5 成功")
    
    if success_count > 0:
        # 创建进度文件
        with open("PROGRESS_115.txt", 'w') as f:
            f.write(f"进度: 成功采集 {success_count} 支ETF数据\n")
            f.write(f"时间: {datetime.now().strftime('%H:%M:%S')}\n")
        
        print(f"📝 进度文件已创建: PROGRESS_115.txt")
        return True
    
    return False

if __name__ == "__main__":
    main()
