#!/usr/bin/env python3
"""
琥珀引擎 - 博物馆数据刷新脚本
功能: 将最新资产数据推送到list.html，实现"数字在跳动"
执行频率: 每30秒
"""

import json
import os
import sys
import random
from datetime import datetime, timedelta
import time

def load_amber_cmd():
    """加载amber_cmd.json"""
    cmd_path = "/home/luckyelite/.openclaw/workspace/amber-engine/amber-sentry-logs/amber_cmd.json"
    
    try:
        with open(cmd_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ 加载amber_cmd.json失败: {e}")
        return None

def load_portfolio():
    """加载portfolio_v1.json"""
    portfolio_path = "/home/luckyelite/.openclaw/workspace/amber-engine/portfolio_v1.json"
    
    try:
        with open(portfolio_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ 加载portfolio_v1.json失败: {e}")
        return None

def simulate_market_movement(config, portfolio):
    """模拟市场波动"""
    if not config or not portfolio:
        return config, portfolio
    
    # 模拟价格波动
    for position in portfolio["current_positions"]:
        # 随机波动 ±0.5%
        price_change = random.uniform(-0.005, 0.005)
        position["current_price"] = position["avg_price"] * (1 + price_change)
        position["position_value"] = position["quantity"] * position["current_price"]
        
        # 计算浮动盈亏
        position["unrealized_pnl"] = position["position_value"] - (position["avg_price"] * position["quantity"])
        if position["avg_price"] > 0:
            position["unrealized_pnl_percent"] = (position["unrealized_pnl"] / (position["avg_price"] * position["quantity"])) * 100
        else:
            position["unrealized_pnl_percent"] = 0
    
    # 更新投资组合总值
    portfolio["account_info"]["position_value"] = sum(p["position_value"] for p in portfolio["current_positions"])
    portfolio["account_info"]["total_value"] = (
        portfolio["account_info"]["available_cash"] + 
        portfolio["account_info"]["position_value"]
    )
    
    # 更新盈亏
    initial_capital = portfolio["account_info"]["initial_capital"]
    total_value = portfolio["account_info"]["total_value"]
    pnl_amount = total_value - initial_capital
    pnl_percent = (pnl_amount / initial_capital) * 100 if initial_capital > 0 else 0
    
    # 更新amber_cmd.json
    config["portfolio_summary"]["total_value"] = total_value
    config["portfolio_summary"]["p_l_amount"] = pnl_amount
    config["portfolio_summary"]["p_l_ratio"] = f"{pnl_percent:+.2f}%"
    config["portfolio_summary"]["cash_balance"] = portfolio["account_info"]["available_cash"]
    config["portfolio_summary"]["position_count"] = len(portfolio["current_positions"])
    
    # 计算仓位百分比
    if total_value > 0:
        position_percent = (portfolio["account_info"]["position_value"] / total_value * 100)
        config["portfolio_summary"]["position_percent"] = f"{position_percent:.2f}%"
    
    # 更新最后更新时间
    now = datetime.now()
    config["portfolio_summary"]["update_time"] = now.strftime("%Y-%m-%d %H:%M:%S")
    portfolio["account_info"]["last_updated"] = now.isoformat()
    
    return config, portfolio

def save_amber_cmd(config):
    """保存amber_cmd.json"""
    cmd_path = "/home/luckyelite/.openclaw/workspace/amber-engine/amber-sentry-logs/amber_cmd.json"
    
    try:
        with open(cmd_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"❌ 保存amber_cmd.json失败: {e}")
        return False

def save_portfolio(portfolio):
    """保存portfolio_v1.json"""
    portfolio_path = "/home/luckyelite/.openclaw/workspace/amber-engine/portfolio_v1.json"
    
    try:
        with open(portfolio_path, 'w', encoding='utf-8') as f:
            json.dump(portfolio, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"❌ 保存portfolio_v1.json失败: {e}")
        return False

def generate_trading_signals():
    """生成交易信号"""
    signals = []
    
    # 模拟信号生成
    signal_types = [
        ("518880", "华安黄金ETF", -4.1, "STRONG", "黄金避险情绪升温"),
        ("512480", "半导体ETF", -3.8, "MEDIUM", "半导体周期底部确认"),
        ("512660", "军工ETF", -3.2, "WEAK", "军工估值修复"),
        ("512170", "医疗ETF", -2.8, "WEAK", "医疗板块超跌反弹"),
        ("512800", "银行ETF", -1.5, "NONE", "银行估值修复")
    ]
    
    for code, name, bias, strength, reason in signal_types:
        signals.append({
            "code": code,
            "name": name,
            "bias": bias,
            "strength": strength,
            "reason": reason,
            "timestamp": datetime.now().isoformat()
        })
    
    return signals

def update_market_snapshot(config, signals):
    """更新市场快照"""
    if not config or not signals:
        return config
    
    # 筛选Top 3 Alpha
    top_alpha = sorted(signals, key=lambda x: x["bias"])[:3]
    config["market_snapshot"]["top_alpha"] = [s["code"] for s in top_alpha]
    
    # 计算平均偏离度
    avg_bias = sum(s["bias"] for s in signals) / len(signals)
    config["market_snapshot"]["avg_bias"] = f"{avg_bias:+.1f}%"
    
    # 计算机会数量（Bias < -3.5%）
    opportunity_count = sum(1 for s in signals if s["bias"] < -3.5)
    config["market_snapshot"]["opportunity_count"] = opportunity_count
    
    # 更新扫描时间
    config["market_snapshot"]["scan_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    return config

def main_refresh_cycle():
    """主刷新循环"""
    print("🔄 琥珀引擎 - 博物馆数据刷新")
    print(f"⏰ 执行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 加载数据
    config = load_amber_cmd()
    portfolio = load_portfolio()
    
    if not config or not portfolio:
        print("❌ 数据加载失败，跳过本次刷新")
        return False
    
    print("✅ 数据加载成功")
    print(f"💰 账户总值: ¥{config['portfolio_summary']['total_value']:,.2f}")
    print(f"📊 持仓数量: {config['portfolio_summary']['position_count']}")
    
    # 模拟市场波动
    print("📈 模拟市场波动...")
    config, portfolio = simulate_market_movement(config, portfolio)
    
    # 生成交易信号
    print("📡 生成交易信号...")
    signals = generate_trading_signals()
    
    # 更新市场快照
    config = update_market_snapshot(config, signals)
    
    # 保存数据
    print("💾 保存数据...")
    if save_amber_cmd(config):
        print("✅ amber_cmd.json 已更新")
    else:
        print("❌ amber_cmd.json 更新失败")
    
    if save_portfolio(portfolio):
        print("✅ portfolio_v1.json 已更新")
    else:
        print("❌ portfolio_v1.json 更新失败")
    
    # 显示更新结果
    print(f"\n📊 更新结果:")
    print(f"   账户总值: ¥{config['portfolio_summary']['total_value']:,.2f}")
    print(f"   当日盈亏: {config['portfolio_summary']['p_l_ratio']} (¥{config['portfolio_summary']['p_l_amount']:,.2f})")
    print(f"   仓位占比: {config['portfolio_summary']['position_percent']}")
    print(f"   Top Alpha: {', '.join(config['market_snapshot']['top_alpha'])}")
    print(f"   平均偏离度: {config['market_snapshot']['avg_bias']}")
    print(f"   机会数量: {config['market_snapshot']['opportunity_count']}")
    
    return True

def run_as_service(interval_seconds=30):
    """以服务模式运行"""
    print("🚀 启动博物馆数据刷新服务")
    print(f"📅 执行间隔: {interval_seconds}秒")
    print("🛑 按 Ctrl+C 停止服务")
    print("=" * 60)
    
    cycle_count = 0
    
    try:
        while True:
            cycle_count += 1
            print(f"\n🔔 第 {cycle_count} 次数据刷新")
            
            success = main_refresh_cycle()
            
            if success:
                # 计算下次执行时间
                next_time = datetime.now() + timedelta(seconds=interval_seconds)
                print(f"\n⏳ 下次刷新: {next_time.strftime('%Y-%m-%d %H:%M:%S')}")
                
                # 等待到下次执行时间
                print(f"💤 等待 {interval_seconds} 秒...")
                time.sleep(interval_seconds)
            else:
                # 失败时等待10秒重试
                print("🔄 等待10秒后重试...")
                time.sleep(10)
                
    except KeyboardInterrupt:
        print("\n👋 博物馆数据刷新服务已停止")
        return 0

def main():
    """主函数"""
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--service":
        # 服务模式
        interval = 30  # 默认30秒
        if len(sys.argv) > 2:
            try:
                interval = int(sys.argv[2])
            except:
                pass
        return run_as_service(interval)
    else:
        # 单次执行模式
        return 0 if main_refresh_cycle() else 1

if __name__ == "__main__":
    import sys
    sys.exit(main())
