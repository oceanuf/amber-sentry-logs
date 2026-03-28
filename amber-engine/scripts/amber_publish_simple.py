#!/usr/bin/env python3
"""
琥珀引擎 Amber-Engine V1.0 - 简化版发布工具
快速完成打样和测试
"""

import os
import sys
import json
import sqlite3
import argparse
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
import re
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

class AmberPublisherSimple:
    """简化版琥珀引擎发布器"""
    
    def __init__(self):
        self.db = None
        self.connect_database()
        logger.info("✅ 琥珀引擎简化版发布器初始化完成")
    
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
        """初始化数据库（如果不存在）"""
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
            {
                "title": "港股科技股估值修复，南向资金持续流入",
                "slug": "hk-tech-valuation",
                "content": "近期港股科技股出现估值修复行情，南向资金连续多日净流入。分析师认为，经过深度调整后，港股科技股已具备较好的投资价值。",
                "tags": ["港股", "科技股", "金融股"],
                "score": 8.1,
                "source": "琥珀引擎"
            },
            {
                "title": "半导体行业迎来周期拐点，国产替代加速",
                "slug": "semiconductor-cycle-turn",
                "content": "全球半导体行业库存逐步消化，行业周期有望迎来拐点。同时，国产替代进程加速，国内半导体企业迎来发展机遇。",
                "tags": ["半导体", "科技股", "A股"],
                "score": 9.0,
                "source": "证券时报"
            }
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
        
        logger.info("✅ 示例数据插入完成: 5篇文章，10个标签")
    
    def generate_static_site(self):
        """生成静态站点"""
        logger.info("🚀 开始生成静态站点...")
        
        try:
            # 1. 生成首页
            self.generate_homepage()
            
            # 2. 生成文章页
            self.generate_article_pages()
            
            # 3. 生成标签页
            self.generate_tag_pages()
            
            # 4. 生成搜索索引
            self.generate_search_index()
            
            logger.info("🎉 静态站点生成完成!")
            return True
            
        except Exception as e:
            logger.error(f"❌ 生成静态站点失败: {e}")
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
            cursor.execute('''
                SELECT id, title, slug, excerpt, publish_time, source, total_score
                FROM articles 
                ORDER BY publish_time DESC 
                LIMIT 5
            ''')
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
            cursor.execute('''
                SELECT name, slug, count
                FROM tags 
                WHERE count > 0
                ORDER BY count DESC 
                LIMIT 15
            ''')
            hot_tags = []
            for row in cursor.fetchall():
                hot_tags.append({
                    'name': row['name'],
                    'slug': row['slug'],
                    'count': row['count']
                })
            
            # 读取基础模板
            with open(os.path.join(TEMPLATES_DIR, 'base.html'), 'r', encoding='utf-8') as f:
                base_template = f.read()
            
            with open(os.path.join(TEMPLATES_DIR, 'index.html'), 'r', encoding='utf-8') as f:
                index_template = f.read()
            
            # 合并模板
            full_template = base_template.replace('{% block content %}', index_template)
            
            # 替换变量
            html = full_template
            html = html.replace('{{ stats.article_count }}', str(article_count))
            html = html.replace('{{ stats.tag_count }}', str(tag_count))
            html = html.replace('{{ stats.last_update }}', datetime.now().strftime('%H:%M'))
            html = html.replace('{{ last_updated }}', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            
            # 生成文章列表HTML
            articles_html = ''
            for i, article in enumerate(latest_articles, 1):
                articles_html += f'''
                <article class="article-preview">
                    <div class="article-date">
                        <span class="day">{article['publish_day']}</span>
                        <span class="month">{article['publish_month']}</span>
                    </div>
                    <div class="article-info">
                        <h3>
                            <a href="{article['url']}">{article['title']}</a>
                        </h3>
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
            
            # 替换内容块
            html = html.replace('{% for article in latest_articles %}', '')
            html = html.replace('{% endfor %}', '')
            html = html.replace('{% for tag in hot_tags %}', '')
            html = html.replace('{% endfor %}', '')
            html = html.replace('{{ article.title }}', 'TITLE_PLACEHOLDER')
            html = html.replace('{{ tag.name }}', 'TAG_PLACEHOLDER')
            
            # 插入实际内容
            html = html.replace('TITLE_PLACEHOLDER', articles_html)
            html = html.replace('TAG_PLACEHOLDER', tags_html)
            
            # 保存首页
            output_path = os.path.join(OUTPUT_DIR, 'index.html')
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html)
            
            logger.info(f"✅ 首页生成完成: {output_path}")
            
        except Exception as e:
            logger.error(f"❌ 生成首页失败: {e}")
            raise
    
    def generate_article_pages(self):
        """生成文章详情页"""
        try:
            cursor = self.db.cursor()
            
            # 获取所有文章
            cursor.execute('''
                SELECT a.*, GROUP_CONCAT(t.name) as tags
                FROM articles a
                LEFT JOIN article_tags at ON a.id = at.article_id
                LEFT JOIN tags t ON at.tag_id = t.id
                GROUP BY a.id
            ''')
            
            articles = cursor.fetchall()
            
            for article in articles:
                # 读取基础模板
                with open(os.path.join(TEMPLATES_DIR, 'base.html'), 'r', encoding='utf-8') as f:
                    base_template = f.read()
                
                # 创建文章详情模板
                article_template = '''
                <section class="dashboard-section">
                    <h1 class="section-title">{{ article.title }}</h1>
                    
                    <div class="article-meta mb-4">
                        <span class="source-tag">{{ article.source }}</span>
                        <span class="time-tag">{{ article.publish_time }}</span>
                        <span class="score-tag">RICH: {{ article.total_score|float|round(1) }}</span>
                    </div>
                    
                    <div class="finance-card">
                        <div class="card-content">
                            {{ article.content_html|safe }}
                        </div>
                        
                        {% if article.tags %}
                        <div class="card-footer">
                            <div class="tags">
                                {% for tag in article.tags %}
                                <a href="/tag/{{ tag.slug }}.html">#{{ tag.name }}</a>
                                {% endfor %}
                            </div>
                        </div>
                        {% endif %}
                    </div>
                    
                    <div class="text-center mt-5">
                        <a href="/" class="source-tag p-3">返回首页</a>
                    </div>
                </section>
                '''
                
                # 合并模板
                full_template = base_template.replace('{% block content %}', article_template)
                
                # 处理标签
                tags = []
                if article['tags']:
                    tag_names = article['tags'].split(',')
                    for tag_name in tag_names:
                        cursor.execute('SELECT slug FROM tags WHERE name = ?', (tag_name,))
                        tag_row = cursor.fetchone()
                        if tag_row:
                            tags.append({'name': tag_name, 'slug': tag_row['slug']})
                
                # 替换变量
                html = full_template
                html = html.replace('{{ article.title }}', article['title'])
                html = html.replace('{{ article.source }}', article['source'])
                html = html.replace('{{ article.publish_time }}', article['publish_time'])
                html = html.replace('{{ article.total_score|float|round(1) }}', f"{article['total_score']:.1f}")
                html = html.replace('{{ article.content_html|safe }}', article['content_html'])
                html = html.replace('{{ last_updated }}', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                
                # 生成标签HTML
                tags_html = ''
                for tag in tags:
                    tags_html += f'<a href="/tag/{tag["slug"]}.html">#{tag["name"]}</a> '
                html = html.replace('{% for tag in article.tags %}', '')
                html = html.replace('{% endfor %}', '')
                html = html.replace('{{ tag.name }}', 'TAG_NAME')
                html = html.replace('{{ tag.slug }}', 'TAG_SLUG')
                html = html.replace('TAG_NAME', tags_html)
                html = html.replace('TAG_SLUG', '')  # 清理占位符
                
                # 保存文章页
                output_path = os.path.join(OUTPUT_DIR, 'article', f'{article["slug"]}.html')
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
                
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(html)
            
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
                    SELECT a.id, a.title, a.slug, a.excerpt, a.publish_time, a.source, a.total_score
                    FROM articles a
                    JOIN article_tags at ON a.id = at.article_id
                    WHERE at.tag_id