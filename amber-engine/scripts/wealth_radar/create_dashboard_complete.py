#!/usr/bin/env python3
"""
创建主编私人作战室 - 完整版本
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime
from config import PORTFOLIO, BENCHMARK_8_PERCENT, REBALANCING_CONFIG, T0_MAPPING
from config import calculate_current_weights, calculate_daily_contributions
from config import check_rebalancing_warnings, check_fee_optimization, estimate_t0_pnl

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
DASHBOARD_DIR = os.path.join(OUTPUT_DIR, "my-wealth")

def create_scrolling_display(contributions, total_pnl):
    """创建首页滚动显示数据"""
    # 生成滚动显示内容
    scroll_items = []
    
    for contrib in contributions:
        sign = "+" if contrib["daily_pnl"] > 0 else ""
        scroll_items.append(f"{contrib['name']}: {sign}{contrib['daily_pnl']:.1f}元 ({contrib['daily_change']:+.2f}%)")
    
    total_sign = "+" if total_pnl > 0 else ""
    scroll_items.append(f"总计: {total_sign}{total_pnl:.1f}元")
    
    # 创建滚动显示HTML
    scroll_html = f'''
    <!-- 主编持仓盈亏贡献榜 - 首页滚动显示 -->
    <div class="wealth-scroll-container">
        <div class="wealth-scroll-content">
            <span class="wealth-scroll-label">📊 主编持仓今日盈亏:</span>
            {' • '.join(scroll_items)}
        </div>
    </div>
    
    <style>
        .wealth-scroll-container {{
            background: linear-gradient(90deg, #f3e5f5 0%, #e1bee7 100%);
            border-left: 4px solid #9c27b0;
            padding: 0.5rem 1rem;
            margin: 1rem 0;
            border-radius: 0.5rem;
            overflow: hidden;
        }}
        
        .wealth-scroll-content {{
            white-space: nowrap;
            animation: scroll-left 30s linear infinite;
            font-size: 0.875rem;
            color: #333;
        }}
        
        .wealth-scroll-label {{
            font-weight: 600;
            color: #9c27b0;
            margin-right: 0.5rem;
        }}
        
        @keyframes scroll-left {{
            0% {{ transform: translateX(100%); }}
            100% {{ transform: translateX(-100%); }}
        }}
        
        @media (max-width: 768px) {{
            .wealth-scroll-container {{
                padding: 0.5rem;
            }}
            
            .wealth-scroll-content {{
                font-size: 0.75rem;
                animation: scroll-left 20s linear infinite;
            }}
        }}
    </style>
    '''
    
    # 保存到单独文件，供首页引用
    scroll_path = os.path.join(DASHBOARD_DIR, "scroll_display.html")
    with open(scroll_path, 'w', encoding='utf-8') as f:
        f.write(scroll_html)
    
    print(f"✅ 滚动显示创建完成: {scroll_path}")
    return scroll_path

def create_dashboard():
    """创建主编私人作战室"""
    print("🚀 创建主编私人作战室...")
    
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
    
    # 创建数据JSON文件（供其他页面使用）
    create_data_json(current_weights, contributions, total_daily_pnl, total_daily_change)
    
    return dashboard_path

def generate_dashboard_html(weights, contributions, warnings, fee_suggestion, t0_estimate, total_pnl, total_change):
    """生成作战室HTML"""
    
    # 计算统计数据
    positive_contributions = sum(1 for c in contributions if c["daily_pnl"] > 0)
    negative_contributions = len(contributions) - positive_contributions
    
    # 头部统计卡片
    stats_html = f'''
    <div class="wealth-stats">
        <div class="wealth-stat-card">
            <div class="wealth-stat-label">总持仓</div>
            <div class="wealth-stat-value">{PORTFOLIO["total_amount"]/10000:.1f}万</div>
        </div>
        
        <div class="wealth-stat-card">
            <div class="wealth-stat-label">今日盈亏</div>
            <div class="wealth-stat-value {'positive' if total_pnl > 0 else 'negative'}">
                {'+' if total_pnl > 0 else ''}{total_pnl:.1f}元
            </div>
            <div class="wealth-stat-label">{total_change:+.2f}%</div>
        </div>
        
        <div class="wealth-stat-card">
            <div class="wealth-stat-label">8%目标对比</div>
            <div class="wealth-stat-value {'positive' if total_change > BENCHMARK_8_PERCENT['daily_return']*100 else 'negative'}">
                {'✅ 超越' if total_change > BENCHMARK_8_PERCENT['daily_return']*100 else '⚠️ 未达'}
            </div>
            <div class="wealth-stat-label">目标: {BENCHMARK_8_PERCENT['daily_return']*100:.3f}%</div>
        </div>
        
        <div class="wealth-stat-card">
            <div class="wealth-stat-label">上涨基金</div>
            <div class="wealth-stat-value positive">{positive_contributions}只</div>
            <div class="wealth-stat-label">下跌基金: {negative_contributions}只</div>
        </div>
    </div>
    '''
    
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
        
        # 判断是否超越8%目标
        vs_target = "✅" if fund["daily_change"] > BENCHMARK_8_PERCENT['daily_return']*100 else "⚠️"
        
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
                        <p><strong>日涨跌幅:</strong> <span class="{pnl_class}">{fund["daily_change"]:+.2f}% {vs_target}</span></p>
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
                    </