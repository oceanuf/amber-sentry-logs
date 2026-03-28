#!/usr/bin/env python3
"""
创建主编私人作战室
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime, timedelta
import json
from config import PORTFOLIO, BENCHMARK_8_PERCENT, REBALANCING_CONFIG, T0_MAPPING
from config import calculate_current_weights, calculate_daily_contributions
from config import check_rebalancing_warnings, check_fee_optimization, estimate_t0_pnl

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
DASHBOARD_DIR = os.path.join(OUTPUT_DIR, "my-wealth")

def create_dashboard():
    """创建主编私人作战室"""
    print("创建主编私人作战室...")
    
    # 创建目录
    os.makedirs(DASHBOARD_DIR, exist_ok=True)
    
    # 计算各项数据
    current_weights = calculate_current_weights(PORTFOLIO)
    contributions = calculate_daily_contributions(PORTFOLIO)
    warnings = check_rebalancing_warnings(PORTFOLIO)
    fee_suggestion = check_fee_optimization(PORTFOLIO)
    t0_estimate = estimate_t0_pnl(PORTFOLIO)
    
    # 计算总盈亏
    total_daily_pnl = sum(contrib["daily_pnl"] for contrib in contributions)
    total_daily_change = (total_daily_pnl / PORTFOLIO["total_amount"]) * 100
    
    # 生成HTML
    html = generate_dashboard_html(
        current_weights, contributions, warnings, 
        fee_suggestion, t0_estimate, total_daily_pnl, total_daily_change
    )
    
    # 保存页面
    dashboard_path = os.path.join(DASHBOARD_DIR, "index.html")
    with open(dashboard_path, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"✅ 私人作战室创建完成: {dashboard_path}")
    
    # 创建滚动显示数据
    create_scrolling_display(contributions, total_daily_pnl)
    
    return dashboard_path

def generate_dashboard_html(weights, contributions, warnings, fee_suggestion, t0_estimate, total_pnl, total_change):
    """生成作战室HTML"""
    
    # 生成基金卡片
    fund_cards = ""
    for fund in PORTFOLIO["funds"]:
        weight_data = weights[fund["code"]]
        deviation = weight_data["deviation_percent"]
        
        # 判断是否需要预警
        warning_class = "rebalance-warning" if abs(deviation) > REBALANCING_CONFIG["deviation_threshold"] else ""
        
        # 计算盈亏
        daily_pnl = fund["amount"] * (fund["daily_change"] / 100)
        pnl_class = "price-up" if daily_pnl > 0 else "price-down"
        pnl_sign = "+" if daily_pnl > 0 else ""
        
        fund_cards += f'''
        <div class="finance-card {warning_class}">
            <div class="card-header">
                <h3>{fund["name"]} ({fund["code"]})</h3>
                <span class="source-tag">{fund["category"]}</span>
            </div>
            <div class="card-content">
                <div class="grid-2">
                    <div>
                        <p><strong>持仓金额:</strong> {fund["amount"]/10000:.1f}万</p>
                        <p><strong>当前权重:</strong> {weight_data["current_weight"]:.1f}%</p>
                        <p><strong>初始权重:</strong> {fund["initial_weight"]:.1f}%</p>
                        <p><strong>偏离度:</strong> <span class="{pnl_class}">{deviation:+.1f}%</span></p>
                    </div>
                    <div>
                        <p><strong>最新净值:</strong> {fund["current_nav"]:.4f}</p>
                        <p><strong>日涨跌幅:</strong> <span class="{pnl_class}">{fund["daily_change"]:+.2f}%</span></p>
                        <p><strong>今日盈亏:</strong> <span class="{pnl_class}">{pnl_sign}{daily_pnl:.1f}元</span></p>
                        <p><strong>风险等级:</strong> {fund["risk_level"]}</p>
                    </div>
                </div>
                <div class="mt-3">
                    <p><strong>场内映射:</strong> {fund["etf_mapping"]}</p>
                    <p><strong>管理费率:</strong> {fund["fee_rate"]:.2f}%</p>
                    <p class="text-sm">{fund["description"]}</p>
                </div>
            </div>
        </div>
        '''
    
    # 生成预警信息
    warnings_html = ""
    if warnings:
        warnings_html = '''
        <div class="finance-card rebalance-warning">
            <h3 class="section-title">⚠️ 再平衡预警</h3>
            <div class="grid-2">
        '''
        
        for warning in warnings:
            warnings_html += f'''
                <div class="point-card">
                    <h4>{warning["name"]}</h4>
                    <p>{warning["message"]}</p>
                    <p class="text-sm">建议关注权重偏离情况</p>
                </div>
            '''
        
        warnings_html += '''
            </div>
        </div>
        '''
    
    # 生成费率优化建议
    fee_html = ""
    if fee_suggestion:
        fee_html = f'''
        <div class="finance-card">
            <h3 class="section-title">💰 费率优化建议</h3>
            <div class="amber-metrics-card">
                <div class="metrics-grid">
                    <div class="metric-item">
                        <div class="metric-label">增强型基金</div>
                        <div class="metric-value">{fee_suggestion["enhanced_fund"]}</div>
                    </div>
                    <div class="metric-item">
                        <div class="metric-label">被动型基金</div>
                        <div class="metric-value">{fee_suggestion["passive_fund"]}</div>
                    </div>
                    <div class="metric-item">
                        <div class="metric-label">超额收益</div>
                        <div class="metric-value">{fee_suggestion["excess_return"]:.2f}%</div>
                    </div>
                    <div class="metric-item">
                        <div class="metric-label">费率差</div>
                        <div class="metric-value">{REBALANCING_CONFIG["fee_comparison"]["fee_difference"]:.2f}%</div>
                    </div>
                </div>
                <div class="mt-3 text-center">
                    <h4 class="etf-highlight-up">{fee_suggestion["suggestion"]}</h4>
                    <p>{fee_suggestion["reason"]}</p>
                </div>
            </div>
        </div>
        '''
    
    # 生成T+0估算
    t0_html = f'''
    <div class="finance-card">
        <h3 class="section-title">⚡ T+0 实时盈亏估算</h3>
        <div class="amber-metrics-card">
            <div class="metrics-grid">
                <div class="metric-item">
                    <div class="metric-label">总持仓</div>
                    <div class="metric-value">{PORTFOLIO["total_amount"]/10000:.1f}万</div>
                </div>
                <div class="metric-item">
                    <div class="metric-label">估算总盈亏</div>
                    <div class="metric-value {'price-up' if t0_estimate['total_estimated_pnl'] > 0 else 'price-down'}">
                        {t0_estimate['total_estimated_pnl']:+.1f}元
                    </div>
                </div>
                <div class="metric-item">
                    <div class="metric-label">估算涨跌幅</div>
                    <div class="metric-value">{total_change:+.2f}%</div>
                </div>
                <div class="metric-item">
                    <div class="metric-label">更新时间</div>
                    <div class="metric-value">{t0_estimate['update_time']}</div>
                </div>
            </div>
        </div>
        
        <div class="mt-4">
            <h4>各基金估算盈亏</h4>
            <table class="price-table">
                <thead>
                    <tr>
                        <th>基金名称</th>
                        <th>场内映射</th>
                        <th>估算涨跌</th>
                        <th>估算盈亏</th>
                    </tr>
                </thead>
                <tbody>
    '''
    
    for estimate in t0_estimate["fund_estimates"]:
        change_class = "price-up" if estimate["estimated_change"] > 0 else "price-down"
        pnl_class = "price-up" if estimate["estimated_pnl"] > 0 else "price-down"
        change_sign = "+" if estimate["estimated_change"] > 0 else ""
        pnl_sign = "+" if estimate["estimated_pnl"] > 0 else ""
        
        t0_html += f'''
                    <tr>
                        <td>{estimate["name"]}</td>
                        <td>{estimate["etf_mapping"]}</td>
                        <td class="{change_class}">{change_sign}{estimate["estimated_change"]:.2f}%</td>
                        <td class="{pnl_class}">{pnl_sign}{estimate["estimated_pnl"]:.1f}元</td>
                    </tr>
        '''
    
    t0_html += '''
                </tbody>
            </table>
        </div>
    </div>
    '''
    
    # 生成8%基准线说明
    benchmark_html = f'''
    <div class="finance-card">
        <h3 class="section-title">🎯 8% 年化收益追踪器</h3>
        <div class="amber-metrics-card">
            <div class="metrics-grid">
                <div class="metric-item">
                    <div class="metric-label">目标年化</div>
                    <div class="metric-value">{BENCHMARK_8_PERCENT["annual_return"]}%</div>
                </div>
                <div class="metric-item">
                    <div class="metric-label">日化收益率</div>
                    <div class="metric-value">{BENCHMARK_8_PERCENT["daily_return"]*100:.3f}%</div>
                </div>
                <div class="metric-item">
                    <div class="metric-label">基准线颜色</div>
                    <div class="metric-value" style="color: {BENCHMARK_8_PERCENT['line_color']};">金黄色</div>
                </div>
                <div class="metric-item">
                    <div class="metric-label">今日表现</div>
                    <div class="metric-value {'price-up' if total_change > BENCHMARK_8_PERCENT['daily_return']*100 else 'price-down'}">
                        {total_change:+.2f}%
                    </div>
                </div>
            </div>
        </div>
        
        <div class="mt-4">
            <h4>基准线说明</h4>
            <p>在净值图中绘制斜率为年化8%的金黄色虚线 ({BENCHMARK_8_PERCENT['line_color']})。</p>
            <p>今日目标: {BENCHMARK_8_PERCENT['daily_return']*100:.3f}% | 实际表现: {total_change:+.2f}%</p>
            <p class="mt-3 {'price-up' if total_change > BENCHMARK_8_PERCENT['daily_return']*100 else 'price-down'}">
                {'✅ 超越8%日化目标' if total_change > BENCHMARK_8_PERCENT['daily_return']*100 else '⚠️ 未达8%日化目标'}
            </p>
        </div>
    </div>
    '''
    
    # 生成盈亏贡献榜
    contributions_html = '''
    <div class="finance-card">
        <h3 class="section-title">📊 盈亏贡献榜</h3>
        <div class="amber-metrics-card">
            <div class="metrics-grid">
    '''
    
    for i, contrib in enumerate(contributions[:3], 1):
        medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉"
        pnl_class = "price-up" if contrib["daily_pnl"] > 0 else "price-down"
        pnl_sign = "+" if contrib["daily_pnl"] > 0 else ""
        
        contributions_html += f'''
                <div class="metric-item">
                    <div class="metric-label">{medal} {contrib["name"]}</div>
                    <div class="metric-value {pnl_class}">
                        {pnl_sign}{contrib["daily_pnl"]:.1f}元
                    </div>
                    <div class="metric-sub">{contrib["daily_change"]:+.2f}%</div>
                </div>
        '''
    
    contributions_html += '''
            </div>
        </div>
        
        <div class="mt-4">
            <h4>详细贡献</h4>
            <table class="price-table">
                <thead>
                    <tr>
                        <th>排名</th>
                        <th>基金名称</th>
                        <th>涨跌幅</th>
                        <th>盈亏贡献</th>
                        <th>贡献占比</th>
                    </tr>
                </thead>
                <tbody>
    '''
    
    for i, contrib in enumerate(contributions, 1):
        pnl_class = "price-up" if contrib["daily_pnl"] > 0 else "price-down"
        pnl_sign = "+" if contrib["daily_pnl"] > 0 else ""
        contribution_percent = (contrib["daily_pnl"] / total_pnl * 100) if total_pnl != 0 else 0
        
        contributions_html += f'''
                    <tr>
                        <td>{i}</td>
                        <td>{contrib["name"]}</td>
                        <td class="{pnl_class}">{contrib["daily_change"]:+.2f}%</td>
                        <td class="{pnl_class}">{pnl_sign}{contrib["daily_pnl"]:.1f}元</td>
                        <td>{contribution_percent:.1f}%</td>
                    </tr>
        '''
    
    contributions_html += '''
                </tbody>
            </table>
        </div>
    </div>
    '''
    
    # 完整的HTML
    html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>主编私人作战室 - 50.4万持仓雷达</title>
    <link rel="stylesheet" href="/static/css/amber-v2.2.min.css">
    <style>
        /* 再平衡预警样式 */
        .rebalance-warning {{
            border: 2px solid {REBALANCING_CONFIG["warning_color"]};
            animation: pulse-warning 2s infinite;
        }}
        
        @keyframes pulse-warning {{
            0%, 100% {{ box-shadow: 0 0 10px {REBALANCING_CONFIG["warning_color"]}80; }}
            50% {{ box-shadow: 0 0 20px {REBALANCING_CONFIG["warning_color"]}; }}
        }}
        
        /* 8%基准线样式 */
        .benchmark-line {{
            stroke: {BENCHMARK_8_PERCENT["line_color"]};
            stroke-width: {BENCHMARK_8_PERCENT["line_width"]};
            stroke-dasharray: 5,5;
        }}
        
        /* 作战室专属样式 */
        .wealth-header {{
            background: linear-gradient(135deg, #0d47a1 0%, #1a237e 100%);
            color: white;
            padding: 2rem 0;
            margin-bottom: 2rem;
            border-radius: 0 0 1rem 1rem;
        }}
        
        .wealth-stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1rem;
            margin: 2rem 0;
        }}
        
        .wealth-stat-card {{
            background: white;
            padding: 1.5rem;
            border-radius: 0.75rem;
            box-shadow: var(--shadow-md);
            text-align: center;
        }}
        
        .wealth-stat-value {{
            font-size: 2rem;
            font-weight: 800;
            margin: 0.5rem 0;
        }}
        
        .wealth-stat-label {{
            font-size: 0.875rem;
            color: var(--graphite-gray);
        }}
        
        .positive {{
            color: var(--success-green);
        }}
        
        .negative {{
            color: var(--error-red);
        }}
        
        /* 响应式调整 */
        @media (max-width: 768px) {{
            .wealth-stats {{
                grid-template-columns: 1fr;
            }}
            
            .wealth-stat-card {{
                padding: 1rem;
            }}
            
            .wealth-stat-value {{
                font-size: 1.5rem;
            }}
        }}
    </style>
</head>
<body>
    <!-- 作战室头部 -->
    <header class="wealth-header">
        <div class="container">
            <h1>主编私人作战室</h1>
            <p>50.4万持仓专项雷达 | 实时监控与智能分析</p>
            <div class="mt-4">
                <a href="/" class="source-tag">返回首页</a>
                <span class="ml-3 text-sm">最后