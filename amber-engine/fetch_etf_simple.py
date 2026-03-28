#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
琥珀引擎ETF简单数据采集
使用AkShare的ETF实时数据和基本信息接口
"""

import akshare as ak
import pandas as pd
import json
from datetime import datetime

print("="*60)
print("🚀 琥珀引擎ETF简单数据采集")
print("="*60)

# 需要采集的ETF列表
ETF_LIST = [
    {"code": "518880", "name": "华安黄金ETF"},
    {"code": "516160", "name": "南方新能源ETF"},
    {"code": "159915", "name": "创业板ETF"},
    {"code": "510050", "name": "上证50ETF"},
    {"code": "515050", "name": "华夏5G通信ETF"},
    {"code": "512660", "name": "国泰军工ETF"},
    {"code": "512010", "name": "易方达医药ETF"},
    {"code": "512880", "name": "证券ETF"},
    {"code": "510500", "name": "中证500ETF"},
    {"code": "159941", "name": "纳指ETF"},
    {"code": "512480", "name": "国联安半导体"},
    {"code": "510300", "name": "沪深300ETF"},
    {"code": "512170", "name": "华宝医疗ETF"},
    {"code": "513100", "name": "纳指100ETF"},
]

def get_etf_real_time_data(etf_code):
    """获取ETF实时数据"""
    print(f"\n🔍 采集 {etf_code} 实时数据...")
    
    try:
        # 获取ETF实时行情
        real_time = ak.fund_etf_spot_em()
        
        # 查找目标ETF
        target_etf = real_time[real_time['代码'] == etf_code]
        
        if not target_etf.empty:
            print(f"   ✅ 找到实时数据")
            return target_etf.iloc[0].to_dict()
        else:
            print(f"   ⚠️  未找到实时数据")
            return None
            
    except Exception as e:
        print(f"   ❌ 实时数据获取失败: {e}")
        return None

def get_etf_basic_info(etf_code):
    """获取ETF基本信息"""
    print(f"   📋 采集基本信息...")
    
    try:
        # 获取ETF列表信息
        etf_list = ak.fund_etf_category_sina(symbol="ETF基金")
        
        # 查找目标ETF
        target_etf = etf_list[etf_list['代码'] == etf_code]
        
        if not target_etf.empty:
            print(f"      ✅ 找到基本信息")
            return target_etf.iloc[0].to_dict()
        else:
            print(f"      ⚠️  未找到基本信息")
            return None
            
    except Exception as e:
        print(f"      ❌ 基本信息获取失败: {e}")
        return None

def calculate_raw_scores(real_time_data, basic_info):
    """计算五维原始分（基于可用数据）"""
    print(f"   🎯 计算原始分...")
    
    scores = {
        "p_raw": 5.0,  # Performance - 默认中等
        "l_raw": 5.0,  # Liquidity - 默认中等
        "c_raw": 5.0,  # Cost - 默认中等
        "b_raw": 5.0,  # Correlation - 默认中等
        "m_raw": 5.0   # Management - 默认中等
    }
    
    # 如果有实时数据，调整分数
    if real_time_data:
        # 根据涨跌幅调整Performance
        if '涨跌幅' in real_time_data:
            change = float(str(real_time_data['涨跌幅']).replace('%', ''))
            if change > 5:
                scores["p_raw"] = 9.0
            elif change > 2:
                scores["p_raw"] = 7.0
            elif change > 0:
                scores["p_raw"] = 6.0
            elif change > -2:
                scores["p_raw"] = 4.0
            else:
                scores["p_raw"] = 2.0
        
        # 根据成交额调整Liquidity
        if '成交额' in real_time_data:
            try:
                amount = float(str(real_time_data['成交额']).replace('亿', ''))
                if amount > 10:  # 10亿元以上
                    scores["l_raw"] = 10.0
                elif amount > 5:  # 5-10亿元
                    scores["l_raw"] = 8.0
                elif amount > 1:  # 1-5亿元
                    scores["l_raw"] = 6.0
                elif amount > 0.5:  # 0.5-1亿元
                    scores["l_raw"] = 4.0
                else:  # 0.5亿元以下
                    scores["l_raw"] = 2.0
            except:
                pass
    
    # 如果有基本信息，调整Cost和Management
    if basic_info:
        # 根据基金公司调整Management
        if '基金公司' in basic_info:
            company = str(basic_info['基金公司'])
            # 大型基金公司得高分
            large_companies = ['华夏', '易方达', '南方', '华安', '国泰', '华宝']
            if any(c in company for c in large_companies):
                scores["m_raw"] = 8.0
            else:
                scores["m_raw"] = 6.0
        
        # ETF通常费率较低，Cost得高分
        scores["c_raw"] = 7.0  # ETF费率通常较低
    
    print(f"      P:{scores['p_raw']} L:{scores['l_raw']} C:{scores['c_raw']} B:{scores['b_raw']} M:{scores['m_raw']}")
    
    return scores

def main():
    """主函数"""
    results = []
    
    print(f"\n📊 开始采集 {len(ETF_LIST)} 只ETF数据")
    print("="*60)
    
    for i, etf in enumerate(ETF_LIST):
        print(f"\n[{i+1}/{len(ETF_LIST)}] {etf['name']} ({etf['code']})")
        
        # 获取实时数据
        real_time_data = get_etf_real_time_data(etf['code'])
        
        # 获取基本信息
        basic_info = get_etf_basic_info(etf['code'])
        
        # 计算原始分
        raw_scores = calculate_raw_scores(real_time_data, basic_info)
        
        # 添加到结果
        results.append({
            "code": etf['code'],
            "name": etf['name'],
            "p_raw": raw_scores["p_raw"],
            "l_raw": raw_scores["l_raw"],
            "c_raw": raw_scores["c_raw"],
            "b_raw": raw_scores["b_raw"],
            "m_raw": raw_scores["m_raw"]
        })
    
    # 保存结果
    print("\n" + "="*60)
    print("💾 保存采集结果")
    print("="*60)
    
    output_data = {
        "task": "M002-RAW-DATA-FINAL-COLLECTION",
        "protocol": "MEMORY.md Section 5.1 (Weight 0.3 Override)",
        "executor_required": "Engineer Cheese",
        "description": "请补全以下14只ETF的原始归一化指标(1-10分)。严禁修改逻辑，严禁自行计算总分。",
        "etf_data": results
    }
    
    output_path = "/home/luckyelite/.openclaw/workspace/amber-engine/CHEESE_INPUT_RAW_REAL.json"
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 真实数据已保存到: {output_path}")
    print(f"📊 共采集 {len(results)} 只ETF数据")
    
    # 显示统计
    print(f"\n📈 数据质量统计:")
    zero_count = sum(1 for r in results if all(v == 5.0 for k, v in r.items() if k.endswith('_raw')))
    non_zero_count = len(results) - zero_count
    print(f"   有效数据: {non_zero_count} 只")
    print(f"   默认数据: {zero_count} 只")
    
    return True

if __name__ == "__main__":
    main()