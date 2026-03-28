#!/usr/bin/env python3
"""
琥珀引擎 - 批量股票页面生成器 (第二部分)
"""

import os
import sys
import sqlite3
import json
import time
from datetime import datetime, timedelta
import random
from typing import List, Dict, Any

# 继续 StockPageGenerator 类
class StockPageGenerator:
    """股票页面批量生成器"""
    
    def get_rating(self, score: float) -> str:
        """根据评分获取评级"""
        if score >= 9.0:
            return "强烈推荐"
        elif score >= 8.0:
            return "推荐"
        elif score >= 7.0:
            return "增持"
        elif score >= 6.0:
            return "持有"
        else:
            return "观望"
    
    def save_stock_page(self, stock_data: Dict, html_content: str) -> bool:
        """保存股票页面"""
        try:
            stock = stock_data["stock"]
            
            # 创建股票目录
            stock_dir = os.path.join(OUTPUT_DIR, "stock", stock["symbol"])
            os.makedirs(stock_dir, exist_ok=True)
            
            # 保存HTML文件
            output_path = os.path.join(stock_dir, "index.html")
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            # 创建符号链接（简化访问）
            symlink_path = os.path.join(OUTPUT_DIR, "stock", f"{stock['symbol']}.html")
            if os.path.exists(symlink_path):
                os.remove(symlink_path)
            os.symlink(f"{stock['symbol']}/index.html", symlink_path)
            
            # 保存数据到数据库
            self.save_to_database(stock_data)
            
            print(f"✅ 页面生成完成: {stock['name']} ({stock['symbol']})")
            return True
            
        except Exception as e:
            print(f"❌ 保存股票页面失败 {stock_data['stock']['name']}: {e}")
            return False
    
    def save_to_database(self, stock_data: Dict):
        """保存数据到数据库"""
        try:
            cursor = self.db.cursor()
            stock = stock_data["stock"]
            
            # 保存股票基本信息
            cursor.execute('''
                INSERT OR REPLACE INTO stock_basic 
                (ts_code, symbol, name, industry, created_at)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                stock["ts_code"],
                stock["symbol"],
                stock["name"],
                stock["industry"],
                datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ))
            
            # 保存日线数据
            for daily in stock_data["daily_data"]:
                cursor.execute('''
                    INSERT OR REPLACE INTO stock_daily 
                    (ts_code, trade_date, open, high, low, close, pct_chg, vol, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    stock["ts_code"],
                    daily["trade_date"],
                    daily["open"],
                    daily["high"],
                    daily["low"],
                    daily["close"],
                    daily["pct_chg"],
                    daily["vol"],
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                ))
            
            # 创建分析文章
            article_content = self.generate_article_content(stock_data)
            cursor.execute('''
                INSERT INTO articles 
                (uuid, title, slug, content_html, excerpt, status, author, source, total_score, view_count, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                f"stock-{stock['symbol']}-{int(time.time())}",
                f"{stock['name']}({stock['symbol']})深度分析报告",
                f"stock-analysis-{stock['symbol'].lower()}",
                article_content,
                f"{stock['name']}作为{stock['industry']}行业的重要公司，具备良好的投资价值。",
                "published",
                "琥珀引擎分析师",
                "琥珀引擎独家分析",
                stock_data["rich_score"],
                0,
                datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ))
            
            article_id = cursor.lastrowid
            
            # 关联股票和文章
            cursor.execute('''
                INSERT OR REPLACE INTO stock_articles 
                (stock_id, article_id, relation_type, created_at)
                VALUES (?, ?, ?, ?)
            ''', (
                stock["ts_code"],
                article_id,
                "analysis",
                datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ))
            
            self.db.commit()
            
        except Exception as e:
            print(f"❌ 数据库保存失败 {stock['name']}: {e}")
            self.db.rollback()
    
    def generate_article_content(self, stock_data: Dict) -> str:
        """生成文章内容"""
        stock = stock_data["stock"]
        
        return f'''
        <div class="stock-analysis">
            <h2>公司概况</h2>
            <p>{stock['name']} ({stock['ts_code']}) 是中国{stock['industry']}行业的重要上市公司，在行业内具有重要地位。公司业务稳健，财务状况良好。</p>
            
            <h2>核心业务</h2>
            <ul>
                <li><strong>主营业务</strong>: 在{stock['industry']}领域具有核心竞争力</li>
                <li><strong>市场地位</strong>: 行业内的领先企业</li>
                <li><strong>技术优势</strong>: 具备较强的技术创新能力</li>
                <li><strong>客户基础</strong>: 拥有稳定的客户群体</li>
            </ul>
            
            <h2>投资亮点</h2>
            <div class="highlight-points">
                <div class="point-card">
                    <h3>📈 行业前景广阔</h3>
                    <p>{stock['industry']}行业未来发展空间巨大</p>
                </div>
                <div class="point-card">
                    <h3>💰 盈利能力稳定</h3>
                    <p>公司盈利模式清晰，现金流充裕</p>
                </div>
                <div class="point-card">
                    <h3>🛡️ 风险控制良好</h3>
                    <p>风险管理体系完善，抗风险能力强</p>
                </div>
                <div class="point-card">
                    <h3>📊 估值合理</h3>
                    <p>当前估值水平具有吸引力</p>
                </div>
            </div>
            
            <h2>近期表现</h2>
            <p>近期股价表现稳健，最新交易日涨跌幅{stock_data['latest_pct_chg']:.2f}%。过去5个交易日平均价格{stock_data['avg_price']:.2f}元。</p>
            
            <h2>风险提示</h2>
            <ul>
                <li>行业政策变化风险</li>
                <li>市场竞争加剧风险</li>
                <li>宏观经济波动风险</li>
                <li>公司经营风险</li>
            </ul>
            
            <h2>投资建议</h2>
            <p>基于公司良好的基本面和合理的估值水平，给予"{self.get_rating(stock_data['rich_score'])}"评级。建议投资者关注公司长期发展价值。</p>
            
            <div class="disclaimer">
                <p><strong>免责声明</strong>: 本分析仅供参考，不构成投资建议。投资有风险，入市需谨慎。</p>
            </div>
        </div>
        '''
    
    def generate_homepage(self, latest_stocks: List[Dict]):
        """生成首页"""
        try:
            print("\n🏠 生成首页...")
            
            # 加载基础模板
            base_template = self.load_template("base_jinja2.html")
            
            # 生成首页内容
            homepage_content = self.render_homepage_content(latest_stocks)
            
            # 替换模板变量
            page_html = base_template
            
            # 替换标题
            page_html = page_html.replace(
                "{% block title %}琥珀引擎 - Cheese Intelligence{% endblock %}",
                "琥珀引擎 - 财经品牌独立站"
            )
            
            # 替换描述
            page_html = page_html.replace(
                "{% block description %}财经品牌独立站 - 数据库驱动 + 静态化生成的专业媒体架构{% endblock %}",
                "琥珀引擎：专业的财经分析平台，提供股票研报、行业分析、投资建议"
            )
            
            # 替换内容
            page_html = page_html.replace("{% block content %}", homepage_content)
            
            # 替换最后更新时间
            last_updated = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            page_html = page_html.replace("{% block last_updated %}{{ last_updated }}{% endblock %}", last_updated)
            
            # 保存首页
            output_path = os.path.join(OUTPUT_DIR, "index.html")
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(page_html)
            
            print(f"✅ 首页生成完成: {output_path}")
            return True
            
        except Exception as e:
            print(f"❌ 生成首页失败: {e}")
            return False
    
    def render_homepage_content(self, latest_stocks: List[Dict]) -> str:
        """渲染首页内容"""
        # 最新文章部分
        latest_articles = ""
        for i, stock_data in enumerate(latest_stocks[:10], 1):
            stock = stock_data["stock"]
            latest_articles += f'''
            <div class="finance-card">
                <div class="card-header">
                    <h3 class="card-title">
                        <span class="card-number">#{i:03d}</span> {stock['name']}({stock['symbol']})
                    </h3>
                    <div class="card-meta">
                        <span class="source-tag">{stock['industry']}</span>
                        <span class="time-tag">今日更新</span>
                        <span class="score-tag">RICH: {stock_data['rich_score']}</span>
                    </div>
                </div>
                <div class="card-content">
                    <p>{stock['name']}作为{stock['industry']}行业的重要公司，具备良好的投资价值。最新价格{stock_data['daily_data'][-1]['close']:.2f}元，日涨跌幅{stock_data['latest_pct_chg']:.2f}%。</p>
                </div>
                <div class="card-footer">
                    <a href="/stock/{stock['symbol']}.html" class="tags">查看详细分析 →</a>
                </div>
            </div>
            '''
        
        # 板块看板
        sectors = {
            "金融": ["银行", "保险", "证券"],
            "消费": ["白酒", "家电", "食品饮料"],
            "科技": ["人工智能", "消费电子", "金融科技"],
            "能源": ["石油", "煤炭", "电力"]
        }
        
        sector_cards = ""
        for sector_name, industries in sectors.items():
            sector_cards += f'''
            <div class="finance-card">
                <div class="card-header">
                    <h3 class="card-title">{sector_name}板块</h3>
                    <div class="card-meta">
                        <span class="source-tag">热门行业</span>
                    </div>
                </div>
                <div class="card-content">
                    <p>包含: {', '.join(industries)}等行业</p>
                    <div class="mt-3">
                        <a href="/sector/{sector_name}.html" class="tags">查看{sector_name}板块</a>
                    </div>
                </div>
            </div>
            '''
        
        # 构建首页内容
        content = f'''
        <!-- 英雄区域 -->
        <section class="stock-header">
            <div class="container">
                <h1 class="stock-title">琥珀引擎</h1>
                <div class="stock-code">财经品牌独立站</div>
                <p class="mt-3">数据库驱动 + 静态化生成的专业媒体架构 | 最新更新: {datetime.now().strftime('%Y-%m-%d')}</p>
            </div>
        </section>
        
        <div class="container">
            <!-- 琥珀精选 -->
            <section class="dashboard-section">
                <div class="insider-header">
                    <span class="insider-badge">🔥 琥珀精选</span>
                    <h2 class="section-title">最新研报</h2>
                </div>
                
                {latest_articles}
            </section>
            
            <!-- 板块看板 -->
            <section class="dashboard-section">
                <h2 class="section-title">📊 板块看板</h2>
                <div class="grid-4">
                    {sector_cards}
                </div>
            </section>
            
            <!-- 统计信息 -->
            <section class="dashboard-section">
                <h2 class="section-title">📈 平台统计</h2>
                <div class="grid-4">
                    <div class="finance-card">
                        <div class="card-header">
                            <h3 class="card-title">覆盖股票</h3>
                        </div>
                        <div class="card-content">
                            <div class="metric-value" style="font-size: 2.5rem;">{len(latest_stocks)}+</div>
                            <p class="metric-label">A股核心标的</p>
                        </div>
                    </div>
                    
                    <div class="finance-card">
                        <div class="card-header">
                            <h3 class="card-title">分析报告</h3>
                        </div>
                        <div class="card-content">
                            <div class="metric-value" style="font-size: 2.5rem;">{len(latest_stocks)}+</div>
                            <p class="metric-label">深度分析文章</p>
                        </div>
                    </div>
                    
                    <div class="finance-card">
                        <div class="card-header">
                            <h3 class="card-title">数据更新</h3>
                        </div>
                        <div class="card-content">
                            <div class="metric-value" style="font-size: 2.5rem;">每日</div>
                            <p class="metric-label">行情数据更新</p>
                        </div>
                    </div>
                    
                    <div class="finance-card">
                        <div class="card-header">
                            <h3 class="card-title">RICH评分</h3>
                        </div>
                        <div class="card-content">
                            <div class="metric-value" style="font-size: 2.5rem;">8.2</div>
                            <p class="metric-label">平均评分</p>
                        </div>
                    </div>
                </div>
            </section>
            
            <!-- 快速链接 -->
            <section class="dashboard-section">
                <h2 class="section-title">🔗 快速链接</h2>
                <div class="grid-4">
                    <a href="/stocks.html" class="finance-card">
                        <div class="card-header">
                            <h3 class="card-title">📈 所有股票</h3>
                        </div>
                        <div class="card-content">
                            <p>查看所有A股核心标的分析报告</p>
                        </div>
                    </a>
                    
                    <a href="/categories.html" class="finance-card">
                        <div class="card-header">
                            <h3 class="card-title">🏷️ 分类浏览</h3>
                        </div>
                        <div class="card-content">
                            <p>按行业分类查看股票</p>
                        </div>
                    </a>
                    
                    <a href="/tags.html" class="finance-card">
                        <div class="card-header">
                            <h3 class="card-title">☁️ 标签云</h3>
                        </div>
                        <div class="card-content">
                            <p>热门标签和关键词</p>
                        </div>
                    </a>
                    
                    <a href="/archives.html" class="finance-card">
                        <div class="card-header">
                            <h3 class="card-title">📅 文章归档</h3>
                        </div>
                        <div class="card-content">
                            <p>按时间查看历史文章</p>
                        </div>
                    </a>
                </div>
            </section>
        </div>
        '''
        
        return content
    
    def copy_static_files(self):
        """复制静态文件"""
        print("\n📁 复制静态文件...")
        
        try:
            # 复制CSS文件
            css_source = os.path.join(STATIC_DIR, "css", "amber-v2.2.min.css")
            css_dest = os.path.join(OUTPUT_DIR, "static", "css", "amber-v2.2.min.css")
            
            os.makedirs(os.path.dirname(css_dest), exist_ok=True)
            
            with open(css_source, 'r', encoding='utf-8') as f:
                css_content = f.read()
            
            with open(css_dest, 'w', encoding='utf-8') as f:
                f.write(css_content)
            
            print(f"✅ CSS文件复制完成: {css_dest}")
            
            # 创建占位JS文件
            js_dest = os.path.join(OUTPUT_DIR, "static", "js", "amber-engine.min.js")
            os.makedirs(os.path.dirname(js_dest), exist_ok=True)
            
            with open(js_dest, 'w', encoding='utf-8') as f:
                f.write('// 琥珀引擎 JavaScript 文件\nconsole.log("琥珀引擎已加载");')
            
            print(f"✅ JS文件创建完成: {js_dest}")
            
            return True
            
        except Exception as e:
            print(f"❌ 复制静态文件失败: {e}")
            return False
    
    def generate_sitemap(self, stocks: List[Dict]):
        """生成网站地图"""
        try:
            print("\n🗺️  生成网站地图...")
            
            sitemap_content = '''<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http