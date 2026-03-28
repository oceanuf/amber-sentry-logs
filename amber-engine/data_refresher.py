#!/usr/bin/env python3
"""
[2613-201号-B] 档案馆效能增强令 - 自动化数据装填脚本 (Hot Loader)
版本: V1.0.0
作者: 工程师 Cheese
创建时间: 2026-03-28 16:22 GMT+8

功能: 每小时抓取518880等标的实时净值，静默更新database/*.json文件
目标: 确保档案馆详情永远是最新鲜的火药
"""

import os
import sys
import json
import time
import logging
import schedule
import requests
from datetime import datetime
from pathlib import Path

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/home/luckyelite/.openclaw/workspace/amber-engine/logs/data_refresher.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# 工作目录
WORKSPACE_DIR = Path("/home/luckyelite/.openclaw/workspace/amber-engine")
DATABASE_DIR = WORKSPACE_DIR / "database"
VAULTS_DATA_DIR = WORKSPACE_DIR / "vaults" / "data"
LOGS_DIR = WORKSPACE_DIR / "logs"

# 确保目录存在
for directory in [DATABASE_DIR, VAULTS_DATA_DIR, LOGS_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# 监控的标的列表 (可扩展)
TARGETS = [
    {"code": "518880", "name": "华安黄金ETF", "type": "etf"},
    {"code": "512800", "name": "华宝银行ETF", "type": "etf"},
    {"code": "510300", "name": "沪深300ETF", "type": "etf"},
    {"code": "159919", "name": "沪深300ETF(深)", "type": "etf"},
    {"code": "510500", "name": "中证500ETF", "type": "etf"},
]

def fetch_tushare_data(code):
    """从Tushare获取实时数据"""
    try:
        # 这里使用Tushare Pro API
        # 实际实现需要配置Tushare Token
        import tushare as ts
        
        # 设置Tushare Token (从环境变量读取)
        ts_token = os.getenv('TUSHARE_TOKEN')
        if not ts_token:
            logger.warning(f"TUSHARE_TOKEN未设置，跳过{code}的数据抓取")
            return None
            
        ts.set_token(ts_token)
        pro = ts.pro_api()
        
        # 获取基金净值
        df = pro.fund_nav(ts_code=f"{code}.SH", fields="ts_code,trade_date,unit_nav,accum_nav")
        if df.empty:
            logger.warning(f"未找到{code}的净值数据")
            return None
            
        latest = df.iloc[0]
        return {
            "code": code,
            "trade_date": latest["trade_date"],
            "unit_nav": float(latest["unit_nav"]),
            "accum_nav": float(latest["accum_nav"]),
            "source": "TUSHARE",
            "fetch_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    except Exception as e:
        logger.error(f"Tushare抓取{code}失败: {e}")
        return None

def fetch_akshare_data(code):
    """从AkShare获取实时数据 (备用)"""
    try:
        import akshare as ak
        
        # 去除后缀
        clean_code = code.split('.')[0] if '.' in code else code
        
        # 获取ETF实时行情
        df = ak.fund_etf_hist_sina(symbol=f"sh{clean_code}", period="daily", adjust="qfq")
        if df.empty:
            logger.warning(f"未找到{code}的AkShare数据")
            return None
            
        latest = df.iloc[0]
        return {
            "code": code,
            "trade_date": latest["date"].strftime("%Y%m%d"),
            "close": float(latest["close"]),
            "source": "AKSHARE",
            "fetch_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    except Exception as e:
        logger.error(f"AkShare抓取{code}失败: {e}")
        return None

def update_database_file(target):
    """更新数据库文件"""
    code = target["code"]
    filename = f"{code}_data.json"
    filepath = DATABASE_DIR / filename
    vaults_filepath = VAULTS_DATA_DIR / filename
    
    # 尝试多种数据源
    data = None
    
    # 1. 优先Tushare
    data = fetch_tushare_data(code)
    
    # 2. 备用AkShare
    if not data:
        data = fetch_akshare_data(code)
    
    if not data:
        logger.warning(f"所有数据源均失败: {code}")
        return False
    
    # 读取现有数据
    existing_data = []
    if filepath.exists():
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                existing_data = json.load(f)
                if not isinstance(existing_data, list):
                    existing_data = []
        except Exception as e:
            logger.error(f"读取现有数据失败: {e}")
            existing_data = []
    
    # 添加新数据
    existing_data.append(data)
    
    # 保留最近100条记录
    if len(existing_data) > 100:
        existing_data = existing_data[-100:]
    
    # 保存到主数据库
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(existing_data, f, ensure_ascii=False, indent=2)
        logger.info(f"更新数据库: {filename} ({len(existing_data)}条记录)")
    except Exception as e:
        logger.error(f"保存数据库失败: {e}")
        return False
    
    # 同步到vaults/data目录
    try:
        with open(vaults_filepath, 'w', encoding='utf-8') as f:
            json.dump(existing_data, f, ensure_ascii=False, indent=2)
        logger.info(f"同步到vaults: {filename}")
    except Exception as e:
        logger.error(f"同步到vaults失败: {e}")
    
    return True

def refresh_all_targets():
    """刷新所有标的"""
    logger.info("开始执行数据刷新任务")
    success_count = 0
    
    for target in TARGETS:
        logger.info(f"处理标的: {target['code']} - {target['name']}")
        if update_database_file(target):
            success_count += 1
        time.sleep(2)  # 避免请求过于频繁
    
    logger.info(f"数据刷新完成: {success_count}/{len(TARGETS)} 成功")
    return success_count

def main():
    """主函数"""
    logger.info("=== 档案馆数据装填器启动 ===")
    logger.info(f"工作目录: {WORKSPACE_DIR}")
    logger.info(f"监控标的: {[t['code'] for t in TARGETS]}")
    
    # 立即执行一次
    logger.info("执行首次数据刷新...")
    refresh_all_targets()
    
    # 设置定时任务
    schedule.every(1).hours.do(refresh_all_targets)
    schedule.every().day.at("09:30").do(lambda: logger.info("交易日开盘时间"))
    schedule.every().day.at("15:00").do(lambda: logger.info("交易日收盘时间"))
    
    logger.info("定时任务已设置: 每小时执行一次数据刷新")
    
    # 主循环
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)  # 每分钟检查一次
    except KeyboardInterrupt:
        logger.info("接收到中断信号，优雅退出")
    except Exception as e:
        logger.error(f"主循环异常: {e}")
        sys.exit(1)

if __name__ == "__main__":
    # 检查依赖
    try:
        import tushare
        import akshare
        import schedule
        logger.info("所有依赖包已安装")
    except ImportError as e:
        logger.error(f"缺少依赖包: {e}")
        logger.info("请运行: pip install tushare akshare schedule")
        sys.exit(1)
    
    main()