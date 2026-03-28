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
        <nav class="amber-nav-bar">
            <a href="/etf/" class="nav-item">ETF 专区</a>
            <a href="/etf/report/" class="nav-item active">ETF 报告</a>
            <a href="/etf/strategy/" class="nav-item">投资策略</a>
            <a href="/" class="nav-item" style="margin-left:auto; font-size:14px; color:#757575;">← 返回首页</a>
        </nav>
        
        <div class="report-header">
            <h1 class="report-title">十五五主题ETF"三维四定"体检报告</h1>
            <p class="report-subtitle">排队枪毙式筛选 | 三道防火墙拦截 | 仪表盘可视化</p>
        </div>
        
        <div class="execution-info">
            <h3>📋 执行信息</h3>
            <p><strong>指令版本</strong>: V3.3.3 "三维四定"体检指令</p>
            <p><strong>执行时间</strong>: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            <p><strong>分析范围</strong>: 除512760外的14只十五五主题ETF</p>
            <p><strong>数据源</strong>: AkShare + Tushare 双源校准 (模拟数据)</p>
            <p><strong>技术架构</strong>: 琥珀引擎量化基金选取标准化体系</p>
        </div>
        
        <div class="dashboard-stats">
            <div class="stat-card">
                <div class="stat-value">{len(analysis_results)}</div>
                <div class="stat-label">分析ETF数量</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{firewall_counts.get("通过", 0)}</div>
                <div class="stat-label">防火墙通过</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{firewall_counts.get("警告", 0)}</div>
                <div class="stat-label">防火墙警告</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{firewall_counts.get("淘汰", 0)}</div>
                <div class="stat-label">防火墙淘汰</div>
            </div>
        </div>
        
        <div class="firewall-details">
            <h3 class="firewall-title">🔥 三道防火墙执行标准</h3>
            <div class="firewall-item">
                <strong>第一道（流动性）</strong>: 过去20个交易日日均成交额 &lt; 5000万 → ❌ 淘汰 (Liquidity Risk)
            </div>
            <div class="firewall-item">
                <strong>第二道（相关性）</strong>: 与对应指数的60日相关系数 &lt; 0.95 → ⚠️ 警告 (Tracking Error)
            </div>
            <div class="firewall-item">
                <strong>第三道（费率）</strong>: 管理费+托管费 &gt; 0.6% → ❌ 淘汰 (High Cost)
            </div>
            <div style="margin-top: 1rem; font-size: 0.9rem; color: #666;">
                <em>注: 红色区域为未通过防火墙品种（灰度处理），绿色区域为评分≥85分的"优秀"品种（高亮显示）</em>
            </div>
        </div>
        
        <h2 class="section-title">📊 ETF体检结果仪表盘</h2>
        <p>按综合评分排序，防火墙状态实时显示</p>
        
        <table class="health-table">
            <thead>
                <tr>
                    <th>ETF代码</th>
                    <th>ETF名称</th>
                    <th>主题映射</th>
                    <th>综合评分</th>
                    <th>防火墙状态</th>
                    <th>架构师建议</th>
                </tr>
            </thead>
            <tbody>
                {etf_rows}
            </tbody>
        </table>
        
        <div class="theme-top-section">
            {theme_top_html}
        </div>
        
        <div class="conclusion-section">
            <h3 class="conclusion-title">📋 体检结论摘要</h3>
            
            <h4>✅ 防火墙拦截统计</h4>
            <ul>
'''
    
    # 添加防火墙拦截详情
    firewall_rejects = []
    firewall_warnings = []
    
    for result in analysis_results:
        etf = result['etf_info']
        firewall_status = result['firewall_status'][0]
        firewall_details = result['firewall_results']
        
        if firewall_status == "❌ 淘汰":
            reject_reasons = []
            for fw_name, fw_result in firewall_details.items():
                if not fw_result["passed"] and fw_name in ["liquidity", "fee"]:
                    reject_reasons.append(fw_result["reason"])
            
            if reject_reasons:
                firewall_rejects.append({
                    "name": etf['name'],
                    "code": etf['code'],
                    "reasons": reject_reasons
                })
        
        elif firewall_status == "⚠️ 警告":
            warning_reasons = []
            for fw_name, fw_result in firewall_details.items():
                if not fw_result["passed"]:
                    warning_reasons.append(fw_result["reason"])
            
            if warning_reasons:
                firewall_warnings.append({
                    "name": etf['name'],
                    "code": etf['code'],
                    "reasons": warning_reasons
                })
    
    # 添加结论内容
    if firewall_rejects:
        html_content += f'<li><strong>❌ 淘汰品种 ({len(firewall_rejects)}只):</strong></li>'
        for reject in firewall_rejects:
            html_content += f'<li style="margin-left: 1.5rem;">{reject["name"]} ({reject["code"]}) - {", ".join(reject["reasons"])}</li>'
    
    if firewall_warnings:
        html_content += f'<