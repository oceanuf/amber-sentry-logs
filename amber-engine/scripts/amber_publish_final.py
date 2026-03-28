#!/usr/bin/env python3
"""
琥珀引擎 Amber-Engine V1.0 - 最终版发布工具
"""

import os
import sys
import json
import sqlite3
import logging
from datetime import datetime
import uuid

# 配置
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "amber_cms.db")
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")

# 创建目录
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(os.path.join(BASE_DIR, "logs"), exist_ok=True)

# 日志配置
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [琥珀引擎] %(levelname)s: %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(BASE_DIR, "logs", "amber_publish.log")),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class AmberEngine:
    """琥珀引擎核心"""
    
    def __init__(self):
        self.db = None
        self.connect_database()
        logger.info("✅ 琥珀引擎初始化完成")
    
    def connect_database(self):
        """连接数据库"""
        try:
            self.db = sqlite3.connect(DB_PATH)
            self.db.row_factory = sqlite3.Row
            logger.info(f"✅ 数据库连接成功: {DB_PATH}")
        except Exception as e:
            logger.error(f"❌ 数据库连接失败: {e}")
            raise
    
    def initialize_database(self):
        """初始化数据库"""
        try:
            cursor = self.db.cursor()
            
            # 检查表是否存在
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='articles'")
            if cursor.fetchone():
                logger.info("✅ 数据库已存在，跳过初始化")
                return True
            
            logger.info("🔧 初始化数据库...")
            
            # 创建文章表
            cursor.execute('''
                CREATE TABLE articles (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    uuid TEXT UNIQUE NOT NULL,
                    title TEXT NOT NULL,
                    slug TEXT UNIQUE NOT NULL,
                    content_html TEXT,
                    excerpt TEXT,
                    status TEXT DEFAULT 'published',
                    publish_time DATETIME DEFAULT CURRENT_TIMESTAMP,
                    author TEXT DEFAULT 'Cheese Intelligence',
                    source TEXT,
                    total_score REAL DEFAULT 0.0,
                    view_count INTEGER DEFAULT 0,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # 创建标签表
            cursor.execute('''
                CREATE TABLE tags (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    slug TEXT UNIQUE NOT NULL,
                    count INTEGER DEFAULT 0
                )
            ''')
            
            # 创建文章-标签关联表
            cursor.execute('''
                CREATE TABLE article_tags (
                    article_id INTEGER NOT NULL,
                    tag_id INTEGER NOT NULL,
                    PRIMARY KEY (article_id, tag_id)
                )
            ''')
            
            # 插入示例数据
            self.insert_sample_data(cursor)
            
            self.db.commit()
            logger.info("✅ 数据库初始化完成")
            return True
            
        except Exception as e:
            logger.error(f"❌ 数据库初始化失败: {e}")
            self.db.rollback()
            return False
    
    def insert_sample_data(self, cursor):
        """插入示例数据"""
        # 插入示例标签
        sample_tags = [
            ("A股", "a-share"),
            ("港股", "hk-share"),
            ("美股", "us-stock"),
            ("宏观经济", "macro-economy"),
            ("科技股", "tech-stock"),
            ("消费股", "consumer-stock"),
            ("金融股", "financial-stock"),
            ("新能源", "new-energy"),
            ("半导体", "semiconductor"),
            ("人工智能", "ai"),
        ]
        
        for name, slug in sample_tags:
            cursor.execute('INSERT OR IGNORE INTO tags (name, slug) VALUES (?, ?)', (name, slug))
        
        # 插入示例文章
        sample_articles = [
            {
                "title": "A股市场迎来技术性反弹，科技股领涨",
                "slug": "a-share-tech-rally",
                "content": "今日A股市场出现技术性反弹，科技板块表现强势。半导体、人工智能等概念股涨幅居前，市场情绪有所回暖。分析师指出，当前市场估值处于历史低位，具备长期配置价值。",
                "tags": ["A股", "科技股", "半导体", "人工智能"],
                "score": 8.5,
                "source": "琥珀引擎"
            },
            {
                "title": "美联储利率决议在即，全球市场静待指引",
                "slug": "fed-rate-decision",
                "content": "美联储即将公布最新利率决议，市场普遍预期将维持利率不变。但投资者更关注美联储对通胀和经济增长的展望，这将影响全球资产价格走势。",
                "tags": ["美股", "宏观经济", "金融股"],
                "score": 9.2,
                "source": "华尔街见闻"
            },
            {
                "title": "新能源车销量超预期，产业链公司受益",
                "slug": "new-energy-vehicle-sales",
                "content": "最新数据显示，新能源车销量同比增长超过50%，超出市场预期。电池、充电桩等产业链公司业绩有望持续改善，投资者可关注相关投资机会。",
                "tags": ["新能源", "A股", "消费股"],
                "score": 7.8,
                "source": "财经网"
            },
        ]
        
        for article_data in sample_articles:
            # 插入文章
            cursor.execute('''
                INSERT INTO articles (uuid, title, slug, content_html, excerpt, source, total_score)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                str(uuid.uuid4()),
                article_data["title"],
                article_data["slug"],
                f"<p>{article_data['content']}</p>",
                article_data["content"][:100] + "...",
                article_data["source"],
                article_data["score"]
            ))
            
            article_id = cursor.lastrowid
            
            # 处理标签
            for tag_name in article_data["tags"]:
                # 获取标签ID
                cursor.execute('SELECT id FROM tags WHERE name = ?', (tag_name,))
                tag_row = cursor.fetchone()
                
                if tag_row:
                    tag_id = tag_row[0]
                    # 关联文章和标签
                    cursor.execute('INSERT OR IGNORE INTO article_tags (article_id, tag_id) VALUES (?, ?)', (article_id, tag_id))
                    # 更新标签计数
                    cursor.execute('UPDATE tags SET count = count + 1 WHERE id = ?', (tag_id,))
        
        logger.info("✅ 示例数据插入完成: 3篇文章，10个标签")
    
    def generate_site(self):
        """生成整个站点"""
        logger.info("🚀 开始生成琥珀引擎站点...")
        
        try:
            # 生成首页
            self.generate_homepage()
            
            # 生成文章页
            self.generate_article_pages()
            
            # 生成标签页
            self.generate_tag_pages()
            
            # 生成搜索索引
            self.generate_search_index()
            
            logger.info("🎉 琥珀引擎站点生成完成!")
            return True
            
        except Exception as e:
            logger.error(f"❌ 生成站点失败: {e}")
            return False
    
    def generate_homepage(self):
        """生成首页"""
        try:
            cursor = self.db.cursor()
            
            # 获取统计数据
            cursor.execute('SELECT COUNT(*) FROM articles')
            article_count = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM tags')
            tag_count = cursor.fetchone()[0]
            
            # 获取最新文章
            cursor.execute('SELECT title, slug, excerpt, publish_time, source, total_score FROM articles ORDER BY publish_time DESC LIMIT 5')
            latest_articles = []
            for row in cursor.fetchall():
                dt = datetime.strptime(row['publish_time'], '%Y-%m-%d %H:%M:%S')
                latest_articles.append({
                    'title': row['title'],
                    'url': f'article/{row["slug"]}.html',
                    'excerpt': row['excerpt'],
                    'publish_day': dt.day,
                    'publish_month': dt.strftime('%b'),
                    'source': row['source'],
                    'total_score': row['total_score']
                })
            
            # 获取热门标签
            cursor.execute('SELECT name, slug, count FROM tags WHERE count > 0 ORDER BY count DESC LIMIT 15')
            hot_tags = []
            for row in cursor.fetchall():
                hot_tags.append({
                    'name': row['name'],
                    'slug': row['slug'],
                    'count': row['count']
                })
            
            # 读取模板
            with open(os.path.join(TEMPLATES_DIR, 'base.html'), 'r', encoding='utf-8') as f:
                base_html = f.read()
            
            # 生成文章列表HTML
            articles_html = ''
            for article in latest_articles:
                articles_html += f'''
                <article class="article-preview">
                    <div class="article-date">
                        <span class="day">{article['publish_day']}</span>
                        <span class="month">{article['publish_month']}</span>
                    </div>
                    <div class="article-info">
                        <h3><a href="{article['url']}">{article['title']}</a></h3>
                        <p class="article-excerpt">{article['excerpt']}</p>
                        <div class="article-meta">
                            <span class="source-tag">{article['source']}</span>
                            <span>RICH: {article['total_score']:.1f}</span>
                        </div>
                    </div>
                </article>
                '''
            
            # 生成标签云HTML
            tags_html = ''
            for tag in hot_tags:
                size = 12 + (tag['count'] * 2)
                tags_html += f'<a href="tag/{tag["slug"]}.html" style="font-size: {size}px;">{tag["name"]} ({tag["count"]})</a> '
            
            # 构建首页内容
            homepage_content = f'''
            <section class="hero-section">
                <h1 class="hero-title">琥珀引擎</h1>
                <p class="hero-subtitle">
                    财经品牌独立站 · 数据库驱动 + 静态化生成的专业媒体架构<br>
                    每日财经分析 · 市场趋势洞察 · 投资策略研究
                </p>
                <div class="hero-stats">
                    <div class="stat-item">
                        <span class="stat-number">{article_count}</span>
                        <span class="stat-label">文章总数</span>
                    </div>
                    <div class="stat-item">
                        <span class="stat-number">{tag_count}</span>
                        <span class="stat-label">标签数量</span>
                    </div>
                    <div class="stat-item">
                        <span class="stat-number">{datetime.now().strftime('%H:%M')}</span>
                        <span class="stat-label">最后更新</span>
                    </div>
                </div>
            </section>
            
            <section class="dashboard-section">
                <h2 class="section-title">📰 最新文章</h2>
                <div class="latest-articles">
                    {articles_html}
                </div>
            </section>
            
            <section class="tag-cloud-section">
                <h2 class="section-title">🏷️ 热门标签</h2>
                <div class="tag-cloud">
                    {tags_html}
                </div>
            </section>
            '''
            
            # 替换基础模板中的内容块
            final_html = base_html.replace('{% block content %}', homepage_content)
            final_html = final_html.replace('{% block last_updated %}', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            final_html = final_html.replace('{{ last_updated }}', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            
            # 保存首页
            output_path = os.path.join(OUTPUT_DIR, 'index.html')
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(final_html)
            
            logger.info(f"✅ 首页生成完成: {output_path}")
            
        except Exception as e:
            logger.error(f"❌ 生成首页失败: {e}")
            raise
    
    def generate_article_pages(self):
        """生成文章详情页"""
        try:
            cursor = self.db.cursor()
            
            # 获取所有文章
            cursor.execute('SELECT * FROM articles')
            articles = cursor.fetchall()
            
            for article in articles:
                # 获取文章标签
                cursor.execute('''
                    SELECT t.name, t.slug 
                    FROM tags t
                    JOIN article_tags at ON t.id = at.tag_id
                    WHERE at.article_id = ?
                ''', (article['id'],))
                
                tags = []
                for tag_row in cursor.fetchall():
                    tags.append({
                        'name': tag_row['name'],
                        'slug': tag_row['slug']
                    })
                
                # 读取基础模板
                with open(os.path.join(TEMPLATES_DIR, 'base.html'), 'r', encoding='utf-8') as f:
                    base_html = f.read()
                
                # 生成标签HTML
                tags_html = ''
                for tag in tags:
                    tags_html += f'<a href="/tag/{tag["slug"]}.html">#{tag["name"]}</a> '
                
                # 构建文章内容
                article_content = f'''
                <section class="dashboard-section">
                    <h1 class="section-title">{article['title']}</h1>
                    
                    <div class="article-meta mb-4">
                        <span class="source-tag">{article['source']}</span>
                        <span class="time-tag">{article['publish_time']}</span>
                        <span class="score-tag">RICH: {article['total_score']:.1f}</span>
                    </div>
                    
                    <div class="finance-card">
                        <div class="card-content">
                            {article['content_html']}
                        </div>
                        
                        <div class="card-footer">
                            <div class="tags">
                                {tags_html}
                            </div>
                        </div>
                    </div>
                    
                    <div class="text-center mt-5">
                        <a href="/" class="source-tag p-3">返回首页</a>
                    </div>
                </section>
                '''
                
                # 替换基础模板中的内容块
                final_html = base_html.replace('{% block content %}', article_content)
                final_html = final_html.replace('{% block last_updated %}', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                final_html = final_html.replace('{{ last_updated }}', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                
                # 保存文章页
                output_path = os.path.join(OUTPUT_DIR, 'article', f'{article["slug"]}.html')
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
                
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(final_html)
            
            logger.info(f"✅ 文章详情页生成完成: {len(articles)} 篇")
            
        except Exception as e:
            logger.error(f"❌ 生成文章详情页失败: {e}")
            raise
    
    def generate_tag_pages(self):
        """生成标签页"""
        try:
            cursor = self.db.cursor()
            
            # 获取所有标签
            cursor.execute('SELECT id, name, slug, count FROM tags WHERE count > 0')
            tags = cursor.fetchall()
            
            for tag in tags:
                # 获取该标签下的文章
                cursor.execute('''
                    SELECT a.title, a.slug, a.excerpt, a.publish_time, a.source, a.total_score
                    FROM articles a
                    JOIN article_tags at ON a.id = at.article_id
                    WHERE at.tag_id = ?
                    ORDER BY a.publish_time DESC
                ''', (tag['id'],))
                
                articles = []
                for row in cursor.fetchall():
                    articles.append({
                        'title': row['title'],
                        'url': f'/article/{row["slug"]}.html',
                        'excerpt': row['excerpt'],
                        'publish_time': row['publish_time'],
                        'source': row['source'],
                        'total_score': row['total_score']
                    })
                
                # 读取基础模板
                with open(os.path.join(TEMPLATES_DIR, 'base.html'), 'r', encoding='utf-8') as f:
                    base_html = f.read()
                
                # 生成文章列表HTML
                articles_html = ''
                for article in articles:
                    articles_html += f'''
                    <div class="finance-card">
                        <div class="card-header">
                            <h3 class="card-title">
                                <a href="{article['url']}">{article['title']}</a>
                            </h3>
                            <div class="card-meta">
                                <span class="source-tag">{article['source']}</span>
                                <span class="time-tag">{article['publish_time']}</span>
                                <span class="score-tag">RICH: {article['total_score']:.1f}</span>
                            </div>
                        </div>
                        <div class="card-content">
                            <p>{article['excerpt']}</p>
                        </div>
                    </div>
                    '''
                
                # 构建标签页内容
                tag_content = f'''
                <section class="dashboard-section">
                    <h1 class="section-title">标签: {tag['name']}</h1>
                    <p class="mb-4">共有 {tag['count']} 篇文章</p>
                    
                    <div class="tag-articles">
                        {articles_html}
                    </div>
                    
                    <div class="text-center mt-5">
                        <a href="/" class="source-tag p-3">返回首页</a