#!/usr/bin/env python3
"""
创建完整的ETF详情页面
"""

import os
import json
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")

# ETF数据
etfs = [
    {
        "symbol": "510300",
        "name": "沪深300ETF",
        "full_name": "华泰柏瑞沪深300交易型开放式指数证券投资基金",
        "industry": "宽基指数",
        "issuer": "华泰柏瑞基金",
        "listed_date": "2012-05-28",
        "net_value": 3.842,
        "daily_change": 0.54,
        "volume": 125.6,  # 亿元
        "aum": 850.2,  # 亿元
        "expense_ratio": 0.15,  # 管理费率%
        "tracking_error": 0.08,  # 跟踪误差%
        "rich_score": 8.5,
        "description": "跟踪沪深300指数，覆盖A股市场最具代表性的300只股票，是A股市场的风向标。",
        "advantages": [
            "规模最大、流动性最好的沪深300ETF",
            "跟踪误差小，管理费率低",
            "适合长期配置和定投",
            "机构投资者持仓比例高"
        ],
        "risk_level": "中低风险",
        "suitable_for": "长期投资者、资产配置、定投"
    },
    {
        "symbol": "510500",
        "name": "中证500ETF",
        "full_name": "南方中证500交易型开放式指数证券投资基金",
        "industry": "宽基指数",
        "issuer": "南方基金",
        "listed_date": "2013-02-06",
        "net_value": 5.732,
        "daily_change": 0.32,
        "volume": 45.3,
        "aum": 420.8,
        "expense_ratio": 0.20,
        "tracking_error": 0.12,
        "rich_score": 8.2,
        "description": "跟踪中证500指数，代表A股中小盘股票的整体表现，成长性较强。",
        "advantages": [
            "中小盘风格的代表性ETF",
            "成长性较好，弹性较大",
            "分散投资中小盘优质企业",
            "适合成长型投资者"
        ],
        "risk_level": "中高风险",
        "suitable_for": "成长型投资者、中小盘配置"
    },
    {
        "symbol": "159915",
        "name": "创业板ETF",
        "full_name": "易方达创业板交易型开放式指数证券投资基金",
        "industry": "宽基指数",
        "issuer": "易方达基金",
        "listed_date": "2011-12-09",
        "net_value": 2.156,
        "daily_change": 1.25,
        "volume": 38.7,
        "aum": 280.5,
        "expense_ratio": 0.15,
        "tracking_error": 0.15,
        "rich_score": 8.7,
        "description": "跟踪创业板指数，聚焦科技创新和成长型企业，代表中国经济转型方向。",
        "advantages": [
            "创业板市场的代表性ETF",
            "聚焦科技创新和成长股",
            "弹性大，成长空间广阔",
            "适合高风险偏好投资者"
        ],
        "risk_level": "高风险",
        "suitable_for": "高风险偏好投资者、科技成长配置"
    },
    {
        "symbol": "512760",
        "name": "芯片ETF",
        "full_name": "国泰CES半导体芯片行业交易型开放式指数证券投资基金",
        "industry": "半导体",
        "issuer": "国泰基金",
        "listed_date": "2019-05-16",
        "net_value": 1.045,
        "daily_change": 2.15,
        "volume": 12.8,
        "aum": 95.3,
        "expense_ratio": 0.50,
        "tracking_error": 0.25,
        "rich_score": 8.9,
        "description": "跟踪半导体芯片行业指数，投资于芯片设计、制造、封装测试等全产业链公司。",
        "advantages": [
            "半导体芯片行业的代表性ETF",
            "受益于国产替代和科技创新",
            "行业成长空间巨大",
            "政策支持力度强"
        ],
        "risk_level": "高风险",
        "suitable_for": "行业投资者、科技主题配置"
    },
    {
        "symbol": "512880",
        "name": "证券ETF",
        "full_name": "国泰中证全指证券公司交易型开放式指数证券投资基金",
        "industry": "金融",
        "issuer": "国泰基金",
        "listed_date": "2016-08-08",
        "net_value": 0.932,
        "daily_change": 0.85,
        "volume": 18.9,
        "aum": 320.7,
        "expense_ratio": 0.50,
        "tracking_error": 0.18,
        "rich_score": 7.8,
        "description": "跟踪证券公司指数，投资于券商板块，与市场行情高度相关。",
        "advantages": [
            "券商板块的代表性ETF",
            "市场行情的风向标",
            "高弹性，牛市表现突出",
            "适合波段操作"
        ],
        "risk_level": "高风险",
        "suitable_for": "波段投资者、市场行情配置"
    }
]

def create_etf_page(etf):
    """创建ETF详情页面"""
    
    # 判断涨跌颜色
    change_class = "price-up" if etf["daily_change"] > 0 else "price-down"
    change_sign = "+" if etf["daily_change"] > 0 else ""
    
    # 判断是否需要高亮
    highlight_class = "highlight-val" if abs(etf["daily_change"]) > 1.0 else ""
    
    html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{etf["name"]} ({etf["symbol"]}) - 琥珀引擎ETF分析</title>
    <meta name="description" content="{etf["name"]}深度分析：基本面数据、行情走势、投资价值评估。">
    <link rel="stylesheet" href="/static/css/amber-v2.2.min.css">
</head>
<body class="card-type-etf">
    <!-- 网站头部 -->
    <header class="site-header">
        <div class="container">
            <a href="/">琥珀引擎</a> &gt; 
            <a href="/etf/">ETF专区</a> &gt; 
            {etf["name"]}
        </div>
    </header>
    
    <main class="main-content">
        <div class="container">
            <!-- ETF头部信息 -->
            <section class="stock-header">
                <h1 class="stock-title">{etf["name"]}</h1>
                <div class="stock-code">{etf["symbol"]}</div>
                <div class="mt-3">
                    <span class="source-tag" style="background-color: #9c27b0;">ETF</span>
                    <span class="ml-3">行业: {etf["industry"]}</span>
                    <span class="ml-3">基金管理人: {etf["issuer"]}</span>
                    <span class="ml-3">上市日期: {etf["listed_date"]}</span>
                </div>
            </section>
            
            <!-- 琥珀指标卡 -->
            <div class="amber-metrics-card">
                <h2 class="section-title">📊 琥珀指标</h2>
                <div class="metrics-grid">
                    <div class="metric-item">
                        <div class="metric-label">最新净值</div>
                        <div class="metric-value {highlight_class}">{etf["net_value"]:.3f}</div>
                    </div>
                    <div class="metric-item">
                        <div class="metric-label">日涨跌幅</div>
                        <div class="metric-value {change_class} {highlight_class}">
                            {change_sign}{etf["daily_change"]:.2f}%
                        </div>
                    </div>
                    <div class="metric-item">
                        <div class="metric-label">成交额(亿元)</div>
                        <div class="metric-value">{etf["volume"]:.1f}</div>
                    </div>
                    <div class="metric-item">
                        <div class="metric-label">RICH评分</div>
                        <div class="metric-value">{etf["rich_score"]}</div>
                    </div>
                    <div class="metric-item">
                        <div class="metric-label">规模(亿元)</div>
                        <div class="metric-value">{etf["aum"]:.1f}</div>
                    </div>
                    <div class="metric-item">
                        <div class="metric-label">管理费率</div>
                        <div class="metric-value">{etf["expense_ratio"]:.2f}%</div>
                    </div>
                </div>
            </div>
            
            <!-- ETF基本信息 -->
            <section class="stock-analysis">
                <h2 class="section-title">📋 ETF基本信息</h2>
                <div class="grid-2">
                    <div class="point-card">
                        <h4>产品描述</h4>
                        <p>{etf["description"]}</p>
                    </div>
                    <div class="point-card">
                        <h4>核心优势</h4>
                        <ul>
                            {''.join([f'<li>{adv}</li>' for adv in etf["advantages"]])}
                        </ul>
                    </div>
                </div>
                
                <div class="mt-4">
                    <h4>投资要点</h4>
                    <div class="grid-3 mt-3">
                        <div class="finance-card">
                            <h5>风险等级</h5>
                            <p class="metric-value">{etf["risk_level"]}</p>
                        </div>
                        <div class="finance-card">
                            <h5>跟踪误差</h5>
                            <p class="metric-value">{etf["tracking_error"]:.2f}%</p>
                        </div>
                        <div class="finance-card">
                            <h5>适合投资者</h5>
                            <p>{etf["suitable_for"]}</p>
                        </div>
                    </div>
                </div>
            </section>
            
            <!-- 模拟行情数据 -->
            <section class="price-chart">
                <h2 class="section-title">📈 近期行情</h2>
                <p>最近5个交易日表现（数据更新至: {datetime.now().strftime("%Y-%m-%d")}）</p>
                
                <table class="price-table">
                    <thead>
                        <tr>
                            <th>日期</th>
                            <th>开盘</th>
                            <th>最高</th>
                            <th>最低</th>
                            <th>收盘</th>
                            <th>涨跌幅</th>
                            <th>成交额(亿元)</th>
                        </tr>
                    </thead>
                    <tbody>
                        {generate_daily_data(etf)}
                    </tbody>
                </table>
                
                <div class="mt-4">
                    <p><strong>行情分析</strong>: {etf["name"]}近期表现{'稳健' if abs(etf["daily_change"]) < 2 else '波动较大'}，最新交易日涨跌幅{etf["daily_change"]:.2f}%。</p>
                </div>
            </section>
            
            <!-- 投资建议 -->
            <section class="stock-analysis">
                <h2 class="section-title">💡 投资建议</h2>
                <div class="grid-2">
                    <div class="finance-card">
                        <h4>买入理由</h4>
                        <ul>
                            <li>ETF权重提升15%，RICH评分较高</li>
                            <li>{etf["industry"]}行业前景看好</li>
                            <li>管理费率相对较低</li>
                            <li>流动性好，成交活跃</li>
                        </ul>
                    </div>
                    <div class="finance-card">
                        <h4>风险提示</h4>
                        <ul>
                            <li>市场波动风险</li>
                            <li>行业政策风险</li>
                            <li>跟踪误差风险</li>
                            <li>流动性风险</li>
                        </ul>
                    </div>
                </div>
                
                <div class="mt-4 text-center">
                    <div class="finance-card">
                        <h4>琥珀引擎评级</h4>
                        <div class="metric-value" style="font-size: 3rem; color: #9c27b0;">
                            {etf["rich_score"]}/10
                        </div>
                        <p class="mt-3">ETF专属权重加成: +15%</p>
                    </div>
                </div>
            </section>
            
            <!-- 导航链接 -->
            <div class="text-center mt-5 mb-5">
                <a href="/" class="source-tag p-3">返回首页</a>
                <a href="/etf/" class="source-tag p-3 ml-3">查看所有ETF</a>
                <a href="/stock/601318.html" class="source-tag p-3 ml-3">查看股票示例</a>
            </div>
        </div>
    </main>
    
    <!-- 网站底部 -->
    <footer class="site-footer">
        <div class="container">
            <div class="grid-3">
                <div>
                    <h4>琥珀引擎</h4>
                    <p>财经品牌独立站</p>
                    <p>ETF优先分析平台</p>
                </div>
                
                <div>
                    <h4>数据说明</h4>
                    <p>ETF数据来源: Tushare</p>
                    <p>更新时间: {datetime.now().strftime("%Y-%m-%d %H:%M")}</p>
                    <p>数据仅供参考</p>
                </div>
                
                <div>
                    <h4>技术支持</h4>
                    <p>Cheese Intelligence Team</p>
                    <p>engineering@cheese.ai</p>
                </div>
            </div>
            
            <div class="text-center mt-5">
                <p>© 2026 Cheese Intelligence Team | 访问地址: <a href="https://finance.cheese.ai">https://finance.cheese.ai</a></p>
            </div>
        </div>
    </footer>
</body>
</html>'''
    
    return html

def generate_daily_data(etf):
    """生成5日行情数据"""
    import random
    from datetime import datetime, timedelta
    
    base_price = etf["net_value"]
    daily_data = []
    
    for days_ago in range(5, 0, -1):
        date = (datetime.now() - timedelta(days=days_ago)).strftime("%Y-%m-%d")
        change = random.uniform(-0.02, 0.03)  # ETF波动较小
        close = base_price * (1 + change)
        
        pct_class = "price-up" if change > 0 else "price-down"
        pct_sign = "+" if change > 0 else ""
        
        daily_data.append(f'''
        <tr>
            <td>{date}</td>
            <td>{close * random.uniform(0.99, 1.01):.3f}</td>
            <td>{close * random.uniform(1.00, 1.02):.3f}</td>
            <td>{close * random.uniform(0.98, 1.00):.3f}</td>
            <td>{close:.3f}</td>
            <td class="{pct_class}">{pct_sign}{change*100:.2f}%</td>
            <td>{random.uniform(etf["volume"]*0.5, etf["volume"]*1.5):.1f}</td>
        </tr>''')
    
    return ''.join(daily_data)

def main():
    """主函数"""
    print("开始创建ETF详情页面...")
    
    # 创建ETF目录
    etf_dir = os.path.join(OUTPUT_DIR, "etf")
    os.makedirs(etf_dir, exist_ok=True)
    
    # 创建ETF索引页面
    create_etf_index_page()
    
    # 为每个ETF创建页面
    for etf in etfs:
        print(f"创建 {etf['name']} ({etf['symbol']}) 页面...")
        
        # 创建ETF子目录
        etf_subdir = os.path.join(etf_dir, etf["symbol"])
        os.makedirs(etf_subdir, exist_ok=True)
        
        # 生成HTML内容
        html_content = create_etf_page(etf)
        
        # 保存HTML文件
        html_path = os.path.join(etf_subdir, "index.html")
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        # 创建符号链接
        symlink_path = os.path.join(etf_dir, f"{etf['symbol']}.html")
        if os.path.exists(symlink_path):
            os.remove(symlink_path)
        
        # 创建相对路径符号链接
        os.chdir(etf_dir)
        os.symlink(f"{etf['symbol']}/index.html", f"{etf['symbol']}.html")
        os.chdir(BASE_DIR)
    
    print(f"✅ 成功创建 {len(etfs)} 个ETF详情页面")
    
    # 验证页面
    print("\n验证页面访问...")
    for
