#!/usr/bin/env python3
"""
琥珀引擎 - 批量股票页面生成器
生成 A 股核心标的详情页
"""

import os
import sys
import sqlite3
import json
import time
from datetime import datetime, timedelta
import random
from typing import List, Dict, Any

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 配置
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "amber_cms.db")
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
STATIC_DIR = os.path.join(BASE_DIR, "static")

# 创建目录
os.makedirs(os.path.join(OUTPUT_DIR, "stock"), exist_ok=True)
os.makedirs(os.path.join(OUTPUT_DIR, "article"), exist_ok=True)
os.makedirs(os.path.join(OUTPUT_DIR, "static"), exist_ok=True)

print("=" * 70)
print("琥珀引擎 - 批量股票页面生成器")
print("=" * 70)

class StockPageGenerator:
    """股票页面批量生成器"""
    
    def __init__(self):
        self.db = None
        self.connect_database()
        self.template_cache = {}
        
    def connect_database(self):
        """连接数据库"""
        try:
            self.db = sqlite3.connect(DB_PATH)
            self.db.row_factory = sqlite3.Row
            print("✅ 数据库连接成功")
        except Exception as e:
            print(f"❌ 数据库连接失败: {e}")
            raise
    
    def load_template(self, template_name: str) -> str:
        """加载模板文件"""
        if template_name in self.template_cache:
            return self.template_cache[template_name]
        
        template_path = os.path.join(TEMPLATES_DIR, template_name)
        try:
            with open(template_path, 'r', encoding='utf-8') as f:
                template = f.read()
            self.template_cache[template_name] = template
            print(f"✅ 模板加载成功: {template_name}")
            return template
        except Exception as e:
            print(f"❌ 模板加载失败 {template_name}: {e}")
            raise
    
    def get_top_stocks(self, limit: int = 100) -> List[Dict]:
        """获取A股核心标的（模拟数据）"""
        print(f"\n📊 获取A股核心标的 (前{limit}只)...")
        
        # 模拟A股核心股票数据
        top_stocks = [
            # 金融板块
            {"ts_code": "601318.SH", "symbol": "601318", "name": "中国平安", "industry": "保险"},
            {"ts_code": "600036.SH", "symbol": "600036", "name": "招商银行", "industry": "银行"},
            {"ts_code": "601166.SH", "symbol": "601166", "name": "兴业银行", "industry": "银行"},
            {"ts_code": "600000.SH", "symbol": "600000", "name": "浦发银行", "industry": "银行"},
            {"ts_code": "601988.SH", "symbol": "601988", "name": "中国银行", "industry": "银行"},
            {"ts_code": "601328.SH", "symbol": "601328", "name": "交通银行", "industry": "银行"},
            {"ts_code": "601398.SH", "symbol": "601398", "name": "工商银行", "industry": "银行"},
            {"ts_code": "601939.SH", "symbol": "601939", "name": "建设银行", "industry": "银行"},
            {"ts_code": "601628.SH", "symbol": "601628", "name": "中国人寿", "industry": "保险"},
            {"ts_code": "601601.SH", "symbol": "601601", "name": "中国太保", "industry": "保险"},
            
            # 消费板块
            {"ts_code": "600519.SH", "symbol": "600519", "name": "贵州茅台", "industry": "白酒"},
            {"ts_code": "000858.SZ", "symbol": "000858", "name": "五粮液", "industry": "白酒"},
            {"ts_code": "000333.SZ", "symbol": "000333", "name": "美的集团", "industry": "家电"},
            {"ts_code": "000651.SZ", "symbol": "000651", "name": "格力电器", "industry": "家电"},
            {"ts_code": "002415.SZ", "symbol": "002415", "name": "海康威视", "industry": "安防"},
            {"ts_code": "600887.SH", "symbol": "600887", "name": "伊利股份", "industry": "食品饮料"},
            {"ts_code": "000568.SZ", "symbol": "000568", "name": "泸州老窖", "industry": "白酒"},
            {"ts_code": "600276.SH", "symbol": "600276", "name": "恒瑞医药", "industry": "医药"},
            {"ts_code": "600104.SH", "symbol": "600104", "name": "上汽集团", "industry": "汽车"},
            {"ts_code": "000002.SZ", "symbol": "000002", "name": "万科A", "industry": "房地产"},
            
            # 科技板块
            {"ts_code": "000001.SZ", "symbol": "000001", "name": "平安银行", "industry": "银行"},
            {"ts_code": "002594.SZ", "symbol": "002594", "name": "比亚迪", "industry": "新能源汽车"},
            {"ts_code": "300750.SZ", "symbol": "300750", "name": "宁德时代", "industry": "锂电池"},
            {"ts_code": "002475.SZ", "symbol": "002475", "name": "立讯精密", "industry": "消费电子"},
            {"ts_code": "002241.SZ", "symbol": "002241", "name": "歌尔股份", "industry": "消费电子"},
            {"ts_code": "300059.SZ", "symbol": "300059", "name": "东方财富", "industry": "互联网金融"},
            {"ts_code": "002230.SZ", "symbol": "002230", "name": "科大讯飞", "industry": "人工智能"},
            {"ts_code": "600570.SH", "symbol": "600570", "name": "恒生电子", "industry": "金融科技"},
            {"ts_code": "600588.SH", "symbol": "600588", "name": "用友网络", "industry": "企业软件"},
            {"ts_code": "002008.SZ", "symbol": "002008", "name": "大族激光", "industry": "激光设备"},
            
            # 能源板块
            {"ts_code": "601857.SH", "symbol": "601857", "name": "中国石油", "industry": "石油"},
            {"ts_code": "600028.SH", "symbol": "600028", "name": "中国石化", "industry": "石油化工"},
            {"ts_code": "601088.SH", "symbol": "601088", "name": "中国神华", "industry": "煤炭"},
            {"ts_code": "601225.SH", "symbol": "601225", "name": "陕西煤业", "industry": "煤炭"},
            {"ts_code": "600011.SH", "symbol": "600011", "name": "华能国际", "industry": "电力"},
            {"ts_code": "600900.SH", "symbol": "600900", "name": "长江电力", "industry": "水电"},
            {"ts_code": "600795.SH", "symbol": "600795", "name": "国电电力", "industry": "电力"},
            {"ts_code": "600023.SH", "symbol": "600023", "name": "浙能电力", "industry": "电力"},
            {"ts_code": "600886.SH", "symbol": "600886", "name": "国投电力", "industry": "电力"},
            {"ts_code": "600027.SH", "symbol": "600027", "name": "华电国际", "industry": "电力"},
            
            # 更多股票...
        ]
        
        # 如果不够100只，添加更多模拟数据
        if len(top_stocks) < limit:
            base_count = len(top_stocks)
            for i in range(base_count, limit):
                stock_num = 600000 + i
                top_stocks.append({
                    "ts_code": f"{stock_num}.SH",
                    "symbol": str(stock_num),
                    "name": f"模拟股票{i+1}",
                    "industry": random.choice(["科技", "制造", "医药", "消费", "金融"])
                })
        
        print(f"✅ 获取到 {len(top_stocks)} 只核心股票")
        return top_stocks[:limit]
    
    def generate_stock_data(self, stock: Dict) -> Dict:
        """生成股票模拟数据"""
        # 随机生成价格数据
        base_price = random.uniform(10, 100)
        
        # 生成5日行情数据
        daily_data = []
        for days_ago in range(5, 0, -1):
            date = (datetime.now() - timedelta(days=days_ago)).strftime("%Y%m%d")
            change = random.uniform(-0.05, 0.05)
            close = base_price * (1 + change)
            
            daily_data.append({
                "trade_date": date,
                "open": close * random.uniform(0.98, 1.02),
                "high": close * random.uniform(1.01, 1.05),
                "low": close * random.uniform(0.95, 0.99),
                "close": close,
                "pct_chg": change * 100,
                "vol": random.randint(1000000, 10000000)
            })
        
        # 计算最新涨跌幅
        latest_pct_chg = daily_data[-1]["pct_chg"] if daily_data else 0
        
        return {
            "stock": stock,
            "daily_data": daily_data,
            "latest_pct_chg": latest_pct_chg,
            "avg_price": sum(d["close"] for d in daily_data) / len(daily_data) if daily_data else 0,
            "rich_score": round(random.uniform(6.0, 9.5), 1)
        }
    
    def generate_stock_page(self, stock_data: Dict) -> str:
        """生成单个股票页面"""
        try:
            # 加载基础模板
            base_template = self.load_template("base_jinja2.html")
            
            # 生成股票内容
            stock_content = self.render_stock_content(stock_data)
            
            # 替换模板变量
            page_html = base_template
            
            # 替换标题
            title = f"{stock_data['stock']['name']} ({stock_data['stock']['symbol']}) - 琥珀引擎财经分析"
            page_html = page_html.replace("{% block title %}琥珀引擎 - Cheese Intelligence{% endblock %}", title)
            
            # 替换描述
            description = f"{stock_data['stock']['name']}深度分析：基本面、行情数据、投资价值评估"
            page_html = page_html.replace(
                "{% block description %}财经品牌独立站 - 数据库驱动 + 静态化生成的专业媒体架构{% endblock %}",
                description
            )
            
            # 替换内容
            page_html = page_html.replace("{% block content %}", stock_content)
            
            # 替换最后更新时间
            last_updated = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            page_html = page_html.replace("{% block last_updated %}{{ last_updated }}{% endblock %}", last_updated)
            
            return page_html
            
        except Exception as e:
            print(f"❌ 生成股票页面失败 {stock_data['stock']['name']}: {e}")
            return None
    
    def render_stock_content(self, stock_data: Dict) -> str:
        """渲染股票页面内容"""
        stock = stock_data["stock"]
        daily_data = stock_data["daily_data"]
        latest_pct_chg = stock_data["latest_pct_chg"]
        avg_price = stock_data["avg_price"]
        rich_score = stock_data["rich_score"]
        
        # 判断是否需要高亮
        highlight_class = "highlight-val" if latest_pct_chg > 1.0 else ""
        
        # 生成日线表格
        daily_table = ""
        for row in daily_data:
            pct_class = "price-up" if row["pct_chg"] > 0 else "price-down"
            pct_sign = "+" if row["pct_chg"] > 0 else ""
            
            daily_table += f"""
            <tr>
                <td>{row['trade_date']}</td>
                <td>{row['open']:.2f}</td>
                <td>{row['high']:.2f}</td>
                <td>{row['low']:.2f}</td>
                <td>{row['close']:.2f}</td>
                <td class="{pct_class}">{pct_sign}{row['pct_chg']:.2f}%</td>
                <td>{row['vol']/10000:.2f}万</td>
            </tr>
            """
        
        # 构建页面内容
        content = f'''
        <!-- 股票头部 -->
        <section class="stock-header">
            <div class="container">
                <h1 class="stock-title">{stock['name']}</h1>
                <div class="stock-code">{stock['ts_code']}</div>
                <p class="mt-3">行业: {stock['industry']} | 最新更新: {datetime.now().strftime('%Y-%m-%d')}</p>
            </div>
        </section>
        
        <div class="container">
            <!-- 琥珀指标卡 -->
            <div class="amber-metrics-card">
                <h2 class="section-title">📊 琥珀指标</h2>
                <div class="metrics-grid">
                    <div class="metric-item">
                        <div class="metric-label">最新价格</div>
                        <div class="metric-value {highlight_class}">{daily_data[-1]['close']:.2f if daily_data else 'N/A'}</div>
                    </div>
                    <div class="metric-item">
                        <div class="metric-label">日涨跌幅</div>
                        <div class="metric-value {highlight_class}">
                            {pct_sign if daily_data else ''}{latest_pct_chg:.2f}%
                        </div>
                    </div>
                    <div class="metric-item">
                        <div class="metric-label">5日均价</div>
                        <div class="metric-value">
                            {avg_price:.2f if daily_data else 'N/A'}
                        </div>
                    </div>
                    <div class="metric-item">
                        <div class="metric-label">RICH评分</div>
                        <div class="metric-value">{rich_score}</div>
                    </div>
                </div>
            </div>
            
            <!-- 行情图表区域 -->
            <section class="price-chart">
                <h2 class="section-title">📈 近期行情</h2>
                <p>最近5个交易日表现（数据更新至: {daily_data[-1]['trade_date'] if daily_data else 'N/A'}）</p>
                
                <table class="price-table">
                    <thead>
                        <tr>
                            <th>日期</th>
                            <th>开盘</th>
                            <th>最高</th>
                            <th>最低</th>
                            <th>收盘</th>
                            <th>涨跌幅</th>
                            <th>成交量</th>
                        </tr>
                    </thead>
                    <tbody>
                        {daily_table}
                    </tbody>
                </table>
                
                <div class="mt-4">
                    <p><strong>行情分析</strong>: {stock['name']}近期股价表现{'稳健' if abs(latest_pct_chg) < 2 else '波动较大'}，最新交易日涨跌幅{latest_pct_chg:.2f}%。</p>
                </div>
            </section>
            
            <!-- 公司分析 -->
            <section class="stock-analysis">
                <h2 class="section-title">🏢 公司深度分析</h2>
                
                <div class="company-overview">
                    <h3>公司概况</h3>
                    <p>{stock['name']} ({stock['ts_code']}) 是中国{stock['industry']}行业的重要上市公司，在行业内具有重要地位。</p>
                    
                    <h3>核心优势</h3>
                    <div class="highlight-points">
                        <div class="point-card">
                            <h4>📈 行业地位</h4>
                            <p>在{stock['industry']}行业具有竞争优势</p>
                        </div>
                        <div class="point-card">
                            <h4>💰 盈利能力</h4>
                            <p>财务状况稳健，盈利能力良好</p>
                        </div>
                        <div class="point-card">
                            <h4>🛡️ 风险管控</h4>
                            <p>风险管理体系完善，抗风险能力强</p>
                        </div>
                        <div class="point-card">
                            <h4>📊 成长潜力</h4>
                            <p>具备良好的成长性和发展空间</p>
                        </div>
                    </div>
                    
                    <h3>投资建议</h3>
                    <div class="finance-card">
                        <div class="card-header">
                            <h3 class="card-title">琥珀引擎评级: <span class="source-tag">{self.get_rating(rich_score)}</span></h3>
                            <div class="card-meta">
                                <span class="score-tag">RICH评分