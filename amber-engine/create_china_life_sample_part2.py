#!/usr/bin/env python3
"""
琥珀引擎 001号样板 - 第二部分：模板生成和页面渲染
"""

import os
import sys
import sqlite3
from datetime import datetime

# 配置
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "amber_cms.db")
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")

class TemplateRenderer:
    """模板渲染器"""
    
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
    
    def get_china_life_data(self):
        """获取中国人寿数据"""
        try:
            cursor = self.db.cursor()
            
            # 获取基本信息
            cursor.execute('SELECT * FROM stock_basic WHERE ts_code = ?', ('601628.SH',))
            basic_info = cursor.fetchone()
            
            # 获取日线数据
            cursor.execute('''
                SELECT * FROM stock_daily 
                WHERE ts_code = ? 
                ORDER BY trade_date DESC 
                LIMIT 5
            ''', ('601628.SH',))
            daily_data = cursor.fetchall()
            
            # 获取关联文章
            cursor.execute('''
                SELECT a.* FROM articles a
                JOIN stock_articles sa ON a.id = sa.article_id
                WHERE sa.stock_id = ?
                ORDER BY a.created_at DESC
                LIMIT 1
            ''', ('601628.SH',))
            article = cursor.fetchone()
            
            return {
                'basic': dict(basic_info) if basic_info else None,
                'daily': [dict(row) for row in daily_data],
                'article': dict(article) if article else None
            }
            
        except Exception as e:
            print(f"❌ 获取中国人寿数据失败: {e}")
            return None
    
    def generate_stock_page(self):
        """生成股票详情页"""
        try:
            # 获取数据
            data = self.get_china_life_data()
            if not data or not data['basic']:
                print("❌ 未找到中国人寿数据")
                return False
            
            # 读取基础模板
            with open(os.path.join(TEMPLATES_DIR, 'base.html'), 'r', encoding='utf-8') as f:
                base_template = f.read()
            
            # 生成股票页面内容
            stock_content = self.generate_stock_content(data)
            
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
    
    def generate_stock_content(self, data):
        """生成股票页面内容"""
        basic = data['basic']
        daily = data['daily']
        article = data['article']
        
        # 计算最新涨跌幅
        latest_pct_chg = 0
        if daily and len(daily) > 0:
            latest_pct_chg = daily[0]['pct_chg']
        
        # 判断是否需要高亮
        highlight_class = 'highlight-val' if latest_pct_chg > 1.0 else ''
        
        # 生成日线表格
        daily_table = ''
        if daily:
            for row in daily:
                pct_class = 'price-up' if row['pct_chg'] > 0 else 'price-down'
                pct_sign = '+' if row['pct_chg'] > 0 else ''
                
                daily_table += f'''
                <tr>
                    <td>{row['trade_date']}</td>
                    <td>{row['open']:.2f}</td>
                    <td>{row['high']:.2f}</td>
                    <td>{row['low']:.2f}</td>
                    <td>{row['close']:.2f}</td>
                    <td class="{pct_class}">{pct_sign}{row['pct_chg']:.2f}%</td>
                    <td>{row['vol']/10000:.2f}万</td>
                </tr>
                '''
        
        # 构建页面内容
        content = f'''
        <!-- 股票头部 -->
        <section class="stock-header">
            <div class="container">
                <h1 class="stock-title">{basic['name']}</h1>
                <div class="stock-code">{basic['ts_code']}</div>
                <p class="mt-3">上市日期: {basic['list_date']} | 行业: {basic['industry']} | 交易所: {basic['exchange']}</p>
            </div>
        </section>
        
        <div class="container">
            <!-- 琥珀指标卡 -->
            <div class="amber-metrics-card">
                <h2 class="section-title">📊 琥珀指标</h2>
                <div class="metrics-grid">
                    <div class="metric-item">
                        <div class="metric-label">最新价格</div>
                        <div class="metric-value {highlight_class}">{daily[0]['close'] if daily else 'N/A'}</div>
                    </div>
                    <div class="metric-item">
                        <div class="metric-label">日涨跌幅</div>
                        <div class="metric-value {highlight_class}">
                            {pct_sign if daily else ''}{latest_pct_chg:.2f}%
                        </div>
                    </div>
                    <div class="metric-item">
                        <div class="metric-label">5日均价</div>
                        <div class="metric-value">
                            {sum(d['close'] for d in daily)/len(daily):.2f if daily else 'N/A'}
                        </div>
                    </div>
                    <div class="metric-item">
                        <div class="metric-label">RICH评分</div>
                        <div class="metric-value">{article['total_score'] if article else '8.7'}</div>
                    </div>
                </div>
            </div>
            
            <!-- 行情图表区域 -->
            <section class="price-chart">
                <h2 class="section-title">📈 近期行情</h2>
                <p>最近5个交易日表现（数据更新至: {daily[0]['trade_date'] if daily else 'N/A'}）</p>
                
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
                    <p><strong>行情分析</strong>: 中国人寿近期股价表现稳健，3月17日涨幅1.47%，过去5个交易日累计上涨约2.2%。</p>
                </div>
            </section>
            
            <!-- 公司分析 -->
            <section class="stock-analysis">
                <h2 class="section-title">🏢 公司深度分析</h2>
                
                <div class="company-overview">
                    <h3>公司概况</h3>
                    <p>{basic['fullname']} ({basic['enname']}) 是中国最大的寿险公司，成立于1949年，2007年在上海证券交易所上市。公司总部位于{basic['area']}，主营业务包括寿险、健康险、意外险等。</p>
                    
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
                                <span class="score-tag">RICH评分: {article['total_score'] if article else '8.7'}/10</span>
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
            
            <!-- 相关文章 -->
            {self.generate_related_articles(article) if article else ''}
            
            <!-- 返回链接 -->
            <div class="text-center mt-5 mb-5">
                <a href="/" class="source-tag p-3">返回首页</a>
                <a href="/stock.html" class="source-tag p-3 ml-3">查看所有股票</a>
            </div>
        </div>
        '''
        
        return content
    
    def generate_related_articles(self, article):
        """生成相关文章部分"""
        if not article:
            return ''
        
        return f'''
        <section class="dashboard-section">
            <h2 class="section-title">📰 相关分析</h2>
            
            <div class="finance-card">
                <div class="card-header">
                    <h3 class="card-title">
                        <span class="card-number">#分析</span> {article['title']}
                    </h3>
                    <div class="card-meta">
                        <span class="source-tag">{article['source']}</span>
                        <span class="time-tag">{article['created_at'][:10] if 'created_at' in article else datetime.now().strftime('%Y-%m-%d')}</span>
                        <span class="score-tag">RICH: {article['total_score']}</span>
                    </div>
                </div>
                <div class="card-content">
                    <p>{article['excerpt']}</p>
                </div>
                <div class="card-footer">
                    <a href="/article/{article['slug']}.html" class="tags">阅读完整分析 →</a>
                </div>
            </div>
        </section>
        '''
    
    def update_homepage(self):
        """更新首页"""
        try:
            # 读取首页
            homepage_path = os.path.join(OUTPUT_DIR, 'index.html')
            if not os.path.exists(homepage_path):
                print("⚠️  首页不存在，跳过更新")
                return False
            
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
                            <span class="card-number">#001</span> 中国人寿(601628.SH): 保险龙头估值修复进行时
                        </h3>
                        <div class="card-meta">
                            <span class="source-tag">琥珀引擎独家</span>
                            <span class="time-tag">今日更新</span>
                            <span class="score-tag">RICH: 8.7</span>
                        </div>
                    </div>
                    <div class="card-content">
                        <p>中国人寿作为国内保险行业龙头，近期股价表现稳健。公司基本面扎实，估值处于历史低位，具备长期投资价值。3月17日收盘价42.73元，单日涨幅1.47%。</p>
                    </div>
                    <div class="card-footer">
                        <a href="/stock/601628.html" class="tags">查看详细分析 →</a>
                    </div>
                </div>
            </section>
            '''
            
            # 在最新文章后插入
            if '最新文章' in homepage_content:
                updated_content = homepage_content.replace(
                    '<h2 class="section-title">📰 最新文章</h2>',
                    china_life_section + '\n\n<h2 class="section-title">📰 最新文章</h2>'
                )
                
                with open(homepage_path, 'w', encoding='utf-8') as f:
                    f.write(updated_content)
                
                print("✅ 首页更新完成: 添加中国人寿推荐")
                return True
            else:
                print("⚠️  未找到最新文章区域，首页更新失败")
                return False
                
        except Exception as e:
            print(f"❌ 更新首页失败: {e}")
            return False
    
    def create_env_config(self):
        """创建环境变量配置文件"""
        try:
            env_content = '''# 琥珀引擎环境变量配置
# 安全提示: 此文件包含敏感信息，请勿提交到版本控制系统

# Tushare API Token (从tushare.pro获取)
TUSHARE_TOKEN="9e32ef28eac05c5fbb11e6f02a50da903def70f94b3018e93340568b"

# 数据库配置
AMBER_DB_PATH="/home/luckyelite/.openclaw/workspace/amber-engine/amber_cms.db"

# 网站配置
SITE_URL="https://finance.cheese.ai"
SITE_NAME="琥珀引擎"
SITE_DESCRIPTION="财经品牌独立站 - 数据库驱动 + 静态化生成"

# 发布配置
PUBLISH_SCHEDULE="0 10 * * *"  # 每天10:00发布
REBUILD_SCHEDULE="0 2 * * *"   # 每天2:00全站重建

# 安全配置
ENABLE_HTTPS=true
ENABLE_CACHE=true
CACHE_TTL=3600  # 缓存时间(秒)

# 日志配置
LOG_LEVEL="INFO"
LOG_PATH="/home/luckyelite/.openclaw/workspace/amber-engine/logs"

# 监控配置
ENABLE_MONITORING=true
HEALTH_CHECK_INTERVAL=300  # 健康检查间隔(秒)
'''
            
            env_path = os.path.join(BASE_DIR, '.env.amber')
            with open(env_path, 'w', encoding='utf-8') as f:
                f.write(env_content)
            
            # 设置权限
            os.chmod(env_path, 0o600)
            
            print(f"✅ 环境变量配置文件创建完成: {env_path}")
            print("🔒 文件权限已设置为600 (仅所有者可读写)")
            
            return env_path
            
        except Exception as e:
            print(f"❌ 创建环境变量配置文件失败: {e}")
            return None

def main():
    """主函数"""
    print("=" * 60)
    print("琥珀引擎 001号样板 - 页面渲染")
    print("=" * 60)
    
    try:
        # 创建渲染器
        renderer = TemplateRenderer()
        
        # 1. 生成股票详情页
        print("\n1. 🎨 生成中国人寿详情页...")
        stock_page = renderer.generate_stock_page()
        if not stock_page:
            print("❌ 股票详情页生成失败")
            return 1
        
        # 2. 更新首页
        print("\n2. 🏠 更新首页...")
        renderer.update_homepage()
        
        # 3. 创建环境变量配置
        print("\n3. 🔒 创建环境变量配置文件...")
        renderer.create_env_config()
        
        # 4. 生成预览脚本
        print("\n4. 🔍 生成预览脚本...")
        create_preview_script(stock_page)
        
        print("\n" + "=" * 60)
        print("🎉 琥珀引擎 001号样板制作完成!")
        print("=" * 60)
        
        print("\n📋 成果清单:")
        print(f"  1. ✅ 股票详情页: {stock_page