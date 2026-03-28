#!/usr/bin/env python3
"""
创建完全静态的青铜法典页面
绕过所有JavaScript问题
"""

import os
import json
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SEEDS_FILE = os.path.join(BASE_DIR, "etf_50_seeds.json")
STATIC_FILE = os.path.join(BASE_DIR, "web", "bronze_static.html")
TARGET_DIR = "/var/www/gemini_master/bronze_details"

def load_etf_data():
    """加载ETF数据"""
    with open(SEEDS_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data.get("etf_data", [])

def create_static_html(etf_list):
    """创建完全静态的HTML页面"""
    print(f"📊 创建静态页面，共 {len(etf_list)} 支标的")
    
    # 按赛道分组
    sectors = {}
    for etf in etf_list:
        sector = etf["sector"]
        if sector not in sectors:
            sectors[sector] = []
        sectors[sector].append(etf)
    
    # 生成静态HTML
    html = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>青铜法典 · 静态标的列表</title>
    
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: 'Segoe UI', 'Microsoft YaHei', sans-serif;
        }
        
        body {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 30px;
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
            overflow: hidden;
        }
        
        .header {
            background: linear-gradient(90deg, #1a237e 0%, #283593 100%);
            color: white;
            padding: 40px;
            text-align: center;
            border-bottom: 6px solid #3949ab;
        }
        
        .header h1 {
            font-size: 3rem;
            margin-bottom: 15px;
            font-weight: 800;
            letter-spacing: 1px;
        }
        
        .header .subtitle {
            font-size: 1.4rem;
            opacity: 0.9;
            margin-bottom: 10px;
        }
        
        .header .instruction {
            font-size: 1.1rem;
            opacity: 0.8;
            margin-top: 20px;
            max-width: 800px;
            margin-left: auto;
            margin-right: auto;
            line-height: 1.6;
        }
        
        .stats {
            display: flex;
            justify-content: center;
            gap: 40px;
            margin-top: 30px;
            flex-wrap: wrap;
        }
        
        .stat-item {
            background: rgba(255, 255, 255, 0.15);
            padding: 20px 30px;
            border-radius: 15px;
            min-width: 200px;
            text-align: center;
            backdrop-filter: blur(10px);
        }
        
        .stat-value {
            font-size: 2.5rem;
            font-weight: 700;
            margin-bottom: 5px;
        }
        
        .stat-label {
            font-size: 1rem;
            opacity: 0.9;
        }
        
        .content {
            padding: 40px;
        }
        
        .section-title {
            font-size: 2rem;
            color: #1a237e;
            margin-bottom: 30px;
            padding-bottom: 15px;
            border-bottom: 3px solid #3949ab;
            display: flex;
            align-items: center;
            gap: 15px;
        }
        
        .section-title::before {
            content: "📊";
            font-size: 1.8rem;
        }
        
        .sector-section {
            margin-bottom: 40px;
        }
        
        .sector-header {
            font-size: 1.5rem;
            color: #3949ab;
            margin-bottom: 20px;
            padding: 10px 20px;
            background: #e3f2fd;
            border-radius: 10px;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .sector-header::before {
            content: "🏷️";
        }
        
        .etf-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 25px;
            margin-top: 20px;
        }
        
        .etf-card {
            background: white;
            border-radius: 15px;
            padding: 25px;
            box-shadow: 0 5px 20px rgba(0, 0, 0, 0.08);
            border: 2px solid #e0e0e0;
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
        }
        
        .etf-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 15px 30px rgba(0, 0, 0, 0.15);
            border-color: #3949ab;
        }
        
        .etf-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 5px;
            background: linear-gradient(90deg, #1a237e, #3949ab);
        }
        
        .etf-code {
            font-size: 1.8rem;
            font-weight: 700;
            color: #1a237e;
            margin-bottom: 10px;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .etf-code::before {
            content: "🧀";
            font-size: 1.5rem;
        }
        
        .etf-name {
            font-size: 1.2rem;
            color: #333;
            margin-bottom: 15px;
            line-height: 1.4;
        }
        
        .etf-metrics {
            display: flex;
            gap: 15px;
            margin-bottom: 20px;
            flex-wrap: wrap;
        }
        
        .metric {
            background: #f5f5f5;
            padding: 8px 15px;
            border-radius: 8px;
            font-size: 0.9rem;
        }
        
        .metric-label {
            color: #666;
            font-size: 0.8rem;
            margin-bottom: 3px;
        }
        
        .metric-value {
            font-weight: 600;
            color: #1a237e;
        }
        
        .etf-link {
            display: inline-block;
            width: 100%;
            padding: 12px;
            background: #3949ab;
            color: white;
            text-align: center;
            text-decoration: none;
            border-radius: 10px;
            font-weight: 600;
            transition: background 0.3s;
            margin-top: 15px;
        }
        
        .etf-link:hover {
            background: #283593;
        }
        
        .footer {
            background: #f5f5f5;
            padding: 30px 40px;
            text-align: center;
            color: #666;
            border-top: 1px solid #e0e0e0;
        }
        
        .footer p {
            margin-bottom: 10px;
            line-height: 1.6;
        }
        
        .footer strong {
            color: #1a237e;
        }
        
        .toc {
            background: #f8f9fa;
            padding: 25px;
            border-radius: 15px;
            margin-bottom: 30px;
        }
        
        .toc-title {
            font-size: 1.3rem;
            color: #1a237e;
            margin-bottom: 15px;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .toc-title::before {
            content: "📑";
        }
        
        .toc-list {
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
        }
        
        .toc-item {
            background: white;
            padding: 8px 15px;
            border-radius: 8px;
            border: 1px solid #ddd;
        }
        
        .toc-item a {
            color: #3949ab;
            text-decoration: none;
            font-weight: 600;
        }
        
        .toc-item a:hover {
            text-decoration: underline;
        }
        
        @media (max-width: 768px) {
            body {
                padding: 15px;
            }
            
            .header {
                padding: 25px 20px;
            }
            
            .header h1 {
                font-size: 2.2rem;
            }
            
            .content {
                padding: 25px 20px;
            }
            
            .etf-grid {
                grid-template-columns: 1fr;
            }
            
            .stats {
                gap: 20px;
            }
            
            .stat-item {
                min-width: 150px;
                padding: 15px 20px;
            }
            
            .stat-value {
                font-size: 2rem;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🧀 青铜法典 · 静态标的列表</h1>
            <div class="subtitle">基于 [2613-095] 号生产指令 · 完全静态版本</div>
            <div class="instruction">
                本页面展示59支ETF标的的详细分析页面链接。点击任意卡片可查看该标的的净值趋势、数据存证等完整信息。
                <strong>此版本为完全静态HTML，无JavaScript依赖，确保100%可访问。</strong>
            </div>
            
            <div class="stats">
                <div class="stat-item">
                    <div class="stat-value">''' + str(len(etf_list)) + '''</div>
                    <div class="stat-label">标的数量</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value">''' + str(len(sectors)) + '''</div>
                    <div class="stat-label">核心赛道</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value">30</div>
                    <div class="stat-label">交易日数据</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value">10168</div>
                    <div class="stat-label">访问端口</div>
                </div>
            </div>
        </div>
        
        <div class="content">
            <div class="toc">
                <div class="toc-title">快速导航</div>
                <div class="toc-list">'''
    
    # 添加目录
    for sector in sorted(sectors.keys()):
        html += f'''
                    <div class="toc-item">
                        <a href="#sector-{sector}">{sector}</a>
                    </div>'''
    
    html += '''
                </div>
            </div>
            
            <div class="section-title">📈 标的列表（按赛道分组）</div>'''
    
    # 按赛道添加标的
    for sector, sector_etfs in sorted(sectors.items()):
        html += f'''
            <div class="sector-section" id="sector-{sector}">
                <div class="sector-header">{sector} · {len(sector_etfs)} 支标的</div>
                <div class="etf-grid">'''
        
        for etf in sector_etfs:
            html += f'''
                    <div class="etf-card">
                        <div class="etf-code">{etf["code"]}</div>
                        <div class="etf-name">{etf["name"]}</div>
                        
                        <div class="etf-metrics">
                            <div class="metric">
                                <div class="metric-label">逻辑穿透</div>
                                <div class="metric-value">{etf["p_raw"]}</div>
                            </div>
                            <div class="metric">
                                <div class="metric-label">战略稀缺</div>
                                <div class="metric-value">{etf["l_raw"]}</div>
                            </div>
                            <div class="metric">
                                <div class="metric-label">财务稳健</div>
                                <div class="metric-value">{etf["c_raw"]}</div>
                            </div>
                        </div>
                        
                        <a href="bronze_details/{etf["code"]}.html" class="etf-link">查看详情 →</a>
                    </div>'''
        
        html += '''
                </div>
            </div>'''
    
    html += f'''
        </div>
        
        <div class="footer">
            <p><strong>生产指令</strong>: [2613-095] 全量生产指令灌注 · 50支标的静态化全量产出</p>
            <p><strong>原型布局</strong>: [2613-094] 号逻辑布局（身份区、趋势区、存证表）</p>
            <p><strong>数据源</strong>: Tushare Pro fund_nav接口 · 单位净值(unit_nav)字段</p>
            <p><strong>生成时间</strong>: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")} · <strong>执行人</strong>: 工程师 Cheese</p>
            <p><strong>版本说明</strong>: 完全静态HTML版本 · 无JavaScript依赖 · 确保100%可访问</p>
            <p><strong>访问地址</strong>: https://gemini.googlemanager.cn:10168/bronze_details/bronze_static.html</p>
        </div>
    </div>
</body>
</html>'''
    
    # 保存文件
    with open(STATIC_FILE, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"✅ 静态页面创建完成: {STATIC_FILE}")
    return STATIC_FILE

def deploy_static_version():
    """部署静态版本到Web服务器"""
    print("🚀 部署静态版本到Web服务器...")
    
    # 复制文件
    os.system(f"sudo cp {STATIC_FILE} {TARGET_DIR}/")
    os.system(f"sudo chown www-data:www-data {TARGET_DIR}/bronze_static.html")
    
    # 创建符号链接到master-audit
    symlink = "/var/www/gemini_master/master-audit/bronze_static.html"
    if os.path.exists(symlink):
        os.system(f"sudo rm {symlink}")
    os.system(f"sudo ln -s {TARGET_DIR}/bronze_static.html {symlink}")
    
    print(f"✅ 部署到: {TARGET_DIR}/bronze_static.html")
    print(f"✅ 符号链接: {symlink}")

def test_access():
    """测试访问"""
    print("🔗 测试访问...")
    
    import subprocess
    
    # 测试静态页面
    result = subprocess.run(
        ['curl', '-k', '-s', '-o', '/dev/null', '-w', '%{http_code}', 
         'https://localhost:10168/bronze_details/bronze_static.html'],
        capture_output=True,
        text=True
    )
    
    if result.stdout.strip() == '200':
        print("✅ 静态页面HTTP 200正常")
        
        # 检查内容
        result2 = subprocess.run(
            ['curl', '-k', '-s', 'https://localhost:10168/bronze_details/bronze_static.html'],
            capture_output=True,
            text=True
        )
        
        if '青铜法典 · 静态标的列表' in result2.stdout:
            print("✅ 静态页面标题正确")
        
        # 检查ETF数量
        etf_count = result2.stdout.count('etf-card')
        print(f"✅ 静态页面包含 {etf_count} 张ETF卡片")
        
        return True
    else:
        print(f"❌ 静态页面HTTP错误: {result.stdout}")
        return False

def main():
    """主函数"""
    print("=" * 60)
    print("🔄 创建完全静态青铜法典页面")
    print("   绕过JavaScript问题，确保100%可访问")
    print("=" * 60)
    
    # 加载数据
    etf_list = load_etf_data()
    if not etf_list:
        print("❌ 无法加载ETF数据")
        return
    
    print(f"📋 加载 {len(etf_list)} 支ETF数据")
    
    # 创建静态页面
    static_file = create_static_html(etf_list)
    
    # 部署
    deploy_static_version()
    
    # 测试
    if test_access():
        print("\n✅ 静态版本创建成功！")
        print("🌐 访问地址:")
        print("   1. https://gemini.googlemanager.cn:10168/bronze_details/bronze_static.html")
        print("   2. https://gemini.googlemanager.cn:10168/master-audit/bronze_static.html")
        print("\n📋 版本特性:")
        print("   • 完全静态HTML，无JavaScript依赖")
        print("   • 按赛道分组显示59支标的")
        print("   • 包含原始评分数据")
        print("   •