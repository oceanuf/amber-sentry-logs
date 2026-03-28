        skeleton_score += max(0, (top10 / 60) * 30)
    skeleton_max += 30
    
    # 自我进化 (25%)
    rebalance = etf_data.get("rebalance_frequency", 12)
    if rebalance <= 6:
        skeleton_score += 25
    else:
        skeleton_score += max(0, (6 / rebalance) * 25)
    skeleton_max += 25
    
    # 行业纯度 (25%)
    purity = etf_data.get("industry_purity", 0)
    if purity >= 90:
        skeleton_score += 25
    else:
        skeleton_score += max(0, (purity / 90) * 25)
    skeleton_max += 25
    
    # 市值覆盖 (20%)
    coverage = etf_data.get("market_cap_coverage", 0)
    if coverage >= 80:
        skeleton_score += 20
    else:
        skeleton_score += max(0, (coverage / 80) * 20)
    skeleton_max += 20
    
    scores["skeleton"] = round((skeleton_score / skeleton_max) * 100, 2)
    
    # 精度维度 (25%)
    precision_score = 0
    precision_max = 0
    
    # 跟踪偏离度 (40%)
    tracking_error = etf_data.get("tracking_error", 1)
    if tracking_error <= 0.5:
        precision_score += 40
    else:
        precision_score += max(0, (0.5 / tracking_error) * 40)
    precision_max += 40
    
    # 信息比率 (30%)
    info_ratio = etf_data.get("information_ratio", 0)
    if info_ratio >= 0.5:
        precision_score += 30
    else:
        precision_score += max(0, (info_ratio / 0.5) * 30)
    precision_max += 30
    
    # 年度胜率 (30%)
    win_rate = etf_data.get("annual_win_rate", 0)
    if win_rate >= 70:
        precision_score += 30
    else:
        precision_score += max(0, (win_rate / 70) * 30)
    precision_max += 30
    
    scores["precision"] = round((precision_score / precision_max) * 100, 2)
    
    # 体量维度 (25%)
    liquidity_score = 0
    liquidity_max = 0
    
    # 规模红线 (40%)
    fund_size = etf_data.get("fund_size", 0)
    if fund_size >= 500000000:  # 5亿
        liquidity_score += 40
    else:
        liquidity_score += max(0, (fund_size / 500000000) * 40)
    liquidity_max += 40
    
    # 日均成交额 (35%)
    daily_volume = etf_data.get("avg_daily_volume", 0)
    if daily_volume >= 100000000:  # 1亿
        liquidity_score += 35
    else:
        liquidity_score += max(0, (daily_volume / 100000000) * 35)
    liquidity_max += 35
    
    # 买卖价差 (25%)
    spread = etf_data.get("bid_ask_spread", 0.2)
    if spread <= 0.001:  # 0.1%
        liquidity_score += 25
    else:
        liquidity_score += max(0, (0.001 / spread) * 25)
    liquidity_max += 25
    
    scores["liquidity"] = round((liquidity_score / liquidity_max) * 100, 2)
    
    # 损耗维度 (25%)
    cost_score = 0
    cost_max = 0
    
    # 综合费率 (50%)
    total_fee = etf_data.get("total_expense_ratio", 0.01)
    if total_fee <= 0.006:  # 0.6%
        cost_score += 50
    else:
        cost_score += max(0, (0.006 / total_fee) * 50)
    cost_max += 50
    
    # 管理费对比 (30%)
    mgmt_fee = etf_data.get("management_fee", 0.01)
    if mgmt_fee <= 0.005:  # 0.5%
        cost_score += 30
    else:
        cost_score += max(0, (0.005 / mgmt_fee) * 30)
    cost_max += 30
    
    # 费率趋势 (20%) - 模拟数据，假设稳定
    cost_score += 20
    cost_max += 20
    
    scores["cost"] = round((cost_score / cost_max) * 100, 2)
    
    return scores

def calculate_total_score(scores):
    """计算总分"""
    weights = {
        "skeleton": 0.25,
        "precision": 0.25,
        "liquidity": 0.25,
        "cost": 0.25
    }
    
    total_score = 0
    for dim, score in scores.items():
        total_score += score * weights.get(dim, 0.25)
    
    return round(total_score, 2)

def get_rating(total_score):
    """获取评级"""
    if total_score >= 85:
        return "优秀", "核心配置", "#4caf50"  # 绿色
    elif total_score >= 70:
        return "良好", "推荐配置", "#2196f3"  # 蓝色
    elif total_score >= 60:
        return "一般", "观察名单", "#ff9800"  # 橙色
    else:
        return "较差", "淘汰", "#f44336"  # 红色

def get_firewall_status(firewall_results):
    """获取防火墙状态"""
    all_passed = all(fw["passed"] for fw in firewall_results.values())
    if all_passed:
        return "✅ 通过", "#4caf50"
    
    # 检查是否有淘汰项
    has_reject = False
    for fw_name, fw_result in firewall_results.items():
        if not fw_result["passed"]:
            if fw_name in ["liquidity", "fee"]:  # 流动性或费率不通过直接淘汰
                has_reject = True
    
    if has_reject:
        return "❌ 淘汰", "#f44336"
    else:
        return "⚠️ 警告", "#ff9800"

def generate_html_report(analysis_results):
    """生成HTML体检报告"""
    print("\n📄 生成琥珀体检报告...")
    
    # 读取琥珀引擎CSS
    css_path = "/home/luckyelite/.openclaw/workspace/amber-engine/static/css/amber-v2.2.min.css"
    try:
        with open(css_path, 'r', encoding='utf-8') as f:
            amber_css = f.read()
    except:
        amber_css = ""
    
    # 构建ETF表格行
    etf_rows = ""
    theme_stats = {"科技自立": [], "绿色转型": [], "安全韧性": []}
    
    for result in analysis_results:
        etf = result['etf_info']
        scores = result['dimension_scores']
        total_score = result['total_score']
        rating, recommendation, rating_color = result['rating_info']
        firewall_status, firewall_color = result['firewall_status']
        firewall_details = result['firewall_results']
        
        # 按主题分类
        theme_stats[etf['theme']].append({
            "name": etf['name'],
            "code": etf['code'],
            "score": total_score,
            "rating": rating
        })
        
        # 确定行样式
        row_class = ""
        if firewall_status == "❌ 淘汰":
            row_class = "reject-row"
        elif total_score >= 85:
            row_class = "excellent-row"
        elif "警告" in firewall_status:
            row_class = "warning-row"
        
        # 防火墙详情
        firewall_detail_html = ""
        for fw_name, fw_result in firewall_details.items():
            status_icon = "✅" if fw_result["passed"] else "❌"
            firewall_detail_html += f"<div>{status_icon} {fw_name}: {fw_result['reason']}</div>"
        
        etf_rows += f'''
        <tr class="{row_class}">
            <td><strong>{etf['code']}</strong></td>
            <td><strong>{etf['name']}</strong></td>
            <td>
                <span style="font-weight:600; color:#1a237e;">
                    {etf['theme']}
                </span>
            </td>
            <td>
                <div style="font-size:1.2rem; font-weight:800; color:{rating_color};">
                    {total_score}
                </div>
            </td>
            <td>
                <div style="font-weight:600; color:{firewall_color};">
                    {firewall_status}
                </div>
                <div style="font-size:0.85rem; margin-top:4px;">
                    {firewall_detail_html}
                </div>
            </td>
            <td>
                <span style="color:{rating_color}; font-weight:600;">
                    {recommendation}
                </span>
            </td>
        </tr>
        '''
    
    # 主题Top品种
    theme_top_html = ""
    for theme, etfs in theme_stats.items():
        if etfs:
            # 按分数排序
            etfs.sort(key=lambda x: x['score'], reverse=True)
            top_etf = etfs[0]
            
            theme_color = {
                "科技自立": "#1a237e",
                "绿色转型": "#4caf50",
                "安全韧性": "#ff9800"
            }.get(theme, "#666")
            
            theme_top_html += f'''
            <div class="theme-top-card">
                <h4 style="color:{theme_color}; border-bottom:2px solid {theme_color}; padding-bottom:5px;">
                    {theme}主线 Top 1
                </h4>
                <div class="top-etf-info">
                    <div class="top-etf-name">{top_etf['name']}</div>
                    <div class="top-etf-code">{top_etf['code']}</div>
                    <div class="top-etf-score">评分: <strong>{top_etf['score']}</strong></div>
                    <div class="top-etf-rating">评级: <strong>{top_etf['rating']}</strong></div>
                </div>
            </div>
            '''
    
    # 统计信息
    rating_counts = {"优秀": 0, "良好": 0, "一般": 0, "较差": 0}
    firewall_counts = {"通过": 0, "警告": 0, "淘汰": 0}
    
    for result in analysis_results:
        rating = result['rating_info'][0]
        firewall_status = result['firewall_status'][0]
        
        rating_counts[rating] = rating_counts.get(rating, 0) + 1
        
        if "通过" in firewall_status:
            firewall_counts["通过"] += 1
        elif "警告" in firewall_status:
            firewall_counts["警告"] += 1
        elif "淘汰" in firewall_status:
            firewall_counts["淘汰"] += 1
    
    # 构建完整HTML
    html_content = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>十五五主题ETF"三维四定"体检报告 - 琥珀引擎</title>
    <style>
        {amber_css}
        
        /* 自定义样式 */
        .report-header {{
            background: linear-gradient(135deg, #1a237e 0%, #283593 100%);
            color: white;
            padding: 2rem 1rem;
            border-radius: 10px;
            margin-bottom: 2rem;
        }}
        .report-title {{
            font-size: 2.5rem;
            font-weight: 700;
            margin-bottom: 0.5rem;
            color: #FFF;
        }}
        .report-subtitle {{
            font-size: 1.2rem;
            opacity: 0.9;
        }}
        .execution-info {{
            background: #f5f5f5;
            padding: 1rem;
            border-radius: 8px;
            margin: 1rem 0;
            border-left: 4px solid #ff9800;
        }}
        .dashboard-stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1.5rem;
            margin: 2rem 0;
        }}
        .stat-card {{
            background: white;
            padding: 1.5rem;
            border-radius: 10px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            text-align: center;
        }}
        .stat-value {{
            font-size: 2.5rem;
            font-weight: 800;
            margin: 0.5rem 0;
        }}
        .stat-label {{
            color: #666;
            font-size: 0.9rem;
        }}
        .health-table {{
            width: 100%;
            border-collapse: collapse;
            margin: 2rem 0;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            border-radius: 10px;
            overflow: hidden;
        }}
        .health-table th {{
            background: #1a237e;
            color: white;
            font-weight: 600;
            padding: 1rem;
            text-align: left;
        }}
        .health-table td {{
            padding: 1rem;
            border-bottom: 1px solid #e0e0e0;
        }}
        .health-table tr:nth-child(even) {{
            background: #f9f9f9;
        }}
        .excellent-row {{
            background-color: #e8f5e9 !important;
            border-left: 4px solid #4caf50 !important;
        }}
        .warning-row {{
            background-color: #fff3e0 !important;
            border-left: 4px solid #ff9800 !important;
        }}
        .reject-row {{
            background-color: #ffebee !important;
            opacity: 0.7;
            border-left: 4px solid #f44336 !important;
        }}
        .theme-top-section {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 1.5rem;
            margin: 2rem 0;
        }}
        .theme-top-card {{
            background: white;
            padding: 1.5rem;
            border-radius: 10px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }}
        .top-etf-info {{
            margin-top: 1rem;
        }}
        .top-etf-name {{
            font-size: 1.2rem;
            font-weight: 600;
            margin-bottom: 0.5rem;
        }}
        .top-etf-code {{
            color: #666;
            font-family: monospace;
            margin-bottom: 0.5rem;
        }}
        .top-etf-score {{
            color: #1a237e;
            font-weight: 600;
        }}
        .top-etf-rating {{
            color: #4caf50;
            font-weight: 600;
        }}
        .firewall-details {{
            background: #f8f9fa;
            padding: 1.5rem;
            border-radius: 8px;
            margin: 1.5rem 0;
            border: 2px solid #e9ecef;
        }}
        .firewall-title {{
            color: #1a237e;
            font-size: 1.3rem;
            margin-bottom: 1rem;
            border-bottom: 2px solid #dee2e6;
            padding-bottom: 0.5rem;
        }}
        .firewall-item {{
            margin-bottom: 0.8rem;
            padding-left: 1.5rem;
            position: relative;
        }}
        .firewall-item:before {{
            content: "•";
            position: absolute;
            left: 0;
            color: #1a237e;
            font-weight: bold;
        }}
        .conclusion-section {{
            background: linear-gradient(135deg, #fff3e0 0%, #ffecb3 100%);
            padding: 2rem;
            border-radius: 10px;
            margin: 2rem 0;
            border: 3px solid #ff9800;
        }}
        .conclusion-title {{
            color: #1a237e;
            font-size: 1.8rem;
            margin-bottom: 1.5rem;
            border-bottom: 2px solid #ff9800;
            padding-bottom: 0.5rem;
        }}
        .footer {{
            margin-top: 3rem;
            padding-top: 2rem;
            border-top: 2px solid #e0e0e0;
            color: #757575;
            font-size: 0.9rem;
            text-align: center;
        }}
        @media (max-width: 768px) {{
            .health-table {{
                display: block;
                overflow-x: auto;
            }}
            .dashboard-stats {{
                grid-template-columns: 1fr;
            }}
            .theme-top-section {{
                grid-template-columns: 1fr;
            }}
            .report-title {{
                font-size: 2rem;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <!-- 琥珀全局导航条 - V3.2.9 -->
