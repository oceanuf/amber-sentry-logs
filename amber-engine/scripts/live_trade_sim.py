#!/usr/bin/env python3
"""
琥珀引擎 - 50万量化实验室实战算法 (长周期量化策略库集成版)
功能: 基于"星辰引力"系统 + 10大量化公式的自动化实战脚本
逻辑: 集成10大长周期策略，N=60天持有期，胜率目标78%
强制令: 持仓未满30天禁止自动止盈卖出（除非触碰熔断线）
版本: V2.0.0 (2613-173号指令集成)
创建时间: 2026-03-27 20:55
"""

import json
import os
import sys
import random
from datetime import datetime, timedelta
import time
import math
import sys
sys.path.append('./scripts')
from strategy_lib import strategy_lib

def load_config():
    """加载配置"""
    cmd_path = "./amber-sentry-logs/amber_cmd.json"
    portfolio_path = "./portfolio_v1.json"
    
    try:
        with open(cmd_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        with open(portfolio_path, 'r', encoding='utf-8') as f:
            portfolio = json.load(f)
        
        # 升级投资组合结构（添加N天倒计时字段）
        portfolio = upgrade_portfolio_structure(portfolio)
        
        return config, portfolio
    except Exception as e:
        print(f"❌ 加载配置失败: {e}")
        return None, None

def upgrade_portfolio_structure(portfolio):
    """升级投资组合结构，添加N天倒计时字段"""
    try:
        upgraded = False
        
        # 为每个持仓添加N天倒计时字段
        for position in portfolio.get("current_positions", []):
            if "entry_date" not in position and "entry_time" in position:
                position["entry_date"] = position["entry_time"]
                upgraded = True
            
            if "n_day_countdown" not in position:
                position["n_day_countdown"] = 60  # 默认N=60天
                upgraded = True
            
            if "strategy_used" not in position:
                position["strategy_used"] = "引力超跌模型 (Gravity-Dip)"  # 默认策略
                upgraded = True
            
            if "strategy_id" not in position:
                position["strategy_id"] = 1  # 默认策略ID
                upgraded = True
        
        # 添加N天持有期配置
        if "n_day_config" not in portfolio:
            portfolio["n_day_config"] = {
                "primary_n_days": 60,
                "min_hold_days_for_profit_taking": 30,
                "win_rate_targets": {30: 0.65, 60: 0.78, 90: 0.85},
                "last_upgraded": datetime.now().isoformat()
            }
            upgraded = True
        
        if upgraded:
            print("✅ 投资组合结构已升级 (N天倒计时字段已添加)")
        
        return portfolio
    except Exception as e:
        print(f"⚠️ 投资组合结构升级失败: {e}")
        return portfolio

def scan_127_report():
    """模拟扫描127号报告结果（实际应从REPORT_Gist_00127.md读取）"""
    # 模拟127号扫描结果
    scan_results = [
        {
            "code": "518880",
            "name": "华安黄金ETF",
            "bias": -4.1,
            "ma20": 4.85,
            "ma20_trend": "UP",
            "price": 4.82,
            "volume": 1500000,
            "signal_strength": "STRONG"
        },
        {
            "code": "512480",
            "name": "半导体ETF",
            "bias": -3.8,
            "ma20": 1.24,
            "ma20_trend": "UP",
            "price": 1.22,
            "volume": 800000,
            "signal_strength": "MEDIUM"
        },
        {
            "code": "512660",
            "name": "军工ETF",
            "bias": -3.2,
            "ma20": 1.10,
            "ma20_trend": "UP",
            "price": 1.08,
            "volume": 500000,
            "signal_strength": "WEAK"
        },
        {
            "code": "512170",
            "name": "医疗ETF",
            "bias": -2.8,
            "ma20": 0.84,
            "ma20_trend": "UP",
            "price": 0.83,
            "volume": 300000,
            "signal_strength": "WEAK"
        },
        {
            "code": "512800",
            "name": "银行ETF",
            "bias": -1.5,
            "ma20": 1.04,
            "ma20_trend": "FLAT",
            "price": 1.03,
            "volume": 200000,
            "signal_strength": "NONE"
        }
    ]
    
    return scan_results

def evaluate_strategy_signals(etf_data):
    """
    评估10大长周期量化策略信号
    返回策略评估结果
    """
    try:
        # 模拟数据 - 实际应从数据源获取
        symbol_data = {
            "symbol": etf_data["code"],
            "gravity_dip": {
                "current_price": etf_data["price"],
                "ma_200": etf_data.get("ma200", etf_data["price"] * 1.2),  # 模拟MA200
                "atr_14": etf_data.get("atr14", etf_data["price"] * 0.05)   # 模拟ATR14
            },
            "dual_momentum": {
                "current_price": etf_data["price"],
                "ma_200": etf_data.get("ma200", etf_data["price"] * 1.2),
                "price_90d_ago": etf_data.get("price_90d_ago", etf_data["price"] * 0.9)
            },
            "z_score": {
                "current_price": etf_data["price"],
                "ma_60": etf_data.get("ma60", etf_data["price"] * 1.1),
                "std_60": etf_data.get("std60", etf_data["price"] * 0.03)
            },
            "weekly_rsi": {
                "rsi_weekly": etf_data.get("rsi_weekly", 40)  # 模拟周线RSI
            }
        }
        
        # 使用策略库进行评估
        evaluation = strategy_lib.evaluate_all_strategies(symbol_data)
        
        return evaluation
    except Exception as e:
        print(f"⚠️ 策略信号评估失败 {etf_data['code']}: {e}")
        return {
            "symbol": etf_data["code"],
            "final_signal": "HOLD",
            "avg_confidence": 0.0,
            "error": str(e)
        }

def filter_hunting_targets(scan_results, config):
    """
    筛选符合猎杀条件的标的 (集成10大长周期策略)
    新增逻辑: 必须通过至少2个策略的BUY信号，且平均置信度>0.3
    """
    bias_threshold = config["trading_rules"]["bias_threshold"]
    hunting_priority = config["trading_rules"]["hunting_priority"]
    
    filtered = []
    
    for etf in scan_results:
        # 基础条件检查 (兼容旧逻辑)
        if etf["bias"] < bias_threshold and etf["ma20_trend"] == "UP":
            
            # 评估长周期策略信号
            strategy_eval = evaluate_strategy_signals(etf)
            
            # 策略过滤条件
            buy_signals = strategy_eval.get("buy_signals", 0)
            avg_confidence = strategy_eval.get("avg_confidence", 0)
            final_signal = strategy_eval.get("final_signal", "HOLD")
            
            # 策略要求: 至少2个BUY信号且平均置信度>0.3
            strategy_passed = (buy_signals >= 2 and avg_confidence > 0.3)
            
            # 计算优先级分数
            priority_score = 0
            if etf["code"] in hunting_priority:
                priority_score = hunting_priority.index(etf["code"]) + 1
            else:
                priority_score = len(hunting_priority) + 1
            
            # 计算综合分数 (基础分数 + 策略分数)
            bias_distance = abs(etf["bias"] - bias_threshold)
            base_score = bias_distance * 10
            strategy_score = buy_signals * 20 + avg_confidence * 100
            total_score = base_score + strategy_score - priority_score
            
            # 添加策略评估结果
            etf["priority_score"] = priority_score
            etf["base_score"] = base_score
            etf["strategy_score"] = strategy_score
            etf["total_score"] = total_score
            etf["strategy_evaluation"] = strategy_eval
            etf["strategy_passed"] = strategy_passed
            etf["buy_signals"] = buy_signals
            etf["avg_confidence"] = avg_confidence
            etf["final_signal"] = final_signal
            
            # 只有通过策略过滤的才加入候选
            if strategy_passed:
                filtered.append(etf)
            else:
                print(f"📭 {etf['code']} 未通过策略过滤: {buy_signals}买入信号, 置信度{avg_confidence:.2f}")
    
    # 按总分排序（分数越高越优先）
    filtered.sort(key=lambda x: x["total_score"], reverse=True)
    
    # 输出策略统计
    if filtered:
        print(f"🎯 策略过滤结果: {len(filtered)}/{len(scan_results)} 个标的通过")
        for i, target in enumerate(filtered[:3]):  # 只显示前3个
            print(f"  {i+1}. {target['code']}: {target['buy_signals']}个买入信号, 置信度{target['avg_confidence']:.2f}, 总分{target['total_score']:.1f}")
    
    return filtered

def check_position_limits(portfolio, etf_code, trade_amount, config):
    """检查持仓限制"""
    single_limit = config["account_config"]["single_etf_limit"]
    
    # 检查当前该ETF持仓
    current_position = 0
    for position in portfolio["current_positions"]:
        if position["code"] == etf_code:
            current_position = position["position_value"]
            break
    
    # 检查是否超过单ETF上限
    if current_position + trade_amount > single_limit:
        available = single_limit - current_position
        print(f"⚠️  {etf_code} 持仓将超过单ETF上限，可用额度: ¥{available:,.2f}")
        return min(trade_amount, available)
    
    return trade_amount

def execute_trade(portfolio, etf_info, trade_amount, config):
    """执行交易"""
    commission_rate = config["account_config"]["commission_rate"]
    tax_rate = config["account_config"]["tax_rate"]
    
    # 计算交易成本
    commission = trade_amount * commission_rate
    tax = trade_amount * tax_rate
    total_cost = trade_amount + commission + tax
    
    # 检查现金余额
    if portfolio["account_info"]["available_cash"] < total_cost:
        print(f"❌ 现金不足，需要: ¥{total_cost:,.2f}，可用: ¥{portfolio['account_info']['available_cash']:,.2f}")
        return False
    
    # 生成交易记录
    trade_id = f"TRADE_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{etf_info['code']}"
    
    trade_record = {
        "trade_id": trade_id,
        "timestamp": datetime.now().isoformat(),
        "code": etf_info["code"],
        "name": etf_info["name"],
        "action": "BUY",
        "price": etf_info["price"],
        "quantity": math.floor(trade_amount / etf_info["price"]),
        "amount": trade_amount,
        "commission": commission,
        "tax": tax,
        "total_cost": total_cost,
        "signal": {
            "bias": etf_info["bias"],
            "ma20_trend": etf_info["ma20_trend"],
            "signal_strength": etf_info["signal_strength"]
        },
        "strategy": {
            "strategy_passed": etf_info.get("strategy_passed", False),
            "buy_signals": etf_info.get("buy_signals", 0),
            "avg_confidence": etf_info.get("avg_confidence", 0),
            "final_signal": etf_info.get("final_signal", "HOLD"),
            "strategy_evaluation": etf_info.get("strategy_evaluation", {}),
            "primary_strategy": "引力超跌模型 (Gravity-Dip)" if etf_info.get("buy_signals", 0) > 0 else "未知"
        },
        "n_day_config": {
            "target_hold_days": 60,
            "min_hold_days_for_profit_taking": 30,
            "entry_date": datetime.now().isoformat()
        },
        "status": "EXECUTED"
    }
    
    # 更新投资组合
    portfolio["account_info"]["available_cash"] -= total_cost
    
    # 更新或添加持仓
    position_found = False
    for position in portfolio["current_positions"]:
        if position["code"] == etf_info["code"]:
            # 更新现有持仓
            avg_price = ((position["avg_price"] * position["quantity"] + etf_info["price"] * trade_record["quantity"]) / 
                        (position["quantity"] + trade_record["quantity"]))
            position["quantity"] += trade_record["quantity"]
            position["avg_price"] = avg_price
            position["position_value"] = position["quantity"] * etf_info["price"]
            position["last_updated"] = datetime.now().isoformat()
            position_found = True
            break
    
    if not position_found:
        # 添加新持仓 (集成策略信息)
        new_position = {
            "code": etf_info["code"],
            "name": etf_info["name"],
            "quantity": trade_record["quantity"],
            "avg_price": etf_info["price"],
            "current_price": etf_info["price"],
            "position_value": trade_record["quantity"] * etf_info["price"],
            "unrealized_pnl": 0.00,
            "unrealized_pnl_percent": 0.00,
            "entry_time": datetime.now().isoformat(),
            "entry_date": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat(),
            "strategy_used": trade_record["strategy"]["primary_strategy"],
            "strategy_id": 1,  # 默认引力超跌模型
            "n_day_countdown": 60,
            "strategy_evaluation": etf_info.get("strategy_evaluation", {})
        }
        portfolio["current_positions"].append(new_position)
    
    # 添加交易记录
    portfolio["trading_history"].append(trade_record)
    
    # 更新性能指标
    portfolio["performance_metrics"]["total_trades"] += 1
    
    # 更新账户总值
    portfolio["account_info"]["position_value"] = sum(p["position_value"] for p in portfolio["current_positions"])
    portfolio["account_info"]["total_value"] = (
        portfolio["account_info"]["available_cash"] + 
        portfolio["account_info"]["position_value"]
    )
    
    # 更新最后更新时间
    portfolio["account_info"]["last_updated"] = datetime.now().isoformat()
    
    return trade_record

def update_amber_cmd_with_trade(config, trade_record, portfolio):
    """更新amber_cmd.json交易信息"""
    try:
        # 更新投资组合摘要
        config["portfolio_summary"]["total_value"] = portfolio["account_info"]["total_value"]
        config["portfolio_summary"]["cash_balance"] = portfolio["account_info"]["available_cash"]
        config["portfolio_summary"]["position_count"] = len(portfolio["current_positions"])
        
        # 计算仓位百分比
        if portfolio["account_info"]["total_value"] > 0:
            position_percent = (portfolio["account_info"]["position_value"] / 
                              portfolio["account_info"]["total_value"] * 100)
            config["portfolio_summary"]["position_percent"] = f"{position_percent:.2f}%"
        
        # 更新摘要统计
        config["summary_stats"]["trades_today"] += 1
        
        # 更新自动化状态
        config["automation_status"]["live_trading"] = "ACTIVE"
        config["automation_status"]["last_trade"] = trade_record["timestamp"]
        
        # 保存更新
        cmd_path = "./amber-sentry-logs/amber_cmd.json"
        with open(cmd_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        
        print("✅ 更新amber_cmd.json交易信息")
        
    except Exception as e:
        print(f"⚠️ 更新amber_cmd.json失败: {e}")

def save_portfolio(portfolio):
    """保存投资组合"""
    portfolio_path = "./portfolio_v1.json"
    
    try:
        with open(portfolio_path, 'w', encoding='utf-8') as f:
            json.dump(portfolio, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"❌ 保存投资组合失败: {e}")
        return False

def generate_trading_signals():
    """生成交易信号（模拟）"""
    signals = []
    
    # 模拟信号生成
    signal_types = [
        ("518880", "华安黄金ETF", -4.1, "STRONG", "黄金避险情绪升温"),
        ("512480", "半导体ETF", -3.8, "MEDIUM", "半导体周期底部确认"),
        ("512660", "军工ETF", -3.2, "WEAK", "军工估值修复")
    ]
    
    for code, name, bias, strength, reason in signal_types:
        if bias < -3.5:
            signals.append({
                "code": code,
                "name": name,
                "bias": bias,
                "strength": strength,
                "reason": reason,
                "timestamp": datetime.now().isoformat()
            })
    
    return signals

def check_min_hold_days(position, min_days=30, current_date_str=None):
    """
    检查是否满足最低持有天数要求 (30天禁售锁)
    参数:
        position: 持仓记录
        min_days: 最低持有天数 (默认30天)
        current_date_str: 当前日期字符串 (可选，默认使用当前时间)
    返回:
        dict: 包含检查结果
    """
    try:
        if current_date_str is None:
            current_date = datetime.now()
        else:
            current_date = datetime.fromisoformat(current_date_str.replace('Z', '+00:00'))
        
        # 获取入场时间
        entry_time_str = position.get("entry_date") or position.get("entry_time")
        if not entry_time_str:
            return {
                "passed": False,
                "reason": "持仓缺少入场时间字段",
                "days_held": 0,
                "min_days": min_days
            }
        
        entry_date = datetime.fromisoformat(entry_time_str.replace('Z', '+00:00'))
        
        # 计算已持有天数
        days_held = (current_date - entry_date).days
        
        # 检查是否满足最低持有天数
        passed = days_held >= min_days
        
        return {
            "passed": passed,
            "reason": f"已持有{days_held}天，{'满足' if passed else '未满足'}{min_days}天最低要求",
            "days_held": days_held,
            "min_days": min_days,
            "entry_date": entry_date.isoformat(),
            "current_date": current_date.isoformat()
        }
    except Exception as e:
        return {
            "passed": False,
            "reason": f"检查异常: {str(e)}",
            "days_held": 0,
            "min_days": min_days
        }

def check_force_liquidation_conditions(portfolio, config, current_price_data):
    """
    检查强制清仓条件 (法典熔断)
    条件: 单日账户总值回撤 ≥ 1.5%
    返回:
        dict: 清仓检查结果
    """
    try:
        # 计算当前账户总值
        current_total = portfolio["account_info"]["total_value"]
        
        # 这里需要获取前一交易日的账户总值
        # 模拟实现: 假设昨日总值为初始资本
        initial_capital = portfolio["account_info"]["initial_capital"]
        
        # 计算回撤
        drawdown = (initial_capital - current_total) / initial_capital * 100
        
        # 检查是否触发熔断
        trigger_percent = 1.5  # 1.5%回撤触发熔断
        triggered = drawdown >= trigger_percent
        
        return {
            "triggered": triggered,
            "drawdown_percent": round(drawdown, 2),
            "trigger_threshold": trigger_percent,
            "current_total": current_total,
            "reason": f"单日回撤{drawdown:.2f}% {'≥' if triggered else '<'} {trigger_percent}%熔断线"
        }
    except Exception as e:
        return {
            "triggered": False,
            "drawdown_percent": 0,
            "trigger_threshold": 1.5,
            "reason": f"熔断检查异常: {str(e)}"
        }

def evaluate_sell_signals(portfolio, current_market_data):
    """
    评估卖出信号 (集成10大策略)
    注意: 受30天禁售锁限制，除非触发熔断
    返回:
        list: 卖出建议列表
    """
    sell_recommendations = []
    
    for position in portfolio.get("current_positions", []):
        code = position["code"]
        
        # 检查30天禁售锁
        hold_check = check_min_hold_days(position, min_days=30)
        
        # 模拟市场数据 (实际应从current_market_data获取)
        mock_market_data = {
            "code": code,
            "price": position.get("current_price", position["avg_price"] * 1.05),  # 假设上涨5%
            "ma200": position["avg_price"] * 1.15,
            "atr14": position["avg_price"] * 0.03
        }
        
        # 评估策略信号 (使用策略库)
        strategy_eval = evaluate_strategy_signals(mock_market_data)
        
        # 检查是否触发卖出信号
        if strategy_eval.get("final_signal") == "SELL":
            sell_recommendations.append({
                "code": code,
                "name": position["name"],
                "quantity": position["quantity"],
                "current_price": mock_market_data["price"],
                "position_value": position["position_value"],
                "strategy_signal": "SELL",
                "strategy_confidence": strategy_eval.get("avg_confidence", 0),
                "buy_signals": strategy_eval.get("buy_signals", 0),
                "sell_signals": strategy_eval.get("sell_signals", 0),
                "hold_check": hold_check,
                "can_sell": hold_check["passed"],  # 只有满足30天才能卖出
                "reason": f"策略信号: {strategy_eval.get('final_signal')}, {hold_check['reason']}"
            })
    
    return sell_recommendations

def main_trading_cycle():
    """主交易循环"""
    print("🧀 琥珀引擎 - 50万量化实验室实战算法")
    print("=" * 60)
    print(f"⏰ 执行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 加载配置
    config, portfolio = load_config()
    if not config or not portfolio:
        return False
    
    print("✅ 加载配置和投资组合")
    print(f"💰 账户总值: ¥{portfolio['account_info']['total_value']:,.2f}")
    print(f"💵 可用现金: ¥{portfolio['account_info']['available_cash']:,.2f}")
    print(f"📊 持仓数量: {len(portfolio['current_positions'])}")
    
    # 扫描127号报告
    print("🔍 扫描127号报告...")
    scan_results = scan_127_report()
    
    # 筛选猎杀目标
    print("🎯 筛选猎杀目标...")
    hunting_targets = filter_hunting_targets(scan_results, config)
    
    # 评估卖出信号 (30天禁售锁检查)
    print("🔍 评估卖出信号...")
    sell_recommendations = evaluate_sell_signals(portfolio, scan_results)
    
    if sell_recommendations:
        print(f"📉 发现 {len(sell_recommendations)} 个卖出信号:")
        for rec in sell_recommendations:
            if rec["can_sell"]:
                print(f"   ✅ {rec['code']} {rec['name']}: 可卖出 ({rec['reason']})")
            else:
                print(f"   ⏳ {rec['code']} {rec['name']}: 持有中 ({rec['hold_check']['reason']})")
    
    # 检查强制熔断条件
    liquidation_check = check_force_liquidation_conditions(portfolio, config, scan_results)
    if liquidation_check["triggered"]:
        print(f"🚨 法典熔断触发! {liquidation_check['reason']}")
        print("   ⚠️ 强制清仓逻辑待实现 (架构师特别指令)")
    
    if not hunting_targets:
        print("📭 未找到符合猎杀条件的标的")
        
        # 生成交易信号（即使不交易也显示）
        signals = generate_trading_signals()
        if signals:
            print("\n📡 监控信号:")
            for signal in signals:
                print(f"   [{signal['strength']}] {signal['code']} {signal['name']}: Bias={signal['bias']}% - {signal['reason']}")
        
        return True
    
    print(f"🎯 找到 {len(hunting_targets)} 个猎杀目标:")
    for i, target in enumerate(hunting_targets[:3]):  # 只显示前3个
        print(f"  {i+1}. {target['code']} {target['name']}: Bias={target['bias']}%, MA20趋势={target['ma20_trend']}")
    
    # 执行交易（只交易最高优先级目标）
    primary_target = hunting_targets[0]
    batch_size = config["trading_rules"]["batch_size"]
    
    print(f"\n🎯 准备猎杀: {primary_target['code']} {primary_target['name']}")
    print(f"   Bias: {primary_target['bias']}% (阈值: <{config['trading_rules']['bias_threshold']}%)")
    print(f"   MA20趋势: {primary_target['ma20_trend']}")
    print(f"   价格: ¥{primary_target['price']:.2f}")
    print(f"   批次大小: ¥{batch_size:,.2f}")
    
    # 检查持仓限制
    adjusted_amount = check_position_limits(portfolio, primary_target["code"], batch_size, config)
    
    if adjusted_amount <= 0:
        print("❌ 交易额度不足或超过限制")
        return True
    
    # 确认执行
    print(f"\n⚠️ 确认执行交易:")
    print(f"   标的: {primary_target['code']} {primary_target['name']}")
    print(f"   方向: 买入")
    print(f"   金额: ¥{adjusted_amount:,.2f}")
    print(f"   价格: ¥{primary_target['price']:.2f}")
    print(f"   数量: {math.floor(adjusted_amount / primary_target['price']):,} 股")
    
    # 模拟用户确认（实际应为自动执行）
    print("\n⏳ 模拟交易执行中...")
    time.sleep(2)
    
    # 执行交易
    trade_record = execute_trade(portfolio, primary_target, adjusted_amount, config)
    
    if trade_record:
        print(f"\n✅ 交易执行成功!")
        print(f"   交易ID: {trade_record['trade_id']}")
        print(f"   标的: {trade_record['code']} {trade_record['name']}")
        print(f"   数量: {trade_record['quantity']:,} 股")
        print(f"   金额: ¥{trade_record['amount']:,.2f}")
        print(f"   佣金: ¥{trade_record['commission']:,.2f}")
        print(f"   税费: ¥{trade_record['tax']:,.2f}")
        print(f"   总成本: ¥{trade_record['total_cost']:,.2f}")
        print(f"   信号: Bias={trade_record['signal']['bias']}%, MA20趋势={trade_record['signal']['ma20_trend']}")
        
        # 更新配置
        update_amber_cmd_with_trade(config, trade_record, portfolio)
        
        # 保存投资组合
        if save_portfolio(portfolio):
            print("✅ 投资组合已保存")
            
            # 显示更新后状态
            print(f"\n📊 更新后账户状态:")
            print(f"   账户总值: ¥{portfolio['account_info']['total_value']:,.2f}")
            print(f"   可用现金: ¥{portfolio['account_info']['available_cash']:,.2f}")
            print(f"   持仓市值: ¥{portfolio['account_info']['position_value']:,.2f}")
            print(f"   持仓数量: {len(portfolio['current_positions'])}")
            
            # 生成交易信号显示
            signals = generate_trading_signals()
            if signals:
                print(f"\n📡 活跃交易信号:")
                for signal in signals:
                    if signal['code'] == primary_target['code']:
                        print(f"   🎯 [ACTIVE] {signal['code']} {signal['name']}: 已建仓，Bias={signal['bias']}%")
                    else:
                        print(f"   📡 [{signal['strength']}] {signal['code']} {signal['name']}: Bias={signal['bias']}%")
        
        return True
    else:
        print("❌ 交易执行失败")
        return False

def run_as_service(interval_minutes=15):
    """以服务模式运行"""
    print("🚀 启动50万量化实验室实战服务")
    print(f"📅 执行间隔: {interval_minutes}分钟")
    print("🛑 按 Ctrl+C 停止服务")
    print("=" * 60)
    
    cycle_count = 0
    
    try:
        while True:
            cycle_count += 1
            print(f"\n🔔 第 {cycle_count} 次交易扫描")
            
            success = main_trading_cycle()
            
            if success:
                # 计算下次执行时间
                next_time = datetime.now() + timedelta(minutes=interval_minutes)
                print(f"\n⏳ 下次扫描: {next_time.strftime('%Y-%m-%d %H:%M:%S')}")
                
                # 等待到下次执行时间
                wait_seconds = interval_minutes * 60
                print(f"💤 等待 {interval_minutes} 分钟...")
                time.sleep(wait_seconds)
            else:
                # 失败时等待1分钟重试
                print("🔄 等待1分钟后重试...")
                time.sleep(60)
                
    except KeyboardInterrupt:
        print("\n👋 50万量化实验室实战服务已停止")
        return 0

def main():
    """主函数"""
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--service":
        # 服务模式
        interval = 15  # 默认15分钟
        if len(sys.argv) > 2:
            try:
                interval = int(sys.argv[2])
            except:
                pass
        return run_as_service(interval)
    else:
        # 单次执行模式
        return 0 if main_trading_cycle() else 1

if __name__ == "__main__":
    import sys
    sys.exit(main())