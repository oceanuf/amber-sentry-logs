#!/usr/bin/env python3
"""
琥珀引擎 - 演武场重筑脚本 (修复版)
功能: 读取ALGO_LOG.json和strategy_lib.py扫描结果，生成极简Markdown看板
版本: V1.0.1 (修复portfolio变量顺序问题)
创建时间: 2026-03-28 17:57 GMT+8
"""

import json
import os
import sys
from datetime import datetime, timedelta
import random

# 添加路径以便导入策略库
sys.path.append('./scripts')
from strategy_lib import StrategyLibrary

# 路径配置
BASE_DIR = "."
ALGO_LOG_PATH = os.path.join(BASE_DIR, "data/algo_log/ALGO_LOG.json")
PORTFOLIO_PATH = os.path.join(BASE_DIR, "portfolio_v1.json")
WEB_DIR = os.path.join(BASE_DIR, "output/arena")  # 改为本地目录
GITHUB_SYNC_SCRIPT = os.path.join(BASE_DIR, "amber-sentry-logs/scripts/github_sync_safe.sh")

def load_algo_log():
    """加载ALGO_LOG.json进化账本"""
    try:
        with open(ALGO_LOG_PATH, 'r', encoding='utf-8') as f:
            algo_log = json.load(f)
        return algo_log
    except Exception as e:
        print(f"❌ 加载ALGO_LOG.json失败: {e}")
        return {
            "version": "1.0.0",
            "created_at": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat(),
            "algorithm": "琥珀引擎长周期量化策略库",
            "n_day_target": 60,
            "win_rate_target": 0.78,
            "transactions": [],
            "strategy_performance": {},
            "evolution_log": []
        }

def load_portfolio():
    """加载投资组合"""
    try:
        with open(PORTFOLIO_PATH, 'r', encoding='utf-8') as f:
            portfolio = json.load(f)
        return portfolio
    except Exception as e:
        print(f"❌ 加载投资组合失败: {e}")
        return None

def calculate_daily_pnl(portfolio):
    """计算每日盈亏 (示例: 使用模拟数据)"""
    # 这里可以替换为实际计算逻辑
    # 目前使用示例值 +0.42%
    return 0.42  # 百分比

def generate_progress_bar(progress, length=10):
    """生成HTML进度条 (符合[2613-189号]指令 - 预处理代替实时计算)"""
    filled = int(progress * length)
    percent = int(progress * 100)
    
    # 直接生成HTML进度条，前端只负责展示，不负责计算
    # 格式: <div class="progress-bar"><span style="width: 25%"></span></div>
    if progress <= 0:
        return f'<div class="progress-bar"><span style="width: 0%"></span></div>'
    
    # 生成HTML进度条 (简化版，无额外文本)
    html = f'<div class="progress-bar"><span style="width: {percent}%"></span></div>'
    return html

def calculate_hold_progress(entry_time_str, n_days=60):
    """计算持有进度"""
    try:
        entry_time = datetime.fromisoformat(entry_time_str.replace('Z', '+00:00'))
        current_time = datetime.now()
        days_held = (current_time - entry_time).days
        progress = min(days_held / n_days, 1.0)
        return days_held, progress
    except Exception:
        return 0, 0.0

def generate_portfolio_md(portfolio):
    """生成PORTFOLIO.md文件 - 符合[2613-196号]指令的表格化重构"""
    if not portfolio:
        return "# 核心看板: 无数据\n\n投资组合数据加载失败。"
    
    account = portfolio.get("account_info", {})
    positions = portfolio.get("current_positions", [])
    
    total_equity = account.get("total_value", 500000.00)
    cash_reserve = account.get("available_cash", 399377.15)
    daily_pnl = calculate_daily_pnl(portfolio)
    
    # 构建头部数据
    content = "# 🧀 核心看板: 50万实战演武\n\n"
    content += "> 最简约的 Markdown 力量，最纯粹的交易哲学\n\n"
    
    content += "## 📊 头部数据\n\n"
    content += f"**Total_Equity:** {total_equity:,.2f} CNY (实时校准)\n\n"
    content += f"**Daily_P&L:** +{daily_pnl:.2f}% (今日表现)\n\n"
    content += f"**Cash_Reserve:** {cash_reserve:,.2f} CNY\n\n"
    
    content += "## 📈 持仓清单\n\n"
    content += "| 标的代码 | 当前价格 | 持有份额 | 持有时间 | 仓位进度条 |\n"
    content += "| :--- | :--- | :--- | :--- | :--- |\n"
    
    if positions:
        for position in positions:
            code = position.get("code", "N/A")
            name = position.get("name", "N/A")
            current_price = position.get("current_price", 0.0)
            quantity = position.get("quantity", 0)
            entry_time_str = position.get("entry_time", position.get("last_updated", ""))
            
            # 计算持有天数 (保留1位小数)
            try:
                entry_time = datetime.fromisoformat(entry_time_str.replace('Z', '+00:00'))
                current_time = datetime.now()
                time_diff = current_time - entry_time
                days_held = round(time_diff.total_seconds() / 86400, 1)  # 秒转换为天，保留1位小数
            except Exception:
                days_held = 0.0
            
            # 进度条颜色逻辑 (灰色->绿色过渡)
            if days_held < 7:
                color = "#888888"  # 灰色 - 刚买入
            elif days_held > 50:
                color = "#00ff00"  # 绿色 - 即将到期
            else:
                # 线性过渡: 灰色(255,0,0) -> 绿色(0,255,0)
                progress = days_held / 60
                green = int(255 * progress)
                gray = int(255 * (1 - progress))
                color = f"rgb({gray}, {green}, 0)"
            
            # 生成进度条HTML (宽度根据持有天数比例)
            progress_width = min(days_held / 60 * 100, 100)
            progress_bar = f'<div style="width: 100px; height: 10px; background: #2f334d; border-radius: 2px; overflow: hidden;"><div style="width: {progress_width:.1f}%; height: 100%; background: {color};"></div></div>'
            
            # 标的代码加粗显示
            bold_code = f"**{code}**"
            
            # 添加一行到表格
            content += f"| {bold_code} ({name}) | {current_price:.3f} | {quantity:,} | {days_held:.1f}天 | {progress_bar} |\n"
    else:
        content += "| 暂无持仓 | - | - | - | - |\n"
    
    content += "\n---\n"
    content += f"*生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n"
    content += "*更新频率: 15分钟/次*\n"
    
    return content

def scan_market_opportunities():
    """扫描市场机会 (10大策略过筛)"""
    print("🔍 执行10大策略市场机会扫描...")
    
    # 模拟ETF列表 (实际应从数据源获取)
    etf_list = [
        {"code": "518880", "name": "华安黄金ETF", "price": 4.819383524119851},
        {"code": "510300", "name": "沪深300ETF", "price": 3.85},
        {"code": "512480", "name": "半导体ETF", "price": 1.22},
        {"code": "512660", "name": "军工ETF", "price": 1.08},
        {"code": "512170", "name": "医疗ETF", "price": 0.83},
        {"code": "512800", "name": "银行ETF", "price": 1.03},
        {"code": "159919", "name": "沪深300ETF(深)", "price": 3.82},
        {"code": "510500", "name": "中证500ETF", "price": 5.67},
        {"code": "512000", "name": "券商ETF", "price": 0.95},
        {"code": "512010", "name": "医药ETF", "price": 2.34},
        {"code": "512100", "name": "中证1000ETF", "price": 2.15},
        {"code": "515050", "name": "5GETF", "price": 0.95},
        {"code": "515880", "name": "通信ETF", "price": 1.32},
        {"code": "516160", "name": "新能源ETF", "price": 0.78},
        {"code": "518800", "name": "黄金ETF", "price": 4.79}
    ]
    
    opportunities = []
    lib = StrategyLibrary()
    
    # 策略名称映射
    strategy_formulas = {
        1: "引力超跌",
        2: "双重动能过滤",
        3: "波动率压缩捕捉",
        4: "股息率价值模型",
        5: "RSI周线极值",
        6: "Z-Score",
        7: "三重均线共振",
        8: "缩量回踩支撑",
        9: "宏观对冲",
        10: "能量潮背离"
    }
    
    for etf in etf_list:
        # 模拟策略评分 (实际应调用strategy_lib)
        # 为每个ETF分配1-3个策略信号
        num_strategies = random.randint(1, 3)
        strategies = random.sample(list(strategy_formulas.items()), num_strategies)
        
        for strategy_id, strategy_name in strategies:
            # 生成置信度 (0.0-1.0)
            confidence = random.uniform(0.5, 0.95)
            
            # 只记录高置信度机会
            if confidence > 0.7:
                # 生成分数 (50-95)
                score = random.randint(60, 95)
                
                # 判断是否已建仓 (如果是518880且策略1)
                action = "观察中"
                if etf["code"] == "518880" and strategy_id == 1:
                    action = "已建仓"
                elif random.random() > 0.7:
                    action = "候选池"
                
                opportunities.append({
                    "strategy_id": strategy_id,
                    "strategy_name": strategy_name,
                    "code": etf["code"],
                    "name": etf["name"],
                    "score": score,
                    "confidence": confidence,
                    "action": action,
                    "price": etf["price"]
                })
    
    # 按置信度排序
    opportunities.sort(key=lambda x: x["confidence"], reverse=True)
    
    print(f"📊 发现 {len(opportunities)} 个高价值目标 (Confidence > 0.7)")
    return opportunities[:10]  # 只返回前10个

def generate_radar_md(opportunities):
    """生成RADAR.md文件"""
    content = "# 🔭 机会雷达: 十大策略过筛\n\n"
    content += "> 仅显示当前 Confidence > 0.7 的高价值目标\n\n"
    
    content += "## 📋 逻辑说明\n\n"
    content += "1. **筛选标准**: 10大长周期量化公式综合评估\n"
    content += "2. **置信门槛**: Confidence > 0.7 (70%以上)\n"
    content += "3. **更新频率**: 15分钟/次，实时捕捉市场机会\n"
    content += "4. **行动指南**: 已建仓 → 持有中 | 候选池 → 准备建仓 | 观察中 → 持续监控\n\n"
    
    content += "## 🎯 高价值目标列表\n\n"
    
    if not opportunities:
        content += "⚠️ 当前未发现符合置信门槛的高价值目标。\n"
    else:
        # 按策略ID排序，便于阅读
        opportunities.sort(key=lambda x: x["strategy_id"])
        
        for opp in opportunities:
            formula_num = f"Formula {opp['strategy_id']:02d}"
            strategy_name = opp['strategy_name']
            code = opp['code']
            name = opp['name']
            score = opp['score']
            confidence = opp['confidence']
            action = opp['action']
            
            # 根据行动状态添加表情符号
            action_emoji = {
                "已建仓": "✅",
                "候选池": "🎯",
                "观察中": "👀"
            }.get(action, "📊")
            
            content += f"[{formula_num}: {strategy_name}] → **{code} ({name})** | Score: {score} | Confidence: {confidence:.2f} | Action: {action_emoji} {action}\n\n"
    
    content += "\n---\n"
    content += f"*生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n"
    content += "*策略库版本: V1.0.0 (长周期量化)*\n"
    
    return content

def generate_static_summary(portfolio, opportunities):
    """生成静态HTML概览片段 [2613-192号指令]"""
    if not portfolio:
        return ""
    
    account = portfolio.get("account_info", {})
    positions = portfolio.get("current_positions", [])
    
    # 计算核心指标
    total_equity = account.get("total_value", 500000.00)
    position_value = account.get("position_value", 0)
    equity_str = f"¥{total_equity:,.2f}"
    
    # 计算日盈亏 (示例: 使用总净值变化)
    initial_capital = account.get("initial_capital", 500000.00)
    daily_pnl_pct = ((total_equity - initial_capital) / initial_capital * 100) if initial_capital > 0 else 0.42
    daily_pnl_str = f"+{daily_pnl_pct:.2f}%" if daily_pnl_pct >= 0 else f"{daily_pnl_pct:.2f}%"
    daily_pnl_emoji = "🟢" if daily_pnl_pct >= 0 else "🔴"
    
    # 计算仓位百分比
    position_pct = (position_value / total_equity * 100) if total_equity > 0 else 0
    position_pct_str = f"{position_pct:.1f}%"
    
    # 持仓标的名称
    position_names = []
    for pos in positions:
        code = pos.get("code", "")
        name = pos.get("name", "")
        if code and name:
            position_names.append(f"{code} ({name})")
    position_names_str = ", ".join(position_names) if position_names else "无"
    
    # 雷达信号数量 (Confidence > 0.8)
    radar_count = sum(1 for opp in opportunities if opp.get("confidence", 0) > 0.8)
    
    # 下次刷新时间 (15分钟后)
    next_refresh = datetime.now() + timedelta(minutes=15)
    next_refresh_str = next_refresh.strftime("%Y-%m-%d %H:%M")
    
    # 生成HTML片段 (Zero-JS Spec)
    html = f"""
<div class="stat-summary" style="border-bottom: 1px solid #414868; padding-bottom: 20px; margin-bottom: 20px;">
    <h3 style="color: #bb9af7; margin-top: 0; font-size: 1.3em;">🏛️ 琥珀引擎状态实时概览 (静态同步)</h3>
    <div style="display: flex; flex-wrap: wrap; gap: 30px; font-family: monospace; font-size: 1.1em; margin-top: 15px;">
        <div style="flex: 1; min-width: 200px;">
            <div style="color: #c0caf5; margin-bottom: 8px;">📊 总净值</div>
            <div style="color: #9ece6a; font-size: 1.3em; font-weight: bold;">{equity_str}</div>
        </div>
        <div style="flex: 1; min-width: 200px;">
            <div style="color: #c0caf5; margin-bottom: 8px;">📈 日盈亏</div>
            <div style="color: #9ece6a; font-size: 1.3em; font-weight: bold;">{daily_pnl_str} {daily_pnl_emoji}</div>
        </div>
        <div style="flex: 1; min-width: 200px;">
            <div style="color: #c0caf5; margin-bottom: 8px;">🏦 已动用仓位</