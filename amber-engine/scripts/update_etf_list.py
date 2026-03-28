#!/usr/bin/env python3
"""
更新ETF列表页面，添加排序功能和净值日期显示
"""

import os
from datetime import datetime, timedelta

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR = os.path.join(BASE_DIR, "output")

def update_etf_list():
    """更新ETF列表页面"""
    print("更新ETF列表页面...")
    
    # ETF数据（带日期信息）
    etfs = [
        {
            "symbol": "510300",
            "name": "沪深300ETF",
            "industry": "宽基指数",
            "net_value": 3.842,
            "nav_date": "2026-03-18",  # 净值日期
            "daily_change": 0.54,
            "rich_score": 9.0,
            "volume": 125.6,
            "aum": 850.2
        },
        {
            "symbol": "510500",
            "name": "中证500ETF",
            "industry": "宽基指数",
            "net_value": 5.732,
            "nav_date": "2026-03-18",
            "daily_change": 0.32,
            "rich_score": 8.6,
            "volume": 45.3,
            "aum": 420.8
        },
        {
            "symbol": "159915",
            "name": "创业板ETF",
            "industry": "宽基指数",
            "net_value": 2.156,
            "nav_date": "2026-03-18",
            "daily_change": 1.25,
            "rich_score": 9.2,
            "volume": 38.7,
            "aum": 280.5
        },
        {
            "symbol": "512760",
            "name": "芯片ETF",
            "industry": "半导体",
            "net_value": 1.045,
            "nav_date": "2026-03-18",
            "daily_change": 2.15,
            "rich_score": 9.4,
            "volume": 12.8,
            "aum": 95.3
        },
        {
            "symbol": "512880",
            "name": "证券ETF",
            "industry": "金融",
            "net_value": 0.932,
            "nav_date": "2026-03-18",
            "daily_change": 0.85,
            "rich_score": 8.1,
            "volume": 18.9,
            "aum": 320.7
        },
        {
            "symbol": "510050",
            "name": "上证50ETF",
            "industry": "宽基指数",
            "net_value": 2.654,
            "nav_date": "2026-03-18",
            "daily_change": 0.42,
            "rich_score": 8.3,
            "volume": 65.4,
            "aum": 520.1
        },
        {
            "symbol": "512480",
            "name": "半导体ETF",
            "industry": "半导体",
            "net_value": 0.875,
            "nav_date": "2026-03-18",
            "daily_change": 1.85,
            "rich_score": 8.6,
            "volume": 8.9,
            "aum": 78.9
        },
        {
            "symbol": "512000",
            "name": "券商ETF",
            "industry": "金融",
            "net_value": 0.912,
            "nav_date": "2026-03-18",
            "daily_change": 0.92,
            "rich_score": 7.9,
            "volume": 15.2,
            "aum": 210.5
        },
        {
            "symbol": "510880",
            "name": "红利ETF",
            "industry": "红利策略",
            "net_value": 3.125,
            "nav_date": "2026-03-18",
            "daily_change": 0.28,
            "rich_score": 8.1,
            "volume": 22.5,
            "aum": 150.8
        },
        {
            "symbol": "512010",
            "name": "医药ETF",
            "industry": "医药",
            "net_value": 1.234,
            "nav_date": "2026-03-18",
            "daily_change": 0.65,
            "rich_score": 8.4,
            "volume": 9.8,
            "aum": 98.7
        }
    ]
    
    # 生成带排序功能的HTML
    html = generate_etf_list_html(etfs)
    
    # 保存页面
    etf_index_path = os.path.join(OUTPUT_DIR, "etf", "index.html")
    with open(etf_index_path, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"✅ ETF列表页面更新完成: {etf_index_path}")
    
    # 同时更新首页的ETF推荐部分
    update_homepage_etf_section(etfs[:6])
    
    return etf_index_path

def generate_etf_list_html(etfs):
    """生成带排序功能的ETF列表HTML"""
    
    # 生成ETF数据JSON（供JavaScript排序使用）
    etf_json = []
    for etf in etfs:
        etf_json.append({
            "symbol": etf["symbol"],
            "name": etf["name"],
            "industry": etf["industry"],
            "net_value": etf["net_value"],
            "nav_date": etf["nav_date"],
            "daily_change": etf["daily_change"],
            "rich_score": etf["rich_score"],
            "volume": etf["volume"],
            "aum": etf["aum"]
        })
    
    # 生成表格行HTML
    table_rows = ""
    for etf in etfs:
        change_class = "price-up" if etf["daily_change"] > 0 else "price-down"
        change_sign = "+" if etf["daily_change"] > 0 else ""
        
        table_rows += f'''
                <tr data-symbol="{etf["symbol"]}" 
                    data-name="{etf["name"]}" 
                    data-industry="{etf["industry"]}"
                    data-net_value="{etf["net_value"]}"
                    data-nav_date="{etf["nav_date"]}"
                    data-daily_change="{etf["daily_change"]}"
                    data-rich_score="{etf["rich_score"]}"
                    data-volume="{etf["volume"]}"
                    data-aum="{etf["aum"]}">
                    <td>{etf["name"]}</td>
                    <td>{etf["symbol"]}</td>
                    <td>{etf["industry"]}</td>
                    <td class="nav-cell">{etf["net_value"]:.3f} <span class="nav-date">({etf["nav_date"]})</span></td>
                    <td class="{change_class}">{change_sign}{etf["daily_change"]:.2f}%</td>
                    <td>{etf["rich_score"]}</td>
                    <td>{etf["volume"]:.1f}亿</td>
                    <td><a href="/etf/{etf["symbol"]}.html">查看详情</a></td>
                </tr>
        '''
    
    html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ETF专区 - 琥珀引擎</title>
    <link rel="stylesheet" href="/static/css/amber-v2.2.min.css">
    <style>
        /* 排序功能样式 */
        .sortable-header {{
            cursor: pointer;
            position: relative;
            padding-right: 20px;
            user-select: none;
        }}
        
        .sortable-header:hover {{
            background-color: rgba(0, 0, 0, 0.05);
        }}
        
        .sortable-header::after {{
            content: "↕";
            position: absolute;
            right: 5px;
            color: #666;
            font-size: 0.9em;
        }}
        
        .sortable-header.asc::after {{
            content: "↑";
            color: #4caf50;
        }}
        
        .sortable-header.desc::after {{
            content: "↓";
            color: #f44336;
        }}
        
        /* 净值日期样式 */
        .nav-date {{
            font-size: 0.8em;
            color: #666;
            margin-left: 5px;
        }}
        
        /* 表格响应式 */
        @media (max-width: 768px) {{
            .nav-date {{
                display: block;
                margin-left: 0;
                margin-top: 2px;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <header class="site-header">
            <h1>ETF专区</h1>
            <p>交易所交易基金 - 支持多维度排序</p>
        </header>
        
        <div class="mt-4">
            <a href="/" class="source-tag">返回首页</a>
            <span class="ml-3">数据更新时间: {datetime.now().strftime("%Y-%m-%d %H:%M")} (北京时间)</span>
        </div>
        
        <h2 class="section-title mt-5">📊 ETF列表 (支持点击表头排序)</h2>
        <p class="mb-4">点击表头可进行升序/降序排序，支持多维度数据比较</p>
        
        <table class="price-table" id="etf-table">
            <thead>
                <tr>
                    <th class="sortable-header" data-sort="name">ETF名称</th>
                    <th class="sortable-header" data-sort="symbol">代码</th>
                    <th class="sortable-header" data-sort="industry">行业</th>
                    <th class="sortable-header" data-sort="net_value">最新净值</th>
                    <th class="sortable-header" data-sort="daily_change">日涨跌幅</th>
                    <th class="sortable-header" data-sort="rich_score">RICH评分</th>
                    <th class="sortable-header" data-sort="volume">成交额(亿)</th>
                    <th>操作</th>
                </tr>
            </thead>
            <tbody id="etf-table-body">
                {table_rows}
            </tbody>
        </table>
        
        <div class="mt-4">
            <h4>排序说明</h4>
            <div class="grid-3">
                <div class="point-card">
                    <h5>净值排序</h5>
                    <p>点击"最新净值"表头，按净值从高到低或从低到高排序</p>
                </div>
                <div class="point-card">
                    <h5>涨跌幅排序</h5>
                    <p>点击"日涨跌幅"表头，查看表现最佳/最差的ETF</p>
                </div>
                <div class="point-card">
                    <h5>评分排序</h5>
                    <p>点击"RICH评分"表头，按投资价值排序</p>
                </div>
            </div>
        </div>
        
        <div class="text-center mt-5">
            <a href="/" class="source-tag p-3">返回首页</a>
        </div>
    </div>
    
    <footer class="site-footer">
        <div class="container text-center">
            <p>© 2026 Cheese Intelligence Team | ETF数据来源: 模拟数据</p>
            <p>净值日期: {datetime.now().strftime("%Y年%m月%d日")} (北京时间)</p>
        </div>
    </footer>
    
    <script>
        // ETF数据
        const etfData = {str(etf_json).replace("'", '"')};
        
        // 排序功能
        document.addEventListener('DOMContentLoaded', function() {{
            const headers = document.querySelectorAll('.sortable-header');
            const tableBody = document.getElementById('etf-table-body');
            
            let currentSort = {{
                column: 'rich_score',
                direction: 'desc'
            }};
            
            // 初始排序
            sortTable(currentSort.column, currentSort.direction);
            
            headers.forEach(header => {{
                header.addEventListener('click', function() {{
                    const column = this.dataset.sort;
                    
                    // 切换排序方向
                    if (currentSort.column === column) {{
                        currentSort.direction = currentSort.direction === 'asc' ? 'desc' : 'asc';
                    }} else {{
                        currentSort.column = column;
                        currentSort.direction = 'desc';
                    }}
                    
                    // 更新表头样式
                    headers.forEach(h => {{
                        h.classList.remove('asc', 'desc');
                        if (h.dataset.sort === currentSort.column) {{
                            h.classList.add(currentSort.direction);
                        }}
                    }});
                    
                    // 执行排序
                    sortTable(currentSort.column, currentSort.direction);
                }});
            }});
            
            function sortTable(column, direction) {{
                const rows = Array.from(tableBody.querySelectorAll('tr'));
                
                rows.sort((a, b) => {{
                    let aValue, bValue;
                    
                    if (column === 'name' || column === 'symbol' || column === 'industry') {{
                        aValue = a.dataset[column];
                        bValue = b.dataset[column];
                        return direction === 'asc' 
                            ? aValue.localeCompare(bValue)
                            : bValue.localeCompare(aValue);
                    }} else {{
                        aValue = parseFloat(a.dataset[column]);
                        bValue = parseFloat(b.dataset[column]);
                        return direction === 'asc' 
                            ? aValue - bValue
                            : bValue - aValue;
                    }}
                }});
                
                // 重新插入排序后的行
                rows.forEach(row => tableBody.appendChild(row));
            }}
        }});
    </script>
</body>
</html>'''
    
    return html

def update_homepage_etf_section(etfs):
    """更新首页的ETF推荐部分"""
    homepage_path = os.path.join(OUTPUT_DIR, "index.html")
    
    if not os.path.exists(homepage_path):
        print("⚠️ 首页不存在")
        return
    
    # 读取首页内容
    with open(homepage_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 生成ETF推荐卡片
    etf_cards = ""
    for etf in etfs[:6]:  # 首页显示6只
        change_class = "price-up" if etf["daily_change"] > 0 else "price-down"
        change_sign = "+" if etf["daily_change"] > 0 else ""
        
        etf_cards += f'''
            <div class="finance-card card-type-etf">
                <div class="card-header">
                    <h3>{etf["name"]}</h3>
                    <span class="score-tag">{etf["rich_score"]}</span>
                </div>
                <div class="card-content">
                    <p>代码: {etf["symbol"]}</p>
                    <p>行业: {etf["industry"]}</p>
                    <p>净值: {etf["net_value"]:.3f} <span class="nav-date">({etf["nav_date"]})</span></p>
                    <p>涨跌: <span class="{change_class}">{change_sign}{etf["daily_change"]:.2f}%</span></p>
                </div>
                <div class="card-footer">
                    <a href="/etf/{etf["symbol"]}.html">查看详情</a>
                </div>
            </div>
        '''
    
    # 替换首页中的ETF推荐部分
    target_start = '<!-- ETF推荐开始 -->'
    target_end = '<!-- ETF推荐结束 -->'
    
    if target_start in content and target_end in content:
        start_index = content.find(target_start)
        end_index = content.find(target_end) + len(target_end)
        
        new_etf_section = f'''{target_start}
        <div class="grid-3">
            {etf_cards}
        </div>
        {target_end}'''
        
        content = content[:start_index] + new_etf_section + content[end_index:]
        
        # 保存更新后的首页
        with open(homepage_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ 首页ETF推荐部分更新完成")
    else:
        print("⚠️ 未找到ETF推荐部分的标记")

if __name__ == "__main__":
    update_etf_list()
    print("\n🎉 ETF列表排序功能和净值日期显示已更新完成！")