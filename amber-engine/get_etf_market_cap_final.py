#!/usr/bin/env python3
"""
获取ETF市值数据 - 最终版本
获取10支ETF在两个日期的市值，计算涨跌幅
"""

import tushare as ts
import pandas as pd
import json
import time
import os

# 设置Tushare Token
TOKEN = "9e32ef28eac05c5fbb11e6f02a50da903def70f94b3018e93340568b"
ts.set_token(TOKEN)
pro = ts.pro_api()

# 日期
BASE_DATE = "20260227"
END_DATE = "20260320"

# ETF列表
etfs = [
    {"rank": 1, "name": "人工智能ETF", "code": "515070.SH", "industry": "人工智能"},
    {"rank": 2, "name": "半导体芯片ETF", "code": "512480.SH", "industry": "半导体芯片"},
    {"rank": 3, "name": "新能源车ETF", "code": "515030.SH", "industry": "新能源产业链"},
    {"rank": 4, "name": "光伏ETF", "code": "515790.SH", "industry": "光伏风电"},
    {"rank": 5, "name": "创新药ETF", "code": "512290.SH", "industry": "生物医药"},
    {"rank": 6, "name": "云计算ETF", "code": "516510.SH", "industry": "云计算"},
    {"rank": 7, "name": "军工ETF", "code": "512660.SH", "industry": "国防军工"},
    {"rank": 8, "name": "5GETF", "code": "515050.SH", "industry": "5G通信"},
    {"rank": 9, "name": "机器人ETF", "code": "562360.SH", "industry": "机器人"},
    {"rank": 10, "name": "大数据ETF", "code": "515400.SH", "industry": "大数据"}
]

def get_market_cap(ts_code, trade_date):
    """获取ETF在指定日期的市值（亿元）"""
    try:
        # 获取份额数据
        df_share = pro.fund_share(ts_code=ts_code, trade_date=trade_date)
        if len(df_share) == 0:
            return None
        
        share_data = df_share.iloc[0]
        fd_share = share_data['fd_share']  # 万份
        
        # 获取净值数据
        df_nav = pro.fund_nav(ts_code=ts_code, end_date=trade_date)
        if len(df_nav) == 0:
            return None
        
        # 查找指定日期的净值
        df_nav_date = df_nav[df_nav['nav_date'] == trade_date]
        if len(df_nav_date) == 0:
            # 使用最近日期的净值
            nav_data = df_nav.iloc[0]
        else:
            nav_data = df_nav_date.iloc[0]
        
        unit_nav = nav_data['unit_nav']  # 元
        
        # 计算市值：份额(万份) × 净值(元) = 市值(万元)
        # 转换为亿元：除以10000
        market_cap = fd_share * unit_nav / 10000
        return round(market_cap, 2)
        
    except Exception as e:
        print(f"获取 {ts_code} 市值失败: {e}")
        return None

def get_all_market_caps():
    """获取所有ETF的市值数据"""
    results = []
    
    print("📊 开始获取ETF市值数据...")
    
    for etf in etfs:
        print(f"\n🔍 处理 {etf['rank']}. {etf['name']} ({etf['code']})...")
        
        # 获取基准日市值
        base_cap = get_market_cap(etf['code'], BASE_DATE)
        
        # 获取结束日市值
        end_cap = get_market_cap(etf['code'], END_DATE)
        
        # 计算涨跌幅
        if base_cap and end_cap and base_cap > 0:
            pct_change = ((end_cap - base_cap) / base_cap) * 100
            pct_change_str = f"{pct_change:+.2f}%"
        else:
            pct_change_str = "N/A"
        
        # 获取净值变化（用于验证）
        try:
            df_nav_base = pro.fund_nav(ts_code=etf['code'], end_date=BASE_DATE)
            df_nav_end = pro.fund_nav(ts_code=etf['code'], end_date=END_DATE)
            
            nav_base = None
            nav_end = None
            
            if len(df_nav_base) > 0:
                df_nav_base_date = df_nav_base[df_nav_base['nav_date'] == BASE_DATE]
                if len(df_nav_base_date) > 0:
                    nav_base = df_nav_base_date.iloc[0]['unit_nav']
            
            if len(df_nav_end) > 0:
                df_nav_end_date = df_nav_end[df_nav_end['nav_date'] == END_DATE]
                if len(df_nav_end_date) > 0:
                    nav_end = df_nav_end_date.iloc[0]['unit_nav']
            
            nav_change = None
            if nav_base and nav_end and nav_base > 0:
                nav_change = ((nav_end - nav_base) / nav_base) * 100
                nav_change_str = f"{nav_change:+.2f}%"
            else:
                nav_change_str = "N/A"
                
        except:
            nav_base = None
            nav_end = None
            nav_change_str = "N/A"
        
        result = {
            "rank": etf['rank'],
            "name": etf['name'],
            "code": etf['code'],
            "industry": etf['industry'],
            "base_date": BASE_DATE,
            "base_market_cap": base_cap,
            "end_date": END_DATE,
            "end_market_cap": end_cap,
            "market_cap_change": pct_change_str,
            "base_nav": round(nav_base, 4) if nav_base else None,
            "end_nav": round(nav_end, 4) if nav_end else None,
            "nav_change": nav_change_str
        }
        
        results.append(result)
        
        print(f"  ✅ {BASE_DATE}: {base_cap}亿元, {END_DATE}: {end_cap}亿元, 涨跌幅: {pct_change_str}")
        if nav_base and nav_end:
            print(f"  📈 净值变化: {nav_base} → {nav_end} ({nav_change_str})")
        
        # API频率限制
        time.sleep(0.3)
    
    return results

def update_original_report(market_cap_results):
    """使用市值数据更新原始报告"""
    # 读取原始报告
    original_path = "/home/luckyelite/.openclaw/workspace/amber-engine/reports/etf_analysis/etf_analysis_20260320_222615.json"
    with open(original_path, 'r', encoding='utf-8') as f:
        report = json.load(f)
    
    # 创建市值数据映射
    market_cap_map = {r['code']: r for r in market_cap_results}
    
    # 更新ETF数据
    updated_etfs = []
    for etf in report['top_performing_etfs']:
        code = etf['code']
        if code in market_cap_map:
            cap_data = market_cap_map[code]
            updated_etf = etf.copy()
            
            # 添加市值数据
            updated_etf['base_market_cap'] = cap_data['base_market_cap']
            updated_etf['end_market_cap'] = cap_data['end_market_cap']
            updated_etf['market_cap_change'] = cap_data['market_cap_change']
            updated_etf['base_nav'] = cap_data['base_nav']
            updated_etf['end_nav'] = cap_data['end_nav']
            updated_etf['nav_change'] = cap_data['nav_change']
            
            updated_etfs.append(updated_etf)
        else:
            updated_etfs.append(etf)
    
    report['top_performing_etfs'] = updated_etfs
    
    # 更新报告说明
    report['data_source'] = "Tushare Pro数据库（净值+份额计算市值）"
    report['analysis_method'] = "基于净值与份额计算市值，重新计算涨跌幅"
    
    # 保存更新后的报告
    updated_path = original_path.replace(".json", "_with_market_cap.json")
    with open(updated_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 更新后的报告已保存: {updated_path}")
    return updated_path, report

def main():
    """主函数"""
    print("=" * 70)
    print("📊 ETF市值数据获取")
    print("=" * 70)
    
    try:
        # 获取市值数据
        market_cap_results = get_all_market_caps()
        
        # 显示汇总
        print("\n" + "=" * 70)
        print("📋 市值数据汇总")
        print("=" * 70)
        print(f"{'排名':<4} {'ETF名称':<12} {'基准日市值':<12} {'结束日市值':<12} {'涨跌幅':<10}")
        print("-" * 70)
        
        for r in market_cap_results:
            base = f"{r['base_market_cap']}亿" if r['base_market_cap'] else "N/A"
            end = f"{r['end_market_cap']}亿" if r['end_market_cap'] else "N/A"
            print(f"{r['rank']:<4} {r['name']:<12} {base:<12} {end:<12} {r['market_cap_change']:<10}")
        
        print("-" * 70)
        
        # 更新原始报告
        updated_path, updated_report = update_original_report(market_cap_results)
        
        print("\n✅ 任务完成!")
        print(f"📁 更新后的报告: {updated_path}")
        print("📊 需要更新HTML生成脚本以显示市值列")
        
        # 保存市值数据单独文件
        cap_data_path = "/home/luckyelite/.openclaw/workspace/amber-engine/reports/etf_market_cap/final_results.json"
        os.makedirs(os.path.dirname(cap_data_path), exist_ok=True)
        with open(cap_data_path, 'w', encoding='utf-8') as f:
            json.dump(market_cap_results, f, ensure_ascii=False, indent=2)
        
        print(f"📁 市值数据: {cap_data_path}")
        
        return True
        
    except Exception as e:
        print(f"❌ 执行失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)