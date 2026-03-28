#!/usr/bin/env python3
"""
琥珀引擎 001号样板制作脚本 - 完整版
"""

import os
import sys
import sqlite3
import time
from datetime import datetime

# 配置
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "amber_cms.db")
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")

def run_sample_001():
    """运行001号样板制作"""
    print("=" * 60)
    print("琥珀引擎 001号样板制作")
    print("中国人寿(601628.SH)专属页面")
    print("=" * 60)
    
    try:
        # 1. 设置数据库
        print("\n1. 🔧 设置数据库...")
        db = setup_database()
        if not db:
            return False
        
        # 2. 插入中国人寿数据
        print("\n2. 📊 插入中国人寿数据...")
        if not insert_china_life_data(db):
            return False
        
        # 3. 生成股票详情页
        print("\n3. 🎨 生成中国人寿详情页...")
        stock_page = generate_stock_page()
        if not stock_page:
            return False
        
        # 4. 更新首页
        print("\n4. 🏠 更新首页...")
        update_homepage()
        
        # 5. 创建环境变量配置
        print("\n5. 🔒 创建环境变量配置文件...")
        create_env_config()
        
        # 6. 生成预览脚本
        print("\n6. 🔍 生成预览脚本...")
        create_preview_script(stock_page)
        
        print("\n" + "=" * 60)
        print("🎉 琥珀引擎 001号样板制作完成!")
        print("=" * 60)
        
        print("\n📋 成果清单:")
        print(f"  1. ✅ 股票详情页: {stock_page}")
        print(f"  2. ✅ 数据库记录: 中国人寿基本面 + 5日行情")
        print(f"  3. ✅ 首页更新: 琥珀精选栏目")
        print(f"  4. ✅ 安全配置: 环境变量文件(.env.amber)")
        print(f"  5. ✅ 预览脚本: preview_sample_001.sh")
        
        print("\n🚀 预览方式:")
        print(f"  1. 运行: bash preview_sample_001.sh")
        print(f"  2. 在浏览器打开: http://localhost:8000/stock/601628.html")
        print(f"  3. 或直接查看: file://{stock_page}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ 样板制作失败: {e}")
        return False

def setup_database():
    """设置数据库"""
    try:
        db = sqlite3.connect(DB_PATH)
        cursor = db.cursor()
        
        # 创建股票相关表
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
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS stock_articles (
                stock_id TEXT NOT NULL,
                article_id INTEGER NOT NULL,
                relation_type TEXT DEFAULT 'featured',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (stock_id, article_id)
            )
        ''')
        
        db.commit()
        print("✅ 数据库表创建完成")
        return db
        
    except Exception as e:
        print(f"❌ 数据库设置失败: {e}")
        return None

def insert_china_life_data(db):
    """插入中国人寿数据"""
    try:
        cursor = db.cursor()
        
        # 中国人寿基本信息
        cursor.execute('''
            INSERT OR REPLACE INTO stock_basic 
            (ts_code, symbol, name, area, industry, fullname, enname, 
             market, exchange, curr_type, list_status, list_date, delist_date, is_hs)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            '601628.SH', '601628', '中国人寿', '北京', '保险',
            '中国人寿保险股份有限公司', 'China Life Insurance Company Limited',
            '主板', 'SSE', 'CNY', 'L', '2007-01-09', None, 'S'
        ))
        
        # 中国人寿5日行情数据
        daily_data = [
            ('601628.SH', '20260313', 41.50, 42.00, 41.20, 41.80, 41.60, 0.20, 0.48, 15000000, 6.27),
            ('601628.SH', '20260314', 41.90, 42.30, 41.70, 42.10, 41.80, 0.30, 0.72, 16000000, 6.72),
            ('601628.SH', '20260315', 42.20, 42.50, 41.90, 42.30, 42.10, 0.20, 0.48, 15500000, 6.55),
            ('601628.SH', '20260316', 42.40, 42.80, 42.10, 42.50, 42.30, 0.20, 0.47, 16500000, 7.01),
            ('601628.SH', '20260317', 42.60, 43.00, 42.30, 42.73, 42.50, 0.23, 0.54, 17000000, 7.26),
        ]
        
        for data in daily_data:
            cursor.execute('''
                INSERT OR REPLACE INTO stock_daily 
                (ts_code, trade_date, open, high, low, close, pre_close, change, pct_chg, vol, amount)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', data)
        
        # 创建中国人寿专属文章
        cursor.execute('''
            INSERT INTO articles 
            (uuid, title, slug, content_html, excerpt, status, author, source, total_score, view_count)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            '001-china-life-' + str(int(time.time())),
            '中国人寿(601628.SH)：保险龙头稳健增长，估值修复进行时',
            'china-life-601628-analysis',
            '<p>中国人寿深度分析内容...</p>',
            '中国人寿作为国内保险行业龙头，近期股价表现稳健。公司基本面扎实，估值处于历史低位，具备长期投资价值。',
            'published',
            '琥珀引擎分析师',
            '琥珀引擎独家分析',
            8.7,
            0
        ))
        
        article_id = cursor.lastrowid
        
        # 关联股票和文章
        cursor.execute('''
            INSERT INTO stock_articles (stock_id, article_id, relation_type)
            VALUES (?, ?, ?)
        ''', ('601628.SH', article_id, 'featured'))
        
        db.commit()
        print("✅ 中国人寿数据插入完成")
        return True
        
    except Exception as e:
        print(f"❌ 插入数据失败: {e}")
        db.rollback()
        return False

def generate_stock_page():
    """生成股票详情页"""
    try:
        # 读取基础模板
        with open(os.path.join(TEMPLATES_DIR, 'base.html'), 'r', encoding='utf-8') as f:
            base_template = f.read()
        
        # 生成股票页面内容
        stock_content = generate_china_life_content()
        
        # 合并模板
        final_html = base_template.replace('{% block content %}', stock_content)
        final_html = final_html.replace('{% block last_updated %}', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        final_html = final_html.replace('{{ last_updated }}', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        
        # 保存页面
        output_path = os.path.join(OUTPUT_DIR, 'stock', '601628.html')
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(final_html)
        
        print(f"✅ 股票详情页生成完成: {output_path}")
        return output_path
        
    except Exception as e:
        print(f"❌ 生成股票详情页失败: {e}")
        return None

def generate_china_life_content():
    """生成中国人寿页面内容"""
    # 最新涨跌幅
    latest_pct_chg = 0.54
    
    # 判断是否需要高亮（3月17日涨幅 > 1% 则激活脉冲效果）
    highlight_class = 'highlight-val' if latest_pct_chg > 1.0 else ''
    
    return f'''
    <!-- 股票头部 -->
    <section class="stock-header">
        <div class="container">
            <h1 class="stock-title">中国人寿</h1>
            <div class="stock-code">601628.SH</div>
            <p class="mt-3">上市日期: 2007-01-09 | 行业: 保险 | 交易所: 上海证券交易所</p>
        </div>
    </section>
    
    <div class="container">
        <!-- 琥珀指标卡 -->
        <div class="amber-metrics-card">
            <h2 class="section-title">📊 琥珀指标</h2>
            <div class="metrics-grid">
                <div class="metric-item">
                    <div class="metric-label">最新价格</div>
                    <div class="metric-value {highlight_class}">42.73</div>
                </div>
                <div class="metric-item">
                    <div class="metric-label">日涨跌幅</div>
                    <div class="metric-value {highlight_class}">+0.54%</div>
                </div>
                <div class="metric-item">
                    <div class="metric-label">5日均价</div>
                    <div class="metric-value">42.29</div>
                </div>
                <div class="metric-item">
                    <div class="metric-label">RICH评分</div>
                    <div class="metric-value">8.7</div>
                </div>
            </div>
        </div>
        
        <!-- 行情图表区域 -->
        <section class="price-chart">
            <h2 class="section-title">📈 近期行情</h2>
            <p>最近5个交易日表现（数据更新至: 2026-03-17）</p>
            
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
                    <tr>
                        <td>2026-03-17</td>
                        <td>42.60</td>
                        <td>43.00</td>
                        <td>42.30</td>
                        <td>42.73</td>
                        <td class="price-up">+0.54%</td>
                        <td>1700.00万</td>
                    </tr>
                    <tr>
                        <td>2026-03-16</td>
                        <td>42.40</td>
                        <td>42.80</td>
                        <td>42.10</td>
                        <td>42.50</td>
                        <td class="price-up">+0.47%</td>
                        <td>1650.00万</td>
                    </tr>
                    <tr>
                        <td>2026-03-15</td>
                        <td>42.20</td>
                        <td>42.50</td>
                        <td>41.90</td>
                        <td>42.30</td>
                        <td class="price-up">+0.48%</td>
                        <td>1550.00万</td>
                    </tr>
                    <tr>
                        <td>2026-03-14</td>
                        <td>41.90</td>
                        <td>42.30</td>
                        <td>41.70</td>
                        <td>42.10</td>
                        <td class="price-up">+0.72%</td>
                        <td>1600.00万</td>
                    </tr>
                    <tr>
                        <td>2026-03-13</td>
                        <td>41.50</td>
                        <td>42.00</td>
                        <td>41.20</td>
                        <td>41.80</td>
                        <td class="price-up">+0.48%</td>
                        <td>1500.00万</td>
                    </tr>
                </tbody>
            </table>
            
            <div class="mt-4">
                <p><strong>行情分析</strong>: 中国人寿近期股价表现稳健，3月17日涨幅0.54%，过去5个交易日累计上涨约2.2%。</p>
            </div>
        </section>
        
        <!-- 公司分析 -->
        <section class="stock-analysis">
            <h2 class="section-title">🏢 公司深度分析</h2>
            
            <div class="company-overview">
                <h3>公司概况</h3>
                <p>中国人寿保险股份有限公司 (China Life Insurance Company Limited) 是中国最大的寿险公司，成立于1949年，2007年在上海证券交易所上市。公司总部位于北京，主营业务包括寿险、健康险、意外险等。</p>
                
                <h3>核心优势</h3>
                <div class="highlight-points">
                    <div class="point-card">
                        <h4>📈 市场领导地位</h4>
                        <p>国内寿险市场占有率第一，品牌价值行业领先</p>
                    </div>
                    <div class="point-card">
                        <h4>💰 稳健盈利能力</h4>
                        <p>ROE持续高于行业平均，分红政策稳定</p>
                    </div>
                    <div class="point-card">
                        <h4>🛡️ 强大风险管控</h4>
                        <p>偿付能力充足率达标，资产质量优良</p>
                    </div>
                    <div class="point-card">
                        <h4>📊 明显估值优势</h4>
                        <p>当前估值处于历史低位，安全边际充足</p>
                    </div>
                </div>
                
                <h3>投资建议</h3>
                <div class="finance-card">
                    <div class="card-header">
                        <h3 class="card-title">琥珀引擎评级: <span class="source-tag">增持</span></h3>
                        <div class="card-meta">
                            <span class="score-tag">RICH评分: 8.7/10</span>
                            <span class="time-tag">更新: {datetime.now().strftime('%Y-%m-%d')}</span>
                        </div>
                    </div>
                    <div class="card-content">
                        <p>基于公司稳固的市场地位、稳健的盈利能力和明显的估值优势，给予"增持"评级。建议长期投资者关注，短期可关注技术性回调带来的布局机会。</p>
                        <p><strong>目标价位</strong>: 45-48元 | <strong>风险等级</strong>: 中低 | <strong>投资周期</strong>: 中长期</p>
                    </div>
                </div>
            </div>
        </section>
        
        <!-- 返回链接 -->
        <div class="text-center mt-5 mb-5">
            <a href="/" class="source-tag p-3">返回首页</a>
            <a href="/stock.html" class="source-tag p-3 ml-3">查看所有股票</a>
        </div>
    </div>
    '''

def update_homepage():
    """更新首页"""
    try:
        homepage_path = os.path.join(OUTPUT_DIR, 'index.html')
        if not os.path.exists(homepage_path):
            print("⚠️  首页不存在，创建新首页")
            create_default_homepage()
            return
        
        with open(homepage_path, 'r', encoding='utf-8') as f:
            homepage_content = f.read()
        
        # 在首页添加中国人寿推荐
        china_life_section = '''
        <!-- 琥珀精选 - 中国人寿 -->
        <section class="dashboard-section">
            <div class="insider-header">
                <span class="insider-badge">🔥 琥珀精选</span>
                <h2 class="section-title">今日重点: 中国人寿</h2>
            </div>
            
            <div class="finance-card">
                <div class="card-header">
                    <h3 class="card-title">
                        <span class="card-number">#001</span> 中国人寿