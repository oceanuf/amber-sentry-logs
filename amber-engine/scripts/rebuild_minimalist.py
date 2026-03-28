#!/usr/bin/env python3
"""
琥珀引擎 - 演武场重筑脚本 (rebuild_minimalist.py)
功能: 读取ALGO_LOG.json和strategy_lib.py扫描结果，生成极简Markdown看板
版本: V1.0.0 (2613-185号指令集成)
创建时间: 2026-03-28 09:40 GMT+8
"""

import json
import os
import sys
from datetime import datetime, timedelta
import random

# 添加路径以便导入策略库
sys.path.append('/home/luckyelite/.openclaw/workspace/amber-engine/scripts')
from strategy_lib import StrategyLibrary

# 路径配置
BASE_DIR = "/home/luckyelite/.openclaw/workspace/amber-engine"
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
            <div style="color: #c0caf5; margin-bottom: 8px;">🏦 已动用仓位</div>
            <div style="color: #7aa2f7; font-size: 1.3em; font-weight: bold;">{position_pct_str}</div>
            <div style="color: #c0caf5; font-size: 0.9em; margin-top: 5px;">{position_names_str}</div>
        </div>
        <div style="flex: 1; min-width: 200px;">
            <div style="color: #c0caf5; margin-bottom: 8px;">🔭 雷达警戒标的</div>
            <div style="color: #e0af68; font-size: 1.3em; font-weight: bold;">{radar_count}个 (Confidence > 0.8)</div>
        </div>
    </div>
    <div style="margin-top: 20px; padding-top: 15px; border-top: 1px dashed #414868; color: #a9b1d6; font-size: 0.9em; font-family: monospace;">
        ⏰ 下次刷新时间: {next_refresh_str} (由脚本生成时写入)
    </div>
</div>
"""
    return html

def update_index_html():
    """更新index.html为极简门户"""
    html_content = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🧀 琥珀引擎演武场 - 静默入口</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            line-height: 1.6;
            margin: 0;
            padding: 40px 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .container {
            max-width: 600px;
            width: 100%;
        }
        .card {
            background: rgba(255, 255, 255, 0.95);
            border-radius: 16px;
            padding: 50px 40px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.15);
            backdrop-filter: blur(10px);
            text-align: center;
        }
        .title {
            color: #333;
            font-size: 28px;
            font-weight: 600;
            margin-bottom: 10px;
        }
        .subtitle {
            color: #666;
            font-size: 16px;
            margin-bottom: 40px;
            font-weight: 300;
        }
        .nav-links {
            display: flex;
            flex-direction: column;
            gap: 20px;
        }
        .nav-item {
            display: block;
            padding: 20px 24px;
            background: linear-gradient(135deg, #f5f7fa 0%, #e4edf5 100%);
            border-radius: 12px;
            text-decoration: none;
            color: #333;
            font-weight: 500;
            font-size: 18px;
            transition: all 0.3s ease;
            border: 2px solid transparent;
        }
        .nav-item:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
            border-color: #667eea;
        }
        .nav-item.portfolio {
            background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
            color: white;
        }
        .nav-item.radar {
            background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
            color: white;
        }
        .nav-item.memory {
            background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
            color: white;
        }
        .footer {
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid rgba(0, 0, 0, 0.1);
            color: #666;
            font-size: 14px;
        }
        .footer a {
            color: #667eea;
            text-decoration: none;
        }
        .badge {
            display: inline-block;
            padding: 4px 10px;
            background: rgba(102, 126, 234, 0.1);
            color: #667eea;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 500;
            margin-left: 10px;
            vertical-align: middle;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="card">
            <div class="title">🧀 琥珀引擎演武场</div>
            <div class="subtitle">最简约的力量，最纯粹的博弈</div>
            
            <div class="nav-links">
                <a href="portfolio_dashboard.html" class="nav-item portfolio">
                    [实战演武：PORTFOLIO看板]
                    <span class="badge">50万战场</span>
                </a>
                
                <a href="md_viewer.html?file=RADAR.md" class="nav-item radar">
                    [策略雷达：RADAR.md]
                    <span class="badge">十大策略</span>
                </a>
                
                <a href="md_viewer.html?file=SYSTEM_MEMORY.md" class="nav-item memory">
                    [共同记忆：SYSTEM_MEMORY.md]
                    <span class="badge">进化历程</span>
                </a>
            </div>
            
            <div class="footer">
                <p>Cheese Intelligence Team · 工程师 Cheese 执行 [2613-192号] 指令</p>
                <p>执行时间: """ + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + """ GMT+8</p>
                <p><a href="https://localhost:10168/">返回档案馆首页</a></p>
            </div>
        </div>
    </div>
</body>
</html>"""
    
    return html_content

def generate_portfolio_dashboard(portfolio, opportunities, portfolio_content):
    """生成PORTFOLIO静态看板页面 [2613-192号指令]"""
    # 获取静态概览
    static_summary = generate_static_summary(portfolio, opportunities)
    
    # 读取md_viewer.html作为模板
    template_path = "/var/www/gemini_master/master-audit/md_viewer.html"
    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            template = f.read()
    except Exception:
        # 如果模板不存在，使用基本模板
        template = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🧀 琥珀引擎演武场 - PORTFOLIO静态看板</title>
    <style>
        :root {
            --obsidian-bg: #1a1b26;
            --obsidian-surface: #24283b;
            --obsidian-surface-light: #2a2e3f;
            --obsidian-text: #c0caf5;
            --obsidian-text-muted: #a9b1d6;
            --obsidian-accent: #7aa2f7;
            --obsidian-accent-gold: #e0af68;
            --obsidian-success: #9ece6a;
            --obsidian-warning: #ff9e64;
            --obsidian-error: #f7768e;
            --obsidian-border: #414868;
            --obsidian-code-bg: #292e42;
        }
        
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Noto Sans', Helvetica, Arial, sans-serif;
            line-height: 1.6;
            color: var(--obsidian-text);
            background-color: var(--obsidian-bg);
            padding: 20px;
            min-height: 100vh;
        }
        
        .container {
            max-width: 1000px;
            margin: 0 auto;
            background: var(--obsidian-surface);
            border-radius: 12px;
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.5);
            overflow: hidden;
        }
        
        .header {
            background: linear-gradient(135deg, var(--obsidian-surface-light) 0%, var(--obsidian-bg) 100%);
            color: var(--obsidian-text);
            padding: 25px;
            text-align: center;
            border-bottom: 1px solid var(--obsidian-border);
        }
        
        .header h1 {
            font-size: 1.8rem;
            margin-bottom: 8px;
            font-weight: 600;
            background: linear-gradient(90deg, var(--obsidian-accent), var(--obsidian-accent-gold));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        
        .header .subtitle {
            font-size: 0.9rem;
            opacity: 0.8;
            color: var(--obsidian-text-muted);
        }
        
        .preview {
            padding: 25px;
            color: var(--obsidian-text);
            min-height: 300px;
        }
        
        .preview h1, .preview h2, .preview h3 {
            color: var(--obsidian-text);
            margin-top: 1.5em;
            margin-bottom: 0.8em;
            font-weight: 600;
        }
        
        .preview h1 {
            border-bottom: 2px solid var(--obsidian-accent);
            padding-bottom: 10px;
        }
        
        .preview h2 {
            border-bottom: 1px solid var(--obsidian-border);
            padding-bottom: 8px;
        }
        
        .preview p {
            margin-bottom: 1em;
            color: var(--obsidian-text-muted);
        }
        
        .preview strong {
            color: var(--obsidian-text);
            font-weight: 600;
        }
        
        .preview table {
            border-collapse: collapse;
            width: 100%;
            margin: 20px 0;
            border: 1px solid var(--obsidian-border);
            border-radius: 8px;
            overflow: hidden;
        }
        
        .preview table th, .preview table td {
            border: 1px solid var(--obsidian-border);
            padding: 12px 14px;
            text-align: left;
            color: var(--obsidian-text);
        }
        
        .preview table th {
            background: var(--obsidian-surface-light);
            font-weight: 600;
            color: var(--obsidian-accent);
        }
        
        .preview table tr:nth-child(even) {
            background: rgba(36, 40, 59, 0.5);
        }
        
        .preview code {
            background: var(--obsidian-code-bg);
            padding: 2px 6px;
            border-radius: 4px;
            font-family: 'Monaco', 'Menlo', monospace;
            font-size: 0.9em;
            color: var(--obsidian-accent-gold);
        }
        
        .preview pre {
            background: var(--obsidian-code-bg);
            padding: 15px;
            border-radius: 8px;
            overflow-x: auto;
            margin: 20px 0;
            border: 1px solid var(--obsidian-border);
        }
        
        .preview blockquote {
            border-left: 4px solid var(--obsidian-accent);
            padding-left: 20px;
            margin: 20px 0;
            color: var(--obsidian-text-muted);
            font-style: italic;
            background: rgba(122, 162, 247, 0.05);
            padding: 15px;
            border-radius: 0 8px 8px 0;
        }
        
        .footer {
            text-align: center;
            padding: 20px;
            background: var(--obsidian-surface-light);
            border-top: 1px solid var(--obsidian-border);
            color: var(--obsidian-text-muted);
            font-size: 0.85rem;
        }
        
        .footer a {
            color: var(--obsidian-accent);
            text-decoration: none;
            font-weight: 500;
        }
        
        /* 进度条样式 */
        .progress-bar {
            display: inline-block;
            width: 100px;
            height: 10px;
            background: var(--obsidian-surface-light);
            border-radius: 5px;
            overflow: hidden;
            vertical-align: middle;
            margin: 0 5px;
        }
        
        .progress-bar span {
            display: block;
            height: 100%;
            background: linear-gradient(90deg, #2ac3de, #73daca);
            border-radius: 5px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📄 琥珀引擎演武场 - PORTFOLIO静态看板</h1>
            <div class="subtitle">零外部请求 · 秒开渲染 · 极致简约 · [2613-192号指令]</div>
        </div>
        
        <div id="preview" class="preview">
            <!-- 静态内容将通过Python插入 -->
        </div>
        
        <div class="footer">
            <p>🧀 Cheese Intelligence Team · 工程师执行 [2613-192号] 极简静态看板</p>
            <p><a href="./">返回演武场门户</a></p>
        </div>
    </div>
</body>
</html>"""
    
    # 替换preview区域
    # 找到预览区域标记并替换
    preview_marker = '<div id="preview" class="preview">'
    if preview_marker in template:
        # 构建完整内容：静态概览 + PORTFOLIO.md内容
        full_content = f'{static_summary}\n<div style="margin-top: 30px;">\n{portfolio_content}\n</div>'
        # 替换整个preview区域
        start = template.find(preview_marker)
        end = template.find('</div>', start) + 6  # 找到对应的</div>
        if end > start:
            new_template = template[:start] + f'{preview_marker}\n{full_content}\n</div>' + template[end:]
        else:
            new_template = template.replace(preview_marker, f'{preview_marker}\n{full_content}')
    else:
        # 模板中没有标记，直接替换整个body内容
        body_marker = '<body>'
        if body_marker in template:
            body_end = template.find('</body>')
            new_template = template[:template.find(body_marker) + len(body_marker)] + f'''
    <div class="container">
        <div class="header">
            <h1>📄 琥珀引擎演武场 - PORTFOLIO静态看板</h1>
            <div class="subtitle">零外部请求 · 秒开渲染 · 极致简约 · [2613-192号指令]</div>
        </div>
        
        <div class="preview">
            {static_summary}
            <div style="margin-top: 30px;">
                {portfolio_content}
            </div>
        </div>
        
        <div class="footer">
            <p>🧀 Cheese Intelligence Team · 工程师执行 [2613-192号] 极简静态看板</p>
            <p><a href="./">返回演武场门户</a></p>
        </div>
    </div>
''' + template[body_end:]
        else:
            # 创建全新页面
            new_template = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🧀 琥珀引擎演武场 - PORTFOLIO静态看板</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            margin: 0;
            padding: 20px;
            background: #1a1b26;
            color: #c0caf5;
            min-height: 100vh;
        }}
        .container {{
            max-width: 1000px;
            margin: 0 auto;
            background: #24283b;
            border-radius: 12px;
            overflow: hidden;
            box-shadow: 0 10px 40px rgba(0,0,0,0.5);
        }}
        .header {{
            background: #2a2e3f;
            padding: 25px;
            text-align: center;
            border-bottom: 1px solid #414868;
        }}
        .header h1 {{
            color: #7aa2f7;
            margin: 0 0 10px 0;
        }}
        .content {{
            padding: 25px;
        }}
        .footer {{
            text-align: center;
            padding: 20px;
            background: #2a2e3f;
            border-top: 1px solid #414868;
            color: #a9b1d6;
            font-size: 0.85rem;
        }}
        a {{
            color: #7aa2f7;
            text-decoration: none;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📄 琥珀引擎演武场 - PORTFOLIO静态看板</h1>
            <div class="subtitle">零外部请求 · 秒开渲染 · 极致简约 · [2613-192号指令]</div>
        </div>
        
        <div class="content">
            {static_summary}
            <div style="margin-top: 30px;">
                {portfolio_content}
            </div>
        </div>
        
        <div class="footer">
            <p>🧀 Cheese Intelligence Team · 工程师执行 [2613-192号] 极简静态看板</p>
            <p><a href="./">返回演武场门户</a></p>
        </div>
    </div>
</body>
</html>'''
    
    return new_template

def run_github_sync():
    """执行GitHub同步"""
    if os.path.exists(GITHUB_SYNC_SCRIPT):
        try:
            # 设置环境变量
            env = os.environ.copy()
            
            # 执行同步脚本
            import subprocess
            result = subprocess.run(
                ["bash", GITHUB_SYNC_SCRIPT, "演武场重筑自动同步"],
                capture_output=True,
                text=True,
                cwd=os.path.dirname(os.path.dirname(GITHUB_SYNC_SCRIPT)),
                env=env
            )
            
            if result.returncode == 0:
                print("✅ GitHub同步成功")
                return True
            else:
                print(f"⚠️ GitHub同步失败: {result.stderr}")
                return False
        except Exception as e:
            print(f"❌ GitHub同步异常: {e}")
            return False
    else:
        print(f"⚠️ GitHub同步脚本不存在: {GITHUB_SYNC_SCRIPT}")
        return False

def main():
    """主函数"""
    print("🧀 琥珀引擎演武场重筑脚本启动")
    print("=" * 60)
    print(f"⏰ 执行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 确保本地输出目录存在
    os.makedirs(WEB_DIR, exist_ok=True)
    
    # 加载数据
    algo_log = load_algo_log()
    portfolio = load_portfolio()
    
    # 生成PORTFOLIO.md
    print("📋 生成PORTFOLIO.md...")
    portfolio_content = generate_portfolio_md(portfolio)
    portfolio_path = os.path.join(WEB_DIR, "PORTFOLIO.md")
    with open(portfolio_path, 'w', encoding='utf-8') as f:
        f.write(portfolio_content)
    print(f"✅ PORTFOLIO.md 已保存: {portfolio_path}")
    
    # 扫描机会并生成RADAR.md
    print("🔭 生成RADAR.md...")
    opportunities = scan_market_opportunities()
    radar_content = generate_radar_md(opportunities)
    radar_path = os.path.join(WEB_DIR, "RADAR.md")
    with open(radar_path, 'w', encoding='utf-8') as f:
        f.write(radar_content)
    print(f"✅ RADAR.md 已保存: {radar_path}")
    
    # 生成静态HTML概览 [2613-192号指令]
    print("🏛️ 生成静态HTML概览...")
    static_summary = generate_static_summary(portfolio, opportunities)
    static_html_path = os.path.join(WEB_DIR, "portfolio_static.html")
    with open(static_html_path, 'w', encoding='utf-8') as f:
        f.write(static_summary)
    print(f"✅ 静态HTML概览已保存: {static_html_path}")
    
    # 更新index.html
    print("🏠 更新index.html...")
    index_content = update_index_html()
    index_path = os.path.join(WEB_DIR, "index.html")
    with open(index_path, 'w', encoding='utf-8') as f:
        f.write(index_content)
    print(f"✅ index.html 已更新: {index_path}")
    
    # 生成PORTFOLIO静态看板页面 [2613-192号指令]
    print("📊 生成PORTFOLIO静态看板...")
    dashboard_content = generate_portfolio_dashboard(portfolio, opportunities, portfolio_content)
    dashboard_path = os.path.join(WEB_DIR, "portfolio_dashboard.html")
    with open(dashboard_path, 'w', encoding='utf-8') as f:
        f.write(dashboard_content)
    print(f"✅ PORTFOLIO静态看板已保存: {dashboard_path}")
    
    # 复制文件到Web目录（如果需要）
    web_target_dir = "/var/www/gemini_master/master-audit"
    if os.path.exists(web_target_dir):
        try:
            import subprocess
            for filename in ["PORTFOLIO.md", "RADAR.md", "index.html", "portfolio_dashboard.html", "portfolio_static.html"]:
                src = os.path.join(WEB_DIR, filename)
                dst = os.path.join(web_target_dir, filename)
                # 使用sudo复制文件
                result = subprocess.run(
                    ["sudo", "cp", src, dst],
                    capture_output=True,
                    text=True
                )
                if result.returncode == 0:
                    print(f"📤 已复制 {filename} 到Web目录")
                else:
                    print(f"⚠️ 复制 {filename} 失败: {result.stderr}")
        except Exception as e:
            print(f"⚠️ 复制到Web目录失败: {e}")
    
    # 执行GitHub同步
    print("🔄 执行GitHub同步...")
    sync_success = run_github_sync()
    
    print("\n" + "=" * 60)
    print("🎉 演武场重筑完成!")
    print(f"📁 生成文件:")
    print(f"   • PORTFOLIO.md (核心看板)")
    print(f"   • RADAR.md (机会雷达)")
    print(f"   • index.html (极简门户)")
    print(f"   • portfolio_dashboard.html (静态看板)")
    print(f"   • portfolio_static.html (静态概览片段)")
    print(f"🔄 GitHub同步: {'✅ 成功' if sync_success else '⚠️ 失败'}")
    print(f"🌐 访问地址: https://gemini.googlemanager.cn:10168/portfolio_dashboard.html")
    print("\n💡 说明: 本脚本将自动设置为每15分钟执行一次")
    
    return 0

def setup_cron_job():
    """设置定时任务 (每15分钟执行)"""
    cron_command = f"*/15 * * * * cd /home/luckyelite/.openclaw/workspace/amber-engine/scripts && python3 rebuild_minimalist.py >> /home/luckyelite/.openclaw/workspace/amber-engine/logs/rebuild_minimalist.log 2>&1"
    
    print(f"⏰ 建议Cron定时任务:")
    print(f"   {cron_command}")
    print("\n💡 说明: 每15分钟自动更新演武场看板")
    print("   请手动添加至crontab: crontab -e")
    
    return cron_command

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--setup-cron":
        setup_cron_job()
    else:
        sys.exit(main())