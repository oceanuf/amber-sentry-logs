#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
十五五规划主题ETF专项筛选分析器 - V3.3.0
执行环境：Amber-Data-Engine v3.3.0
核心算法：主题关联度评分 (Keyword Semantic Mapping)
"""

import tushare as ts
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import os
import sys
import time

# Tushare Pro配置
TOKEN = '9e32ef28ea6c2b1d3c8b9e9e32ef28ea6c2b1d3c8b9e9e32ef28ea6c2b1d3c8b9e9e32ef28ea6c2b1d3c8b9e9'
ts.set_token(TOKEN)
pro = ts.pro_api()

# 关键词匹配引擎
KEYWORD_MAPPING = {
    '科技自立': ['芯片', '半导体', '集成电路', '人工智能', 'AI', '信创', '量子', '航空航天', '科技', '创新', '5G', '通信', '软件', '硬件'],
    '绿色转型': ['光伏', '风电', '新能源', '新能源车', '储能', '碳中和', '碳达峰', '电力', 'ESG', '环保', '清洁能源', '太阳能', '电池', '锂电'],
    '安全韧性': ['军工', '国防', '粮食安全', '种业', '农业', '能源', '稀土', '煤炭', '关键矿产', '资源', '安全', '应急', '网络安全']
}

# 主题颜色映射
THEME_COLORS = {
    '科技自立': '#1a237e',  # 深蓝色
    '绿色转型': '#4caf50',  # 绿色
    '安全韧性': '#ff9800'   # 琥珀色
}

def get_all_etfs():
    """获取所有上市ETF列表"""
    print("📊 获取所有上市ETF列表...")
    
    # 获取基金基本信息
    df_fund = pro.fund_basic(market='E')
    
    # 筛选ETF
    etfs = df_fund[df_fund['fund_type'].str.contains('ETF', na=False)].copy()
    
    # 过滤掉货币ETF等非股票型
    etfs = etfs[~etfs['name'].str.contains('货币|现金|债券', na=False)]
    
    print(f"✅ 获取到 {len(etfs)} 只ETF")
    return etfs

def calculate_theme_score(name, industry=None):
    """计算主题关联度评分"""
    name = str(name).lower()
    
    scores = {}
    for theme, keywords in KEYWORD_MAPPING.items():
        score = 0
        matched_keywords = []
        
        for keyword in keywords:
            keyword_lower = keyword.lower()
            if keyword_lower in name:
                score += 3  # 名称直接包含核心关键词
                matched_keywords.append(keyword)
        
        # 根据匹配关键词数量调整分数
        if len(matched_keywords) >= 2:
            score += 2
        elif len(matched_keywords) == 1:
            score += 1
        
        # 星级划分
        if score >= 4:
            star_rating = '★★★'
        elif score >= 2:
            star_rating = '★★☆'
        elif score >= 1:
            star_rating = '★☆☆'
        else:
            star_rating = '☆☆☆'
        
        scores[theme] = {
            'score': score,
            'stars': star_rating,
            'keywords': matched_keywords
        }
    
    return scores

def calculate_performance(ts_code, start_date, end_date):
    """计算ETF在指定区间的表现"""
    print(f"📈 计算 {ts_code} 表现...")
    
    try:
        # 获取日线数据
        df = pro.fund_daily(ts_code=ts_code, start_date=start_date, end_date=end_date)
        
        if df.empty or len(df) < 2:
            return None, None, None, None
        
        # 按日期排序
        df = df.sort_values('trade_date')
        
        # 获取起始和结束价格
        start_val = df.iloc[0]['close']  # 2月27日
        end_val = df.iloc[-1]['close']   # 3月19日
        
        # 计算涨跌幅
        pct_change = (end_val - start_val) / start_val * 100
        
        # 获取最新净值
        latest_nav = end_val
        
        return start_val, end_val, pct_change, latest_nav
        
    except Exception as e:
        print(f"⚠️ 计算 {ts_code} 表现时出错: {e}")
        return None, None, None, None

def calculate_hs300_performance(start_date, end_date):
    """计算沪深300在指定区间的表现"""
    print("📊 计算沪深300基准表现...")
    
    try:
        # 获取沪深300日线数据
        df = pro.index_daily(ts_code='000300.SH', start_date=start_date, end_date=end_date)
        
        if df.empty or len(df) < 2:
            return None, None
        
        # 按日期排序
        df = df.sort_values('trade_date')
        
        # 获取起始和结束价格
        start_val = df.iloc[0]['close']  # 2月27日
        end_val = df.iloc[-1]['close']   # 3月19日
        
        # 计算涨跌幅
        pct_change = (end_val - start_val) / start_val * 100
        
        return start_val, end_val, pct_change
        
    except Exception as e:
        print(f"⚠️ 计算沪深300表现时出错: {e}")
        return None, None, None

def analyze_etfs():
    """主分析函数"""
    print("🚀 开始十五五规划主题ETF专项分析...")
    
    # 时间参数
    start_date = '20260227'
    end_date = '20260319'
    
    # 获取所有ETF
    etfs = get_all_etfs()
    
    # 计算沪深300基准表现
    hs300_start, hs300_end, hs300_pct = calculate_hs300_performance(start_date, end_date)
    
    if hs300_pct is None:
        print("❌ 无法获取沪深300基准数据，退出分析")
        return None
    
    print(f"📊 沪深300基准: {hs300_start:.2f} → {hs300_end:.2f} ({hs300_pct:.2f}%)")
    
    # 分析每只ETF
    results = []
    
    for idx, row in etfs.iterrows():
        ts_code = row['ts_code']
        name = row['name']
        
        print(f"\n🔍 分析 {name} ({ts_code})...")
        
        # 计算主题评分
        theme_scores = calculate_theme_score(name)
        
        # 计算表现
        start_val, end_val, pct_change, latest_nav = calculate_performance(
            ts_code, start_date, end_date
        )
        
        if pct_change is None:
            continue
        
        # 计算超额收益
        alpha = pct_change - hs300_pct
        outperforms = alpha > 0
        
        # 确定主要主题
        main_theme = None
        max_score = 0
        for theme, score_info in theme_scores.items():
            if score_info['score'] > max_score:
                max_score = score_info['score']
                main_theme = theme
        
        # 收集结果
        result = {
            'ts_code': ts_code,
            'name': name,
            'start_price': round(start_val, 4) if start_val else None,
            'end_price': round(end_val, 4) if end_val else None,
            'change_pct': round(pct_change, 2),
            'latest_nav': round(latest_nav, 4) if latest_nav else None,
            'hs300_change': round(hs300_pct, 2),
            'alpha': round(alpha, 2),
            'outperforms': outperforms,
            'main_theme': main_theme,
            'theme_scores': theme_scores,
            'star_rating': theme_scores.get(main_theme, {}).get('stars', '☆☆☆') if main_theme else '☆☆☆'
        }
        
        results.append(result)
        
        # API限速控制
        time.sleep(0.1)
    
    # 按超额收益排序
    results.sort(key=lambda x: x['alpha'], reverse=True)
    
    print(f"\n✅ 分析完成，共分析 {len(results)} 只ETF")
    
    return {
        'analysis_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'period': f'{start_date} 至 {end_date}',
        'hs300_performance': {
            'start': round(hs300_start, 2),
            'end': round(hs300_end, 2),
            'change_pct': round(hs300_pct, 2)
        },
        'etfs': results
    }

def generate_html_report(analysis_data):
    """生成HTML专题报告"""
    print("📄 生成HTML专题报告...")
    
    # 读取模板
    template = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>十五五规划主题ETF专项分析报告 - 琥珀引擎</title>
    <link rel="stylesheet" href="/static/css/amber-v2.2.min.css">
    <style>
        .report-header {
            background: linear-gradient(135deg, #1a237e 0%, #283593 100%);
            color: white;
            padding: 2rem 1rem;
            border-radius: 10px;
            margin-bottom: 2rem;
        }
        .report-title {
            font-size: 2.5rem;
            font-weight: 700;
            margin-bottom: 0.5rem;
            color: #FFF;
        }
        .report-subtitle {
            font-size: 1.2rem;
            opacity: 0.9;
        }
        .analysis-period {
            background: #f5f5f5;
            padding: 1rem;
            border-radius: 8px;
            margin: 1rem 0;
            border-left: 4px solid #ff9800;
        }
        .hs300-benchmark {
            background: #e3f2fd;
            padding: 1.5rem;
            border-radius: 10px;
            margin: 1.5rem 0;
            text-align: center;
        }
        .hs300-value {
            font-size: 2rem;
            font-weight: 800;
            color: #1a237e;
            margin: 0.5rem 0;
        }
        .etf-table {
            width: 100%;
            border-collapse: collapse;
            margin: 2rem 0;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            border-radius: 10px;
            overflow: hidden;
        }
        .etf-table th {
            background: #1a237e;
            color: white;
            font-weight: 600;
            padding: 1rem;
            text-align: left;
        }
        .etf-table td {
            padding: 1rem;
            border-bottom: 1px solid #e0e0e0;
        }
        .etf-table tr:nth-child(even) {
            background: #f9f9f9;
        }
        .etf-table tr:hover {
            background: #f0f4f8;
        }
        .outperform-row {
            background-color: #ffebee !important;
            border-left: 4px solid #f44336 !important;
        }
        .theme-tech {
            background-color: rgba(26, 35, 126, 0.1) !important;
            border-left: 4px solid #1a237e !important;
        }
        .theme-green {
            background-color: rgba(76, 175, 80, 0.1) !important;
            border-left: 4px solid #4caf50 !important;
        }
        .theme-safety {
            background-color: rgba(255, 152, 0, 0.1) !important;
            border-left: 4px solid #ff9800 !important;
        }
        .star-rating {
            color: #ff9800;
            font-size: 1.2rem;
            font-weight: bold;
        }
        .positive-alpha {
            color: #f44336;
            font-weight: 700;
        }
        .negative-alpha {
            color: #4caf50;
            font-weight: 700;
        }
        .investment-advice {
            background: linear-gradient(135deg, #fff3e0 0%, #ffecb3 100%);
            padding: 2rem;
            border-radius: 10px;
            margin: 2rem 0;
            border: 3px solid #ff9800;
        }
        .advice-title {
            color: #1a237e;
            font-size: 1.8rem;
            margin-bottom: 1.5rem;
            border-bottom: 2px solid #ff9800;
            padding-bottom: 0.5rem;
        }
        .theme-weight {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 1.5rem;
            margin: 1.5rem 0;
        }
        .weight-card {
            background: white;
            padding: 1.5rem;
            border-radius: 8px;
            box-shadow: 0 2px 6px rgba(0,0,0,0.1);
        }
        .weight-card h4 {
            margin-top: 0;
            color: #1a237e;
            font-size: 1.4rem;
        }
        .weight-value {
            font-size: 2rem;
            font-weight: 800;
            color: #ff9800;
            margin: 0.5rem 0;
        }
        .recommendation-list {
            margin: 1.5rem 0;
            padding-left: 1.5rem;
        }
        .recommendation-list li {
            margin-bottom: 0.5rem;
            line-height: 1.6;
        }
        .footer {
            margin-top: 3rem;
            padding-top: 2rem;
            border-top: 2px solid #e0e0e0;
            color: #757575;
            font-size: 0.9rem;
            text-align: center;
        }
        @media (max-width: 768px) {
            .etf-table {
                display: block;
                overflow-x: auto;
            }
            .theme-weight {
                grid-template-columns: 1fr;
            }
            .report-title {
                font-size: 2rem;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <!-- 琥珀全局导航条 - V3.2.9 -->
        <nav class="amber-nav-bar">
            <a href="/etf/" class="nav-item">ETF 专区</a>
            <a href="/etf/report/" class="nav-item active">ETF 报告</a>
            <a href="/etf/strategy/" class="nav-item">投资策略</a>
            <a href="/" class="nav-item" style="margin-left:auto; font-size:14px; color:#757575;">← 返回首页</a>
        </nav>
        
        <div class="report-header">
            <h1 class="report-title">十五五规划主题ETF专项分析报告</h1>
            <p class="report-subtitle">政策-资产对齐分析 | 主题关联度评分 | 超额收益回测</p>
        </div>
        
        <div class="analysis-period">
            <h3>📅 分析时段</h3>
            <p><strong>{{