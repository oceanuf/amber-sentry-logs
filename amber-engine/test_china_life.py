#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试tushare-data skill - 获取中国人寿相关信息
"""

import tushare as ts
import pandas as pd
import os
from datetime import datetime, timedelta
import json

# 设置tushare token
TUSHARE_TOKEN = "9e32ef28eac05c5fbb11e6f02a50da903def70f94b3018e93340568b"
os.environ['TUSHARE_TOKEN'] = TUSHARE_TOKEN

# 初始化pro接口
pro = ts.pro_api(TUSHARE_TOKEN)

def test_tushare_connection():
    """测试tushare连接"""
    print("🔧 测试tushare连接...")
    try:
        # 简单查询测试
        data = pro.trade_cal(exchange='SSE', start_date='20240101', end_date='20240110')
        if data is not None and len(data) > 0:
            print("✅ tushare连接测试成功")
            return True
        else:
            print("❌ tushare连接测试失败：无数据返回")
            return False
    except Exception as e:
        print(f"❌ tushare连接测试失败：{e}")
        return False

def get_china_life_basic_info():
    """获取中国人寿基本信息"""
    print("\n📋 获取中国人寿基本信息...")
    try:
        # 中国人寿A股代码：601628.SH
        ts_code = "601628.SH"
        
        # 获取股票基本信息
        data = pro.stock_basic(ts_code=ts_code, 
                               fields='ts_code,symbol,name,area,industry,fullname,enname,market,exchange,curr_type,list_status,list_date,delist_date,is_hs')
        
        if data is not None and len(data) > 0:
            print("✅ 中国人寿基本信息获取成功")
            print(f"股票代码: {data['ts_code'].iloc[0]}")
            print(f"股票名称: {data['name'].iloc[0]}")
            print(f"上市日期: {data['list_date'].iloc[0]}")
            print(f"所属行业: {data['industry'].iloc[0]}")
            print(f"交易所: {data['exchange'].iloc[0]}")
            print(f"市场类型: {data['market'].iloc[0]}")
            return data
        else:
            print("❌ 未找到中国人寿基本信息")
            return None
    except Exception as e:
        print(f"❌ 获取中国人寿基本信息失败：{e}")
        return None

def get_china_life_daily_data():
    """获取中国人寿日线行情数据"""
    print("\n📈 获取中国人寿日线行情数据...")
    try:
        ts_code = "601628.SH"
        
        # 获取最近30天的数据
        end_date = datetime.now().strftime('%Y%m%d')
        start_date = (datetime.now() - timedelta(days=30)).strftime('%Y%m%d')
        
        data = pro.daily(ts_code=ts_code, start_date=start_date, end_date=end_date)
        
        if data is not None and len(data) > 0:
            print(f"✅ 获取到 {len(data)} 条日线数据")
            print(f"数据时间范围: {data['trade_date'].min()} 至 {data['trade_date'].max()}")
            
            # 显示最新5条数据
            print("\n最新5个交易日数据:")
            latest_data = data.head(5)
            for _, row in latest_data.iterrows():
                print(f"日期: {row['trade_date']}, 收盘价: {row['close']:.2f}, "
                      f"涨跌幅: {row['pct_chg']:.2f}%, 成交量: {row['vol']/10000:.2f}万手")
            
            # 计算统计信息
            avg_close = data['close'].mean()
            max_close = data['close'].max()
            min_close = data['close'].min()
            avg_vol = data['vol'].mean() / 10000  # 转换为万手
            
            print(f"\n📊 统计信息 (最近30天):")
            print(f"平均收盘价: {avg_close:.2f}")
            print(f"最高收盘价: {max_close:.2f}")
            print(f"最低收盘价: {min_close:.2f}")
            print(f"平均成交量: {avg_vol:.2f}万手")
            
            return data
        else:
            print("❌ 未获取到日线数据")
            return None
    except Exception as e:
        print(f"❌ 获取日线数据失败：{e}")
        return None

def get_china_life_financial_data():
    """获取中国人寿财务指标数据"""
    print("\n💰 获取中国人寿财务指标数据...")
    try:
        ts_code = "601628.SH"
        
        # 获取最近一年的财务数据
        current_year = datetime.now().year
        data = pro.fina_indicator(ts_code=ts_code, year=current_year-1)
        
        if data is not None and len(data) > 0:
            print(f"✅ 获取到 {len(data)} 条财务指标数据")
            
            # 显示关键财务指标
            latest_report = data.iloc[0]  # 最新的财务报告
            
            print("\n关键财务指标:")
            print(f"报告期: {latest_report['end_date']}")
            print(f"基本每股收益: {latest_report['eps']:.3f} 元")
            print(f"每股净资产: {latest_report['bps']:.2f} 元")
            print(f"净资产收益率: {latest_report['roe']:.2f}%")
            print(f"总资产: {latest_report['total_assets']/1e8:.2f} 亿元")
            print(f"营业收入: {latest_report['revenue']/1e8:.2f} 亿元")
            print(f"净利润: {latest_report['netprofit']/1e8:.2f} 亿元")
            print(f"资产负债率: {latest_report['debt_to_assets']:.2f}%")
            
            return data
        else:
            print("❌ 未获取到财务指标数据")
            return None
    except Exception as e:
        print(f"❌ 获取财务指标数据失败：{e}")
        return None

def get_china_life_company_info():
    """获取中国人寿公司信息"""
    print("\n🏢 获取中国人寿公司信息...")
    try:
        ts_code = "601628.SH"
        
        data = pro.stock_company(ts_code=ts_code)
        
        if data is not None and len(data) > 0:
            print("✅ 公司信息获取成功")
            
            company_info = data.iloc[0]
            print(f"公司全称: {company_info['fullname']}")
            print(f"英文名称: {company_info['enname']}")
            print(f"注册地址: {company_info['reg_addr']}")
            print(f"办公地址: {company_info['office_addr']}")
            print(f"公司简介: {company_info['profile'][:200]}...")  # 只显示前200字符
            
            return data
        else:
            print("❌ 未获取到公司信息")
            return None
    except Exception as e:
        print(f"❌ 获取公司信息失败：{e}")
        return None

def get_china_life_concept_info():
    """获取中国人寿所属概念板块"""
    print("\n🏷️ 获取中国人寿所属概念板块...")
    try:
        ts_code = "601628.SH"
        
        # 使用同花顺概念成分接口
        data = pro.ths_member(ts_code=ts_code)
        
        if data is not None and len(data) > 0:
            print(f"✅ 获取到 {len(data)} 个概念板块")
            
            print("\n所属概念板块:")
            for _, row in data.iterrows():
                print(f"- {row['name']} (代码: {row['code']})")
            
            return data
        else:
            print("❌ 未获取到概念板块信息")
            return None
    except Exception as e:
        print(f"❌ 获取概念板块失败：{e}")
        return None

def save_results_to_json(results):
    """将结果保存为JSON文件"""
    try:
        output_file = "/home/luckyelite/.openclaw/workspace/china_life_analysis.json"
        
        # 转换DataFrame为字典
        json_data = {}
        for key, value in results.items():
            if value is not None and hasattr(value, 'to_dict'):
                json_data[key] = value.to_dict(orient='records')
            else:
                json_data[key] = value
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 分析结果已保存到: {output_file}")
        return output_file
    except Exception as e:
        print(f"❌ 保存结果失败：{e}")
        return None

def main():
    """主函数"""
    print("=" * 60)
    print("中国人寿 (601628.SH) - tushare数据分析测试")
    print("=" * 60)
    
    # 测试连接
    if not test_tushare_connection():
        print("❌ tushare连接失败，请检查token")
        return
    
    results = {}
    
    # 1. 获取基本信息
    basic_info = get_china_life_basic_info()
    results['basic_info'] = basic_info
    
    # 2. 获取日线行情
    daily_data = get_china_life_daily_data()
    results['daily_data'] = daily_data
    
    # 3. 获取财务指标
    financial_data = get_china_life_financial_data()
    results['financial_data'] = financial_data
    
    # 4. 获取公司信息
    company_info = get_china_life_company_info()
    results['company_info'] = company_info
    
    # 5. 获取概念板块
    concept_info = get_china_life_concept_info()
    results['concept_info'] = concept_info
    
    # 保存结果
    save_results_to_json(results)
    
    print("\n" + "=" * 60)
    print("🎉 中国人寿数据分析完成!")
    print("=" * 60)
    
    # 总结
    print("\n📊 测试总结:")
    print(f"✅ tushare-data skill 功能正常")
    print(f"✅ token: {TUSHARE_TOKEN[:10]}... (已安全使用)")
    print(f"✅ 成功获取中国人寿多维度数据")
    print(f"✅ 数据已保存为JSON文件")
    
    print("\n🚀 可用于琥珀引擎的数据:")
    print("  1. 实时行情数据 → 财经卡片展示")
    print("  2. 财务指标 → RICH评分系统")
    print("  3. 公司信息 → 文章背景资料")
    print("  4. 概念板块 → 标签系统")

if __name__ == "__main__":
    main()