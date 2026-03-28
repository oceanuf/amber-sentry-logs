#!/usr/bin/env python3
"""
琥珀引擎 - ETF优先生成脚本
架构师指令：前20只ETF使用真实数据，其余80只使用模拟数据
"""

import os
import sys
import sqlite3
import time
from datetime import datetime, timedelta
import random
import tushare as ts

# 配置
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "amber_cms.db")
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")

print("=" * 70)
print("琥珀引擎 - ETF优先生成脚本")
print("架构师指令：20只ETF真实数据 + 80只模拟数据")
print("=" * 70)

class ETFPriorityGenerator:
    """ETF优先生成器"""
    
    def __init__(self):
        self.db = None
        self.pro = None
        self.connect_database()
        self.init_tushare()
        
    def connect_database(self):
        """连接数据库"""
        try:
            self.db = sqlite3.connect(DB_PATH)
            self.db.row_factory = sqlite3.Row
            print("✅ 数据库连接成功")
        except Exception as e:
            print(f"❌ 数据库连接失败: {e}")
            raise
    
    def init_tushare(self):
        """初始化Tushare"""
        try:
            # 从环境变量获取token
            token = os.getenv('TUSHARE_TOKEN', '9e32ef28eac05c5fbb11e6f02a50da903def70f94b3018e93340568b')
            self.pro = ts.pro_api(token)
            print("✅ Tushare Pro接口初始化成功")
        except Exception as e:
            print(f"❌ Tushare初始化失败: {e}")
            self.pro = None
    
    def get_etf_list(self):
        """获取ETF列表（前20只核心行业ETF）"""
        print("\n📊 获取核心行业ETF列表...")
        
        # 核心行业ETF列表
        core_etfs = [
            # 宽基指数ETF
            {"ts_code": "510300.SH", "symbol": "510300", "name": "沪深300ETF", "industry": "宽基指数"},
            {"ts_code": "510500.SH", "symbol": "510500", "name": "中证500ETF", "industry": "宽基指数"},
            {"ts_code": "510050.SH", "symbol": "510050", "name": "上证50ETF", "industry": "宽基指数"},
            {"ts_code": "159915.SZ", "symbol": "159915", "name": "创业板ETF", "industry": "宽基指数"},
            {"ts_code": "159919.SZ", "symbol": "159919", "name": "沪深300ETF", "industry": "宽基指数"},
            
            # 行业主题ETF
            {"ts_code": "512760.SH", "symbol": "512760", "name": "芯片ETF", "industry": "半导体"},
            {"ts_code": "515000.SH", "symbol": "515000", "name": "科技ETF", "industry": "科技"},
            {"ts_code": "512480.SH", "symbol": "512480", "name": "半导体ETF", "industry": "半导体"},
            {"ts_code": "512880.SH", "symbol": "512880", "name": "证券ETF", "industry": "金融"},
            {"ts_code": "512000.SH", "symbol": "512000", "name": "券商ETF", "industry": "金融"},
            
            # 策略主题ETF
            {"ts_code": "510880.SH", "symbol": "510880", "name": "红利ETF", "industry": "红利策略"},
            {"ts_code": "512070.SH", "symbol": "512070", "name": "非银ETF", "industry": "金融"},
            {"ts_code": "512660.SH", "symbol": "512660", "name": "军工ETF", "industry": "军工"},
            {"ts_code": "512010.SH", "symbol": "512010", "name": "医药ETF", "industry": "医药"},
            {"ts_code": "512800.SH", "symbol": "512800", "name": "银行ETF", "industry": "银行"},
            
            # 更多ETF
            {"ts_code": "159928.SZ", "symbol": "159928", "name": "消费ETF", "industry": "消费"},
            {"ts_code": "159995.SZ", "symbol": "159995", "name": "芯片ETF", "industry": "半导体"},
            {"ts_code": "515050.SH", "symbol": "515050", "name": "5GETF", "industry": "通信"},
            {"ts_code": "512690.SH", "symbol": "512690", "name": "酒ETF", "industry": "消费"},
            {"ts_code": "512170.SH", "symbol": "512170", "name": "医疗ETF", "industry": "医疗"},
        ]
        
        print(f"✅ 获取到 {len(core_etfs)} 只核心行业ETF")
        return core_etfs
    
    def get_simulated_stocks(self, count: int = 80):
        """获取模拟股票数据"""
        print(f"\n📊 生成模拟股票数据 ({count}只)...")
        
        simulated_stocks = []
        for i in range(count):
            stock_num = 600000 + i
            simulated_stocks.append({
                "ts_code": f"{stock_num}.SH",
                "symbol": str(stock_num),
                "name": f"模拟股票{i+1}",
                "industry": random.choice(["科技", "制造", "医药", "消费", "金融", "能源", "材料"]),
                "is_etf": False
            })
        
        print(f"✅ 生成 {len(simulated_stocks)} 只模拟股票")
        return simulated_stocks
    
    def fetch_real_etf_data(self, etf: dict):
        """获取ETF真实数据"""
        try:
            if not self.pro:
                print(f"⚠️  Tushare不可用，使用模拟数据: {etf['name']}")
                return self.generate_simulated_data(etf)
            
            # 获取日线数据（最近5个交易日）
            end_date = datetime.now().strftime("%Y%m%d")
            start_date = (datetime.now() - timedelta(days=10)).strftime("%Y%m%d")
            
            df = self.pro.fund_daily(ts_code=etf["ts_code"], 
                                    start_date=start_date, 
                                    end_date=end_date)
            
            if df is None or df.empty:
                print(f"⚠️  无ETF数据，使用模拟数据: {etf['name']}")
                return self.generate_simulated_data(etf)
            
            # 取最近5条数据
            df = df.sort_values('trade_date', ascending=False).head(5)
            
            daily_data = []
            for _, row in df.iterrows():
                daily_data.append({
                    "trade_date": row['trade_date'],
                    "open": float(row['open']),
                    "high": float(row['high']),
                    "low": float(row['low']),
                    "close": float(row['close']),
                    "pct_chg": float(row['pct_chg']),
                    "vol": float(row['vol'])
                })
            
            # 计算指标
            latest_pct_chg = daily_data[0]["pct_chg"] if daily_data else 0
            avg_price = sum(d["close"] for d in daily_data) / len(daily_data) if daily_data else 0
            
            # ETF RICH评分权重提升15%
            base_score = random.uniform(7.0, 9.0)
            rich_score = min(10.0, base_score * 1.15)  # 提升15%，不超过10
            
            return {
                "daily_data": daily_data,
                "latest_pct_chg": latest_pct_chg,
                "avg_price": avg_price,
                "rich_score": round(rich_score, 1),
                "data_source": "tushare"
            }
            
        except Exception as e:
            print(f"❌ 获取ETF数据失败 {etf['name']}: {e}")
            return self.generate_simulated_data(etf)
    
    def generate_simulated_data(self, asset: dict):
        """生成模拟数据"""
        # 随机生成价格数据
        base_price = random.uniform(1, 5) if asset.get("is_etf", False) else random.uniform(10, 100)
        
        # 生成5日行情数据
        daily_data = []
        for days_ago in range(5, 0, -1):
            date = (datetime.now() - timedelta(days=days_ago)).strftime("%Y%m%d")
            change = random.uniform(-0.03, 0.03)  # ETF波动较小
            close = base_price * (1 + change)
            
            daily_data.append({
                "trade_date": date,
                "open": close * random.uniform(0.99, 1.01),
                "high": close * random.uniform(1.00, 1.02),
                "low": close * random.uniform(0.98, 1.00),
                "close": close,
                "pct_chg": change * 100,
                "vol": random.randint(1000000, 5000000)
            })
        
        # 计算指标
        latest_pct_chg = daily_data[-1]["pct_chg"] if daily_data else 0
        avg_price = sum(d["close"] for d in daily_data) / len(daily_data) if daily_data else 0
        
        # 评分
        if asset.get("is_etf", False):
            base_score = random.uniform(7.0, 9.0)
            rich_score = min(10.0, base_score * 1.15)  # ETF权重提升15%
        else:
            rich_score = round(random.uniform(6.0, 9.0), 1)
        
        return {
            "daily_data": daily_data,
            "latest_pct_chg": latest_pct_chg,
            "avg_price": avg_price,
            "rich_score": rich_score,
            "data_source": "simulated"
        }
    
    def generate_asset_page(self, asset: dict, asset_data: dict):
        """生成资产页面（ETF或股票）"""
        try:
            # 读取模板
            template_path = os.path.join(TEMPLATES_DIR, "base_jinja2.html")
            with open(template_path, 'r', encoding='utf-8') as f:
                template = f.read()
            
            # 生成页面内容
            content = self.render_asset_content(asset, asset_data)
            
            # 替换模板变量
            page_html = template
            
            # 标题
            title = f"{asset['name']} ({asset['symbol']}) - 琥珀引擎财经分析"
            page_html = page_html.replace(
                "{% block title %}琥珀引擎 - Cheese Intelligence{% endblock %}",
                title
            )
            
            # 描述
            asset_type = "ETF" if asset.get("is_etf", False) else "股票"
            description = f"{asset['name']}{asset_type}深度分析：基本面、行情数据、投资价值评估"
            page_html = page_html.replace(
                "{% block description %}财经品牌独立站 - 数据库驱动 + 静态化生成的专业媒体架构{% endblock %}",
                description
            )
            
            # 内容
            page_html = page_html.replace("{% block content %}", content)
            
            # 更新时间
            last_updated = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            page_html = page_html.replace(
                "{% block last_updated %}{{ last_updated }}{% endblock %}",
                last_updated
            )
            
            # 添加ETF专属CSS类
            if asset.get("is_etf", False):
                page_html = page_html.replace(
                    '<main class="main-content">',
                    '<main class="main-content card-type-etf">'
                )
            
            return page_html
            
        except Exception as e:
            print(f"❌ 生成页面失败 {asset['name']}: {e}")
            return None
    
    def render_asset_content(self, asset: dict, asset_data: dict):
        """渲染资产页面内容"""
        daily_data = asset_data["daily_data"]
        latest_pct_chg = asset_data["latest_pct_chg"]
        avg_price = asset_data["avg_price"]
        rich_score = asset_data["rich_score"]
        
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
                <td>{row['open']:.3f}</td>
                <td>{row['high']:.3f}</td>
                <td>{row['low']:.3f}</td>
                <td>{row['close']:.3f}</td>
                <td class="{pct_class}">{pct_sign}{row['pct_chg']:.2f}%</td>
                <td>{row['vol']/10000:.2f}万</td>
            </tr>
            """
        
        # 资产类型标签
        asset_type = "ETF" if asset.get("is_etf", False) else "股票"
        type_badge = f'<span class="source-tag" style="background-color: #9c27b0;">{asset_type}</span>' if asset.get("is_etf", False) else f'<span class="source-tag">{asset_type}</span>'
        
        # 数据源标签
        data_source_badge = f'<span class="time-tag">数据源: {asset_data["data_source"]}</span>'
        
        content = f'''
        <!-- 资产头部 -->
        <section class="stock-header">
            <div class="container">
                <h1 class="stock-title">{asset['name']}</h1>
                <div class="stock-code">{asset['ts_code']}</div>
                <p class="mt-3">
                    {type_badge}
                    <span class="ml-3">行业: {asset['industry']}</span>
                    <span class="ml-3">{data_source_badge}</span>
                </p>
            </div>
        </section>
        
        <div class="container">
            <!-- 琥珀指标卡 -->
            <div class="amber-metrics-card">
                <h2 class="section-title">📊 琥珀指标</h2>
                <div class="metrics-grid">
                    <div class="metric-item">
                        <div class="metric-label">最新净值</div>
                        <div class="metric-value {highlight_class}">{daily_data[-1]['close']:.3f if daily_data else 'N/A'}</div>
                    </div>
                    <div class="metric-item">
                        <div class="metric-label">日涨跌幅</div>
                        <div class="metric-value {highlight_class}">
                            {pct_sign if daily_data else ''}{latest_pct_chg:.2f}%
                        </div>
                    </div>
                    <div class="metric-item">
                        <div class="metric-label">5日均值</div>
                        <div class="metric-value">
                            {avg_price:.3f if daily_data else 'N/A'}
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
                    <p><strong>行情分析</strong>: {asset['name']}近期表现{'稳健' if abs(latest_pct_chg) < 2 else '波动较大'}，最新交易日涨跌幅{latest_pct_chg:.2f}%。</p>
                </div>
            </section>
            
            <!-- 返回链接 -->
            <div class="text-center mt-5 mb-5">
                <a href="/" class="source-tag p-3">返回首页</a>
                <a href="/{"etfs" if asset.get("is_etf", False) else "stocks"}.html" class="source-tag p-3 ml-3">查看所有{asset_type}</a>
            </div>
        </div>
        '''
        
        return content
    
    def save_asset_page(self, asset: dict, html_content: str):
        """保存资产页面"""
        try:
            # 创建目录
            asset_dir = os.path.join(OUTPUT_DIR, "etf" if asset.get("is_etf", False) else "stock", asset["symbol"])
            os