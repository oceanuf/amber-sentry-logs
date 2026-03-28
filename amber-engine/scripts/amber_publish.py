#!/usr/bin/env python3
"""
琥珀引擎 Amber-Engine V1.0 - 发布工具
命令行工具：Markdown/API数据 -> 入库 + 全量静态渲染 + 推送
"""

import os
import sys
import json
import sqlite3
import argparse
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import re
import hashlib
import uuid

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from jinja2 import Environment, FileSystemLoader, select_autoescape

# 配置
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "amber_cms.db")
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
STATIC_DIR = os.path.join(BASE_DIR, "static")

# 创建目录
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(os.path.join(OUTPUT_DIR, "article"), exist_ok=True)
os.makedirs(os.path.join(OUTPUT_DIR, "category"), exist_ok=True)
os.makedirs(os.path.join(OUTPUT_DIR, "tag"), exist_ok=True)
os.makedirs(os.path.join(OUTPUT_DIR, "archive"), exist_ok=True)

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

class AmberPublisher:
    """琥珀引擎发布器"""
    
    def __init__(self):
        self.db = None
        self.env = None
        self.initialize()
    
    def initialize(self):
        """初始化发布器"""
        # 连接数据库
        self.connect_database()
        
        # 初始化模板引擎
        self.initialize_templates()
        
        logger.info("✅ 琥珀引擎发布器初始化完成")
    
    def connect_database(self):
        """连接数据库"""
        try:
            self.db = sqlite3.connect(DB_PATH)
            self.db.row_factory = sqlite3.Row
            logger.info(f"✅ 数据库连接成功: {DB_PATH}")
        except Exception as e:
            logger.error(f"❌ 数据库连接失败: {e}")
            raise
    
    def initialize_templates(self):
        """初始化Jinja2模板引擎"""
        try:
            self.env = Environment(
                loader=FileSystemLoader(TEMPLATES_DIR),
                autoescape=select_autoescape(['html', 'xml']),
                trim_blocks=True,
                lstrip_blocks=True
            )
            
            # 添加自定义过滤器
            self.env.filters['float'] = float
            self.env.filters['round'] = lambda x, d=2: round(float(x), d)
            self.env.filters['truncate'] = lambda s, length=100: s[:length] + '...' if len(s) > length else s
            
            logger.info("✅ 模板引擎初始化完成")
        except Exception as e:
            logger.error(f"❌ 模板引擎初始化失败: {e}")
            raise
    
    def generate_slug(self, title: str) -> str:
        """生成URL友好的slug"""
        # 转换为小写
        slug = title.lower()
        
        # 替换中文标点
        slug = slug.replace('，', '-').replace('。', '-').replace('！', '-').replace('？', '-')
        slug = slug.replace('、', '-').replace('；', '-').replace('：', '-').replace('「', '-')
        slug = slug.replace('」', '-').replace('『', '-').replace('』', '-').replace('《', '-')
        slug = slug.replace('》', '-').replace('（', '-').replace('）', '-').replace('【', '-')
        slug = slug.replace('】', '-').replace('｛', '-').replace('｝', '-').replace('［', '-')
        slug = slug.replace('］', '-').replace('〔', '-').replace('〕', '-')
        
        # 替换空格和特殊字符
        slug = re.sub(r'[^\w\s-]', '', slug)
        slug = re.sub(r'[-\s]+', '-', slug)
        
        # 移除首尾的连字符
        slug = slug.strip('-')
        
        # 如果slug为空，使用时间戳
        if not slug:
            slug = f"article-{int(datetime.now().timestamp())}"
        
        return slug
    
    def process_markdown_file(self, filepath: str) -> Dict[str, Any]:
        """处理Markdown文件"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 解析Front Matter（如果存在）
            front_matter = {}
            body = content
            
            if content.startswith('---'):
                parts = content.split('---', 2)
                if len(parts) >= 3:
                    try:
                        import yaml
                        front_matter = yaml.safe_load(parts[1])
                        body = parts[2].strip()
                    except:
                        # 如果没有yaml，使用简单解析
                        lines = parts[1].strip().split('\n')
                        for line in lines:
                            if ':' in line:
                                key, value = line.split(':', 1)
                                front_matter[key.strip()] = value.strip()
                        body = parts[2].strip()
            
            # 提取标题
            title = front_matter.get('title', '')
            if not title:
                # 从第一行提取标题
                first_line = body.split('\n')[0].strip()
                if first_line.startswith('# '):
                    title = first_line[2:].strip()
                else:
                    title = os.path.basename(filepath).replace('.md', '')
            
            # 生成slug
            slug = front_matter.get('slug', self.generate_slug(title))
            
            # 提取标签
            tags = front_matter.get('tags', [])
            if isinstance(tags, str):
                tags = [tag.strip() for tag in tags.split(',')]
            
            # 提取分类
            categories = front_matter.get('categories', ['未分类'])
            if isinstance(categories, str):
                categories = [cat.strip() for cat in categories.split(',')]
            
            # 构建文章数据
            article = {
                'uuid': str(uuid.uuid4()),
                'title': title,
                'slug': slug,
                'content_markdown': body,
                'content_html': self.markdown_to_html(body),
                'excerpt': front_matter.get('excerpt', self.generate_excerpt(body)),
                'status': front_matter.get('status', 'published'),
                'publish_time': front_matter.get('date', datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
                'author': front_matter.get('author', 'Cheese Intelligence'),
                'source': front_matter.get('source', '琥珀引擎'),
                'source_url': front_matter.get('source_url', ''),
                'total_score': float(front_matter.get('total_score', 0.0)),
                'rich_score': float(front_matter.get('rich_score', 0.0)),
                'importance_score': float(front_matter.get('importance_score', 0.0)),
                'credibility_score': float(front_matter.get('credibility_score', 0.0)),
                'hotness_score': float(front_matter.get('hotness_score', 0.0)),
                'meta_title': front_matter.get('meta_title', title),
                'meta_description': front_matter.get('meta_description', self.generate_excerpt(body, 160)),
                'meta_keywords': front_matter.get('meta_keywords', ', '.join(tags)),
                'custom_fields': json.dumps(front_matter.get('custom', {})),
                'tags': tags,
                'categories': categories,
            }
            
            logger.info(f"✅ 处理Markdown文件: {filepath} -> {title}")
            return article
            
        except Exception as e:
            logger.error(f"❌ 处理Markdown文件失败 {filepath}: {e}")
            return None
    
    def markdown_to_html(self, markdown: str) -> str:
        """将Markdown转换为HTML（简化版）"""
        # 这里可以使用第三方库如markdown或mistune
        # 暂时使用简单转换
        html = markdown
        
        # 标题
        html = re.sub(r'^# (.*?)$', r'<h1>\1</h1>', html, flags=re.MULTILINE)
        html = re.sub(r'^## (.*?)$', r'<h2>\1</h2>', html, flags=re.MULTILINE)
        html = re.sub(r'^### (.*?)$', r'<h3>\1</h3>', html, flags=re.MULTILINE)
        
        # 粗体和斜体
        html = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', html)
        html = re.sub(r'\*(.*?)\*', r'<em>\1</em>', html)
        
        # 链接
        html = re.sub(r'\[(.*?)\]\((.*?)\)', r'<a href="\2">\1</a>', html)
        
        # 列表
        html = re.sub(r'^- (.*?)$', r'<li>\1</li>', html, flags=re.MULTILINE)
        html = re.sub(r'(<li>.*?</li>\n?)+', r'<ul>\g<0></ul>', html)
        
        # 段落
        lines = html.split('\n')
        result = []
        in_paragraph = False
        current_paragraph = []
        
        for line in lines:
            if line.strip() and not line.startswith(('<', '- ', '# ')):
                if not in_paragraph:
                    in_paragraph = True
                    current_paragraph = [line]
                else:
                    current_paragraph.append(line)
            else:
                if in_paragraph:
                    result.append(f'<p>{" ".join(current_paragraph)}</p>')
                    in_paragraph = False
                result.append(line)
        
        if in_paragraph:
            result.append(f'<p>{" ".join(current_paragraph)}</p>')
        
        return '\n'.join(result)
    
    def generate_excerpt(self, text: str, length: int = 100) -> str:
        """生成摘要"""
        # 移除Markdown标记
        excerpt = re.sub(r'[#*`\[\]]', '', text)
        excerpt = re.sub(r'!\[.*?\]\(.*?\)', '', excerpt)
        
        # 截取指定长度
        if len(excerpt) > length:
            excerpt = excerpt[:length].rsplit(' ', 1)[0] + '...'
        
        return excerpt.strip()
    
    def save_article(self, article: Dict[str, Any]) -> Optional[int]:
        """保存文章到数据库"""
        try:
            cursor = self.db.cursor()
            
            # 检查是否已存在
            cursor.execute('SELECT id FROM articles WHERE slug = ?', (article['slug'],))
            existing = cursor.fetchone()
            
            if existing:
                # 更新现有文章
                article_id = existing[0]
                cursor.execute('''
                    UPDATE articles SET
                        title = ?, content_markdown = ?, content_html = ?, excerpt = ?,
                        status = ?, publish_time = ?, update_time = ?,
                        author = ?, source = ?, source_url = ?,
                        total_score = ?, rich_score = ?, importance_score = ?,
                        credibility_score = ?, hotness_score = ?,
                        meta_title = ?, meta_description = ?, meta_keywords = ?,
                        custom_fields = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                ''', (
                    article['title'], article['content_markdown'], article['content_html'],
                    article['excerpt'], article['status'], article['publish_time'],
                    datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    article['author'], article['source'], article['source_url'],
                    article['total_score'], article['rich_score'], article['importance_score'],
                    article['credibility_score'], article['hotness_score'],
                    article['meta_title'], article['meta_description'], article['meta_keywords'],
                    article['custom_fields'], article_id
                ))
                logger.info(f"📝 更新文章: {article['title']} (ID: {article_id})")
            else:
                # 插入新文章
                cursor.execute('''
                    INSERT INTO articles (
                        uuid, title, slug, content_markdown, content_html, excerpt,
                        status, publish_time, author, source, source_url,
                        total_score, rich_score, importance_score, credibility_score, hotness_score,
                        meta_title, meta_description, meta_keywords, custom_fields
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    article['uuid'], article['title'], article['slug'],
                    article['content_markdown'], article['content_html'], article['excerpt'],
                    article['status'], article['publish_time'],
                    article['author'], article['source'], article['source_url'],
                    article['total_score'], article['rich_score'], article['importance_score'],
                    article['credibility_score'], article['hotness_score'],
                    article['meta_title'], article['meta_description'], article['meta_keywords'],
                    article['custom_fields']
                ))
                article_id = cursor.lastrowid
                logger.info(f"📝 创建新文章: {article['title']} (ID: {article_id})")
            
            # 处理标签
            if 'tags' in article and article['tags']:
                self.process_tags(article_id, article['tags'])
            
            # 处理分类
            if 'categories' in article and article['categories']:
                self.process_categories(article_id, article['categories'])
            
            # 更新搜索索引
            self.update_search_index(article_id)
            
            # 更新归档
            self.update_archive(article['publish_time'])
            
            self.db.commit()
            return article_id
            
        except Exception as e:
            logger.error(f"❌ 保存文章失败: {e}")
            self.db.rollback()
            return None
    
    def process_tags(self, article_id: int, tags: List[str]):
        """处理文章标签"""
        try:
            cursor = self.db.cursor()
            
            # 清除现有标签关联
            cursor.execute('DELETE FROM article_tags WHERE article_id = ?', (article_id,))
            
            for tag_name in tags:
                # 获取或创建标签
                cursor.execute('SELECT id FROM tags WHERE name = ?', (tag_name,))
                tag_row = cursor.fetchone()
                
                if tag_row:
                    tag_id = tag_row[0]
                else:
                    # 创建新标签
                    tag_slug = self.generate_slug(tag_name)
                    cursor.execute('INSERT INTO tags (name, slug) VALUES (?, ?)', (tag_name, tag_slug))
                    tag_id = cursor.lastrowid
                
                # 关联文章和标签
                cursor.execute('''
                    INSERT OR IGNORE INTO article_tags (article_id, tag_id)
                    VALUES (?, ?)
                ''', (article_id, tag_id))
                
                # 更新标签计数
                cursor.execute('''
                    UPDATE tags SET count = (
                        SELECT COUNT(*) FROM article_tags WHERE tag_id = ?
                    ) WHERE id = ?
                ''', (tag_id, tag_id))
            
            logger.info(f"✅ 处理标签完成: {len(tags)} 个标签")
            
        except Exception as e:
            logger.error(f"❌ 处理标签失败: {e}")
            raise
    
    def process_categories(self, article_id: int, categories: List[str]):
        """处理文章分类"""
        try:
            cursor = self.db.cursor()
            
            # 清除现有分类关联
            cursor.execute('DELETE FROM article_categories WHERE article_id = ?', (article_id,))
            
            for cat_name in categories:
                # 获取或创建分类
                cursor.execute('SELECT id FROM categories WHERE name = ?', (cat_name,))
                cat_row = cursor.fetchone()
                
                if cat_row:
                    cat_id = cat_row[0]
                else:
                    # 创建新分类
                    cat_slug = self.generate_slug(cat_name)
                    cursor.execute('''
                        INSERT INTO categories (name, slug, description)
                        VALUES (?, ?, ?)
                    ''', (cat_name, cat_slug, f'{cat_name}分类'))
                    cat_id = cursor.lastrowid
                
                # 关联文章和分类
                cursor.execute('''
                    INSERT OR IGNORE INTO article_categories (article_id, category_id)
                    VALUES (?, ?)
                ''', (article_id, cat_id))
                
                # 更新分类计数
                cursor.execute('''
                    UPDATE categories SET count = (
                        SELECT COUNT(*) FROM article_categories WHERE category_id = ?
                    ) WHERE id = ?
                ''', (cat_id, cat_id))
            
            logger.info(f"✅ 处理分类完成: {len(categories)} 个分类")
            
        except Exception as e:
            logger.error(f"❌ 处理分类失败: {e}")
            raise
    
    def update_search_index(self, article_id: int):
        """更新搜索索引"""
        try:
            cursor = self.db.cursor()
            
            # 获取文章信息
            cursor.execute('''
                SELECT a.title, a.content_markdown, 
                       GROUP_CONCAT(DISTINCT t.name) as tags,
                       GROUP_CONCAT(DISTINCT c.name) as categories
                FROM articles a
                LEFT JOIN