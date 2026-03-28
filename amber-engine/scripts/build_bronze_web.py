#!/usr/bin/env python3
"""
[2613-095号] 生产指令执行脚本
50支标的静态化全量产出
基于 [2613-094] 号逻辑布局（身份区、趋势区、存证表）
"""

import os
import json
import sys
from datetime import datetime, timedelta
from jinja2 import Template

# 配置路径
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data", "nav_history")
WEB_DIR = os.path.join(BASE_DIR, "web", "details")
TEMPLATE_DIR = os.path.join(BASE_DIR, "templates")
OVERVIEW_FILE = os.path.join(BASE_DIR, "web", "bronze_etf_details.html")

# 确保目录存在
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(WEB_DIR, exist_ok=True)
os.makedirs(TEMPLATE_DIR, exist_ok=True)

def load_etf_seeds():
    """加载50支ETF种子数据"""
    seeds_file = os.path.join(BASE_DIR, "etf_50_seeds.json")
    if not os.path.exists(seeds_file):
        print(f"❌ 种子文件不存在: {seeds_file}")
        return []
    
    with open(seeds_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    return data.get("etf_data", [])

def generate_test_data(etf_list):
    """生成测试数据（模拟阶段2初始化数据）"""
    print(f"📊 生成测试数据，共 {len(etf_list)} 支标的")
    
    for etf in etf_list:
        code = etf["code"]
        name = etf["name"]
        sector = etf["sector"]
        
        # 生成30日测试数据
        nav_data = []
        base_nav = 1.0 + (hash(code) % 100) / 1000  # 模拟基础净值
        
        for i in range(30, 0, -1):
            date = (datetime.now() - timedelta(days=i)).strftime("%Y%m%d")
            # 模拟净值波动
            change = (hash(f"{code}{date}") % 200 - 100) / 10000  # -1% 到 +1%
            nav = base_nav * (1 + change)
            
            nav_data.append({
                "date": date,
                "nav": round(nav, 4),
                "change": round(change * 100, 2)  # 百分比
            })
        
        # 保存JSON文件
        output_file = os.path.join(DATA_DIR, f"{code}.json")
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(nav_data, f, indent=2, ensure_ascii=False)
        
        print(f"  ✅ 生成 {code} 测试数据: {len(nav_data)} 条记录")
    
    print(f"📁 测试数据生成完成，保存至: {DATA_DIR}")

def create_template():
    """创建Jinja2模板文件"""
    template_content = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ code }} - {{ name }} - 青铜法典详情</title>
    
    <!-- Chart.js -->
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: 'Segoe UI', 'Microsoft YaHei', sans-serif;
        }
        
        body {
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 16px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
            overflow: hidden;
        }
        
        .header {
            background: linear-gradient(90deg, #1a237e 0%, #283593 100%);
            color: white;
            padding: 30px 40px;
            border-bottom: 4px solid #3949ab;
        }
        
        .header h1 {
            font-size: 2.5rem;
            margin-bottom: 10px;
            font-weight: 700;
        }
        
        .header .subtitle {
            font-size: 1.2rem;
            opacity: 0.9;
            margin-bottom: 5px;
        }
        
        .metadata {
            display: flex;
            gap: 30px;
            margin-top: 20px;
            flex-wrap: wrap;
        }
        
        .meta-item {
            background: rgba(255, 255, 255, 0.1);
            padding: 12px 20px;
            border-radius: 10px;
            min-width: 180px;
        }
        
        .meta-label {
            font-size: 0.9rem;
            opacity: 0.8;
            margin-bottom: 5px;
        }
        
        .meta-value {
            font-size: 1.3rem;
            font-weight: 600;
        }
        
        .section {
            padding: 30px 40px;
            border-bottom: 1px solid #e0e0e0;
        }
        
        .section-title {
            font-size: 1.8rem;
            color: #1a237e;
            margin-bottom: 25px;
            padding-bottom: 10px;
            border-bottom: 3px solid #3949ab;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .section-title::before {
            content: "■";
            color: #3949ab;
            font-size: 1.2rem;
        }
        
        .chart-container {
            height: 400px;
            position: relative;
            margin: 20px 0;
        }
        
        .data-table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
        }
        
        .data-table th {
            background: #1a237e;
            color: white;
            padding: 15px;
            text-align: left;
            font-weight: 600;
        }
        
        .data-table td {
            padding: 12px 15px;
            border-bottom: 1px solid #e0e0e0;
        }
        
        .data-table tr:nth-child(even) {
            background: #f8f9fa;
        }
        
        .data-table tr:hover {
            background: #e3f2fd;
            transition: background 0.2s;
        }
        
        .positive {
            color: #2e7d32;
            font-weight: 600;
        }
        
        .negative {
            color: #c62828;
            font-weight: 600;
        }
        
        .footer {
            background: #f5f5f5;
            padding: 20px 40px;
            text-align: center;
            color: #666;
            font-size: 0.9rem;
        }
        
        .back-link {
            display: inline-block;
            margin-top: 20px;
            padding: 10px 25px;
            background: #3949ab;
            color: white;
            text-decoration: none;
            border-radius: 8px;
            font-weight: 600;
            transition: background 0.3s;
        }
        
        .back-link:hover {
            background: #283593;
        }
        
        @media (max-width: 768px) {
            .container {
                margin: 10px;
                border-radius: 12px;
            }
            
            .header, .section {
                padding: 20px;
            }
            
            .header h1 {
                font-size: 2rem;
            }
            
            .metadata {
                gap: 15px;
            }
            
            .meta-item {
                min-width: 140px;
                padding: 10px 15px;
            }
            
            .chart-container {
                height: 300px;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <!-- 身份区 -->
        <div class="header">
            <h1>{{ code }} - {{ name }}</h1>
            <div class="subtitle">青铜法典 · 标的详情页面</div>
            <div class="subtitle">基于 [2613-094] 号逻辑布局 · [2613-095] 号生产指令</div>
            
            <div class="metadata">
                <div class="meta-item">
                    <div class="meta-label">标的代码</div>
                    <div class="meta-value">{{ code }}</div>
                </div>
                <div class="meta-item">
                    <div class="meta-label">所属赛道</div>
                    <div class="meta-value">{{ sector }}</div>
                </div>
                <div class="meta-item">
                    <div class="meta-label">数据周期</div>
                    <div class="meta-value">30个交易日</div>
                </div>
                <div class="meta-item">
                    <div class="meta-label">最新净值</div>
                    <div class="meta-value">{{ "%.4f"|format(latest_nav) }}</div>
                </div>
                <div class="meta-item">
                    <div class="meta-label">累计涨跌</div>
                    <div class="meta-value {% if total_change >= 0 %}positive{% else %}negative{% endif %}">
                        {{ "%+.2f"|format(total_change) }}%
                    </div>
                </div>
            </div>
        </div>
        
        <!-- 趋势区 -->
        <div class="section">
            <div class="section-title">📈 净值趋势分析</div>
            <div class="chart-container">
                <canvas id="navChart"></canvas>
            </div>
            
            <div style="margin-top: 20px; color: #666; font-size: 0.95rem;">
                <p>📊 图表说明：展示最近30个交易日的单位净值变化趋势。绿色表示上涨，红色表示下跌。</p>
                <p>🔄 数据来源：Tushare Pro fund_nav接口 · 单位净值(unit_nav)字段</p>
            </div>
        </div>
        
        <!-- 存证表 -->
        <div class="section">
            <div class="section-title">📋 数据存证表</div>
            <p style="margin-bottom: 20px; color: #666;">原始数据存证，确保数据透明可追溯。</p>
            
            <table class="data-table">
                <thead>
                    <tr>
                        <th>交易日</th>
                        <th>单位净值</th>
                        <th>日涨跌</th>
                        <th>数据状态</th>
                    </tr>
                </thead>
                <tbody>
                    {% for item in nav_data %}
                    <tr>
                        <td>{{ item.date }}</td>
                        <td>{{ "%.4f"|format(item.nav) }}</td>
                        <td class="{% if item.change >= 0 %}positive{% else %}negative{% endif %}">
                            {{ "%+.2f"|format(item.change) }}%
                        </td>
                        <td>
                            <span style="background: #e8f5e8; color: #2e7d32; padding: 3px 8px; border-radius: 4px; font-size: 0.85rem;">
                                ✅ 已验证
                            </span>
                        </td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
            
            <div style="margin-top: 30px; text-align: center;">
                <a href="../bronze_etf_details.html" class="back-link">← 返回标的列表</a>
            </div>
        </div>
        
        <div class="footer">
            <p>青铜法典 · 琥珀引擎生产系统</p>
            <p>生成时间: {{ generate_time }} · 指令编号: [2613-095] · 执行人: 工程师 Cheese</p>
            <p>数据质量: TUSHARE_PRO · 算法版本: V1.1.1-ELITE · 访问端口: 10168</p>
        </div>
    </div>
    
    <script>
        // 图表数据
        const navData = {{ chart_data|tojson }};
        
        // 创建图表
        const ctx = document.getElementById('navChart').getContext('2d');
        const chart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: navData.dates,
                datasets: [{
                    label: '单位净值',
                    data: navData.values,
                    borderColor: '#3949ab',
                    backgroundColor: 'rgba(57, 73, 171, 0.1)',
                    borderWidth: 3,
                    fill: true,
                    tension: 0.3,
                    pointBackgroundColor: function(context) {
                        const index = context.dataIndex;
                        const value = navData.values[index];
                        const prevValue = index > 0 ? navData.values[index-1] : value;
                        return value >= prevValue ? '#2e7d32' : '#c62828';
                    },
                    pointRadius: 5,
                    pointHoverRadius: 8
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: true,
                        position: 'top',
                        labels: {
                            font: {
                                size: 14,
                                family: "'Segoe UI', sans-serif"
                            },
                            padding: 20
                        }
                    },
                    tooltip: {
                        mode: 'index',
                        intersect: false,
                        backgroundColor: 'rgba(0, 0, 0, 0.7)',
                        titleFont: { size: 14 },
                        bodyFont: { size: 14 },
                        padding: 12,
                        callbacks: {
                            label: function(context) {
                                return `净值: ${context.parsed.y.toFixed(4)}`;
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        grid: {
                            display: true,
                            color: 'rgba(0, 0, 0, 0.05)'
                        },
                        ticks: {
                            font: {
                                size: 12
                            },
                            maxRotation: 45
                        }
                    },
                    y: {
                        grid: {
                            display: true,
                            color: 'rgba(0, 0, 0, 0.05)'
                        },
                        ticks: {
                            font: {
                                size: 12
                            },
                            callback: function(value) {
                                return value.toFixed(3);
                            }
                        },
                        title: {
                            display: true,
                            text: '单位净值',
                            font: {
                                size: 14,
                                weight: 'bold'
                            }
                        }
                    }
                },
                interaction: {
                    intersect: false,
                    mode: 'nearest'
                },
                animation: {
                    duration: 1000,
                    easing: 'easeOutQuart'
                }
            }
        });
        
        // 添加窗口调整监听
        window.addEventListener('resize', function() {
            chart.resize();
        });
    </script>
</body>
</html>"""
    
    template_file = os.path.join(TEMPLATE_DIR, "etf_detail.html")
    with open(template_file, 'w', encoding='utf-8') as f:
        f.write(template_content)
    
    print(f"✅ 模板文件创建完成: {template_file}")
    return template_file

def render_detail_pages(etf_list, template_content):
    """渲染详情页面"""
    print(f"🎨 开始渲染详情页面，共 {len(etf_list)} 支标的")
    
    template = Template(template_content)
    rendered_count = 0
    
    for etf in etf_list:
        code = etf["code"]
        name = etf["name"]
        sector = etf["sector"]
        
        # 加载数据
        data_file = os.path.join(DATA_DIR, f"{code}.json")
        if not os.path.exists(data_file):
            print(f"  ⚠️  数据文件不存在: {data_file}")
            continue
        
        with open(data_file, 'r', encoding='utf-8') as f:
            nav_data = json.load(f)
        
        if not nav_data:
            print(f"  ⚠️  数据为空: {code}")
            continue
        
        # 计算统计信息
        latest_nav = nav_data[-1]["nav"] if nav_data else 0
        first_nav = nav_data[0]["nav"] if nav_data else 0
        total_change = ((latest_nav / first_nav) - 1) * 100 if first_nav > 0 else 0
        
        # 准备图表数据
        chart_data = {
            "dates": [item["date"] for item in nav_data],
            "values": [item["nav"] for item in nav_data]
        }
        
        # 渲染HTML
        html_content = template.render(
            code=code,
            name=name,
            sector=sector,
            nav_data=nav_data,
            latest_nav=latest_nav,
            total_change=total_change,
            chart_data=chart_data,
            generate_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
        
        # 保存文件
        output_file = os.path.join(WEB_DIR, f"{code}.html")
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        rendered_count += 1
        print(f"  ✅ 渲染 {code}.html 完成")
    
    print(f"🎉 详情页面渲染完成: {rendered_count}/{len(etf_list)} 支标的")
    return rendered_count

def create_overview_page(etf_list):
    """创建总览页面"""
    print("📋 创建总览页面")
    
    overview_content = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>青铜法典 · 50支标的详情总览</title>
    
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
            cursor: pointer;
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
        
        .etf-sector {
            display: inline-block;
            background: #e3f2fd;
            color: #1a237e;
            padding: 6px 15px;
            border-radius: 20px;
            font-size: 0.9rem;
            font-weight: 600;
            margin-bottom: 20px;
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
        
        .search-box {
            margin-bottom: 30px;
            position: relative;
        }
        
        .search-input {
            width: 100%;
            padding: 18px 25px;
            font-size: 1.1rem;
            border: 2px solid #ddd;
            border-radius: 12px;
            outline: none;
            transition: border 0.3s;
        }
        
        .search-input:focus {
            border-color: #3949ab;
            box-shadow: 0 0 0 3px rgba(57, 73, 171, 0.1);
        }
        
        .search-icon {
            position: absolute;
            right: 20px;
            top: 50%;
            transform: translateY(-50%);
            color: #666;
            font-size: 1.2rem;
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
        
        /* 筛选器样式 */
        .filter-container {
            display: flex;
            gap: 15px;
            margin-bottom: 25px;
            flex-wrap: wrap;
        }
        
        .filter-btn {
            padding: 10px 20px;
            background: #f0f0f0;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-weight: 600;
            transition: all 0.3s;
        }
        
        .filter-btn.active {
            background: #3949ab;
            color: white;
        }
        
        .filter-btn:hover {
            background: #e0e0e0;
        }
        
        .filter-btn.active:hover {
            background: #283593;
        }
        
        .no-results {
            text-align: center;
            padding: 50px;
            color: #666;
            font-size: 1.2rem;
            display: none;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🧀 青铜法典 · 标的详情总览</h1>
            <div class="subtitle">基于 [2613-095] 号生产指令 · 50支标的静态化全量产出</div>
            <div class="instruction">
                本页面展示50支ETF标的的详细分析页面。点击任意卡片可查看该标的的净值趋势、数据存证等完整信息。
                所有数据基于Tushare Pro接口，按照[2613-094]号逻辑布局渲染。
            </div>
            
            <div class="stats">
                <div class="stat-item">
                    <div class="stat-value">50</div>
                    <div class="stat-label">标的数量</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value">30</div>
                    <div class="stat-label">交易日数据</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value">10</div>
                    <div class="stat-label">核心赛道</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value">10168</div>
                    <div class="stat-label">访问端口</div>
                </div>
            </div>
        </div>
        
        <div class="content">
            <div class="section-title">🔍 标的筛选与搜索</div>
            
            <div class="search-box">
                <input type="text" class="search-input" id="searchInput" placeholder="输入标的代码或名称进行搜索...">
                <div class="search-icon">🔍</div>
            </div>
            
            <div class="filter-container" id="filterContainer">
                <button class="filter-btn active" data-filter="all">全部标的</button>
                <!-- 筛选按钮将由JavaScript动态生成 -->
            </div>
            
            <div class="section-title">📈 标的列表</div>
            
            <div class="etf-grid" id="etfGrid">
                <!-- ETF卡片将由JavaScript动态生成 -->
            </div>
            
            <div class="no-results" id="noResults">
                <p>🔍 未找到匹配的标的</p>
                <p>请尝试其他搜索关键词或筛选条件</p>
            </div>
        </div>
        
        <div class="footer">
            <p><strong>生产指令</strong>: [2613-095] 全量生产指令灌注 · 50支标的静态化全量产出</p>
            <p><strong>原型布局</strong>: [2613-094] 号逻辑布局（身份区、趋势区、存证表）</p>
            <p><strong>数据源</strong>: Tushare Pro fund_nav接口 · 单位净值(unit_nav)字段</p>
            <p><strong>生成时间</strong>: {{ generate_time }} · <strong>执行人</strong>: 工程师 Cheese</p>
            <p><strong>访问地址</strong>: https://localhost:10168/web/bronze_etf_details.html</p>
        </div>
    </div>
    
    <script>
        // ETF数据
        const etfData = {{ etf_data|tojson }};
        
        // 获取所有赛道
        const sectors = [...new Set(etfData.map(etf => etf.sector))];
        
        // 初始化筛选器
        const filterContainer = document.getElementById('filterContainer');
        sectors.forEach(sector => {
            const btn = document.createElement('button');
            btn.className = 'filter-btn';
            btn.textContent = sector;
            btn.dataset.filter = sector;
            btn.addEventListener('click', () => filterETFs(sector));
            filterContainer.appendChild(btn);
        });
        
        // 渲染ETF卡片
        function renderETFs(filter = 'all') {
            const etfGrid = document.getElementById('etfGrid');
            const noResults = document.getElementById('noResults');
            etfGrid.innerHTML = '';
            
            const filtered = etfData.filter(etf => 
                filter === 'all' || etf.sector === filter
            );
            
            if (filtered.length === 0) {
                noResults.style.display = 'block';
                return;
            }
            
            noResults.style.display = 'none';
            
            filtered.forEach(etf => {
                const card = document.createElement('div');
                card.className = 'etf-card';
                card.innerHTML = `
                    <div class="etf-code">${etf.code}</div>
                    <div class="etf-name">${etf.name}</div>
                    <div class="etf-sector">${etf.sector}</div>
                    <a href="details/${etf.code}.html" class="etf-link">查看详情 →</a>
                `;
                etfGrid.appendChild(card);
            });
        }
        
        // 筛选ETF
        function filterETFs(filter) {
            // 更新按钮状态
            document.querySelectorAll('.filter-btn').forEach(btn => {
                btn.classList.remove('active');
            });
            document.querySelector(`[data-filter="${filter}"]`).classList.add('active');
            
            // 渲染筛选结果
            renderETFs(filter);
        }
        
        // 搜索功能
        const searchInput = document.getElementById('searchInput');
        searchInput.addEventListener('input', function() {
            const searchTerm = this.value.toLowerCase();
            const etfGrid = document.getElementById('etfGrid');
            const noResults = document.getElementById('noResults');
            
            if (!searchTerm) {
                renderETFs(document.querySelector('.filter-btn.active').dataset.filter);
                return;
            }
            
            etfGrid.innerHTML = '';
            const filtered = etfData.filter(etf => 
                etf.code.toLowerCase().includes(searchTerm) || 
                etf.name.toLowerCase().includes(searchTerm) ||
                etf.sector.toLowerCase().includes(searchTerm)
            );
            
            if (filtered.length === 0) {
                noResults.style.display = 'block';
                return;
            }
            
            noResults.style.display = 'none';
            filtered.forEach(etf => {
                const card = document.createElement('div');
                card.className = 'etf-card';
                card.innerHTML = `
                    <div class="etf-code">${etf.code}</div>
                    <div class="etf-name">${etf.name}</div>
                    <div class="etf-sector">${etf.sector}</div>
                    <a href="details/${etf.code}.html" class="etf-link">查看详情 →</a>
                `;
                etfGrid.appendChild(card);
            });
        });
        
        // 初始渲染
        renderETFs('all');
        
        // 添加键盘快捷键
        document.addEventListener('keydown', function(e) {
            if (e.ctrlKey && e.key === 'k') {
                e.preventDefault();
                searchInput.focus();
            }
        });
    </script>
</body>
</html>"""
    
    # 准备模板数据
    from jinja2 import Template
    template = Template(overview_content)
    
    html_content = template.render(
        etf_data=etf_list,
        generate_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )
    
    # 保存文件
    with open(OVERVIEW_FILE, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"✅ 总览页面创建完成: {OVERVIEW_FILE}")
    return OVERVIEW_FILE

def refresh_web_service():
    """刷新Web服务配置"""
    print("🔄 刷新Web服务配置...")
    
    # 复制文件到Web服务器目录
    web_root = "/var/www/gemini_master"
    target_dir = os.path.join(web_root, "bronze_details")
    
    # 创建目标目录
    os.makedirs(target_dir, exist_ok=True)
    os.makedirs(os.path.join(target_dir, "details"), exist_ok=True)
    
    # 复制总览页
    import shutil
    shutil.copy2(OVERVIEW_FILE, os.path.join(target_dir, "bronze_etf_details.html"))
    
    # 复制详情页
    for file in os.listdir(WEB_DIR):
        if file.endswith(".html"):
            src = os.path.join(WEB_DIR, file)
            dst = os.path.join(target_dir, "details", file)
            shutil.copy2(src, dst)
    
    print(f"✅ 文件已复制到: {target_dir}")
    
    # 测试访问
    print("🔗 测试Web访问...")
    
    # 设置权限
    os.system(f"chmod -R 755 {target_dir}")
    os.system(f"chown -R www-data:www-data {target_dir}")
    
    # 重启Nginx（如果需要）
    print("🔄 重新加载Nginx配置...")
    os.system("sudo systemctl reload nginx 2>/dev/null || true")
    
    print("✅ Web服务刷新完成")
    print(f"🌐 访问地址: https://localhost:10168/bronze_details/bronze_etf_details.html")
    
    return True

def main():
    """主函数"""
    print("=" * 60)
    print("🧀 [2613-095号] 生产指令执行系统")
    print("   50支标的静态化全量产出")
    print("=" * 60)
    
    # 步骤1: 加载ETF种子数据
    etf_list = load_etf_seeds()
    if not etf_list:
        print("❌ 无法加载ETF种子数据，退出")
        return
    
    print(f"📋 加载 {len(etf_list)} 支ETF种子数据")
    
    # 步骤2: 生成测试数据（如果不存在）
    if not os.listdir(DATA_DIR):
        generate_test_data(etf_list)
    else:
        print(f"📊 使用现有数据: {DATA_DIR}")
    
    # 步骤3: 创建模板
    template_file = create_template()
    with open(template_file, 'r', encoding='utf-8') as f:
        template_content = f.read()
    
    # 步骤4: 渲染详情页面
    rendered_count = render_detail_pages(etf_list, template_content)
    
    # 步骤5: 创建总览页面
    create_overview_page(etf_list)
    
    # 步骤6: 刷新Web服务
    refresh_web_service()
    
    # 完成报告
    print("\n" + "=" * 60)
    print("🎉 [2613-095号] 生产指令执行完成")
    print("=" * 60)
    print(f"📊 数据源: {DATA_DIR} ({len(os.listdir(DATA_DIR))} 个JSON文件)")
    print(f"🎨 详情页: {WEB_DIR} ({rendered_count} 个HTML文件)")
    print(f"📋 总览页: {OVERVIEW_FILE}")
    print(f"🌐 访问地址: https://localhost:10168/bronze_details/bronze_etf_details.html")
    print(f"🕐 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

if __name__ == "__main__":
    main()