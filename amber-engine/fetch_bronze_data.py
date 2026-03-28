#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
琥珀引擎青铜法典数据采集脚本 (Tushare Pro版本)
任务：获取50支ETF的30日单位净值数据
执行者：工程师 Cheese
协议：[2613-115号] 数据引擎全量开采与静态化预演
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
print("🚀 琥珀引擎青铜法典数据采集任务启动 (Tushare Pro)")
print("任务：获取50支ETF的30日单位净值数据")
print("执行者：工程师 Cheese")
print("协议：[2613-115号] 数据引擎全量开采与静态化预演")
print("="*60)

# 设置Tushare Token
TOKEN = "9e32ef28eac05c5fbb11e6f02a50da903def70f94b3018e93340568b"
ts.set_token(TOKEN)
pro = ts.pro_api()

# 青铜法典50支ETF列表 (基于现有数据)
BRONZE_ETFS = [
    # 战略宽基 (12支)
    {"ts_code": "510300.SH", "name": "华泰柏瑞沪深300ETF"},
    {"ts_code": "159915.SZ", "name": "易方达创业板ETF"},
    {"ts_code": "510050.SH", "name": "华夏上证50ETF"},
    {"ts_code": "510500.SH", "name": "南方中证500ETF"},
    {"ts_code": "512990.SH", "name": "华夏MSCI中国A50ETF"},
    {"ts_code": "513500.SH", "name": "博时标普500ETF"},
    {"ts_code": "159901.SZ", "name": "深100ETF"},
    {"ts_code": "159902.SZ", "name": "中小板ETF"},
    {"ts_code": "159903.SZ", "name": "深成ETF"},
    {"ts_code": "159919.SZ", "name": "沪深300ETF"},
    {"ts_code": "159949.SZ", "name": "创业板50ETF"},
    {"ts_code": "512100.SH", "name": "南方中证1000ETF"},
    
    # 内需基石 (10支)
    {"ts_code": "512880.SH", "name": "国泰证券ETF"},
    {"ts_code": "512000.SH", "name": "华宝券商ETF"},
    {"ts_code": "512690.SH", "name": "鹏华酒ETF"},
    {"ts_code": "512800.SH", "name": "华宝银行ETF"},
    {"ts_code": "159869.SZ", "name": "华夏游戏ETF"},
    {"ts_code": "159928.SZ", "name": "汇添富消费ETF"},
    {"ts_code": "512900.SH", "name": "南方证券ETF"},
    {"ts_code": "159732.SZ", "name": "消费电子ETF"},
    {"ts_code": "159766.SZ", "name": "旅游ETF"},
    {"ts_code": "512980.SH", "name": "广发传媒ETF"},
    
    # 前沿技术 (7支)
    {"ts_code": "513100.SH", "name": "国泰纳指100ETF"},
    {"ts_code": "159941.SZ", "name": "广发纳指ETF"},
    {"ts_code": "159807.SZ", "name": "易方达中概互联ETF"},
    {"ts_code": "512770.SH", "name": "华宝港股通互联网ETF"},
    {"ts_code": "513050.SH", "name": "易方达中概互联ETF"},
    {"ts_code": "513600.SH", "name": "南方恒生科技ETF"},
    {"ts_code": "513660.SH", "name": "华夏恒生互联网ETF"},
    
    # 安全韧性 (6支)
    {"ts_code": "518880.SH", "name": "华安黄金ETF"},
    {"ts_code": "512660.SH", "name": "国泰军工ETF"},
    {"ts_code": "518800.SH", "name": "国泰黄金ETF"},
    {"ts_code": "512670.SH", "name": "国防ETF"},
    {"ts_code": "512710.SH", "name": "富国军工龙头ETF"},
    {"ts_code": "512960.SH", "name": "景顺长城军工ETF"},
    
    # 数智基建 (4支)
    {"ts_code": "515050.SH", "name": "华夏5G通信ETF"},
    {"ts_code": "517800.SH", "name": "嘉实软件ETF"},
    {"ts_code": "512330.SH", "name": "南方信息创新ETF"},
    {"ts_code": "515880.SH", "name": "国泰通信ETF"},
    
    # 现代物流 (1支)
    {"ts_code": "159870.SZ", "name": "物流ETF"},
    
    # 生物安全 (4支)
    {"ts_code": "512170.SH", "name": "华宝医疗ETF"},
    {"ts_code": "512010.SH", "name": "易方达医药ETF"},
    {"ts_code": "512290.SH", "name": "国泰生物医药ETF"},
    {"ts_code": "512600.SH", "name": "嘉实医药健康ETF"},
    
    # 科技自立 (6支)
    {"ts_code": "512480.SH", "name": "国联安半导体ETF"},
    {"ts_code": "515000.SH", "name": "华宝科技ETF"},
    {"ts_code": "159801.SZ", "name": "广发芯片ETF"},
    {"ts_code": "159995.SZ", "name": "国泰半导体ETF"},
    {"ts_code": "512760.SH", "name": "国泰半导体芯片ETF"},
    {"ts_code": "588000.SH", "name": "科创50ETF"},
]

def get_trading_dates(days=30):
    """获取最近N个交易日日期"""
    end_date = datetime.now().strftime("%Y%m%d")
    start_date = (datetime.now() - timedelta(days=days*2)).strftime("%Y%m%d")  # 多取一些确保有30个交易日
    
    try:
        # 获取交易日历
        df_cal = pro.trade_cal(exchange='SSE', start_date=start_date, end_date=end_date, is_open='1')
        trading_dates = df_cal['cal_date'].tolist()
        trading_dates.sort(reverse=True)  # 从最新到最旧
        
        # 取最近30个交易日
        if len(trading_dates) >= days:
            return trading_dates[:days]
        else:
            print(f"⚠️  只能获取到{len(trading_dates)}个交易日，少于要求的{days}个")
            return trading_dates
    except Exception as e:
        print(f"❌ 获取交易日历失败: {e}")
        # 生成模拟日期作为fallback
        dates = []
        for i in range(days):
            date = (datetime.now() - timedelta(days=i)).strftime("%Y%m%d")
            dates.append(date)
        return dates

def fetch_etf_nav_data(ts_code, days=30):
    """获取ETF的单位净值数据"""
    print(f"\n🔍 采集ETF单位净值数据: {ts_code}")
    
    try:
        # 获取最近N个交易日日期
        trading_dates = get_trading_dates(days)
        
        # 获取基金净值数据
        end_date = trading_dates[0]  # 最新日期
        start_date = trading_dates[-1]  # 最旧日期
        
        print(f"   日期范围: {start_date} 至 {end_date}")
        print(f"   交易日数量: {len(trading_dates)}")
        
        # 使用fund_nav接口获取单位净值
        df_nav = pro.fund_nav(ts_code=ts_code, start_date=start_date, end_date=end_date)
        
        if df_nav.empty:
            print(f"   ⚠️  无净值数据，尝试获取日线数据...")
            # 尝试使用fund_daily接口
            df_daily = pro.fund_daily(ts_code=ts_code, start_date=start_date, end_date=end_date)
            
            if df_daily.empty:
                print(f"   ❌ 无任何数据，使用T-2回退策略")
                return None
            
            # 使用收盘价作为净值
            df_daily = df_daily.sort_values('trade_date', ascending=False)
            nav_data = []
            
            for i, row in df_daily.iterrows():
                nav_data.append({
                    "date": row['trade_date'],
                    "nav": float(row['close']),
                    "change": float(row['pct_chg']) if not pd.isna(row['pct_chg']) else 0.0
                })
            
            print(f"   ✅ 使用日线数据获取成功: {len(nav_data)}条记录")
            return nav_data[:days]  # 限制为要求的数量
        
        # 处理净值数据
        df_nav = df_nav.sort_values('end_date', ascending=False)
        
        # 优先使用unit_nav（单位净值），如果没有则使用accum_nav（累计净值）
        if 'unit_nav' in df_nav.columns and not df_nav['unit_nav'].isna().all():
            nav_field = 'unit_nav'
        elif 'accum_nav' in df_nav.columns and not df_nav['accum_nav'].isna().all():
            nav_field = 'accum_nav'
        else:
            print(f"   ❌ 无净值字段可用")
            return None
        
        nav_data = []
        for i, row in df_nav.iterrows():
            nav_value = float(row[nav_field]) if not pd.isna(row[nav_field]) else 0.0
            
            # 计算涨跌幅（与前一日比较）
            change = 0.0
            if i < len(df_nav) - 1:
                prev_nav = float(df_nav.iloc[i+1][nav_field]) if not pd.isna(df_nav.iloc[i+1][nav_field]) else nav_value
                if prev_nav > 0:
                    change = round((nav_value / prev_nav - 1) * 100, 2)
            
            nav_data.append({
                "date": row['end_date'],
                "nav": round(nav_value, 4),
                "change": change
            })
        
        print(f"   ✅ 净值数据获取成功: {len(nav_data)}条记录")
        print(f"     最新净值: {nav_data[0]['nav']} ({nav_data[0]['change']}%)")
        print(f"     数据字段: {nav_field}")
        
        return nav_data[:days]  # 限制为要求的数量
        
    except Exception as e:
        print(f"   ❌ 数据采集失败: {e}")
        return None

def save_nav_data(ts_code, nav_data, output_dir="data/nav_history"):
    """保存净值数据到JSON文件"""
    if nav_data is None or len(nav_data) == 0:
        print(f"   ⚠️  无有效数据，跳过保存")
        return False
    
    # 确保输出目录存在
    os.makedirs(output_dir, exist_ok=True)
    
    # 提取代码部分（去除市场后缀）
    code = ts_code.split('.')[0]
    output_path = os.path.join(output_dir, f"{code}.json")
    
    # 保存为JSON
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(nav_data, f, ensure_ascii=False, indent=2)
    
    print(f"   💾 数据已保存: {output_path}")
    print(f"     记录数量: {len(nav_data)}")
    
    return True

def main():
    """主函数"""
    print("\n" + "="*60)
    print("📊 开始采集青铜法典50支ETF净值数据")
    print("="*60)
    
    # 检查参数
    limit = None
    if len(sys.argv) > 1 and sys.argv[1] == "--limit":
        try:
            limit = int(sys.argv[2])
            print(f"📋 限制采集数量: {limit}支ETF")
        except:
            pass
    
    # 确定要采集的ETF列表
    if limit:
        etf_list = BRONZE_ETFS[:limit]
    else:
        etf_list = BRONZE_ETFS
    
    print(f"📋 计划采集 {len(etf_list)} 支ETF数据")
    
    success_count = 0
    failed_count = 0
    
    # 创建进度文件
    progress_file = "PROGRESS_115.txt"
    
    for i, etf in enumerate(etf_list):
        print(f"\n" + "="*50)
        print(f"📈 [{i+1}/{len(etf_list)}] {etf['name']} ({etf['ts_code']})")
        print("="*50)
        
        # 采集净值数据
        nav_data = fetch_etf_nav_data(etf['ts_code'], days=30)
        
        if nav_data:
            # 保存数据
            if save_nav_data(etf['ts_code'], nav_data):
                success_count += 1
            else:
                failed_count += 1
        else:
            print(f"   ❌ 数据采集失败，跳过此ETF")
            failed_count += 1
        
        # 每成功10个ETF，更新进度文件
        if success_count > 0 and success_count % 10 == 0:
            with open(progress_file, 'w', encoding='utf-8') as f:
                f.write(f"进度更新: 已成功采集 {success_count} 支ETF数据\n")
                f.write(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"成功率: {success_count/(success_count+failed_count)*100:.1f}%\n")
            print(f"\n📝 进度文件已更新: {progress_file}")
        
        # 避免请求过于频繁 (Tushare有频率限制)
        time.sleep(1)
    
    # 最终统计
    print("\n" + "="*60)
    print("🎯 数据采集任务完成")
    print("="*60)
    
    total = success_count + failed_count
    success_rate = success_count / total * 100 if total > 0 else 0
    
    print(f"📊 采集统计:")
    print(f"   计划采集: {len(etf_list)} 支ETF")
    print(f"   成功采集: {success_count} 支")
    print(f"   采集失败: {failed_count} 支")
    print(f"   成功率: {success_rate:.1f}%")
    
    # 生成最终报告
    report_file = "REPORT_115_FINAL.txt"
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(f"📋 [2613-115号] 数据引擎全量开采任务报告\n")
        f.write(f"执行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"执行人: 工程师 Cheese\n")
        f.write(f"协议: [2613-115号] 数据引擎全量开采与静态化预演\n")
        f.write(f"\n📊 采集统计:\n")
        f.write(f"   计划采集: {len(etf_list)} 支ETF\n")
        f.write(f"   成功采集: {success_count} 支\n")
        f.write(f"   采集失败: {failed_count} 支\n")
        f.write(f"   成功率: {success_rate:.1f}%\n")
        f.write(f"\n💾 数据存储:\n")
        f.write(f"   目录: data/nav_history/\n")
        f.write(f"   文件数量: {success_count} 个JSON文件\n")
        f.write(f"\n🚀 下一步:\n")
        f.write(f"   运行静态渲染引擎: python3 scripts/build_bronze_web.py\n")
    
    print(f"\n📄 最终报告已生成: {report_file}")
    
    if success_count > 0:
        print(f"\n✅ 数据采集任务完成，准备进行静态渲染")
        return True
    else:
        print(f"\n❌ 数据采集任务失败，无有效数据")
        return False

if __name__ == "__main__":
    main()
