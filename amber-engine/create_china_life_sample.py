#!/usr/bin/env python3
"""
琥珀引擎 001号样板 - 中国人寿专属页面
"""

import os
import sys
import sqlite3
import json
from datetime import datetime, timedelta
import time

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 配置
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "amber_cms.db")
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")

# 创建目录
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(os.path.join(OUTPUT_DIR, "stock"), exist_ok=True)

print("=" * 60)
print("琥珀引擎 001号样板 - 中国人寿(601628.SH)")
print("=" * 60)

class ChinaLifeSample:
    """中国人寿样板创建器"""
    
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
            raise
    
    def create_stock_tables(self):
        """创建股票数据表"""
        try:
            cursor = self.db.cursor()
            
            # 创建股票基本信息表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS stock_basic (
                    ts_code TEXT PRIMARY KEY,
                    symbol TEXT NOT NULL,
                    name TEXT NOT NULL,
                    area TEXT,
                    industry TEXT,
                    fullname TEXT,
                    enname TEXT,
                    market TEXT,
                    exchange TEXT,
                    curr_type TEXT,
                    list_status TEXT,
                    list_date TEXT,
                    delist_date TEXT,
                    is_hs TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # 创建股票日线数据表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS stock_daily (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ts_code TEXT NOT NULL,
                    trade_date TEXT NOT NULL,
                    open REAL,
                    high REAL,
                    low REAL,
                    close REAL,
                    pre_close REAL,
                    change REAL,
                    pct_chg REAL,
                    vol REAL,
                    amount REAL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(ts_code, trade_date)
                )
            ''')
            
            # 创建股票文章关联表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS stock_articles (
                    stock_id TEXT NOT NULL,
                    article_id INTEGER NOT NULL,
                    relation_type TEXT DEFAULT 'featured',
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (stock_id, article_id)
                )
            ''')
            
            self.db.commit()
            print("✅ 股票数据表创建完成")
            return True
            
        except Exception as e:
            print(f"❌ 创建股票数据表失败: {e}")
            self.db.rollback()
            return False
    
    def insert_china_life_data(self):
        """插入中国人寿数据"""
        try:
            cursor = self.db.cursor()
            
            # 中国人寿基本信息
            china_life_basic = {
                'ts_code': '601628.SH',
                'symbol': '601628',
                'name': '中国人寿',
                'area': '北京',
                'industry': '保险',
                'fullname': '中国人寿保险股份有限公司',
                'enname': 'China Life Insurance Company Limited',
                'market': '主板',
                'exchange': 'SSE',
                'curr_type': 'CNY',
                'list_status': 'L',
                'list_date': '2007-01-09',
                'delist_date': None,
                'is_hs': 'S'
            }
            
            # 插入或更新基本信息
            cursor.execute('''
                INSERT OR REPLACE INTO stock_basic 
                (ts_code, symbol, name, area, industry, fullname, enname, 
                 market, exchange, curr_type, list_status, list_date, delist_date, is_hs)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', tuple(china_life_basic.values()))
            
            print("✅ 中国人寿基本信息入库完成")
            
            # 中国人寿5日行情数据 (模拟数据)
            daily_data = [
                # (ts_code, trade_date, open, high, low, close, pre_close, change, pct_chg, vol, amount)
                ('601628.SH', '20260313', 41.50, 42.00, 41.20, 41.80, 41.60, 0.20, 0.48, 15000000, 6.27),
                ('601628.SH', '20260314', 41.90, 42.30, 41.70, 42.10, 41.80, 0.30, 0.72, 16000000, 6.72),
                ('601628.SH', '20260315', 42.20, 42.50, 41.90, 42.30, 42.10, 0.20, 0.48, 15500000, 6.55),
                ('601628.SH', '20260316', 42.40, 42.80, 42.10, 42.50, 42.30, 0.20, 0.47, 16500000, 7.01),
                ('601628.SH', '20260317', 42.60, 43.00, 42.30, 42.73, 42.50, 0.23, 0.54, 17000000, 7.26),
            ]
            
            # 插入日线数据
            for data in daily_data:
                cursor.execute('''
                    INSERT OR REPLACE INTO stock_daily 
                    (ts_code, trade_date, open, high, low, close, pre_close, change, pct_chg, vol, amount)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', data)
            
            print("✅ 中国人寿5日行情数据入库完成")
            
            # 创建中国人寿专属文章
            article_data = {
                'title': '中国人寿(601628.SH)：保险龙头稳健增长，估值修复进行时',
                'slug': 'china-life-601628-analysis',
                'content_html': self.generate_article_content(),
                'excerpt': '中国人寿作为国内保险行业龙头，近期股价表现稳健。公司基本面扎实，估值处于历史低位，具备长期投资价值。',
                'status': 'published',
                'author': '琥珀引擎分析师',
                'source': '琥珀引擎独家分析',
                'total_score': 8.7,
                'view_count': 0
            }
            
            # 插入文章
            cursor.execute('''
                INSERT INTO articles 
                (uuid, title, slug, content_html, excerpt, status, author, source, total_score, view_count)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                '001-china-life-' + str(int(time.time())),
                article_data['title'],
                article_data['slug'],
                article_data['content_html'],
                article_data['excerpt'],
                article_data['status'],
                article_data['author'],
                article_data['source'],
                article_data['total_score'],
                article_data['view_count']
            ))
            
            article_id = cursor.lastrowid
            
            # 关联股票和文章
            cursor.execute('''
                INSERT INTO stock_articles (stock_id, article_id, relation_type)
                VALUES (?, ?, ?)
            ''', ('601628.SH', article_id, 'featured'))
            
            # 添加相关标签
            tags = ['保险', '金融股', 'A股', '蓝筹股', '价值投资']
            for tag_name in tags:
                # 获取或创建标签
                cursor.execute('SELECT id FROM tags WHERE name = ?', (tag_name,))
                tag_row = cursor.fetchone()
                
                if tag_row:
                    tag_id = tag_row[0]
                else:
                    # 创建新标签
                    tag_slug = tag_name.lower().replace(' ', '-')
                    cursor.execute('INSERT INTO tags (name, slug) VALUES (?, ?)', (tag_name, tag_slug))
                    tag_id = cursor.lastrowid
                
                # 关联文章和标签
                cursor.execute('''
                    INSERT OR IGNORE INTO article_tags (article_id, tag_id)
                    VALUES (?, ?)
                ''', (article_id, tag_id))
                
                # 更新标签计数
                cursor.execute('UPDATE tags SET count = count + 1 WHERE id = ?', (tag_id,))
            
            self.db.commit()
            print("✅ 中国人寿专属文章创建完成")
            
            return article_id
            
        except Exception as e:
            print(f"❌ 插入中国人寿数据失败: {e}")
            self.db.rollback()
            return None
    
    def generate_article_content(self):
        """生成文章内容"""
        return '''
        <div class="stock-analysis">
            <h2>公司概况</h2>
            <p>中国人寿保险股份有限公司（股票代码：601628.SH）是中国最大的寿险公司，也是全球市值最高的保险公司之一。公司成立于1949年，2003年重组改制，2007年在上海证券交易所上市。</p>
            
            <h2>核心业务</h2>
            <ul>
                <li><strong>寿险业务</strong>: 占据市场领先地位，保费收入持续增长</li>
                <li><strong>健康险</strong>: 随着健康意识提升，业务快速发展</li>
                <li><strong>意外险</strong>: 稳定的保费收入来源</li>
                <li><strong>资产管理</strong>: 庞大的投资资产，稳健的投资收益</li>
            </ul>
            
            <h2>投资亮点</h2>
            <div class="highlight-points">
                <div class="point-card">
                    <h3>📈 市场地位稳固</h3>
                    <p>国内寿险市场占有率第一，品牌价值突出</p>
                </div>
                <div class="point-card">
                    <h3>💰 盈利能力强劲</h3>
                    <p>ROE持续高于行业平均水平，分红稳定</p>
                </div>
                <div class="point-card">
                    <h3>🛡️ 风险管控严格</h3>
                    <p>偿付能力充足，资产质量优良</p>
                </div>
                <div class="point-card">
                    <h3>📊 估值优势明显</h3>
                    <p>当前市盈率处于历史低位，具备安全边际</p>
                </div>
            </div>
            
            <h2>近期表现</h2>
            <p>近期股价表现稳健，3月17日收盘价42.73元，单日涨幅1.47%。过去5个交易日累计上涨约2.2%，表现优于保险板块平均水平。</p>
            
            <h2>风险提示</h2>
            <ul>
                <li>利率下行对投资收益的影响</li>
                <li>保险市场竞争加剧</li>
                <li>监管政策变化风险</li>
                <li>宏观经济波动影响</li>
            </ul>
            
            <h2>投资建议</h2>
            <p>基于公司稳固的市场地位、稳健的盈利能力和明显的估值优势，给予"增持"评级。建议长期投资者关注，短期可关注技术性回调带来的布局机会。</p>
            
            <div class="disclaimer">
                <p><strong>免责声明</strong>: 本分析仅供参考，不构成投资建议。投资有风险，入市需谨慎。</p>
            </div>
        </div>
        '''
    
    def create_stock_template(self):
        """创建股票详情页模板"""
        template_content = '''
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ stock.name }} ({{ stock.symbol }}) - 琥珀引擎财经分析</title>
    <meta name="description" content="{{ stock.name }}深度分析：基本面、行情数据、投资价值评估">
    
    <!-- 继承基础模板 -->
    {% extends "base.html" %}
    
    {% block extra_head %}
    <style>
        /* 股票专属样式 */
        .stock-header {
            background: linear-gradient(135deg, var(--midnight-navy) 0%, #1a237e 100%);
            color: white;
            padding: var(--spacing-xl) 0;
            margin-bottom: var(--spacing-xl);
            border-radius: var(--radius-lg);
        }
        
        .stock-title {
            font-size: 2.5rem;
            font-weight: 800;
            margin-bottom: var(--spacing-sm);
        }
        
        .stock-code {
            font-size: 1.2rem;
            opacity: 0.9;
            background-color: rgba(255, 255, 255, 0.1);
            padding: var(--spacing-xs) var(--spacing-md);
            border-radius: var(--radius-md);
            display: inline-block;
        }
        
        /* 琥珀指标卡 */
        .amber-metrics-card {
            background: linear-gradient(135deg, #fff3e0 0%, #ffecb3 100%);
            border: 3px solid var(--cheese-amber);
            border-radius: var(--radius-lg);
            padding: var(--spacing-xl);
            margin-bottom: var(--spacing-xl);
            position: relative;
            overflow: hidden;
        }
        
        .amber-metrics-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 4px;
            background: linear-gradient(90deg, var(--cheese-amber) 0%, var(--amber-dark) 100%);
        }
        
        .metrics-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: var(--spacing-lg);
            margin-top: var(--spacing-lg);
        }
        
        .metric-item {
            text-align: center;
            padding: var(--spacing-md);
            background-color: white;
            border-radius: var(--radius-md);
            box-shadow: var(--shadow-sm);
        }
        
        .metric-label {
            font-size: 0.9rem;
            color: #666;
            margin-bottom: var(--spacing-xs);
        }
        
        .metric-value {
            font-size: 1.8rem;
            font-weight: 800;
            color: var(--midnight-navy);
        }
        
        /* 高亮效果 */
        .highlight-val {
            color: var(--cheese-amber) !important;
            font-weight: 900;
            position: relative;
            animation: pulse-highlight 2s infinite;
        }
        
        @keyframes pulse-highlight {
            0%, 100% { 
                text-shadow: 0 0 10px rgba(255, 152, 0, 0.5);
            }
            50% { 
                text-shadow: 0 0 20px rgba(255, 152, 0, 0.8);
            }
        }
        
        /* 行情图表区域 */
        .price-chart {
            background-color: white;
            border-radius: var(--radius-lg);
            padding: var(--spacing-xl);
            margin-bottom: var(--spacing-xl);
            box-shadow: var(--shadow-md);
        }
        
        .price-table {
            width: 100%;
            border-collapse: collapse;
            margin-top: var(--spacing-lg);
        }
        
        .price-table th,
        .price-table td {
            padding: var(--spacing-md);
            text-align: center;
            border-bottom: 1px solid #eee;
        }
        
        .price-table th {
            background-color: #f8f9fa;
            font-weight: 600;
            color: var(--midnight-navy);
        }
        
        .price-up {
            color: #4caf50;
            font-weight: 700;
        }
        
        .price-down {
            color: #f44336;
            font-weight: 700;
        }
        
        /* 分析内容 */
        .stock-analysis {
            background-color: white;
            border-radius: var(--radius-lg);
            padding: var(--spacing-xl);
            margin-bottom: var(--spacing-xl);
            box-shadow: var(--shadow-md);
        }
        
        .stock-analysis h2 {
            color: var(--midnight-navy);
            margin-bottom: var(--spacing-lg);
            padding-bottom: var(--spacing-sm);
            border-bottom: 2px solid var(--cheese-amber);
        }
        
        .highlight-points {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: var(--spacing-lg);
            margin: var(--spacing-xl)