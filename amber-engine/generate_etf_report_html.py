#!/usr/bin/env python3
"""
ETF报告HTML生成器
将JSON报告转换为HTML网页
"""

import json
import os
from datetime import datetime

def load_json_report(json_path):
    """加载JSON报告"""
    with open(json_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def generate_html(report):
    """生成HTML内容"""
    
    # 生成ETF表现表格
    top_etfs_table = ""
    for etf in report['top_performing_etfs']:
        change_class = "price-up" if etf['change'].startswith('+') else "price-down"
        correlation_class = "tag-high" if etf['correlation'] == '高度相关' else "tag-medium" if etf['correlation'] == '中度相关' else "tag-low"
        top_etfs_table += f"""
            <tr>
                <td>{etf['rank']}</td>
                <td>{etf['name']}</td>
                <td>{etf['code']}</td>
                <td>{etf['industry']}</td>
                <td class="{change_class}">{etf['change']}</td>
                <td><span class="{correlation_class}">{etf['correlation']}</span></td>
            </tr>"""
    
    # 生成行业表现表格
    sector_table = ""
    for sector in report['sector_performance']:
        change_class = "price-up" if sector['avg_change'].startswith('+') else "price-down"
        sector_table += f"""
            <tr>
                <td>{sector['sector']}</td>
                <td>{sector['etf_count']}</td>
                <td class="{change_class}">{sector['avg_change']}</td>
                <td>{sector['outlook']}</td>
            </tr>"""
    
    # 生成高度相关产业赛道列表
    correlated_sectors = ""
    for sector in report['fifteen_five_correlation']['highly_correlated_sectors']:
        correlated_sectors += f'<li>{sector}</li>'
    
    # 生成重点推荐ETF表格
    recommended_table = ""
    for rec in report['investment_recommendations']['highly_recommended']:
        recommended_table += f"""
            <tr>
                <td><span class="star-rating">⭐⭐⭐⭐⭐</span></td>
                <td>{rec['name']}</td>
                <td>{rec['reason']}</td>
                <td>{rec['target_sectors']}</td>
            </tr>"""
    
    # 生成观察列表
    watch_list = ""
    for watch in report['investment_recommendations']['watch_list']:
        watch_list += f"""
            <li><strong>{watch['name']}</strong>: {watch['reason']} <em>(关注因素: {watch['monitor_factors']})</em></li>"""
    
    # 生成谨慎对待板块
    cautious_list = ""
    for cautious in report['investment_recommendations']['cautious_sectors']:
        cautious_list += f"""
            <li><strong>{cautious['sector']}</strong>: {cautious['reason']} <em>(建议: {cautious['suggested_approach']})</em></li>"""
    
    # 生成风险列表
    risk_list = ""
    for risk in report['risk_considerations']:
        risk_list += f'<li>{risk}</li>'
    
    # 生成核心发现列表
    key_findings = ""
    for finding in report['executive_summary']['key_findings']:
        key_findings += f'<li>{finding}</li>'
    
    html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ETF基金分析报告 - 琥珀引擎</title>
    <link rel="stylesheet" href="/static/css/amber-v2.2.min.css">
    <style>
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
        }}
        .report-subtitle {{
            font-size: 1.2rem;
            opacity: 0.9;
        }}
        .section-title {{
            font-size: 1.8rem;
            font-weight: 600;
            color: #1a237e;
            border-left: 5px solid #ff9800;
            padding-left: 1rem;
            margin: 2.5rem 0 1.5rem;
        }}
        .subsection-title {{
            font-size: 1.4rem;
            font-weight: 600;
            color: #3949ab;
            margin: 2rem 0 1rem;
        }}
        .info-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 1rem;
            margin: 1.5rem 0;
        }}
        .info-card {{
            background: #f5f5f5;
            padding: 1rem;
            border-radius: 8px;
            border-left: 4px solid #3949ab;
        }}
        .info-card h3 {{
            margin-top: 0;
            color: #1a237e;
            font-size: 1rem;
            font-weight: 600;
        }}
        .info-card p {{
            margin: 0.5rem 0 0;
            font-size: 1.2rem;
            font-weight: 700;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 1.5rem 0;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            border-radius: 8px;
            overflow: hidden;
        }}
        th {{
            background: #1a237e;
            color: white;
            font-weight: 600;
            padding: 1rem;
            text-align: left;
        }}
        td {{
            padding: 1rem;
            border-bottom: 1px solid #e0e0e0;
        }}
        tr:nth-child(even) {{
            background: #f9f9f9;
        }}
        .tag-high {{
            background: #4caf50;
            color: white;
            padding: 0.25rem 0.5rem;
            border-radius: 4px;
            font-size: 0.9rem;
            font-weight: 600;
        }}
        .tag-medium {{
            background: #ff9800;
            color: white;
            padding: 0.25rem 0.5rem;
            border-radius: 4px;
            font-size: 0.9rem;
            font-weight: 600;
        }}
        .tag-low {{
            background: #9e9e9e;
            color: white;
            padding: 0.25rem 0.5rem;
            border-radius: 4px;
            font-size: 0.9rem;
            font-weight: 600;
        }}
        .star-rating {{
            color: #ff9800;
            font-size: 1.2rem;
        }}
        .correlation-stats {{
            display: flex;
            gap: 2rem;
            margin: 1.5rem 0;
        }}
        .stat-card {{
            flex: 1;
            background: #e3f2fd;
            padding: 1.5rem;
            border-radius: 8px;
            text-align: center;
        }}
        .stat-number {{
            font-size: 2.5rem;
            font-weight: 700;
            color: #1a237e;
            margin: 0.5rem 0;
        }}
        .stat-label {{
            font-size: 1rem;
            color: #5c6bc0;
        }}
        .conclusion-box {{
            background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
            padding: 2rem;
            border-radius: 10px;
            margin: 2rem 0;
            border-left: 6px solid #1a237e;
        }}
        .conclusion-title {{
            font-size: 1.6rem;
            color: #1a237e;
            margin-bottom: 1rem;
        }}
        .footer {{
            margin-top: 3rem;
            padding-top: 2rem;
            border-top: 2px solid #e0e0e0;
            color: #757575;
            font-size: 0.9rem;
            text-align: center;
        }}
        .nav-breadcrumb {{
            margin-bottom: 1.5rem;
            font-size: 0.9rem;
        }}
        .nav-breadcrumb a {{
            color: #1a237e;
            text-decoration: none;
        }}
        .nav-breadcrumb a:hover {{
            text-decoration: underline;
        }}
        @media (max-width: 768px) {{
            .info-grid {{
                grid-template-columns: 1fr;
            }}
            .correlation-stats {{
                flex-direction: column;
                gap: 1rem;
            }}
            table {{
                display: block;
                overflow-x: auto;
            }}
            .report-title {{
                font-size: 2rem;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <!-- 导航 -->
        <div class="nav-breadcrumb">
            <a href="/">首页</a> &gt; <a href="/etf/">ETF专区</a> &gt; <a href="/etf/report/">分析报告</a> &gt; ETF基金分析报告
        </div>
        
        <!-- 报告头部 -->
        <div class="report-header">
            <h1 class="report-title">📊 ETF基金分析报告</h1>
            <div class="report-subtitle">基于Tushare Pro数据库的深度分析 | 十五五规划相关性研究</div>
        </div>
        
        <!-- 报告信息 -->
        <div class="info-grid">
            <div class="info-card">
                <h3>报告日期</h3>
                <p>{report['report_date']}</p>
            </div>
            <div class="info-card">
                <h3>分析期间</h3>
                <p>{report['analysis_period']}</p>
            </div>
            <div class="info-card">
                <h3>分析ETF数量</h3>
                <p>{report['total_etfs_analyzed']} 只</p>
            </div>
            <div class="info-card">
                <h3>数据来源</h3>
                <p>{report['data_source']}</p>
            </div>
        </div>
        
        <!-- 一、执行摘要 -->
        <h2 class="section-title">一、执行摘要</h2>
        
        <div class="info-card">
            <h3>整体表现</h3>
            <p>{report['executive_summary']['overall_performance']}</p>
        </div>
        
        <h3 class="subsection-title">核心发现</h3>
        <ul>
            {key_findings}
        </ul>
        
        <div class="info-card">
            <h3>投资建议</h3>
            <p>{report['executive_summary']['recommendation']}</p>
        </div>
        
        <!-- 二、表现最佳ETF -->
        <h2 class="section-title">二、表现最佳ETF（前10名）</h2>
        
        <table>
            <thead>
                <tr>
                    <th>排名</th>
                    <th>ETF名称</th>
                    <th>代码</th>
                    <th>行业</th>
                    <th>涨跌幅</th>
                    <th>十五五相关性</th>
                </tr>
            </thead>
            <tbody>
                {top_etfs_table}
            </tbody>
        </table>
        
        <!-- 三、行业板块表现 -->
        <h2 class="section-title">三、行业板块表现</h2>
        
        <table>
            <thead>
                <tr>
                    <th>行业板块</th>
                    <th>ETF数量</th>
                    <th>平均涨跌幅</th>
                    <th>展望</th>
                </tr>
            </thead>
            <tbody>
                {sector_table}
            </tbody>
        </table>
        
        <!-- 四、十五五规划相关性分析 -->
        <h2 class="section-title">四、十五五规划相关性分析</h2>
        
        <h3 class="subsection-title">高度相关产业赛道</h3>
        <ol>
            {correlated_sectors}
        </ol>
        
        <h3 class="subsection-title">相关性统计</h3>
        <div class="correlation-stats">
            <div class="stat-card">
                <div class="stat-number">{report['fifteen_five_correlation']['highly_correlated_etf_count']}</div>
                <div class="stat-label">高度相关ETF</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{report['fifteen_five_correlation']['medium_correlated_etf_count']}</div>
                <div class="stat-label">中度相关ETF</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{report['fifteen_five_correlation']['low_correlated_etf_count']}</div>
                <div class="stat-label">低度相关ETF</div>
            </div>
        </div>
        
        <!-- 五、投资建议 -->
        <h2 class="section-title">五、投资建议</h2>
        
        <h3 class="subsection-title">重点推荐ETF</h3>
        <table>
            <thead>
                <tr>
                    <th>推荐等级</th>
                    <th>ETF名称</th>
                    <th>推荐理由</th>
                    <th>目标赛道</th>
                </tr>
            </thead>
            <tbody>
                {recommended_table}
            </tbody>
        </table>
        
        <h3 class="subsection-title">观察列表</h3>
        <ul>
            {watch_list}
        </ul>
        
        <h3 class="subsection-title">谨慎对待板块</h3>
        <ul>
            {cautious_list}
        </ul>
        
        <!-- 六、风险考量 -->
        <h2 class="section-title">六、风险考量</h2>
        <ul>
            {risk_list}
        </ul>
        
        <!-- 七、核心结论 -->
        <h2 class="section-title">七、核心结论</h2>
        
        <div class="conclusion-box">
            <h3 class="conclusion-title">核心观点</h3>
            <p>{report['conclusion']['core_view']}</p>
            
            <h3 class="conclusion-title">投资主题</h3>
            <p>{report['conclusion']['investment_theme']}</p>
            
            <h3 class="conclusion-title">策略建议</h3>
            <p>{report['conclusion']['strategy_suggestion']}</p>
            
            <h3 class="conclusion-title">时间视角</h3>
            <p>{report['conclusion']['time_horizon']}</p>
        </div>
        
        <!-- 八、附录 -->
        <h2 class="section-title">八、附录</h2>
        
        <h3 class="subsection-title">分析方法说明</h3>
        <ol>
            <li><strong>数据来源</strong>: Tushare Pro金融数据库</li>
            <li><strong>分析期间</strong>: 2026年2月27日至3月20日</li>
            <li><strong>计算方法</strong>: 基于基金净值计算期间涨跌幅</li>
            <li><strong>行业分类</strong>: 根据基金名称和投资方向进行人工分类</li>
            <li><strong>相关性判断</strong>: 基于十五五规划公开信息进行产业匹配</li>
        </ol>
        
        <h3 class="subsection-title">免责声明</h3>
        <ol>
            <li>本报告基于公开数据和分析模型生成</li>
            <li>报告内容仅供参考，不构成投资建议</li>
            <li>投资有风险，决策需谨慎</li>
            <li>历史表现不代表未来收益</li>
        </ol>
        
        <!-- 页脚 -->
        <div class="footer">
            <p><strong>报告生成</strong>: Cheese Intelligence Team · 工程师</p>
            <p><strong>报告版本</strong>: v1.0 · <strong>生成时间</strong>: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            <p><strong>联系方式</strong>: 通过OpenClaw系统反馈</p>
            <p class="mt-3">© 2026 琥珀引擎 · 所有数据仅供参考，不构成投资建议</p>
        </div>
    </div>
</body>
</html>'''
    
    return html

def main():
    """主函数"""
    print("📊 生成ETF分析报告HTML...")
    
    # 输入JSON文件路径
    json_path = "/home/luckyelite/.openclaw/workspace/amber-engine/reports/etf_analysis/etf_analysis_20260320_222615.json"
    
    # 输出目录
    output_dir = "/home/luckyelite/.openclaw/workspace/amber-engine/output/etf/report"
    os.makedirs(output_dir, exist_ok=True)
    
    # 输出文件路径
    output_path = os.path.join(output_dir, "index.html")
    
    try:
        # 加载报告
        print(f"📂 加载报告: {json_path}")
        report = load_json_report(json_path)
        
        # 生成HTML
        print("🖥️ 生成HTML内容...")
        html_content = generate_html(report)
        
        # 保存HTML
        print(f"💾 保存HTML: {output_path}")
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print("✅ HTML报告生成完成!")
        print(f"📁 文件位置: {output_path}")
        
        # 设置正确的权限
        os.chmod(output_path, 0o644)
        
        # 创建报告列表索引
        create_report_index(output_dir)
        
        return True
        
    except Exception as e:
        print(f"❌ 生成HTML报告失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def create_report_index(output_dir):
    """创建报告索引页面"""
    index_path = os.path.join(output_dir, "reports.html")
    
    index_html = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ETF分析报告库 - 琥珀引擎</title>
    <link rel="stylesheet" href="/static/css/amber-v2.2.min.css">
    <style>
        .header {{
            background: linear-gradient(135deg, #1a237e 0%, #283593 100%);
            color: white;
            padding: 2rem 1rem;
            border-radius: 10px;
            margin-bottom: 2rem;
        }}
        .header h1 {{
            font-size: 2.5rem;
            font-weight: 700;
            margin-bottom: 0.5rem;
        }}
        .header p {{
            font-size: 1.2rem;
            opacity: 0.9;
        }}
        .report-list {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 1.5rem;
            margin: 2rem 0;
        }}
        .report-card {{
            background: white;
            border-radius: 10px;
            padding: 1.5rem;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
            transition: transform 0.3s ease;
            border: 1px solid #e0e0e0;
        }}
        .report-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 8px 24px rgba(0,0,0,0.15);
        }}
        .report-card h3 {{
            color: #1a237e;
            margin-top: 0;
            font-size: 1.4rem;
        }}
        .report-card .meta {{
            color: #757575;
            font-size: 0.9rem;
            margin: 0.5rem 0;
        }}
        .report-card .description {{
            margin: 1rem 0;
            line-height: 1.6;
        }}
        .btn {{
            display: inline-block;
            background: #1a237e;
            color: white;
            padding: 0.5rem 1rem;
            border-radius: 5px;
            text-decoration: none;
            font-weight: 600;
            transition: background 0.3s ease;
        }}
        .btn:hover {{
            background: #283593;
            color: white;
        }}
        .nav-breadcrumb {{
            margin-bottom: 1.5rem;
            font-size: 0.9rem;
        }}
        .nav-breadcrumb a {{
            color: #1a237e;
            text-decoration: none;
        }}
        .nav-breadcrumb a:hover {{
            text-decoration: underline;
        }}
    </style>
</head>
<body>
    <div class="container">
        <!-- 导航 -->
        <div class="nav-breadcrumb">
            <a href="/">首页</a> &gt; <a href="/etf/">ETF专区</a> &gt; 分析报告库
        </div>
        
        <!-- 头部 -->
        <div class="header">
            <h1>📊 ETF分析报告库</h1>
            <p>基于Tushare Pro数据的深度分析报告 | 十五五规划相关性研究</p>
        </div>
        
        <!-- 最新报告 -->
        <h2>最新报告</h2>
        <div class="report-list">
            <div class="report-card">
                <h3>ETF基金分析报告</h3>
                <div class="meta">报告日期: 2026-03-21 | 分析期间: 2026-02-27 至 2026-03-20</div>
                <div class="description">
                    基于158只ETF基金的深度分析，涵盖科技、新能源、医药等成长板块，重点关注与十五五规划高度相关的产业赛道。
                </div>
                <a href="index.html" class="btn">查看完整报告</a>
            </div>
        </div>
        
        <!-- 报告说明 -->
        <div style="margin-top: 3rem; padding: 1.5rem; background: #f5f5f5; border-radius: 8px;">
            <h3>关于本报告库</h3>
            <p><strong>数据来源</strong>: Tushare Pro金融数据库，涵盖A股所有ETF基金</p>
            <p><strong>分析方法</strong>: 基于基金净值计算涨跌幅，按行业分类统计，分析十五五规划相关性</p>
            <p><strong>更新频率</strong>: 每月更新一次，涵盖最新市场数据</p>
            <p><strong>免责声明</strong>: 本报告基于公开数据和分析模型生成，仅供参考，不构成投资建议</p>
        </div>
        
        <!-- 页脚 -->
        <div style="margin-top: 3rem; padding-top: 2rem; border-top: 2px solid #e0e0e0; color: #757575; font-size: 0.9rem; text-align: center;">
            <p><strong>报告生成</strong>: Cheese Intelligence Team · 工程师</p>
            <p><strong>技术支持</strong>: 琥珀引擎 v3.2.7 · Tushare Pro API</p>
            <p>© 2026 琥珀引擎 · 所有数据仅供参考</p>
        </div>
    </div>
</body>
</html>'''
    
    with open(index_path, 'w', encoding='utf-8') as f:
        f.write(index_html)
    
    os.chmod(index_path, 0o644)
    print(f"📁 报告索引页面: {index_path}")

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)