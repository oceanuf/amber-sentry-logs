#!/usr/bin/env python3
"""
琥珀引擎 - 50万实战盈亏结项报告生成脚本
功能: 自动生成当天的《50万实战盈亏结项报告.md》
执行时间: 每晚20:00
"""

import json
import os
import sys
from datetime import datetime, timedelta
import time

def load_amber_cmd():
    """加载amber_cmd.json"""
    cmd_path = "./amber-sentry-logs/amber_cmd.json"
    
    try:
        with open(cmd_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ 加载amber_cmd.json失败: {e}")
        return None

def load_portfolio():
    """加载portfolio_v1.json"""
    portfolio_path = "./portfolio_v1.json"
    
    try:
        with open(portfolio_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ 加载portfolio_v1.json失败: {e}")
        return None

def generate_daily_report(config, portfolio):
    """生成每日报告"""
    if not config or not portfolio:
        return None
    
    today = datetime.now().strftime("%Y-%m-%d")
    report_date = datetime.now().strftime("%Y年%m月%d日")
    
    # 计算当日盈亏
    initial_capital = portfolio["account_info"]["initial_capital"]
    total_value = portfolio["account_info"]["total_value"]
    pnl_amount = total_value - initial_capital
    pnl_percent = (pnl_amount / initial_capital) * 100 if initial_capital > 0 else 0
    
    # 计算交易统计
    total_trades = portfolio["performance_metrics"]["total_trades"]
    winning_trades = portfolio["performance_metrics"]["winning_trades"]
    losing_trades = portfolio["performance_metrics"]["losing_trades"]
    
    if total_trades > 0:
        win_rate = (winning_trades / total_trades) * 100
    else:
        win_rate = 0
    
    # 生成报告内容
    report_content = f"""# 📊 50万实战盈亏结项报告 - {report_date}

## 🎯 报告概况

- **报告日期**: {report_date}
- **生成时间**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
- **报告编号**: DAILY_REPORT_{today.replace('-', '')}
- **系统版本**: {config['system_config']['version']}

## 💰 资金概况

| 项目 | 金额 | 说明 |
|------|------|------|
| **初始本金** | ¥{initial_capital:,.2f} | 50万量化实验室启动资金 |
| **当前总值** | ¥{total_value:,.2f} | 现金 + 持仓市值 |
| **当日盈亏** | ¥{pnl_amount:+,.2f} ({pnl_percent:+.2f}%) | 相对于初始本金 |
| **可用现金** | ¥{portfolio['account_info']['available_cash']:,.2f} | 可继续投资的现金 |
| **持仓市值** | ¥{portfolio['account_info']['position_value']:,.2f} | 当前持仓总价值 |
| **仓位占比** | {config['portfolio_summary']['position_percent']} | 持仓占总资产比例 |

## 📈 交易统计

| 指标 | 数值 | 说明 |
|------|------|------|
| **总交易笔数** | {total_trades} 笔 | 当日所有交易 |
| **盈利交易** | {winning_trades} 笔 | 卖出价 > 买入价的交易 |
| **亏损交易** | {losing_trades} 笔 | 卖出价 < 买入价的交易 |
| **胜率** | {win_rate:.1f}% | 盈利交易占比 |
| **累计佣金** | ¥{portfolio['performance_metrics'].get('total_commission', 0):,.2f} | 万分之二佣金 |
| **累计税费** | ¥{portfolio['performance_metrics'].get('total_tax', 0):,.2f} | 千分之一印花税 |

## 🎯 持仓明细

### 当前持仓 ({len(portfolio['current_positions'])} 支)

"""
    
    # 添加持仓明细
    for i, position in enumerate(portfolio["current_positions"], 1):
        unrealized_pnl = position.get("unrealized_pnl", 0)
        unrealized_pnl_percent = position.get("unrealized_pnl_percent", 0)
        
        report_content += f"""#### {i}. {position['code']} {position['name']}

- **持仓数量**: {position['quantity']:,} 股
- **平均成本**: ¥{position['avg_price']:.2f}
- **当前价格**: ¥{position['current_price']:.2f}
- **持仓市值**: ¥{position['position_value']:,.2f}
- **浮动盈亏**: ¥{unrealized_pnl:+,.2f} ({unrealized_pnl_percent:+.2f}%)
- **建仓时间**: {position['entry_time']}
- **最后更新**: {position['last_updated']}

"""
    
    # 添加交易记录
    report_content += f"""## 📝 交易记录

### 今日交易 ({len(portfolio['trading_history'])} 笔)

"""
    
    for i, trade in enumerate(portfolio["trading_history"], 1):
        if trade["timestamp"].startswith(today):
            report_content += f"""#### {i}. {trade['trade_id']}

- **标的**: {trade['code']} {trade['name']}
- **方向**: {trade['action']}
- **价格**: ¥{trade['price']:.2f}
- **数量**: {trade['quantity']:,} 股
- **金额**: ¥{trade['amount']:,.2f}
- **佣金**: ¥{trade['commission']:.2f}
- **税费**: ¥{trade['tax']:.2f}
- **总成本**: ¥{trade['total_cost']:,.2f}
- **时间**: {trade['timestamp']}
- **信号**: Bias={trade['signal']['bias']}%, MA20趋势={trade['signal']['ma20_trend']}

"""
    
    # 添加策略分析
    report_content += f"""## 🧠 策略分析

### 星辰引力系统表现

- **猎杀条件**: Bias < {config['trading_rules']['bias_threshold']}% 且 MA20趋势向上
- **优先猎杀**: {', '.join(config['trading_rules']['hunting_priority'])}
- **建仓策略**: 分批次建仓，每笔¥{config['trading_rules']['batch_size']:,.2f}
- **仓位限制**: 单ETF最大持仓¥{config['account_config']['single_etf_limit']:,.2f} (20%仓位)
- **执行频率**: 每15分钟扫描一次

### 市场机会分析

- **Top Alpha标的**: {', '.join(config['market_snapshot']['top_alpha'])}
- **平均偏离度**: {config['market_snapshot']['avg_bias']}
- **机会数量**: {config['market_snapshot']['opportunity_count']} 支 (Bias < -3.5%)
- **数据质量**: {config['summary_stats']['data_quality']}%
- **系统运行**: {config['summary_stats']['system_uptime']}

## 📊 绩效指标

| 指标 | 数值 | 评价标准 |
|------|------|----------|
| **夏普比率** | {portfolio['performance_metrics']['sharpe_ratio']:.2f} | >1.0为优秀 |
| **最大回撤** | {portfolio['performance_metrics']['max_drawdown']:.2f}% | <5%为优秀 |
| **总收益率** | {pnl_percent:+.2f}% | 当日表现 |
| **年化收益率** | {(pnl_percent * 252):+.2f}% | 按252个交易日估算 |
| **盈亏比** | {portfolio['performance_metrics'].get('profit_loss_ratio', 0):.2f} | >2.0为优秀 |

## 🔮 明日展望

基于今日表现和市场情况，明日策略建议：

1. **继续持有**: {', '.join([p['code'] for p in portfolio['current_positions']])} - 当前信号依然有效
2. **关注标的**: {', '.join(config['market_snapshot']['top_alpha'])} - 偏离度较大，机会明显
3. **风险控制**: 严格执行20%仓位限制，避免单标的风险集中
4. **信号跟踪**: 继续监控Bias < -3.5%的标的，及时捕捉机会

## 📋 系统状态

- **系统版本**: {config['system_config']['version']}
- **当前任务**: {config['active_status']['current_gist']}
- **系统阶段**: {config['active_status']['phase']}
- **心跳状态**: {config['active_status']['heartbeat']}
- **下次心跳**: {config['active_status']['next_heartbeat']}
- **系统健康**: {config['active_status']['system_health']}

---

*报告生成: 琥珀引擎 50万量化实验室*
*生成时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}*
*系统版本: {config['system_config']['version']}*
"""
    
    return report_content

def save_daily_report(report_content):
    """保存每日报告"""
    today = datetime.now().strftime("%Y-%m-%d")
    report_filename = f"50万实战盈亏结项报告_{today}.md"
    report_path = f"./amber-sentry-logs/archive/reports/{report_filename}"
    
    try:
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        print(f"✅ 每日报告已保存: {report_path}")
        return report_path
    except Exception as e:
        print(f"❌ 保存每日报告失败: {e}")
        return None

def update_reports_index(report_path):
    """更新报告索引"""
    index_path = "./amber-sentry-logs/archive/reports/index.html"
    
    try:
        # 读取现有索引
        with open(index_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 在适当位置插入新报告链接
        insert_marker = "<!-- 报告列表开始 -->"
        if insert_marker in content:
            report_filename = os.path.basename(report_path)
            report_date = datetime.now().strftime("%Y-%m-%d")
            
            new_report_entry = f"""
        <li style="padding: 15px; background: #f8f9fa; border-radius: 8px; margin-bottom: 10px; border-left: 4px solid var(--success-green);">
          <div style="font-weight: 600; color: var(--primary-blue);">📊 50万实战盈亏结项报告 - {report_date}</div>
          <div style="font-size: 14px; color: var(--text-secondary); margin: 5px 0;">{datetime.now().strftime("%Y-%m-%d %H:%M")} · 系统自动生成</div>
          <div style="font-size: 14px;">当日盈亏分析、交易统计、持仓明细、策略展望</div>
          <div style="margin-top: 10px;">
            <a href="/archive/reports/{report_filename}" style="display: inline-block; padding: 5px 10px; background: var(--primary-blue); color: white; text-decoration: none; border-radius: 4px; font-size: 12px;">查看报告</a>
          </div>
        </li>
        """
            
            # 插入新报告
            content = content.replace(insert_marker, insert_marker + new_report_entry)
            
            # 保存更新
            with open(index_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print("✅ 报告索引已更新")
    except Exception as e:
        print(f"⚠️ 更新报告索引失败: {e}")

def main():
    """主函数"""
    print("📊 琥珀引擎 - 50万实战盈亏结项报告生成")
    print(f"⏰ 执行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 加载数据
    config = load_amber_cmd()
    portfolio = load_portfolio()
    
    if not config or not portfolio:
        print("❌ 数据加载失败")
        return 1
    
    print("✅ 数据加载成功")
    
    # 生成报告
    print("📝 生成每日报告...")
    report_content = generate_daily_report(config, portfolio)
    
    if not report_content:
        print("❌ 报告生成失败")
        return 1
    
    # 保存报告
    report_path = save_daily_report(report_content)
    
    if report_path:
        # 更新报告索引
        update_reports_index(report_path)
        
        print(f"\n🎉 每日报告生成完成!")
        print(f"📁 报告位置: {report_path}")
        print(f"🌐 访问地址: http://localhost:10169/archive/reports/{os.path.basename(report_path)}")
        
        return 0
    else:
        print("❌ 报告保存失败")
        return 1

if __name__ == "__main__":
    import sys
    sys.exit(main())
