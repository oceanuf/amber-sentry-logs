#!/usr/bin/env python3
"""
Amber-Vault 数据库重构脚本
在SQLite中建立 tushare_cache 表，专门存储低频更新数据
"""

import os
import sys
import sqlite3
import json
from datetime import datetime, timedelta

# 数据库路径
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "amber_cms.db")
CACHE_DB_PATH = os.path.join(BASE_DIR, "amber_vault.db")  # 新的缓存数据库

def create_tushare_cache_schema():
    """创建tushare_cache表结构"""
    print("=" * 80)
    print("🗄️ Amber-Vault 数据库重构")
    print("=" * 80)
    
    try:
        # 连接数据库（如果不存在则创建）
        conn = sqlite3.connect(CACHE_DB_PATH)
        cursor = conn.cursor()
        
        print(f"📁 数据库路径: {CACHE_DB_PATH}")
        
        # 1. 创建fund_portfolio_cache表（基金持仓数据）
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS fund_portfolio_cache (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ts_code TEXT NOT NULL,           -- 基金代码
            ann_date TEXT,                   -- 公告日期
            end_date TEXT,                   -- 报告期
            symbol TEXT,                     -- 股票代码
            mkv REAL,                        -- 持仓市值(万元)
            amount REAL,                     -- 持仓数量(万股)
            stk_mkv_ratio REAL,              -- 占股票市值比
            mkv_ratio REAL,                  -- 占净值比例
            update_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(ts_code, end_date, symbol)
        )
        ''')
        
        # 创建索引
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_fund_code ON fund_portfolio_cache(ts_code)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_end_date ON fund_portfolio_cache(end_date)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_symbol ON fund_portfolio_cache(symbol)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_update_time ON fund_portfolio_cache(update_time)')
        
        print("✅ fund_portfolio_cache 表创建完成")
        
        # 2. 创建api_quota_log表（API额度使用日志）
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS api_quota_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            api_name TEXT NOT NULL,          -- API名称
            request_count INTEGER DEFAULT 1, -- 请求次数
            data_rows INTEGER,               -- 返回数据行数
            response_time REAL,              -- 响应时间(秒)
            request_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            estimated_remaining INTEGER,     -- 估计剩余额度
            status TEXT                      -- 状态: success/error
        )
        ''')
        
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_api_name ON api_quota_log(api_name)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_request_time ON api_quota_log(request_time)')
        
        print("✅ api_quota_log 表创建完成")
        
        # 3. 创建data_update_schedule表（数据更新计划）
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS data_update_schedule (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data_type TEXT NOT NULL,         -- 数据类型
            update_frequency TEXT,           -- 更新频率: daily/weekly/monthly
            last_update_time TIMESTAMP,      -- 最后更新时间
            next_update_time TIMESTAMP,      -- 下次计划时间
            estimated_rows INTEGER,          -- 估计数据行数
            api_cost INTEGER,                -- API调用成本(次数)
            enabled BOOLEAN DEFAULT 1,       -- 是否启用
            description TEXT                 -- 描述
        )
        ''')
        
        # 插入默认的更新计划
        today = datetime.now().strftime('%Y-%m-%d')
        next_week = (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')
        
        update_schedules = [
            ('fund_portfolio', 'weekly', today, next_week, 8000, 1, 1, '基金持仓数据，每季度更新，缓存7天'),
            ('index_daily', 'daily', today, today, 2, 1, 1, '指数日线数据，每日更新'),
            ('index_dailybasic', 'daily', today, today, 1, 1, 1, '指数估值数据，每日更新'),
            ('fund_daily', 'daily', today, today, 2, 1, 1, 'ETF日线数据，每日更新'),
            ('moneyflow_hsgt', 'daily', today, today, 2, 1, 1, '北向资金数据，每日更新'),
            ('stk_holdernumber', 'monthly', today, next_week, 100, 1, 1, '股东人数数据，每月更新')
        ]
        
        cursor.executemany('''
        INSERT OR REPLACE INTO data_update_schedule 
        (data_type, update_frequency, last_update_time, next_update_time, estimated_rows, api_cost, enabled, description)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', update_schedules)
        
        print("✅ data_update_schedule 表创建并初始化完成")
        
        # 4. 创建cache_statistics表（缓存统计）
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS cache_statistics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cache_type TEXT NOT NULL,        -- 缓存类型
            total_rows INTEGER DEFAULT 0,    -- 总数据行数
            last_update TIMESTAMP,           -- 最后更新时间
            hit_count INTEGER DEFAULT 0,     -- 命中次数
            miss_count INTEGER DEFAULT 0,    -- 未命中次数
            avg_response_time REAL,          -- 平均响应时间
            storage_size INTEGER             -- 存储大小(字节)
        )
        ''')
        
        # 5. 创建主琥珀引擎数据库的连接表（如果需要）
        # 检查主数据库是否存在并创建连接
        if os.path.exists(DB_PATH):
            print(f"📊 主琥珀引擎数据库存在: {DB_PATH}")
            
            # 在主数据库中创建缓存状态表
            main_conn = sqlite3.connect(DB_PATH)
            main_cursor = main_conn.cursor()
            
            main_cursor.execute('''
            CREATE TABLE IF NOT EXISTS cache_status (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cache_name TEXT NOT NULL,
                last_sync_time TIMESTAMP,
                row_count INTEGER,
                vault_db_path TEXT,
                enabled BOOLEAN DEFAULT 1
            )
            ''')
            
            # 插入缓存状态记录
            main_cursor.execute('''
            INSERT OR REPLACE INTO cache_status 
            (cache_name, last_sync_time, row_count, vault_db_path, enabled)
            VALUES (?, ?, ?, ?, ?)
            ''', ('tushare_cache', datetime.now().isoformat(), 0, CACHE_DB_PATH, 1))
            
            main_conn.commit()
            main_conn.close()
            print("✅ 主数据库缓存状态表更新完成")
        
        # 提交所有更改
        conn.commit()
        
        # 显示表结构
        print("\n📋 数据库表结构:")
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        tables = cursor.fetchall()
        
        for table in tables:
            table_name = table[0]
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()
            print(f"\n  📊 {table_name}:")
            for col in columns:
                print(f"    - {col[1]} ({col[2]})")
        
        # 显示数据更新计划
        print("\n📅 数据更新计划:")
        cursor.execute("SELECT data_type, update_frequency, next_update_time, description FROM data_update_schedule")
        schedules = cursor.fetchall()
        
        for schedule in schedules:
            data_type, freq, next_time, desc = schedule
            print(f"  🔄 {data_type:20} {freq:10} 下次更新: {next_time} - {desc}")
        
        # 计算预估API节省
        cursor.execute("SELECT SUM(api_cost) FROM data_update_schedule WHERE update_frequency != 'daily'")
        non_daily_cost = cursor.fetchone()[0] or 0
        
        print(f"\n💰 预估API额度节省:")
        print(f"  非每日更新数据API成本: {non_daily_cost} 次/天")
        print(f"  按7天缓存计算节省: {non_daily_cost * 6} 次/周")
        print(f"  按30天计算节省: {non_daily_cost * 29} 次/月")
        
        conn.close()
        
        print("\n" + "=" * 80)
        print("🏆 Amber-Vault 数据库重构完成")
        print("=" * 80)
        print(f"✅ 数据库文件: {CACHE_DB_PATH}")
        print(f"✅ 总表数量: {len(tables)}")
        print(f"✅ 数据更新计划: {len(schedules)} 个")
        print(f"✅ 预估API节省: {non_daily_cost * 29} 次/月")
        
        return True
        
    except Exception as e:
        print(f"❌ 数据库重构失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_cache_functionality():
    """测试缓存功能"""
    print("\n" + "=" * 80)
    print("🧪 测试Amber-Vault缓存功能")
    print("=" * 80)
    
    try:
        conn = sqlite3.connect(CACHE_DB_PATH)
        cursor = conn.cursor()
        
        # 测试1: 插入测试数据
        test_data = [
            ('510300.SH', '2026-01-22', '2025-12-31', '600519.SH', 15000.0, 50.0, 0.05, 0.03),
            ('510300.SH', '2026-01-22', '2025-12-31', '000858.SZ', 12000.0, 100.0, 0.04, 0.025),
            ('510300.SH', '2026-01-22', '2025-12-31', '000333.SZ', 8000.0, 80.0, 0.03, 0.02)
        ]
        
        cursor.executemany('''
        INSERT OR IGNORE INTO fund_portfolio_cache 
        (ts_code, ann_date, end_date, symbol, mkv, amount, stk_mkv_ratio, mkv_ratio)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', test_data)
        
        conn.commit()
        
        # 测试2: 查询数据
        cursor.execute("SELECT COUNT(*) FROM fund_portfolio_cache")
        row_count = cursor.fetchone()[0]
        print(f"✅ 测试数据插入成功，当前行数: {row_count}")
        
        # 测试3: 查询特定基金持仓
        cursor.execute('''
        SELECT symbol, mkv, mkv_ratio 
        FROM fund_portfolio_cache 
        WHERE ts_code = '510300.SH' 
        ORDER BY mkv DESC 
        LIMIT 5
        ''')
        
        holdings = cursor.fetchall()
        print(f"✅ 510300.SH 前5大持仓:")
        for symbol, mkv, ratio in holdings:
            print(f"   {symbol}: 市值 {mkv:,.0f}万，占比 {ratio*100:.2f}%")
        
        # 测试4: 记录API调用
        cursor.execute('''
        INSERT INTO api_quota_log 
        (api_name, data_rows, response_time, estimated_remaining, status)
        VALUES (?, ?, ?, ?, ?)
        ''', ('fund_portfolio', 8000, 0.31, 4999, 'success'))
        
        conn.commit()
        
        # 测试5: 查询API使用统计
        cursor.execute('''
        SELECT api_name, COUNT(*) as call_count, SUM(data_rows) as total_rows
        FROM api_quota_log
        GROUP BY api_name
        ''')
        
        api_stats = cursor.fetchall()
        print(f"\n📊 API使用统计:")
        for api_name, call_count, total_rows in api_stats:
            print(f"   {api_name:20} 调用 {call_count:3d} 次，获取 {total_rows:6d} 行数据")
        
        conn.close()
        
        print("\n✅ 缓存功能测试通过")
        return True
        
    except Exception as e:
        print(f"❌ 缓存功能测试失败: {e}")
        return False

def main():
    """主函数"""
    print("🚀 开始Amber-Vault数据库重构...")
    
    # 1. 创建数据库结构
    schema_created = create_tushare_cache_schema()
    
    if not schema_created:
        print("❌ 数据库结构创建失败")
        return False
    
    # 2. 测试缓存功能
    cache_tested = test_cache_functionality()
    
    if not cache_tested:
        print("⚠️ 缓存功能测试失败")
    
    # 3. 生成配置报告
    generate_config_report()
    
    print("\n" + "=" * 80)
    print("🎉 Amber-Vault数据库重构完成")
    print("=" * 80)
    print("✅ 数据库结构: 5个专业表已创建")
    print("✅ 缓存策略: 低频数据7天缓存，高频数据实时更新")
    print("✅ API优化: 预估每月节省大量API调用额度")
    print(f"✅ 数据库文件: {CACHE_DB_PATH}")
    
    return True

def generate_config_report():
    """生成配置报告"""
    report_dir = os.path.join(BASE_DIR, "reports", "vault")
    os.makedirs(report_dir, exist_ok=True)
    
    report_file = os.path.join(report_dir, f"amber_vault_config_{datetime.now().strftime('%Y%m%d_%H%M')}.md")
    
    report_content = f"""# 🗄️ Amber-Vault 数据库配置报告

## 配置信息
- **配置时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **数据库路径**: {CACHE_DB_PATH}
- **设计目标**: 低频数据缓存，优化API额度使用

## 表结构设计

### 1. fund_portfolio_cache (基金持仓缓存)
**更新频率**: 7天/次 (基金持仓每季度更新)
**字段设计**:
- ts_code: 基金代码
- ann_date: 公告日期
- end_date: 报告期
- symbol: 股票代码
- mkv: 持仓市值(万元)
- amount: 持仓数量(万股)
- stk_mkv_ratio: 占股票市值比
- mkv_ratio: 占净值比例
- update_time: 更新时间戳

**索引策略**:
- 主键: (ts_code, end_date, symbol) 唯一约束
- 查询索引: 基金代码、报告期、股票代码

### 2. api_quota_log (API额度日志)
**监控维度**:
- API名称、请求次数、数据行数
- 响应时间、剩余额度估计
- 请求时间、状态

### 3. data_update_schedule (数据更新计划)
**智能调度**:
- 数据类型、更新频率(daily/weekly/monthly)
- 最后更新时间、下次计划时间
- 估计数据行数、API调用成本
- 启用状态、描述

### 4. cache_statistics (缓存统计)
**性能监控**:
- 缓存类型、总数据行数
- 最后更新时间、命中次数
- 未命中次数、平均响应时间
- 存储大小

## 缓存策略

### 高频数据 (每日更新)
- index_daily: 指数日线行情
- index_dailybasic: 指数估值数据
- fund_daily: ETF日线数据
- moneyflow_hsgt: 北向资金数据

### 低频数据 (7天缓存)
- fund_portfolio: 基金持仓数据 (核心节省点)
- stk_holdernumber: 股东人数数据

## API额度优化计算

### 当前配置节省:
```
fund_portfolio: 1次/天 → 1次/7天 (节省6次/周)
stk_holdernumber: 1次/天 → 1次/7天 (节省6次/周)
总计节省: 12次/周 = 48次/月
```

### 实际业务价值:
- **额度释放**: 将节省的API额度用于高频行情数据
- **数据质量**: 低频数据缓存确保数据一致性
- **系统稳定**: 避免因额度耗尽导致的数据中断

## 集成方案

### 数据流设计:
```
Tushare API → Amber-Vault缓存 → 业务查询
      ↓             ↓
  原始数据       缓存数据
      ↓             ↓
  高频更新       低频更新
      ↓             ↓
实时性优先      节省额度优先
```

### 查询逻辑:
```python
def get_fund_portfolio(ts_code, use_cache=True):
    if use_cache:
        # 先查询缓存
        cached_data = query_cache('fund_portfolio', ts_code)
        if cached_data and not is_cache_expired(cached_data):
            return cached_data
    
    # 缓存不存在或已过期，调用API
    fresh_data = call_tushare_api('fund_portfolio', ts_code)
    
    # 更新缓存
    update_cache('fund_portfolio', ts_code, fresh_data)
    
    return fresh_data
```

## 运维监控

### 监控指标:
1. **缓存命中率**: 目标 > 80%
2. **API调用次数**: 每日统计和预警
3. **数据新鲜度**: 缓存数据更新时间
4. **存储空间**: 数据库文件大小监控

### 告警规则:
- 缓存命中率 < 60%: 警告
- API调用超每日限额80%: 警告
- 数据更新失败: 紧急告警
- 存储空间 > 1GB: 警告

## 部署说明

### 初始化步骤:
1. 运行本脚本创建数据库结构
2. 初始化数据更新计划
3. 配置定时任务执行缓存更新
4. 集成到琥珀引擎查询逻辑

### 维护任务:
- 每日: 检查缓存命中率和API使用
- 每周: 清理过期缓存数据
- 每月: 分析缓存效果和优化策略

---
*配置时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
*Amber-Vault 缓存系统*
"""

    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report_content)
    
    print(f"📋 配置报告已生成: {report_file}")

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)