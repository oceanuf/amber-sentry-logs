#!/usr/bin/env python3
"""
琥珀引擎 Amber-Engine V1.0 - 数据库初始化脚本
数据库驱动 + 静态化生成的专业媒体架构
"""

import os
import sys
import sqlite3
import json
from datetime import datetime
from typing import Dict, List, Optional
import logging

# 配置
DB_PATH = "/home/luckyelite/.openclaw/workspace/amber-engine/amber_cms.db"
BACKUP_DIR = "/home/luckyelite/.openclaw/workspace/amber-engine/backups"
LOG_DIR = "/home/luckyelite/.openclaw/workspace/amber-engine/logs"

# 创建目录
os.makedirs(BACKUP_DIR, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)

# 日志配置
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [琥珀引擎] %(levelname)s: %(message)s',
    handlers=[
        logging.FileHandler(f'{LOG_DIR}/amber_engine.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class AmberDatabase:
    """琥珀引擎数据库管理器"""
    
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self.conn = None
        self.cursor = None
        
    def connect(self):
        """连接数据库"""
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.conn.row_factory = sqlite3.Row
            self.cursor = self.conn.cursor()
            logger.info(f"✅ 数据库连接成功: {self.db_path}")
            return True
        except Exception as e:
            logger.error(f"❌ 数据库连接失败: {e}")
            return False
    
    def create_tables(self):
        """创建数据库表结构"""
        try:
            # 1. 文章表 (articles)
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS articles (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    uuid TEXT UNIQUE NOT NULL,
                    title TEXT NOT NULL,
                    slug TEXT UNIQUE NOT NULL,
                    content_markdown TEXT,
                    content_html TEXT,
                    excerpt TEXT,
                    status TEXT DEFAULT 'published',
                    publish_time DATETIME DEFAULT CURRENT_TIMESTAMP,
                    update_time DATETIME DEFAULT CURRENT_TIMESTAMP,
                    author TEXT DEFAULT 'Cheese Intelligence',
                    source TEXT,
                    source_url TEXT,
                    total_score REAL DEFAULT 0.0,
                    rich_score REAL DEFAULT 0.0,
                    importance_score REAL DEFAULT 0.0,
                    credibility_score REAL DEFAULT 0.0,
                    hotness_score REAL DEFAULT 0.0,
                    view_count INTEGER DEFAULT 0,
                    like_count INTEGER DEFAULT 0,
                    comment_count INTEGER DEFAULT 0,
                    featured BOOLEAN DEFAULT 0,
                    meta_title TEXT,
                    meta_description TEXT,
                    meta_keywords TEXT,
                    custom_fields TEXT,  -- JSON格式存储自定义字段
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # 2. 分类表 (categories)
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS categories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    slug TEXT UNIQUE NOT NULL,
                    description TEXT,
                    parent_id INTEGER DEFAULT 0,
                    count INTEGER DEFAULT 0,
                    sort_order INTEGER DEFAULT 0,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # 3. 标签表 (tags)
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS tags (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    slug TEXT UNIQUE NOT NULL,
                    description TEXT,
                    count INTEGER DEFAULT 0,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # 4. 文章-标签关联表 (article_tags)
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS article_tags (
                    article_id INTEGER NOT NULL,
                    tag_id INTEGER NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (article_id, tag_id),
                    FOREIGN KEY (article_id) REFERENCES articles(id) ON DELETE CASCADE,
                    FOREIGN KEY (tag_id) REFERENCES tags(id) ON DELETE CASCADE
                )
            ''')
            
            # 5. 文章-分类关联表 (article_categories)
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS article_categories (
                    article_id INTEGER NOT NULL,
                    category_id INTEGER NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (article_id, category_id),
                    FOREIGN KEY (article_id) REFERENCES articles(id) ON DELETE CASCADE,
                    FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE CASCADE
                )
            ''')
            
            # 6. 归档表 (archives) - 按年月归档
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS archives (
                    year INTEGER NOT NULL,
                    month INTEGER NOT NULL,
                    count INTEGER DEFAULT 0,
                    last_article_id INTEGER,
                    last_article_time DATETIME,
                    PRIMARY KEY (year, month)
                )
            ''')
            
            # 7. 搜索索引表 (search_index)
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS search_index (
                    article_id INTEGER NOT NULL,
                    title TEXT NOT NULL,
                    content TEXT,
                    tags TEXT,
                    categories TEXT,
                    search_text TEXT GENERATED ALWAYS AS (title || ' ' || COALESCE(content, '') || ' ' || COALESCE(tags, '') || ' ' || COALESCE(categories, '')) STORED,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (article_id) REFERENCES articles(id) ON DELETE CASCADE
                )
            ''')
            
            # 8. 系统配置表 (settings)
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS settings (
                    key TEXT PRIMARY KEY,
                    value TEXT,
                    description TEXT,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            self.conn.commit()
            logger.info("✅ 数据库表结构创建完成")
            return True
            
        except Exception as e:
            logger.error(f"❌ 创建表结构失败: {e}")
            return False
    
    def create_indexes(self):
        """创建索引以提高查询性能"""
        try:
            # 文章表索引
            self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_articles_status ON articles(status)')
            self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_articles_publish_time ON articles(publish_time)')
            self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_articles_total_score ON articles(total_score)')
            self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_articles_slug ON articles(slug)')
            
            # 标签和分类索引
            self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_tags_slug ON tags(slug)')
            self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_categories_slug ON categories(slug)')
            
            # 关联表索引
            self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_article_tags_tag ON article_tags(tag_id)')
            self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_article_categories_category ON article_categories(category_id)')
            
            # 搜索索引
            self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_search_index_text ON search_index(search_text)')
            
            # 归档索引
            self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_archives_year_month ON archives(year, month)')
            
            self.conn.commit()
            logger.info("✅ 数据库索引创建完成")
            return True
            
        except Exception as e:
            logger.error(f"❌ 创建索引失败: {e}")
            return False
    
    def initialize_default_data(self):
        """初始化默认数据"""
        try:
            # 插入默认分类
            default_categories = [
                ("每日财经", "daily-finance", "每日财经新闻与分析", 0),
                ("市场分析", "market-analysis", "市场趋势与技术分析", 0),
                ("投资策略", "investment-strategy", "投资理念与策略分享", 0),
                ("琥珀内参", "amber-insider", "琥珀引擎独家内参", 0),
            ]
            
            for name, slug, desc, parent in default_categories:
                self.cursor.execute('''
                    INSERT OR IGNORE INTO categories (name, slug, description, parent_id)
                    VALUES (?, ?, ?, ?)
                ''', (name, slug, desc, parent))
            
            # 插入默认标签（热门财经标签）
            default_tags = [
                ("A股", "a-share"),
                ("港股", "hk-share"),
                ("美股", "us-stock"),
                ("宏观经济", "macro-economy"),
                ("货币政策", "monetary-policy"),
                ("科技股", "tech-stock"),
                ("消费股", "consumer-stock"),
                ("金融股", "financial-stock"),
                ("新能源", "new-energy"),
                ("半导体", "semiconductor"),
                ("人工智能", "ai"),
                ("区块链", "blockchain"),
                ("房地产", "real-estate"),
                ("大宗商品", "commodity"),
                ("汇率", "exchange-rate"),
            ]
            
            for name, slug in default_tags:
                self.cursor.execute('''
                    INSERT OR IGNORE INTO tags (name, slug)
                    VALUES (?, ?)
                ''', (name, slug))
            
            # 插入系统配置
            default_settings = [
                ("site_name", "琥珀引擎 - Cheese Intelligence", "网站名称"),
                ("site_description", "财经品牌独立站 - 数据库驱动 + 静态化生成的专业媒体架构", "网站描述"),
                ("site_url", "https://finance.cheese.ai", "网站URL"),
                ("timezone", "Asia/Shanghai", "时区设置"),
                ("articles_per_page", "10", "每页文章数"),
                ("enable_search", "1", "启用站内搜索"),
                ("enable_comments", "0", "启用评论功能"),
                ("version", "Amber-Engine V1.0", "系统版本"),
                ("last_rebuild", datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "最后重建时间"),
            ]
            
            for key, value, desc in default_settings:
                self.cursor.execute('''
                    INSERT OR REPLACE INTO settings (key, value, description)
                    VALUES (?, ?, ?)
                ''', (key, value, desc))
            
            self.conn.commit()
            logger.info("✅ 默认数据初始化完成")
            return True
            
        except Exception as e:
            logger.error(f"❌ 初始化默认数据失败: {e}")
            return False
    
    def backup_database(self):
        """备份数据库"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = f"{BACKUP_DIR}/amber_cms_backup_{timestamp}.db"
            
            # 创建备份
            backup_conn = sqlite3.connect(backup_path)
            self.conn.backup(backup_conn)
            backup_conn.close()
            
            logger.info(f"✅ 数据库备份完成: {backup_path}")
            return backup_path
            
        except Exception as e:
            logger.error(f"❌ 数据库备份失败: {e}")
            return None
    
    def migrate_v2_2_data(self, source_file: str = None):
        """迁移V2.2历史数据到琥珀引擎数据库"""
        try:
            logger.info("🚀 开始迁移V2.2历史数据...")
            
            # 这里需要根据实际的V2.2数据格式进行迁移
            # 暂时创建占位函数，后续根据实际数据格式实现
            
            # 示例：从JSON文件迁移
            if source_file and os.path.exists(source_file):
                with open(source_file, 'r', encoding='utf-8') as f:
                    articles_data = json.load(f)
                
                migrated_count = 0
                for article in articles_data:
                    # 转换V2.2格式到琥珀引擎格式
                    # 这里需要根据实际数据结构实现
                    pass
                
                logger.info(f"✅ 迁移完成: {migrated_count} 篇文章")
            else:
                logger.warning("⚠️ 未找到V2.2数据文件，跳过数据迁移")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ 数据迁移失败: {e}")
            return False
    
    def close(self):
        """关闭数据库连接"""
        if self.conn:
            self.conn.close()
            logger.info("✅ 数据库连接已关闭")
    
    def get_database_info(self):
        """获取数据库信息"""
        try:
            info = {}
            
            # 获取表信息
            self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in self.cursor.fetchall()]
            info['tables'] = tables
            
            # 获取文章数量
            self.cursor.execute("SELECT COUNT(*) FROM articles")
            info['article_count'] = self.cursor.fetchone()[0]
            
            # 获取标签数量
            self.cursor.execute("SELECT COUNT(*) FROM tags")
            info['tag_count'] = self.cursor.fetchone()[0]
            
            # 获取分类数量
            self.cursor.execute("SELECT COUNT(*) FROM categories")
            info['category_count'] = self.cursor.fetchone()[0]
            
            # 获取数据库大小
            db_size = os.path.getsize(self.db_path)
            info['db_size_mb'] = round(db_size / (1024 * 1024), 2)
            
            return info
            
        except Exception as e:
            logger.error(f"❌ 获取数据库信息失败: {e}")
            return {}

def main():
    """主函数"""
    print("=" * 60)
    print("琥珀引擎 Amber-Engine V1.0 - 数据库初始化")
    print("=" * 60)
    
    # 创建数据库管理器
    db = AmberDatabase()
    
    # 连接数据库
    if not db.connect():
        print("❌ 数据库连接失败，退出")
        return 1
    
    try:
        # 备份现有数据库（如果存在）
        if os.path.exists(DB_PATH):
            print("🔧 备份现有数据库...")
            backup_path = db.backup_database()
            if backup_path:
                print(f"✅ 备份完成: {backup_path}")
        
        # 创建表结构
        print("🔧 创建数据库表结构...")
        if not db.create_tables():
            print("❌ 创建表结构失败")
            return 1
        print("✅ 表结构创建完成")
        
        # 创建索引
        print("🔧 创建数据库索引...")
        if not db.create_indexes():
            print("❌ 创建索引失败")
            return 1
        print("✅ 索引创建完成")
        
        # 初始化默认数据
        print("🔧 初始化默认数据...")
        if not db.initialize_default_data():
            print("❌ 初始化默认数据失败")
            return 1
        print("✅ 默认数据初始化完成")
        
        # 获取数据库信息
        print("\n📊 数据库信息:")
        info = db.get_database_info()
        for key, value in info.items():
            print(f"  {key}: {value}")
        
        print("\n🎉 琥珀引擎数据库初始化完成!")
        print(f"数据库位置: {DB_PATH}")
        print("下一步: 运行 amber_publish.py 开始内容发布")
        
        return 0
        
    except Exception as e:
        print(f"❌ 初始化过程中出现错误: {e}")
        return 1
    finally:
        db.close()

if __name__ == "__main__":
    sys.exit(main())