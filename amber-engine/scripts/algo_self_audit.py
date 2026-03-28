#!/usr/bin/env python3
"""
琥珀引擎 - 算法自省脚本 (algo_self_audit.py)
功能: 每周五收盘后自动生成算法性能报告，包含10大策略机会扫描快照
版本: V1.0.0 (2615-175号指令集成)
创建时间: 2026-03-27 22:00
"""

import json
import os
import sys
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

# 添加路径以便导入策略库
sys.path.append('/home/luckyelite/.openclaw/workspace/amber-engine/scripts')
from strategy_lib import strategy_lib

def load_algo_log():
    """加载ALGO_LOG.json进化账本"""
    log_path = "/home/luckyelite/.openclaw/workspace/amber-engine/data/algo_log/ALGO_LOG.json"
    
    try:
        with open(log_path, 'r', encoding='utf-8') as f:
            algo_log = json.load(f)
        return algo_log
    except Exception as e:
        print(f"❌ 加载ALGO_LOG.json失败: {e}")
        # 创建默认结构
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
    portfolio_path = "/home/luckyelite/.openclaw/workspace/amber-engine/portfolio_v1.json"
    
    try:
        with open(portfolio_path, 'r', encoding='utf-8') as f:
            portfolio = json.load(f)
        return portfolio
    except Exception as e:
        print(f"❌ 加载投资组合失败: {e}")
        return None

def scan_market_opportunities():
    """
    扫描市场机会 (10大策略在当前市场下的机会扫描快照)
    返回所有ETF的10大策略评估结果
    """
    print("🔍 执行10大策略市场机会扫描...")
    
    # 模拟ETF列表 (实际应从数据源获取)
    etf_list = [
        {"code": "518880", "name": "华安黄金ETF", "price": 4.8156},
        {"code": "512480", "name": "半导体ETF", "price": 1.22},
        {"code": "512660", "name": "军工ETF", "price": 1.08},
        {"code": "512170", "name": "医疗ETF", "price": 0.83},
        {"code": "512800", "name": "银行ETF", "price": 1.03},
        {"code": "510300", "name": "沪深300ETF", "price": 3.85},
        {"code": "159919", "name": "沪深300ETF(深)", "price": 3.82},
        {"code": "510500", "name": "中证500ETF", "price": 5.67},
        {"code": "512000", "name": "券商ETF", "price": 0.95},
        {"code": "512010", "name": "医药ETF", "price": 2.34}
    ]
    
    opportunities = []
    lib = strategy_lib()
    
    for etf in etf_list:
        # 为每个ETF创建模拟数据
        symbol_data = {
            "symbol": etf["code"],
            "gravity_dip": {
                "current_price": etf["price"],
                "ma_200": etf["price"] * random.uniform(0.95, 1.15),  # 模拟MA200
                "atr_14": etf["price"] * random.uniform(0.02, 0.06)   # 模拟ATR14
            },
            "dual_momentum": {
                "current_price": etf["price"],
                "ma_200": etf["price"] * random.uniform(0.95, 1.15),
                "price_90d_ago": etf["price"] * random.uniform(0.85, 1.05)
            },
            "volatility_squeeze": {
                "upper_bb": etf["price"] * 1.05,
                "lower_bb": etf["price"] * 0.95,
                "ma_20": etf["price"]
            },
            "weekly_rsi": {
                "rsi_weekly": random.uniform(30, 70)
            },
            "z_score": {
                "current_price": etf["price"],
                "ma_60": etf["price"] * random.uniform(0.98, 1.05),
                "std_60": etf["price"] * 0.03
            },
            "triple_cross": {
                "ma_5": etf["price"] * random.uniform(0.99, 1.03),
                "ma_20": etf["price"] * random.uniform(0.98, 1.02),
                "ma_60": etf["price"] * random.uniform(0.97, 1.01)
            }
        }
        
        # 评估策略
        try:
            evaluation = lib.evaluate_all_strategies(symbol_data)
            
            opportunity = {
                "symbol": etf["code"],
                "name": etf["name"],
                "price": etf["price"],
                "buy_signals": evaluation.get("buy_signals", 0),
                "sell_signals": evaluation.get("sell_signals", 0),
                "avg_confidence": round(evaluation.get("avg_confidence", 0), 4),
                "final_signal": evaluation.get("final_signal", "HOLD"),
                "evaluation_time": datetime.now().isoformat()
            }
            
            # 只记录有买入信号的标的
            if opportunity["buy_signals"] >= 2 and opportunity["avg_confidence"] > 0.3:
                opportunities.append(opportunity)
                print(f"  ✅ {etf['code']} {etf['name']}: {opportunity['buy_signals']}个买入信号, 置信度{opportunity['avg_confidence']:.2f}")
            elif opportunity["buy_signals"] > 0:
                print(f"  📊 {etf['code']} {etf['name']}: {opportunity['buy_signals']}个买入信号, 置信度{opportunity['avg_confidence']:.2f} (未达阈值)")
        
        except Exception as e:
            print(f"  ⚠️ {etf['code']} 策略评估失败: {e}")
    
    print(f"📊 机会扫描完成: 发现 {len(opportunities)} 个符合策略标准的标的")
    return opportunities

def analyze_strategy_performance(algo_log):
    """分析策略性能 (基于历史交易数据)"""
    print("📈 分析策略性能...")
    
    transactions = algo_log.get("transactions", [])
    
    if not transactions:
        print("  📭 暂无交易历史")
        return {
            "total_transactions": 0,
            "win_rate": 0,
            "avg_return": 0,
            "strategy_effectiveness": {}
        }
    
    # 计算总体胜率
    winning_trades = [t for t in transactions if t.get("final_return", 0) > 0]
    total_trades = len(transactions)
    win_rate = len(winning_trades) / total_trades if total_trades > 0 else 0
    
    # 计算平均收益率
    returns = [t.get("final_return", 0) for t in transactions]
    avg_return = np.mean(returns) if returns else 0
    
    # 按策略分析性能
    strategy_stats = {}
    for transaction in transactions:
        strategy = transaction.get("primary_strategy", "未知")
        if strategy not in strategy_stats:
            strategy_stats[strategy] = {"trades": 0, "wins": 0, "returns": []}
        
        strategy_stats[strategy]["trades"] += 1
        if transaction.get("final_return", 0) > 0:
            strategy_stats[strategy]["wins"] += 1
        strategy_stats[strategy]["returns"].append(transaction.get("final_return", 0))
    
    # 计算每个策略的胜率和平均收益
    strategy_effectiveness = {}
    for strategy, stats in strategy_stats.items():
        strategy_win_rate = stats["wins"] / stats["trades"] if stats["trades"] > 0 else 0
        strategy_avg_return = np.mean(stats["returns"]) if stats["returns"] else 0
        
        strategy_effectiveness[strategy] = {
            "trades": stats["trades"],
            "win_rate": round(strategy_win_rate, 4),
            "avg_return": round(strategy_avg_return, 4),
            "total_return": round(sum(stats["returns"]), 4)
        }
    
    print(f"  📊 总交易数: {total_trades}")
    print(f"  🎯 总体胜率: {win_rate:.2%}")
    print(f"  📈 平均收益率: {avg_return:.4f}")
    
    return {
        "total_transactions": total_trades,
        "win_rate": round(win_rate, 4),
        "avg_return": round(avg_return, 4),
        "strategy_effectiveness": strategy_effectiveness
    }

def check_n_day_progress(portfolio):
    """检查N天持有期进度"""
    print("⏳ 检查N天持有期进度...")
    
    if not portfolio or "current_positions" not in portfolio:
        print("  📭 无持仓数据")
        return []
    
    positions_progress = []
    lib = strategy_lib()
    
    for position in portfolio["current_positions"]:
        entry_date = position.get("entry_date") or position.get("entry_time")
        if not entry_date:
            continue
        
        # 计算持有进度
        try:
            entry = datetime.fromisoformat(entry_date.replace('Z', '+00:00'))
            current = datetime.now()
            days_held = (current - entry).days
            
            n_days = position.get("n_day_countdown", 60)
            progress = min(days_held / n_days, 1.0)
            
            position_progress = {
                "symbol": position["code"],
                "name": position["name"],
                "entry_date": entry_date,
                "days_held": days_held,
                "n_days": n_days,
                "progress": round(progress, 4),
                "days_remaining": max(n_days - days_held, 0),
                "hold_stage": "早期" if progress < 0.33 else "中期" if progress < 0.66 else "晚期"
            }
            
            positions_progress.append(position_progress)
            
            print(f"  📊 {position['code']} {position['name']}: 持有{days_held}天 (目标{n_days}天), 进度{progress:.1%}")
        
        except Exception as e:
            print(f"  ⚠️ {position['code']} 进度计算失败: {e}")
    
    return positions_progress

def generate_audit_report(algo_log, portfolio, opportunities, strategy_performance, positions_progress):
    """生成算法自省报告"""
    print("📋 生成算法自省报告...")
    
    report = {
        "report_id": f"AUDIT_{datetime.now().strftime('%Y%m%d_%H%M')}",
        "generated_at": datetime.now().isoformat(),
        "report_type": "算法自省周报",
        "period": "本周 (2026-03-21 至 2026-03-27)",
        
        "executive_summary": {
            "total_opportunities": len(opportunities),
            "total_positions": len(portfolio["current_positions"]) if portfolio else 0,
            "overall_win_rate": strategy_performance["win_rate"],
            "n_day_compliance": "100%" if all(p["days_held"] >= 30 for p in positions_progress) else "待改进"
        },
        
        "market_opportunities": opportunities,
        
        "strategy_performance": strategy_performance,
        
        "portfolio_progress": positions_progress,
        
        "algorithm_evolution": {
            "current_version": "V2.0.0 (长周期量化策略库)",
            "n_day_target": 60,
            "win_rate_target": 0.78,
            "key_improvements": [
                "集成10大长周期量化公式",
                "实施30天禁售锁 (法典熔断例外)",
                "建立ALGO_LOG.json进化账本",
                "10169端口策略标签可视化"
            ],
            "next_evolution_targets": [
                "提高N=60天胜率至78%以上",
                "优化引力超跌模型参数",
                "扩展宏观对冲锚点数据源",
                "建立多周期策略共振系统"
            ]
        },
        
        "recommendations": []
    }
    
    # 生成建议
    if len(opportunities) > 5:
        report["recommendations"].append("📈 市场机会丰富，建议增加仓位配置")
    
    if strategy_performance["win_rate"] < 0.65:
        report["recommendations"].append("⚠️ 总体胜率低于65%目标，建议策略参数优化")
    
    for position in positions_progress:
        if position["progress"] < 0.5 and position["days_held"] < 30:
            report["recommendations"].append(f"⏳ {position['symbol']} 处于持有早期，保持耐心")
    
    if len(report["recommendations"]) == 0:
        report["recommendations"].append("✅ 系统运行正常，继续保持当前策略")
    
    return report

def save_report(report):
    """保存报告文件"""
    reports_dir = "/home/luckyelite/.openclaw/workspace/amber-engine/reports/algo_audit"
    os.makedirs(reports_dir, exist_ok=True)
    
    filename = f"algo_audit_{datetime.now().strftime('%Y%m%d_%H%M')}.json"
    filepath = os.path.join(reports_dir, filename)
    
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        print(f"✅ 算法自省报告已保存: {filepath}")
        
        # 同时保存HTML格式便于查看
        html_filepath = filepath.replace('.json', '.html')
        save_html_report(report, html_filepath)
        
        return filepath
    except Exception as e:
        print(f"❌ 保存报告失败: {e}")
        return None

def save_html_report(report, filepath):
    """保存HTML格式报告"""
    try:
        html_content = f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🧀 琥珀引擎算法自省报告 - {report['report_id']}</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.6; margin: 0; padding: 20px; background: #f8f9fa; }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        .header {{ background: linear-gradient(135deg, #1a2980, #26d0ce); color: white; padding: 30px; border-radius: 12px; margin-bottom: 30px; text-align: center; }}
        .card {{ background: white; padding: 25px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); margin-bottom: 20px; }}
        .section-title {{ color: #1a2980; border-bottom: 2px solid #26d0ce; padding-bottom: 10px; margin-bottom: 20px; }}
        .opportunity-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 15px; }}
        .opportunity-card {{ background: #f8f9fa; padding: 15px; border-radius: 6px; border-left: 4px solid #28a745; }}
        .strategy-badge {{ background: linear-gradient(135deg, #667eea, #764ba2); color: white; padding: 3px 10px; border-radius: 12px; font-size: 12px; display: inline-block; margin-right: 5px; }}
        .progress-bar {{ height: 12px; background: #e9ecef; border-radius: 6px; overflow: hidden; margin: 10px 0; }}
        .progress-fill {{ height: 100%; background: linear-gradient(90deg, #28a745, #20c997); border-radius: 6px; }}
        .recommendation {{ background: #fff3cd; border-left: 4px solid #ffc107; padding: 15px; margin: 10px 0; border-radius: 4px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🧀 琥珀引擎算法自省报告</h1>
            <p>{report['report_id']} · 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
        
        <div class="card">
            <h2 class="section-title">📊 执行摘要</h2>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px;">
                <div style="text-align: center;">
                    <div style="font-size: 24px; font-weight: bold; color: #1a2980;">{report['executive_summary']['total_opportunities']}</div>
                    <div>市场机会数量</div>
                </div>
                <div style="text-align: center;">
                    <div style="font-size: 24px; font-weight: bold; color: #28a745;">{report['executive_summary']['overall_win_rate']*100:.1f}%</div>
                    <div>总体胜率</div>
                </div>
                <div style="text-align: center;">
                    <div style="font-size: 24px; font-weight: bold; color: #26d0ce;">{report['executive_summary']['total_positions']}</div>
                    <div>当前持仓数</div>
                </div>
                <div style="text-align: center;">
                    <div style="font-size: 24px; font-weight: bold; color: #ffc107;">{report['executive_summary']['n_day_compliance']}</div>
                    <div>N天合规率</div>
                </div>
            </div>
        </div>
        
        <div class="card">
            <h2 class="section-title">🔍 市场机会扫描 (10大策略快照)</h2>
            <div class="opportunity-grid">
        """
        
        # 添加机会卡片
        for opp in report['market_opportunities'][:10]:  # 最多显示10个
            confidence_color = "#28a745" if opp['avg_confidence'] > 0.5 else "#ffc107" if opp['avg_confidence'] > 0.3 else "#dc3545"
            html_content += f"""
                <div class="opportunity-card">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <div style="font-weight: bold;">{opp['symbol']} {opp['name']}</div>
                            <div style="font-size: 14px; color: #6c757d;">价格: ¥{opp['price']:.4f}</div>
                        </div>
                        <div>
                            <span class="strategy-badge">{opp['buy_signals']}个买入信号</span>
                        </div>
                    </div>
                    <div style="margin-top: 10px;">
                        <div style="display: flex; justify-content: space-between; font-size: 14px;">
                            <span>置信度</span>
                            <span style="color: {confidence_color}; font-weight: bold;">{opp['avg_confidence']:.2%}</span>
                        </div>
                        <div class="progress-bar">
                            <div class="progress-fill" style="width: {opp['avg_confidence']*100}%;"></div>
                        </div>
                    </div>
                    <div style="font-size: 13px; margin-top: 10px; color: #6c757d;">
                        最终信号: <strong style="color: {'#28a745' if opp['final_signal'] == 'BUY' else '#dc3545' if opp['final_signal'] == 'SELL' else '#6c757d'}">{opp['final_signal']}</strong>
                    </div>
                </div>
            """
        
        html_content += """
            </div>
        </div>
        
        <div class="card">
            <h2 class="section-title">📈 策略性能分析</h2>
            <div style="overflow-x: auto;">
                <table style="width: 100%; border-collapse: collapse;">
                    <thead>
                        <tr style="background: #f1f3f5;">
                            <th style="padding: 12px; text-align: left; border-bottom: 2px solid #ddd;">策略名称</th>
                            <th style="padding: 12px; text-align: right; border-bottom: 2px solid #ddd;">交易次数</th>
                            <th style="padding: 12px; text-align: right; border-bottom: 2px solid #ddd;">胜率</th>
                            <th style="padding: 12px; text-align: right; border-bottom: 2px solid #ddd;">平均收益</th>
                        </tr>
                    </thead>
                    <tbody>
        """
        
        # 添加策略性能表格
        for strategy, stats in report['strategy_performance']['strategy_effectiveness'].items():
            win_rate_color = "#28a745" if stats['win_rate'] > 0.65 else "#ffc107" if stats['win_rate'] > 0.5 else "#dc3545"
            html_content += f"""
                        <tr>
                            <td style="padding: 12px; border-bottom: 1px solid #eee;">{strategy}</td>
                            <td style="padding: 12px; text-align: right; border-bottom: 1px solid #eee;">{stats['trades']}</td>
                            <td style="padding: 12px; text-align: right; border-bottom: 1px solid #eee;">
                                <span style="color: {win_rate_color};">{stats['win_rate']:.2%}</span>
                            </td>
                            <td style="padding: 12px; text-align: right; border-bottom: 1px solid #eee;">{stats['avg_return']:.4f}</td>
                        </tr>
            """
        
        html_content += f"""
                    </tbody>
                </table>
            </div>
            <div style="margin-top: 20px; padding: 15px; background: #f8f9fa; border-radius: 6px;">
                <div style="display: flex; justify-content: space-between;">
                    <div>
                        <div style="font-size: 14px; color: #6c757d;">总体交易次数</div>
                        <div style="font-size: 20px; font-weight: bold;">{report['strategy_performance']['total_transactions']}</div>
                    </div>
                    <div>
                        <div style="font-size: 14px; color: #6c757d;">总体胜率</div>
                        <div style="font-size: 20px; font-weight: bold; color: #28a745;">{report['strategy_performance']['win_rate']:.2%}</div>
                    </div>
                    <div>
                        <div style="font-size: 14px; color: #6c757d;">平均收益率</div>
                        <div style="font-size: 20px; font-weight: bold; color: #26d0ce;">{report['strategy_performance']['avg_return']:.4f}</div>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="card">
            <h2 class="section-title">🎯 算法进化建议</h2>
        """
        
        # 添加建议
        for rec in report['recommendations']:
            html_content += f"""
            <div class="recommendation">
                {rec}
            </div>
            """
        
        html_content += f"""
            <div style="margin-top: 20px; padding: 15px; background: #e7f5ff; border-radius: 6px; border-left: 4px solid #1a2980;">
                <div style="font-weight: bold; color: #1a2980; margin-bottom: 10px;">🚀 算法进化目标</div>
                <ul style="margin: 0; padding-left: 20px;">
                    <li>提高N=60天胜率至78%以上</li>
                    <li>优化引力超跌模型参数</li>
                    <li>扩展宏观对冲锚点数据源</li>
                    <li>建立多周期策略共振系统</li>
                </ul>
            </div>
        </div>
        
        <div style="text-align: center; margin-top: 30px; padding: 20px; color: #6c757d; font-size: 14px;">
            琥珀引擎算法自省系统 · 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} · 报告ID: {report['report_id']}
        </div>
    </div>
</body>
</html>
        """
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html_content)
        print(f"✅ HTML格式报告已保存: {filepath}")
        
    except Exception as e:
        print(f"⚠️ 保存HTML报告失败: {e}")

def main():
    """主函数"""
    print("🧀 琥珀引擎算法自省脚本启动")
    print("=" * 60)
    print(f"⏰ 执行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 加载数据
    algo_log = load_algo_log()
    portfolio = load_portfolio()
    
    # 执行分析
    opportunities = scan_market_opportunities()
    strategy_performance = analyze_strategy_performance(algo_log)
    positions_progress = check_n_day_progress(portfolio)
    
    # 生成报告
    report = generate_audit_report(algo_log, portfolio, opportunities, strategy_performance, positions_progress)
    
    # 保存报告
    report_path = save_report(report)
    
    if report_path:
        print(f"\n✅ 算法自省完成!")
        print(f"📁 报告位置: {report_path}")
        print(f"📊 市场机会: {len(opportunities)} 个符合策略标的")
        print(f"🎯 总体胜率: {strategy_performance['win_rate']:.2%}")
        print(f"⏳ 持仓进度: {len(positions_progress)} 个持仓跟踪中")
        
        # 输出关键建议
        print(f"\n🎯 关键建议:")
        for rec in report['recommendations'][:3]:  # 只显示前3个
            print(f"   • {rec}")
        
        return 0
    else:
        print("❌ 算法自省失败")
        return 1

def setup_cron_job():
    """设置定时任务 (每周五收盘后执行)"""
    cron_command = f"5 17 * * 5 cd /home/luckyelite/.openclaw/workspace/amber-engine/scripts && python3 algo_self_audit.py >> /home/luckyelite/.openclaw/workspace/amber-engine/logs/algo_audit.log 2>&1"
    
    print(f"⏰ 建议Cron定时任务:")
    print(f"   {cron_command}")
    print("\n💡 说明: 每周五17:05执行 (收盘后5分钟)")
    print("   请手动添加至crontab: crontab -e")
    
    return cron_command

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--setup-cron":
        setup_cron_job()
    else:
        sys.exit(main())