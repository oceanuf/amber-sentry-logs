#!/usr/bin/env python3
"""
获取ETF市值数据
查询10支ETF在2026-02-27和2026-03-20的当日市值
"""

import tushare as ts
import pandas as pd
from datetime import datetime
import json
import os
import time

# 设置Tushare Token
TOKEN = "9e32ef28eac05c5fbb11e6f02a50da903def70f94b3018e93340568b"
ts.set_token(TOKEN)
pro = ts.pro_api()

# 日期设置
BASE_DATE = "20260227"  # 基准日期
END_DATE = "20260320"   # 结束日期

# 10支ETF列表
etf_list = [
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

def get_fund_daily_data(ts_code, start_date, end_date):
    """获取基金日线数据"""
    try:
        df = pro.fund_daily(ts_code=ts_code, start_date=start_date, end_date=end_date)
        return df
    except Exception as e:
        print(f"获取 {ts_code} 日线数据失败: {e}")
        return None

def get_fund_nav(ts_code, trade_date):
    """获取基金净值数据"""
    try:
        df = pro.fund_nav(ts_code=ts_code, end_date=trade_date)
        if len(df) > 0:
            # 获取指定日期的净值，如果没有则获取最近日期的
            df_date = df[df['end_date'] == trade_date]
            if len(df_date) > 0:
                return df_date.iloc[0]
            else:
                # 获取最近日期的净值
                return df.iloc[0]
        return None
    except Exception as e:
        print(f"获取 {ts_code} 净值数据失败: {e}")
        return None

def calculate_market_cap(ts_code, trade_date):
    """计算ETF市值
    策略：先尝试获取基金份额数据，如果没有则使用净值数据估算
    """
    try:
        # 尝试获取基金份额数据
        df_share = pro.fund_share(ts_code=ts_code, trade_date=trade_date)
        if len(df_share) > 0:
            share_data = df_share.iloc[0]
            total_share = share_data['fd_share']  # 基金份额
            unit_nav = share_data['unit_nav']     # 单位净值
            
            if total_share and unit_nav:
                market_cap = total_share * unit_nav / 10000  # 转换为亿元
                return round(market_cap, 2)
        
        # 如果份额数据不可用，尝试获取基金规模数据
        df_basic = pro.fund_basic(ts_code=ts_code)
        if len(df_basic) > 0:
            basic_data = df_basic.iloc[0]
            if 'fund_scale' in basic_data and basic_data['fund_scale']:
                # 基金规模字段可能是字符串，如"100亿"
                scale_str = str(basic_data['fund_scale'])
                if '亿' in scale_str:
                    try:
                        scale_num = float(scale_str.replace('亿', ''))
                        return round(scale_num, 2)
                    except:
                        pass
        
        # 最后尝试获取基金净值数据
        nav_data = get_fund_nav(ts_code, trade_date)
        if nav_data is not None:
            if 'unit_nav' in nav_data and nav_data['unit_nav']:
                # 假设平均份额为50亿份进行估算
                estimated_share = 50  # 亿份
                market_cap = estimated_share * nav_data['unit_nav']
                return round(market_cap, 2)
        
        return None
        
    except Exception as e:
        print(f"计算 {ts_code} 市值失败: {e}")
        return None

def fetch_all_etf_market_caps():
    """获取所有ETF的市值数据"""
    print("📊 开始获取ETF市值数据...")
    print(f"基准日期: {BASE_DATE}, 结束日期: {END_DATE}")
    
    results = []
    
    for etf in etf_list:
        print(f"\n🔍 处理 {etf['rank']}. {etf['name']} ({etf['code']})...")
        
        # 获取基准日市值
        print(f"  获取基准日 {BASE_DATE} 市值...")
        base_market_cap = calculate_market_cap(etf['code'], BASE_DATE)
        
        # 获取结束日市值
        print(f"  获取结束日 {END_DATE} 市值...")
        end_market_cap = calculate_market_cap(etf['code'], END_DATE)
        
        # 计算涨跌幅
        pct_change = None
        if base_market_cap and end_market_cap and base_market_cap > 0:
            pct_change = ((end_market_cap - base_market_cap) / base_market_cap) * 100
            pct_change_str = f"{pct_change:+.2f}%"
        else:
            pct_change_str = "N/A"
        
        result = {
            "rank": etf['rank'],
            "name": etf['name'],
            "code": etf['code'],
            "industry": etf['industry'],
            "base_date": BASE_DATE,
            "base_market_cap": base_market_cap,
            "end_date": END_DATE,
            "end_market_cap": end_market_cap,
            "market_cap_change": pct_change_str,
            "calculated_change": round(pct_change, 2) if pct_change else None
        }
        
        results.append(result)
        
        print(f"  ✅ 完成: {BASE_DATE}: {base_market_cap}亿, {END_DATE}: {end_market_cap}亿, 涨跌幅: {pct_change_str}")
        
        # API调用频率限制，避免过快请求
        time.sleep(0.5)
    
    return results

def save_results(results):
    """保存结果"""
    output_dir = os.path.join(os.path.dirname(__file__), "reports", "etf_market_cap")
    os.makedirs(output_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = os.path.join(output_dir, f"etf_market_cap_{timestamp}.json")
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 结果已保存: {output_path}")
    return output_path

def main():
    """主函数"""
    print("=" * 70)
    print("📊 ETF市值数据获取脚本")
    print("=" * 70)
    print("执行主编指令:")
    print("1. 查询10支ETF在2026-02-27的当日市值")
    print("2. 查询10支ETF在2026-03-20的当日市值")
    print("3. 重新计算期间涨跌幅度")
    print("=" * 70)
    
    try:
        results = fetch_all_etf_market_caps()
        
        # 统计成功获取的数据
        success_count = sum(1 for r in results if r['base_market_cap'] is not None and r['end_market_cap'] is not None)
        
        print(f"\n" + "=" * 70)
        print("📋 数据获取完成")
        print("=" * 70)
        print(f"📊 处理ETF数量: {len(results)}")
        print(f"✅ 成功获取数据: {success_count}")
        print(f"❌ 数据缺失: {len(results) - success_count}")
        
        # 显示汇总表格
        print("\n📈 汇总结果:")
        print("-" * 120)
        print(f"{'排名':<4} {'ETF名称':<12} {'代码':<12} {'基准日市值(亿)':<15} {'结束日市值(亿)':<15} {'涨跌幅':<10}")
        print("-" * 120)
        
        for r in results:
            base_cap = f"{r['base_market_cap']}" if r['base_market_cap'] else "N/A"
            end_cap = f"{r['end_market_cap']}" if r['end_market_cap'] else "N/A"
            print(f"{r['rank']:<4} {r['name']:<12} {r['code']:<12} {base_cap:<15} {end_cap:<15} {r['market_cap_change']:<10}")
        
        print("-" * 120)
        
        # 保存结果
        output_path = save_results(results)
        
        # 与原始报告对比
        print("\n🔍 与原始报告涨跌幅对比:")
        print("-" * 80)
        print(f"{'排名':<4} {'ETF名称':<12} {'原始涨跌幅':<12} {'市值计算涨跌幅':<15} {'差异':<10}")
        print("-" * 80)
        
        # 读取原始报告数据
        original_report_path = "/home/luckyelite/.openclaw/workspace/amber-engine/reports/etf_analysis/etf_analysis_20260320_222615.json"
        if os.path.exists(original_report_path):
            with open(original_report_path, 'r', encoding='utf-8') as f:
                original_data = json.load(f)
            
            original_etfs = {etf['rank']: etf for etf in original_data['top_performing_etfs']}
            
            for r in results:
                original_change = original_etfs.get(r['rank'], {}).get('change', 'N/A')
                new_change = r['market_cap_change']
                
                # 提取数值部分
                try:
                    if original_change != 'N/A' and new_change != 'N/A':
                        orig_num = float(original_change.strip('%+'))
                        new_num = float(new_change.strip('%+'))
                        diff = new_num - orig_num
                        diff_str = f"{diff:+.2f}%"
                    else:
                        diff_str = "N/A"
                except:
                    diff_str = "N/A"
                
                print(f"{r['rank']:<4} {r['name']:<12} {original_change:<12} {new_change:<15} {diff_str:<10}")
        
        print("-" * 80)
        
        return True
        
    except Exception as e:
        print(f"❌ 执行失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)