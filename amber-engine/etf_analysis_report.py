#!/usr/bin/env python3
"""
ETF分析报告生成脚本
查询Tushare数据库，整理ETF基金数据，生成详细分析报告
"""

import tushare as ts
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import os
import sys
from typing import Dict, List, Tuple, Any

# 设置Tushare Token
TOKEN = "9e32ef28eac05c5fbb11e6f02a50da903def70f94b3018e93340568b"
ts.set_token(TOKEN)
pro = ts.pro_api()

# 日期设置
BASE_DATE = "20260227"  # 基准日期
END_DATE = "20260320"   # 结束日期
REPORT_DATE = "20260321"  # 报告日期

def get_all_etf_funds():
    """获取所有ETF基金基本信息"""
    print("📊 获取所有ETF基金基本信息...")
    
    try:
        # 获取基金基本信息
        df_funds = pro.fund_basic(market='E')
        
        # 筛选ETF基金
        etf_funds = df_funds[df_funds['fund_type'].str.contains('ETF', na=False)].copy()
        
        print(f"✅ 找到 {len(etf_funds)} 只ETF基金")
        return etf_funds
    except Exception as e:
        print(f"❌ 获取ETF基金信息失败: {e}")
        return None

def classify_etf_industry(name: str) -> Tuple[str, str]:
    """根据基金名称分类ETF行业"""
    name = name.upper()
    
    # 宽基指数
    if any(keyword in name for keyword in ['沪深300', '上证50', '中证500', '创业板', '科创50', '中证1000']):
        return "宽基指数", "大盘宽基"
    elif any(keyword in name for keyword in ['中证800', '中证100', '国证2000']):
        return "宽基指数", "中盘宽基"
    
    # 行业ETF
    if any(keyword in name for keyword in ['半导体', '芯片', '集成电路']):
        return "科技", "半导体芯片"
    elif any(keyword in name for keyword in ['新能源', '光伏', '风电', '储能', '锂电池']):
        return "新能源", "新能源产业链"
    elif any(keyword in name for keyword in ['医药', '医疗', '生物', '健康']):
        return "医药", "医疗健康"
    elif any(keyword in name for keyword in ['消费', '食品', '饮料', '白酒', '家电']):
        return "消费", "大消费"
    elif any(keyword in name for keyword in ['金融', '银行', '证券', '保险']):
        return "金融", "大金融"
    elif any(keyword in name for keyword in ['军工', '国防']):
        return "军工", "国防军工"
    elif any(keyword in name for keyword in ['通信', '5G', '物联网']):
        return "通信", "5G通信"
    elif any(keyword in name for keyword in ['计算机', '软件', '云计算', '人工智能']):
        return "科技", "计算机软件"
    elif any(keyword in name for keyword in ['有色金属', '煤炭', '钢铁', '化工']):
        return "周期", "资源周期"
    elif any(keyword in name for keyword in ['房地产', '基建', '建材']):
        return "周期", "房地产基建"
    elif any(keyword in name for keyword in ['环保', '生态']):
        return "环保", "环境保护"
    elif any(keyword in name for keyword in ['农业', '养殖']):
        return "农业", "现代农业"
    elif any(keyword in name for keyword in ['传媒', '游戏', '影视']):
        return "传媒", "文化传媒"
    elif any(keyword in name for keyword in ['汽车', '智能驾驶']):
        return "汽车", "汽车产业"
    elif any(keyword in name for keyword in ['黄金', '白银', '商品']):
        return "商品", "贵金属商品"
    elif any(keyword in name for keyword in ['红利', '股息']):
        return "策略", "红利策略"
    elif any(keyword in name for keyword in ['质量', '价值', '成长']):
        return "策略", "Smart Beta"
    elif any(keyword in name for keyword in ['港股', '恒生', '纳斯达克', '标普', '德国', '日本']):
        return "跨境", "境外市场"
    else:
        return "其他", "未分类"

def calculate_etf_performance(etf_funds):
    """计算ETF基金在指定期间的涨跌幅"""
    print(f"📈 计算ETF基金涨跌幅 ({BASE_DATE} 至 {END_DATE})...")
    
    results = []
    
    for idx, fund in etf_funds.iterrows():
        try:
            ts_code = fund['ts_code']
            name = fund['name']
            
            # 获取基金日线数据
            df_daily = pro.fund_daily(ts_code=ts_code, start_date=BASE_DATE, end_date=END_DATE)
            
            if len(df_daily) < 2:
                continue
            
            # 按日期排序
            df_daily = df_daily.sort_values('trade_date')
            
            # 获取基准日和结束日的净值
            base_data = df_daily[df_daily['trade_date'] == BASE_DATE]
            end_data = df_daily[df_daily['trade_date'] == END_DATE]
            
            if len(base_data) == 0 or len(end_data) == 0:
                # 如果基准日没有数据，使用最早的数据
                base_data = df_daily.iloc[0:1]
                end_data = df_daily.iloc[-1:]
            
            base_nav = float(base_data.iloc[0]['adj_nav'])
            end_nav = float(end_data.iloc[0]['adj_nav'])
            
            # 计算涨跌幅
            pct_change = ((end_nav - base_nav) / base_nav) * 100
            
            # 分类行业
            industry_main, industry_detail = classify_etf_industry(name)
            
            results.append({
                'ts_code': ts_code,
                'name': name,
                'industry_main': industry_main,
                'industry_detail': industry_detail,
                'base_nav': round(base_nav, 4),
                'end_nav': round(end_nav, 4),
                'pct_change': round(pct_change, 2),
                'data_points': len(df_daily)
            })
            
            if len(results) % 20 == 0:
                print(f"  已处理 {len(results)} 只ETF...")
                
        except Exception as e:
            print(f"  处理 {fund.get('name', '未知')} 失败: {e}")
            continue
    
    print(f"✅ 成功计算 {len(results)} 只ETF的涨跌幅")
    return results

def analyze_fifteen_five_plan_correlation(etf_results):
    """分析与十五五规划高度相关的产业赛道"""
    print("🎯 分析与十五五规划相关性...")
    
    # 十五五规划重点产业（根据公开信息预测）
    fifteen_five_key_industries = {
        "科技": ["半导体芯片", "人工智能", "量子计算", "集成电路", "5G通信", "计算机软件"],
        "新能源": ["新能源产业链", "光伏风电", "储能技术", "氢能源", "智能电网"],
        "医药": ["生物医药", "医疗器械", "创新药", "中医药现代化", "基因技术"],
        "高端制造": ["工业母机", "机器人", "航空航天", "海洋工程", "精密仪器"],
        "数字经济": ["大数据", "云计算", "区块链", "工业互联网", "数字孪生"],
        "绿色环保": ["环境保护", "碳交易", "循环经济", "生态修复", "清洁能源"],
        "国家安全": ["国防军工", "网络安全", "粮食安全", "能源安全", "信息安全"],
        "民生保障": ["医疗健康", "养老服务", "职业教育", "保障性住房", "城乡融合"]
    }
    
    # 分析相关性
    high_correlation = []
    medium_correlation = []
    
    for etf in etf_results:
        industry_detail = etf['industry_detail']
        correlation_score = 0
        
        # 检查是否在十五五规划重点产业中
        for main_industry, sub_industries in fifteen_five_key_industries.items():
            if industry_detail in sub_industries:
                correlation_score = 3  # 高度相关
                break
            elif etf['industry_main'] == main_industry:
                correlation_score = 2  # 中度相关
        
        # 根据行业名称关键词进一步判断
        name = etf['name']
        if any(keyword in name for keyword in ['创新', '智能', '数字', '绿色', '安全', '高端']):
            correlation_score = max(correlation_score, 1)  # 轻度相关
        
        etf['fifteen_five_correlation'] = correlation_score
        
        if correlation_score == 3:
            high_correlation.append(etf)
        elif correlation_score == 2:
            medium_correlation.append(etf)
    
    return etf_results, high_correlation, medium_correlation

def generate_etf_report(etf_results, high_correlation, medium_correlation):
    """生成ETF分析报告"""
    print("📝 生成ETF分析报告...")
    
    # 按涨跌幅排序
    sorted_by_performance = sorted(etf_results, key=lambda x: x['pct_change'], reverse=True)
    
    # 按行业统计
    industry_stats = {}
    for etf in etf_results:
        industry = etf['industry_main']
        if industry not in industry_stats:
            industry_stats[industry] = {
                'count': 0,
                'avg_change': 0,
                'total_change': 0,
                'best_performer': None,
                'worst_performer': None
            }
        
        stats = industry_stats[industry]
        stats['count'] += 1
        stats['total_change'] += etf['pct_change']
        
        if stats['best_performer'] is None or etf['pct_change'] > stats['best_performer']['pct_change']:
            stats['best_performer'] = etf
        if stats['worst_performer'] is None or etf['pct_change'] < stats['worst_performer']['pct_change']:
            stats['worst_performer'] = etf
    
    # 计算行业平均涨跌幅
    for industry, stats in industry_stats.items():
        stats['avg_change'] = stats['total_change'] / stats['count']
    
    # 生成报告
    report = {
        'report_date': REPORT_DATE,
        'analysis_period': f"{BASE_DATE} 至 {END_DATE}",
        'total_etfs_analyzed': len(etf_results),
        'performance_summary': {
            'top_gainers': sorted_by_performance[:10],
            'top_losers': sorted_by_performance[-10:],
            'overall_avg_change': np.mean([etf['pct_change'] for etf in etf_results])
        },
        'industry_analysis': industry_stats,
        'fifteen_five_correlation': {
            'high_correlation_count': len(high_correlation),
            'medium_correlation_count': len(medium_correlation),
            'high_correlation_etfs': high_correlation[:20],  # 最多显示20只
            'medium_correlation_etfs': medium_correlation[:20]
        },
        'investment_recommendations': generate_investment_recommendations(sorted_by_performance, high_correlation, industry_stats)
    }
    
    return report

def generate_investment_recommendations(sorted_etfs, high_correlation_etfs, industry_stats):
    """生成投资建议"""
    print("💡 生成投资建议...")
    
    recommendations = {
        'highly_recommended': [],
        'watch_list': [],
        'caution_list': [],
        'sector_outlook': []
    }
    
    # 1. 高度推荐：表现好且与十五五规划高度相关
    for etf in sorted_etfs[:20]:  # 前20名表现好的
        if etf['fifteen_five_correlation'] >= 2 and etf['pct_change'] > 0:
            recommendations['highly_recommended'].append({
                'name': etf['name'],
                'ts_code': etf['ts_code'],
                'pct_change': etf['pct_change'],
                'industry': etf['industry_detail'],
                'reason': f"表现优异(+{etf['pct_change']}%)，且与十五五规划{['中度','高度'][etf['fifteen_five_correlation']-2]}相关"
            })
    
    # 2. 观察列表：与十五五规划相关但表现一般
    for etf in high_correlation_etfs:
        if etf not in [rec['ts_code'] for rec in recommendations['highly_recommended']]:
            recommendations['watch_list'].append({
                'name': etf['name'],
                'ts_code': etf['ts_code'],
                'pct_change': etf['pct_change'],
                'industry': etf['industry_detail'],
                'reason': "与十五五规划高度相关，值得关注"
            })
    
    # 3. 谨慎列表：表现差且与规划相关性低
    for etf in sorted_etfs[-10:]:  # 后10名表现差的
        if etf['fifteen_five_correlation'] <= 1:
            recommendations['caution_list'].append({
                'name': etf['name'],
                'ts_code': etf['ts_code'],
                'pct_change': etf['pct_change'],
                'industry': etf['industry_detail'],
                'reason': f"表现较差({etf['pct_change']}%)，且与十五五规划相关性低"
            })
    
    # 4. 行业展望
    sorted_industries = sorted(industry_stats.items(), key=lambda x: x[1]['avg_change'], reverse=True)
    for industry, stats in sorted_industries[:5]:  # 前5个表现最好的行业
        recommendations['sector_outlook'].append({
            'industry': industry,
            'avg_change': round(stats['avg_change'], 2),
            'count': stats['count'],
            'best_performer': stats['best_performer']['name'],
            'outlook': generate_industry_outlook(industry)
        })
    
    return recommendations

def generate_industry_outlook(industry):
    """生成行业展望"""
    outlooks = {
        "科技": "十五五规划重点支持领域，受益于自主可控和数字化转型，长期成长空间大",
        "新能源": "碳中和目标下的核心赛道，政策支持力度大，技术迭代快，市场空间广阔",
        "医药": "人口老龄化+消费升级双轮驱动，创新药和医疗器械国产替代空间大",
        "高端制造": "制造强国战略核心，受益于产业升级和供应链安全需求",
        "数字经济": "数字中国建设核心，数据要素价值释放，新基建投资持续",
        "军工": "国家安全战略升级，装备现代化需求迫切，订单确定性高",
        "消费": "内需扩大战略受益，消费升级趋势不变，品牌集中度提升",
        "金融": "估值处于历史低位，受益于经济复苏和利率环境改善",
        "周期": "经济周期波动影响大，需关注供给侧改革和需求变化",
        "跨境": "全球资产配置工具，分散风险，捕捉境外市场机会"
    }
    
    return outlooks.get(industry, "需结合具体细分领域和宏观经济环境分析")

def save_report(report, format='both'):
    """保存报告"""
    print("💾 保存报告...")
    
    # 创建报告目录
    report_dir = os.path.join(os.path.dirname(__file__), "reports", "etf_analysis")
    os.makedirs(report_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # 保存JSON格式
    if format in ['json', 'both']:
        json_path = os.path.join(report_dir, f"etf_analysis_{timestamp}.json")
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        print(f"  ✅ JSON报告已保存: {json_path}")
    
    # 保存Markdown格式
    if format in ['markdown', 'both']:
        md_path = os.path.join(report_dir, f"etf_analysis_{timestamp}.md")
        md_content = generate_markdown_report(report)
        with open(md_path, 'w', encoding='utf-8') as f:
            f.write(md_content)
        print(f"  ✅ Markdown报告已保存: {md_path}")
    
    return json_path, md_path

def generate_markdown_report(report):
    """生成Markdown格式报告"""
    md = f"""# ETF基金分析报告

## 报告概览
- **报告日期**: {report['report_date']}
- **分析期间**: {report['analysis_period']}
- **分析ETF数量**: {report['total_etfs_analyzed']}只
- **整体平均涨跌幅**: {report['performance_summary']['overall_avg_change']:.2f}%

## 一、表现最佳ETF（前10名）

|