#!/usr/bin/env python3
"""
RICH-ETF算法实现 - 架构师最高指令
逻辑: Final_Score = Base_Score * (1.15 if is_etf else 1.0)
排序: ORDER BY is_etf DESC, rich_score DESC
"""

import os
import sqlite3
import random
from datetime import datetime, timedelta

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "amber_cms.db")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")

class RICHETFAlgorithm:
    """RICH-ETF算法实现类"""
    
    def __init__(self):
        self.db = None
        self.connect_database()
    
    def connect_database(self):
        """连接数据库"""
        try:
            self.db = sqlite3.connect(DB_PATH)
            self.db.row_factory = sqlite3.Row
            print("✅ 数据库连接成功")
        except Exception as e:
            print(f"❌ 数据库连接失败: {e}")
            # 创建数据库
            self.create_database()
    
    def create_database(self):
        """创建数据库表结构"""
        try:
            cursor = self.db.cursor()
            
            # 创建ETF表
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS etfs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                full_name TEXT,
                industry TEXT,
                issuer TEXT,
                listed_date TEXT,
                base_score REAL,  -- 基础评分
                rich_score REAL,  -- 最终评分 (含ETF权重加成)
                is_etf BOOLEAN DEFAULT 1,
                fund_size REAL,  -- 基金规模(亿元)
                expense_ratio REAL,  -- 管理费率%
                discount_premium REAL,  -- 折溢价率%
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            ''')
            
            # 创建ETF日线数据表
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS etf_daily (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                etf_id INTEGER,
                trade_date TEXT NOT NULL,
                open REAL,
                high REAL,
                low REAL,
                close REAL,
                pct_chg REAL,
                volume REAL,
                amount REAL,
                FOREIGN KEY (etf_id) REFERENCES etfs (id),
                UNIQUE(etf_id, trade_date)
            )
            ''')
            
            # 创建ETF重仓股表
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS etf_holdings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                etf_id INTEGER,
                stock_symbol TEXT,
                stock_name TEXT,
                weight REAL,  -- 持仓权重%
                market_value REAL,  -- 持仓市值(亿元)
                FOREIGN KEY (etf_id) REFERENCES etfs (id)
            )
            ''')
            
            # 创建股票表（对比用）
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS stocks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                industry TEXT,
                base_score REAL,
                rich_score REAL,
                is_etf BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            ''')
            
            self.db.commit()
            print("✅ 数据库表结构创建成功")
            
        except Exception as e:
            print(f"❌ 数据库创建失败: {e}")
    
    def calculate_rich_score(self, base_score, is_etf=True):
        """
        计算RICH评分（含ETF权重加成）
        逻辑: Final_Score = Base_Score * (1.15 if is_etf else 1.0)
        """
        if is_etf:
            rich_score = min(10.0, base_score * 1.15)  # ETF权重加成15%，不超过10分
        else:
            rich_score = base_score
        
        return round(rich_score, 1)
    
    def insert_sample_data(self):
        """插入示例数据"""
        try:
            cursor = self.db.cursor()
            
            # ETF数据
            etfs = [
                {
                    'symbol': '510300', 'name': '沪深300ETF', 'industry': '宽基指数',
                    'issuer': '华泰柏瑞基金', 'base_score': 7.8, 'fund_size': 850.2,
                    'expense_ratio': 0.15, 'discount_premium': 0.02
                },
                {
                    'symbol': '510500', 'name': '中证500ETF', 'industry': '宽基指数',
                    'issuer': '南方基金', 'base_score': 7.5, 'fund_size': 420.8,
                    'expense_ratio': 0.20, 'discount_premium': 0.05
                },
                {
                    'symbol': '159915', 'name': '创业板ETF', 'industry': '宽基指数',
                    'issuer': '易方达基金', 'base_score': 8.0, 'fund_size': 280.5,
                    'expense_ratio': 0.15, 'discount_premium': -0.01
                },
                {
                    'symbol': '512760', 'name': '芯片ETF', 'industry': '半导体',
                    'issuer': '国泰基金', 'base_score': 8.2, 'fund_size': 95.3,
                    'expense_ratio': 0.50, 'discount_premium': 0.08
                },
                {
                    'symbol': '512880', 'name': '证券ETF', 'industry': '金融',
                    'issuer': '国泰基金', 'base_score': 7.0, 'fund_size': 320.7,
                    'expense_ratio': 0.50, 'discount_premium': 0.03
                }
            ]
            
            # 插入ETF数据
            for etf in etfs:
                # 计算RICH评分（含ETF权重加成）
                rich_score = self.calculate_rich_score(etf['base_score'], is_etf=True)
                
                cursor.execute('''
                INSERT OR REPLACE INTO etfs 
                (symbol, name, industry, issuer, base_score, rich_score, is_etf, fund_size, expense_ratio, discount_premium)
                VALUES (?, ?, ?, ?, ?, ?, 1, ?, ?, ?)
                ''', (
                    etf['symbol'], etf['name'], etf['industry'], etf['issuer'],
                    etf['base_score'], rich_score, etf['fund_size'], 
                    etf['expense_ratio'], etf['discount_premium']
                ))
                
                etf_id = cursor.lastrowid
                
                # 插入ETF日线数据
                self.insert_etf_daily_data(cursor, etf_id, etf['symbol'])
                
                # 插入ETF重仓股数据
                self.insert_etf_holdings(cursor, etf_id, etf['symbol'], etf['industry'])
            
            # 股票数据（对比用）
            stocks = [
                {'symbol': '601318', 'name': '中国平安', 'industry': '保险', 'base_score': 7.8},
                {'symbol': '600519', 'name': '贵州茅台', 'industry': '白酒', 'base_score': 9.1},
                {'symbol': '300750', 'name': '宁德时代', 'industry': '新能源', 'base_score': 8.3},
                {'symbol': '000858', 'name': '五粮液', 'industry': '白酒', 'base_score': 8.0},
                {'symbol': '600036', 'name': '招商银行', 'industry': '银行', 'base_score': 7.5},
            ]
            
            for stock in stocks:
                rich_score = self.calculate_rich_score(stock['base_score'], is_etf=False)
                
                cursor.execute('''
                INSERT OR REPLACE INTO stocks 
                (symbol, name, industry, base_score, rich_score, is_etf)
                VALUES (?, ?, ?, ?, ?, 0)
                ''', (
                    stock['symbol'], stock['name'], stock['industry'],
                    stock['base_score'], rich_score
                ))
            
            self.db.commit()
            print(f"✅ 插入 {len(etfs)} 只ETF和 {len(stocks)} 只股票数据")
            
        except Exception as e:
            print(f"❌ 数据插入失败: {e}")
    
    def insert_etf_daily_data(self, cursor, etf_id, symbol):
        """插入ETF日线数据"""
        try:
            base_price = random.uniform(0.8, 5.0)
            
            for days_ago in range(5, 0, -1):
                trade_date = (datetime.now() - timedelta(days=days_ago)).strftime("%Y%m%d")
                pct_chg = random.uniform(-0.03, 0.03)
                close = base_price * (1 + pct_chg)
                
                cursor.execute('''
                INSERT OR REPLACE INTO etf_daily 
                (etf_id, trade_date, open, high, low, close, pct_chg, volume, amount)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    etf_id, trade_date,
                    close * random.uniform(0.99, 1.01),
                    close * random.uniform(1.00, 1.02),
                    close * random.uniform(0.98, 1.00),
                    close,
                    pct_chg * 100,
                    random.uniform(1000000, 5000000),
                    random.uniform(10, 50)
                ))
            
            print(f"  ✅ ETF {symbol} 日线数据插入成功")
            
        except Exception as e:
            print(f"  ❌ ETF {symbol} 日线数据插入失败: {e}")
    
    def insert_etf_holdings(self, cursor, etf_id, symbol, industry):
        """插入ETF重仓股数据"""
        try:
            holdings = []
            
            if industry == '宽基指数':
                holdings = [
                    {'symbol': '600519', 'name': '贵州茅台', 'weight': 5.2},
                    {'symbol': '300750', 'name': '宁德时代', 'weight': 3.8},
                    {'symbol': '601318', 'name': '中国平安', 'weight': 2.5},
                    {'symbol': '000858', 'name': '五粮液', 'weight': 1.8},
                    {'symbol': '600036', 'name': '招商银行', 'weight': 1.5},
                ]
            elif industry == '半导体':
                holdings = [
                    {'symbol': '603501', 'name': '韦尔股份', 'weight': 8.5},
                    {'symbol': '002049', 'name': '紫光国微', 'weight': 6.2},
                    {'symbol': '600703', 'name': '三安光电', 'weight': 5.8},
                    {'symbol': '002156', 'name': '通富微电', 'weight': 4.5},
                    {'symbol': '300661', 'name': '圣邦股份', 'weight': 3.2},
                ]
            elif industry == '金融':
                holdings = [
                    {'symbol': '601318', 'name': '中国平安', 'weight': 12.5},
                    {'symbol': '600036', 'name': '招商银行', 'weight': 8.2},
                    {'symbol': '601166', 'name': '兴业银行', 'weight': 6.8},
                    {'symbol': '600030', 'name': '中信证券', 'weight': 5.5},
                    {'symbol': '601688', 'name': '华泰证券', 'weight': 4.2},
                ]
            
            for holding in holdings:
                market_value = random.uniform(5, 50)  # 模拟持仓市值
                
                cursor.execute('''
                INSERT INTO etf_holdings 
                (etf_id, stock_symbol, stock_name, weight, market_value)
                VALUES (?, ?, ?, ?, ?)
                ''', (
                    etf_id, holding['symbol'], holding['name'], 
                    holding['weight'], market_value
                ))
            
            print(f"  ✅ ETF {symbol} 重仓股数据插入成功")
            
        except Exception as e:
            print(f"  ❌ ETF {symbol} 重仓股数据插入失败: {e}")
    
    def get_etf_momentum_ranking(self, limit=3):
        """
        获取ETF动量榜（按RICH评分排序）
        排序: ORDER BY is_etf DESC, rich_score DESC
        """
        try:
            cursor = self.db.cursor()
            
            # 架构师指令：ORDER BY is_etf DESC, rich_score DESC
            cursor.execute('''
            SELECT symbol, name, rich_score, fund_size, expense_ratio
            FROM etfs
            ORDER BY is_etf DESC, rich_score DESC
            LIMIT ?
            ''', (limit,))
            
            ranking = cursor.fetchall()
            return ranking
            
        except Exception as e:
            print(f"❌ 获取ETF动量榜失败: {e}")
            return []
    
    def get_all_assets_sorted(self):
        """
        获取所有资产（ETF+股票）按架构师指令排序
        排序: ORDER BY is_etf DESC, rich_score DESC
        """
        try:
            cursor = self.db.cursor()
            
            # 合并ETF和股票数据，按架构师指令排序
            cursor.execute('''
            SELECT symbol, name, industry, rich_score, is_etf, 
                   fund_size, expense_ratio, discount_premium
            FROM (
                SELECT symbol, name, industry, rich_score, is_etf, 
                       fund_size, expense_ratio, discount_premium
                FROM etfs
                UNION ALL
                SELECT symbol, name, industry, rich_score, is_etf,
                       NULL as fund_size, NULL as expense_ratio, NULL as discount_premium
                FROM stocks
            )
            ORDER BY is_etf DESC, rich_score DESC
            ''')
            
            assets = cursor.fetchall()
            return assets
            
        except Exception as e:
            print(f"❌ 获取资产排序失败: {e}")
            return []
    
    def update_homepage_with_etf_ranking(self):
        """更新首页，添加ETF动量榜"""
        try:
            # 获取ETF动量榜前三名
            momentum_ranking = self.get_etf_momentum_ranking(limit=3)
            
            if not momentum_ranking:
                print("⚠️  无ETF动量榜数据")
                return
            
            # 读取首页模板
            homepage_path = os.path.join(OUTPUT_DIR, "index.html")
            with open(homepage_path, 'r', encoding='utf-8') as f:
                homepage_content = f.read()
            
            # 构建ETF动量榜HTML
            momentum_html = '''
            <!-- ETF动量榜 - 架构师指令 -->
            <div class="finance-card card-type-etf etf-pulse">
                <div class="card-header">
                    <h3>📈 今日ETF动量榜</h3>
                    <span class="etf-momentum-badge">RICH评分排名</span>
                </div>
                <div class="card-content">
                    <div class="grid-3">
            '''
            
            for i, etf in enumerate(momentum_ranking, 1):
                medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉"
                momentum_html += f'''
                        <div class="text-center">
                            <div class="metric-value etf-rich-score">{etf['rich_score']}</div>
                            <p>{medal} {etf['name']}</p>
                            <p class="text-sm">代码: {etf['symbol']}</p>
                        </div>
                '''
            
            momentum_html += '''
                    </div>
                    <p class="mt-3 text-center">
                        <small>排序规则: ETF优先 + RICH评分降序 (含15%权重加成)</small>
                    </p>
                </div>
            </div>
            '''
            
            # 在首页适当位置插入ETF动量榜
            # 找到第一个h2标签前插入
            if '<h2 class="section-title">🎯 ETF优先推荐</h2>' in homepage_content:
                homepage_content = homepage_content.replace(
                    '<h2 class="section-title">🎯 ETF优先推荐</h2>',
                    momentum_html + '\n<h2 class="section-title">🎯 ETF优先推荐</h2>'
                )
            
            # 保存更新后的首页
            with open(homepage_path, 'w', encoding='utf-8') as f:
                f.write(homepage_content)
            
            print("✅ 首页ETF动量榜更新成功")
            
        except Exception as e:
            print(f"❌ 更新首页失败: {e}")
    
    def update_etf_pages_with_algorithm(self):
        """更新ETF详情页面，注入RICH-ETF算法"""
        try:
            cursor = self.db.cursor()
            
            # 获取所有ETF
            cursor.execute('SELECT symbol, name FROM etfs')
            etfs = cursor.fetchall()
            
            for etf in etfs:
                symbol = etf['symbol']
                etf_page_path = os.path.join(OUTPUT_DIR, "etf", symbol, "index.html")
                
                if not os.path.exists(etf_page_path):
                    print(f"⚠️  ETF页面不存在: {symbol}")
                    continue
                
                # 读取ETF页面
                with open(etf_page_path, 'r', encoding='utf-8') as f:
                    page_content = f.read()
                
                # 获取ETF详细信息
                cursor.execute('''
                SELECT e.*, 
                       GROUP_CONCAT(h.stock_name || '|' || h.weight) as holdings
