#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
琥珀引擎ETF筛选分析器 - V3.3.2 (修正版)
"""

import json
import pandas as pd
import numpy as np
from datetime import datetime

class ETFScreeningAnalyzer:
    """ETF筛选分析器"""
    
    def __init__(self, rules_path="etf_screening_rules.json"):
        """初始化分析器"""
        print("="*60)
        print("🚀 启动琥珀引擎ETF筛选分析器 - V3.3.2")
        print("="*60)
        
        # 加载规则
        with open(rules_path, 'r', encoding='utf-8') as f:
            self.rules = json.load(f)
        
        print(f"✅ 加载筛选规则: {self.rules['name']} v{self.rules['version']}")
    
    def parse_threshold(self, threshold_str):
        """解析阈值字符串"""
        try:
            # 处理中文单位
            if '个月' in threshold_str:
                return float(threshold_str.replace('个月', ''))
            elif '亿元' in threshold_str:
                return float(threshold_str.replace('亿元', '')) * 100000000
            elif '%' in threshold_str:
                return float(threshold_str.replace('%', '')) / 100
            else:
                return float(threshold_str)
        except:
            return 0
    
    def evaluate_etf(self, etf_data):
        """评估单只ETF"""
        print(f"\n🔍 评估ETF: {etf_data.get('name', '未知')} ({etf_data.get('code', '未知')})")
        
        scores = {}
        firewall_results = {}
        
        # 1. 检查防火墙
        print("   🔥 防火墙检查...")
        for firewall_name, firewall in self.rules['firewalls'].items():
            if not firewall['enabled']:
                continue
            
            # 解析防火墙规则
            rule_parts = firewall['rule'].split(' ')
            metric = rule_parts[0]
            operator = rule_parts[1]
            threshold_str = ' '.join(rule_parts[2:])
            threshold = self.parse_threshold(threshold_str)
            
            etf_value = etf_data.get(metric, None)
            if etf_value is None:
                print(f"     ⚠️  {firewall_name}: 缺少数据 {metric}")
                firewall_results[firewall_name] = {'passed': False, 'reason': f'缺少数据 {metric}'}
                continue
            
            # 评估防火墙规则
            if operator == '<':
                passed = etf_value < threshold
            elif operator == '>':
                passed = etf_value > threshold
            elif operator == '<=':
                passed = etf_value <= threshold
            elif operator == '>=':
                passed = etf_value >= threshold
            else:
                passed = True
            
            firewall_results[firewall_name] = {
                'passed': passed,
                'value': etf_value,
                'threshold': threshold,
                'action': firewall['action']
            }
            
            if not passed:
                print(f"     ❌ {firewall_name}: 未通过 ({etf_value} {operator} {threshold}) -> {firewall['action']}")
            else:
                print(f"     ✅ {firewall_name}: 通过")
        
        # 2. 维度评分
        print("   📊 维度评分...")
        for dim_name, dimension in self.rules['dimensions'].items():
            dim_score = 0
            max_dim_score = 0
            
            for rule in dimension['rules']:
                if not rule['enabled']:
                    continue
                
                metric = rule['metric']
                etf_value = etf_data.get(metric, None)
                
                if etf_value is None:
                    print(f"     ⚠️  {rule['name']}: 缺少数据 {metric}")
                    continue
                
                # 根据阈值评估
                threshold_str = rule['threshold']
                threshold = self.parse_threshold(threshold_str)
                weight = rule['weight']
                
                # 简化的评分逻辑
                if '≥' in threshold_str:
                    if etf_value >= threshold:
                        rule_score = 100 * weight
                    else:
                        rule_score = max(0, (etf_value / threshold) * 100 * weight)
                elif '≤' in threshold_str:
                    if etf_value <= threshold:
                        rule_score = 100 * weight
                    else:
                        rule_score = max(0, (threshold / etf_value) * 100 * weight)
                else:
                    rule_score = 50 * weight  # 默认分数
                
                dim_score += rule_score
                max_dim_score += 100 * weight
            
            # 计算维度得分（0-100）
            if max_dim_score > 0:
                final_dim_score = (dim_score / max_dim_score) * 100
            else:
                final_dim_score = 0
            
            scores[dim_name] = round(final_dim_score, 2)
            print(f"     📈 {dimension['name']}: {scores[dim_name]}/100")
        
        # 3. 计算总分
        total_score = 0
        for dim_name, dim_score in scores.items():
            weight = self.rules['scoring_system']['dimension_weights'].get(dim_name, 0.25)
            total_score += dim_score * weight
        
        total_score = round(total_score, 2)
        
        # 4. 确定评级
        rating = "poor"
        rating_info = {}
        for rating_name, rating_range in self.rules['scoring_system']['rating_scale'].items():
            min_score = rating_range.get('min', 0)
            max_score = rating_range.get('max', 100)
            
            if 'min' in rating_range and 'max' in rating_range:
                if min_score <= total_score <= max_score:
                    rating = rating_name
                    rating_info = rating_range
                    break
            elif 'min' in rating_range:
                if total_score >= min_score:
                    rating = rating_name
                    rating_info = rating_range
                    break
            elif 'max' in rating_range:
                if total_score <= max_score:
                    rating = rating_name
                    rating_info = rating_range
                    break
        
        print(f"   🏆 总分: {total_score}/100 - 评级: {rating} ({rating_info.get('action', '未知')})")
        
        return {
            'etf_info': {
                'name': etf_data.get('name', '未知'),
                'code': etf_data.get('code', '未知'),
                'theme': etf_data.get('theme', '未知')
            },
            'firewall_results': firewall_results,
            'dimension_scores': scores,
            'total_score': total_score,
            'rating': rating,
            'rating_info': rating_info,
            'recommendation': rating_info.get('action', '未知'),
            'evaluation_time': datetime.now().isoformat()
        }
    
    def analyze_multiple_etfs(self, etf_list):
        """分析多只ETF"""
        print(f"\n📊 开始批量分析 {len(etf_list)} 只ETF...")
        
        results = []
        for etf_data in etf_list:
            result = self.evaluate_etf(etf_data)
            results.append(result)
        
        # 按总分排序
        results.sort(key=lambda x: x['total_score'], reverse=True)
        
        return results
    
    def generate_report(self, analysis_results):
        """生成分析报告"""
        print("\n" + "="*60)
        print("📋 ETF筛选分析报告")
        print("="*60)
        
        # 统计信息
        rating_counts = {}
        for result in analysis_results:
            rating = result['rating']
            rating_counts[rating] = rating_counts.get(rating, 0) + 1
        
        print(f"\n📈 分析统计:")
        print(f"  分析ETF数量: {len(analysis_results)}")
        for rating, count in rating_counts.items():
            color = self.rules['scoring_system']['rating_scale'][rating]['color']
            action = self.rules['scoring_system']['rating_scale'][rating]['action']
            print(f"  {rating}: {count}只 ({action})")
        
        # 显示Top 5
        print(f"\n🏆 Top 5 ETF:")
        for i, result in enumerate(analysis_results[:5]):
            etf = result['etf_info']
            print(f"  {i+1}. {etf['name']} ({etf['code']})")
            print(f"     主题: {etf['theme']} | 总分: {result['total_score']} | 评级: {result['rating']}")
            print(f"     推荐: {result['recommendation']}")
        
        # 维度平均分
        print(f"\n📊 维度平均分:")
        dimension_totals = {}
        for result in analysis_results:
            for dim, score in result['dimension_scores'].items():
                dimension_totals[dim] = dimension_totals.get(dim, 0) + score
        
        for dim, total in dimension_totals.items():
            avg_score = total / len(analysis_results)
            dim_name = self.rules['dimensions'][dim]['name']
            print(f"  {dim_name}: {avg_score:.2f}/100")
        
        return analysis_results

# 修正示例数据（单位统一）
def create_sample_etf_data():
    """创建示例ETF数据"""
    sample_etfs = [
        {
            "code": "512760",
            "name": "国泰CES半导体芯片ETF",
            "theme": "科技自立",
            "top10_concentration": 68.5,  # %
            "rebalance_frequency": 6,  # 月
            "industry_purity": 95.2,  # %
            "market_cap_coverage": 85.3,  # %
            "tracking_error": 0.32,  # %
            "information_ratio": 0.78,
            "annual_win_rate": 82.5,  # %
            "fund_size": 12560000000,  # 元 (125.6亿)
            "avg_daily_volume": 320000000,  # 元 (3.2亿)
            "bid_ask_spread": 0.08,  # %
            "total_expense_ratio": 0.0055,  # 0.55%
            "management_fee": 0.005,  # 0.5%
            "correlation_with_index": 0.98
        },
        {
            "code": "515030",
            "name": "华夏中证新能源汽车ETF",
            "theme": "绿色转型",
            "top10_concentration": 62.3,
            "rebalance_frequency": 6,
            "industry_purity": 92.8,
            "market_cap_coverage": 82.1,
            "tracking_error": 0.41,
            "information_ratio": 0.65,
            "annual_win_rate": 76.3,
            "fund_size": 8970000000,
            "avg_daily_volume": 280000000,
            "bid_ask_spread": 0.09,
            "total_expense_ratio": 0.0058,
            "management_fee": 0.005,
            "correlation_with_index": 0.97
        },
        {
            "code": "512660",
            "name": "国泰中证军工ETF",
            "theme": "安全韧性",
            "top10_concentration": 58.9,
            "rebalance_frequency": 6,
            "industry_purity": 94.5,
            "market_cap_coverage": 79.8,
            "tracking_error": 0.38,
            "information_ratio": 0.52,
            "annual_win_rate": 71.2,
            "fund_size": 4530000000,
            "avg_daily_volume": 120000000,
            "bid_ask_spread": 0.11,
            "total_expense_ratio": 0.0052,
            "management_fee": 0.0045,
            "correlation_with_index": 0.96
        },
        {
            "code": "512480",
            "name": "国联安中证全指半导体ETF",
            "theme": "科技自立",
            "top10_concentration": 65.7,
            "rebalance_frequency": 6,
            "industry_purity": 96.1,
            "market_cap_coverage": 83.9,
            "tracking_error": 0.35,
            "information_ratio": 0.71,
            "annual_win_rate": 79.8,
            "fund_size": 3280000000,
            "avg_daily_volume": 80000000,
            "bid_ask_spread": 0.12,
            "total_expense_ratio": 0.0062,
            "management_fee": 0.0055,
            "correlation_with_index": 0.97
        },
        {
            "code": "159995",
            "name": "华夏国证半导体芯片ETF",
            "theme": "科技自立",
            "top10_concentration": 70.2,
            "rebalance_frequency": 6,
            "industry_purity": 97.3,
            "market_cap_coverage": 87.5,
            "tracking_error": 0.29,
            "information_ratio": 0.82,
            "annual_win_rate": 85.3,
            "fund_size": 15690000000,
            "avg_daily_volume": 450000000,
            "bid_ask_spread": 0.07,
            "total_expense_ratio": 0.0048,
            "management_fee": 0.004,
            "correlation_with_index": 0.99
        }
    ]
    
    return sample_etfs

def main():
    """主函数"""
    # 创建分析器
    analyzer = ETFScreeningAnalyzer()
    
    # 创建示例数据
    etf_list = create_sample_etf_data()
    
    # 分析ETF
    results = analyzer.analyze_multiple_etfs(etf_list)
    
    # 生成报告
    analyzer.generate_report(results)
    
    # 保存结果
    output_data = {
        "analysis_time": datetime.now().isoformat(),
        "rules_version": analyzer.rules["version"],
        "results": results
    }
    
    with open("etf_screening_results_v3_3_2.json", "w", encoding="utf-8") as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ 分析结果已保存到: etf_screening_results_v3_3_2.json")
    print("\n" + "="*60)
    print("🎉 ETF筛选标准化体系建立完成!")
    print("="*60)

if __name__ == "__main__":
    main()