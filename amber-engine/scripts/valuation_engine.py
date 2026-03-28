#!/usr/bin/env python3
"""
琥珀引擎估值引擎 - 首席架构师指令
计算当前PE在过去10年中的百分位，使用amber_vault.db进行本地化缓存
"""

import os
import sys
import pandas as pd
import numpy as np
import sqlite3
from datetime import datetime, timedelta
import json

# 设置Tushare Token
TUSHARE_TOKEN = "9e32ef28eac05c5fbb11e6f02a50da903def70f94b3018e93340568b"
os.environ['TUSHARE_TOKEN'] = TUSHARE_TOKEN

# 数据库路径
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VAULT_DB_PATH = os.path.join(BASE_DIR, "amber_vault.db")

class ValuationEngine:
    """估值引擎 - 计算PE历史百分位"""
    
    def __init__(self):
        self.pro = None
        self.initialize_tushare()
        self.initialize_database()
    
    def initialize_tushare(self):
        """初始化Tushare Pro接口"""
        try:
            import tushare as ts
            self.pro = ts.pro_api(TUSHARE_TOKEN)
            print("✅ Tushare Pro接口初始化成功")
            return True
        except ImportError as e:
            print(f"❌ Tushare库导入失败: {e}")
            return False
        except Exception as e:
            print(f"❌ Tushare初始化失败: {e}")
            return False
    
    def initialize_database(self):
        """初始化数据库"""
        try:
            # 确保数据库目录存在
            os.makedirs(os.path.dirname(VAULT_DB_PATH), exist_ok=True)
            
            conn = sqlite3.connect(VAULT_DB_PATH)
            cursor = conn.cursor()
            
            # 创建PE历史缓存表
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS pe_history_cache (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ts_code TEXT NOT NULL,
                trade_date TEXT NOT NULL,
                pe REAL,
                pb REAL,
                dividend_yield REAL,
                update_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(ts_code, trade_date)
            )
            ''')
            
            # 创建PE百分位结果表
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS pe_percentile_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ts_code TEXT NOT NULL,
                current_pe REAL,
                percentile REAL,
                valuation_status TEXT,
                sample_count INTEGER,
                start_date TEXT,
                end_date TEXT,
                calculation_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(ts_code, calculation_time)
            )
            ''')
            
            # 创建索引
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_ts_code_date ON pe_history_cache(ts_code, trade_date)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_pe_percentile ON pe_percentile_results(ts_code, percentile)')
            
            conn.commit()
            conn.close()
            
            print(f"✅ 估值数据库初始化完成: {VAULT_DB_PATH}")
            return True
            
        except Exception as e:
            print(f"❌ 数据库初始化失败: {e}")
            return False
    
    def fetch_historical_pe_data(self, ts_code, start_date, end_date):
        """
        获取历史PE数据，优先使用缓存
        """
        print(f"📊 获取历史PE数据: {ts_code} ({start_date} ~ {end_date})")
        
        # 1. 检查缓存中是否有数据
        cached_data = self.get_cached_pe_data(ts_code, start_date, end_date)
        
        if cached_data is not None and not cached_data.empty:
            print(f"   ✅ 使用缓存数据: {len(cached_data)} 条记录")
            return cached_data
        
        # 2. 缓存中没有数据，从Tushare获取
        print(f"   🔄 从Tushare获取数据...")
        
        try:
            # 由于数据量大，分批次获取
            all_data = []
            
            # 将10年时间窗口分成2个5年批次
            start_dt = pd.to_datetime(start_date)
            end_dt = pd.to_datetime(end_date)
            mid_dt = start_dt + (end_dt - start_dt) / 2
            
            # 第一批次
            batch1_start = start_dt.strftime('%Y%m%d')
            batch1_end = mid_dt.strftime('%Y%m%d')
            
            print(f"   📅 批次1: {batch1_start} ~ {batch1_end}")
            df1 = self.pro.index_dailybasic(
                ts_code=ts_code,
                start_date=batch1_start,
                end_date=batch1_end,
                fields='ts_code,trade_date,pe,pb,dividend_yield'
            )
            
            if df1 is not None and not df1.empty:
                all_data.append(df1)
                print(f"      ✅ 获取成功: {len(df1)} 条记录")
            else:
                print(f"      ⚠️ 批次1无数据")
            
            # 第二批次
            batch2_start = (mid_dt + timedelta(days=1)).strftime('%Y%m%d')
            batch2_end = end_dt.strftime('%Y%m%d')
            
            print(f"   📅 批次2: {batch2_start} ~ {batch2_end}")
            df2 = self.pro.index_dailybasic(
                ts_code=ts_code,
                start_date=batch2_start,
                end_date=batch2_end,
                fields='ts_code,trade_date,pe,pb,dividend_yield'
            )
            
            if df2 is not None and not df2.empty:
                all_data.append(df2)
                print(f"      ✅ 获取成功: {len(df2)} 条记录")
            else:
                print(f"      ⚠️ 批次2无数据")
            
            # 合并数据
            if not all_data:
                print(f"   ❌ 无历史PE数据")
                return pd.DataFrame()
            
            df_combined = pd.concat(all_data, ignore_index=True)
            
            # 3. 保存到缓存
            self.save_to_pe_cache(ts_code, df_combined)
            
            print(f"   💾 缓存保存: {len(df_combined)} 条记录")
            return df_combined
            
        except Exception as e:
            print(f"   ❌ 数据获取失败: {e}")
            return pd.DataFrame()
    
    def get_cached_pe_data(self, ts_code, start_date, end_date):
        """
        从缓存获取PE数据
        """
        try:
            conn = sqlite3.connect(VAULT_DB_PATH)
            
            query = '''
            SELECT ts_code, trade_date, pe, pb, dividend_yield 
            FROM pe_history_cache 
            WHERE ts_code = ? AND trade_date BETWEEN ? AND ?
            ORDER BY trade_date
            '''
            
            df = pd.read_sql_query(query, conn, params=(ts_code, start_date, end_date))
            conn.close()
            
            return df if not df.empty else None
            
        except Exception as e:
            print(f"   ⚠️ 缓存查询失败: {e}")
            return None
    
    def save_to_pe_cache(self, ts_code, df_data):
        """
        保存PE数据到缓存
        """
        try:
            conn = sqlite3.connect(VAULT_DB_PATH)
            cursor = conn.cursor()
            
            for _, row in df_data.iterrows():
                cursor.execute('''
                INSERT OR REPLACE INTO pe_history_cache 
                (ts_code, trade_date, pe, pb, dividend_yield)
                VALUES (?, ?, ?, ?, ?)
                ''', (
                    ts_code,
                    row['trade_date'],
                    row.get('pe'),
                    row.get('pb'),
                    row.get('dividend_yield')
                ))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            print(f"   ⚠️ 缓存保存失败: {e}")
            return False
    
    def calculate_pe_percentile(self, ts_code, current_pe):
        """
        首席架构师指令：计算当前 PE 在过去 10 年中的百分位
        """
        print("=" * 80)
        print(f"🔍 计算PE历史百分位: {ts_code}")
        print(f"📊 当前PE: {current_pe}")
        print("=" * 80)
        
        try:
            # 1. 确定时间窗口：今天往前推 10 年
            end_date = pd.Timestamp.now().strftime('%Y%m%d')
            start_date = (pd.Timestamp.now() - pd.DateOffset(years=10)).strftime('%Y%m%d')
            
            print(f"📅 时间窗口: {start_date} ~ {end_date} (10年)")
            
            # 2. 抓取历史估值数据
            df_hist = self.fetch_historical_pe_data(ts_code, start_date, end_date)
            
            if df_hist.empty:
                print("❌ 无历史数据，无法计算百分位")
                return {
                    'percentile': "N/A",
                    'sample_count': 0,
                    'valuation_status': "数据不足",
                    'current_pe': current_pe
                }
            
            # 3. 数据清洗：去除异常值和空值
            pe_series = df_hist['pe'].dropna()
            
            # 去除极端异常值 (超过3个标准差)
            mean_pe = pe_series.mean()
            std_pe = pe_series.std()
            lower_bound = mean_pe - 3 * std_pe
            upper_bound = mean_pe + 3 * std_pe
            
            pe_series_clean = pe_series[(pe_series >= lower_bound) & (pe_series <= upper_bound)]
            
            if len(pe_series_clean) < 100:  # 最少需要100个样本
                print(f"⚠️ 样本数量不足: {len(pe_series_clean)} 个，使用原始数据")
                pe_series_clean = pe_series
            
            # 4. 计算百分位 (Numpy 实现高效率)
            # Percentile Rank = (低于当前值的样本数 / 总样本数) * 100
            sample_count = len(pe_series_clean)
            
            if sample_count == 0:
                print("❌ 清洗后无有效数据")
                return {
                    'percentile': "N/A",
                    'sample_count': 0,
                    'valuation_status': "数据不足",
                    'current_pe': current_pe
                }
            
            percentile = (pe_series_clean < current_pe).sum() / sample_count * 100
            
            # 5. 确定估值状态
            valuation_status = self.get_valuation_status(percentile)
            
            print(f"✅ 计算完成:")
            print(f"   当前PE: {current_pe:.2f}")
            print(f"   历史样本: {sample_count} 个交易日")
            print(f"   历史PE范围: {pe_series_clean.min():.2f} ~ {pe_series_clean.max():.2f}")
            print(f"   历史PE均值: {pe_series_clean.mean():.2f}")
            print(f"   历史PE中位数: {pe_series_clean.median():.2f}")
            print(f"   百分位: {percentile:.2f}%")
            print(f"   估值状态: {valuation_status}")
            
            # 6. 保存结果到数据库
            self.save_percentile_result(ts_code, current_pe, percentile, valuation_status, sample_count, start_date, end_date)
            
            return {
                'percentile': round(percentile, 2),
                'sample_count': sample_count,
                'valuation_status': valuation_status,
                'current_pe': current_pe,
                'pe_range': {
                    'min': round(float(pe_series_clean.min()), 2),
                    'max': round(float(pe_series_clean.max()), 2),
                    'mean': round(float(pe_series_clean.mean()), 2),
                    'median': round(float(pe_series_clean.median()), 2)
                }
            }
            
        except Exception as e:
            print(f"❌ 百分位计算失败: {e}")
            import traceback
            traceback.print_exc()
            return {
                'percentile': "Error",
                'sample_count': 0,
                'valuation_status': "计算失败",
                'current_pe': current_pe
            }
    
    def get_valuation_status(self, percentile):
        """
        根据百分位确定估值状态
        """
        if percentile < 20:
            return "💎 极度低估"
        elif percentile < 80:
            return "🌤️ 估值合理"
        else:
            return "🔥 情绪亢奋"
    
    def save_percentile_result(self, ts_code, current_pe, percentile, valuation_status, sample_count, start_date, end_date):
        """
        保存百分位计算结果到数据库
        """
        try:
            conn = sqlite3.connect(VAULT_DB_PATH)
            cursor = conn.cursor()
            
            cursor.execute('''
            INSERT INTO pe_percentile_results 
            (ts_code, current_pe, percentile, valuation_status, sample_count, start_date, end_date)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (ts_code, current_pe, percentile, valuation_status, sample_count, start_date, end_date))
            
            conn.commit()
            conn.close()
            
            print(f"💾 结果保存到数据库")
            return True
            
        except Exception as e:
            print(f"⚠️ 结果保存失败: {e}")
            return False
    
    def get_valuation_display_html(self, ts_code, current_pe, percentile_result):
        """
        生成估值显示的HTML代码
        前端视觉语义化要求：
        - Pctl < 20%: 💎 极度低估 (20% Pctl)，颜色：琥珀绿 (#4CAF50)
        - 20% ≤ Pctl < 80%: 🌤️ 估值合理 (50% Pctl)，颜色：琥珀灰 (#757575)
        - Pctl ≥ 80%: 🔥 情绪亢奋 (85% Pctl)，颜色：亮红 (#F44336) + 闪烁动画
        """
        if percentile_result['percentile'] == "N/A" or percentile_result['percentile'] == "Error":
            return '''
            <div class="valuation-item valuation-na">
                <div class="valuation-header">
                    <span class="valuation-name">估值云图</span>
                    <span class="valuation-market">沪深300</span>
                </div>
                <div class="valuation-value">📊 数据更新中</div>
                <div class="valuation-detail">PE: -- | 历史分位: --</div>
            </div>
            '''
        
        percentile = percentile_result['percentile']
        valuation_status = percentile_result['valuation_status']
        
        # 确定CSS类名和颜色
        if percentile < 20:
            css_class = "valuation-extreme-low"
            color = "#4CAF50"
            emoji = "💎"
            status_text = f"{emoji} 极度低估 ({percentile}% Pctl)"
        elif percentile < 80:
            css_class = "valuation-reasonable"
            color = "#757575"
            emoji = "🌤️"
            status_text = f"{emoji} 估值合理 ({percentile}% Pctl)"
        else:
            css_class = "valuation-high"
            color = "#F44336"
            emoji = "🔥"
            status_text = f"{emoji} 情绪亢奋 ({percentile}% Pctl)"
        
        # 生成HTML
        html = f'''
        <div class="valuation-item {css_class}">
            <div class="valuation-header">
                <span class="valuation-name">估值云图</span>
                <span class="valuation-market">沪深300</span>
            </div>
            <div class="valuation-value">{status_text}</div>
            <div class="valuation-detail">PE: {current_pe:.2f}x | 历史分位: {percentile}%</div>
            <div class="valuation-stats">
                <span class="stat-item">样本: {percentile_result['sample_count']}天</span>
                <span class="stat-item">范围: {percentile_result['pe_range']['min']}x~{percentile_result['pe_range']['max']}x</span>
                <span class="stat-item">均值: {percentile_result['pe_range']['mean']}x</span>
            </div>
        </div>
        '''
        
        return html
    
    def generate_risk_audit_report(self, top_holdings):
        """
        生成风险审计报告 - 架构师致主编
        针对穿透出的Top 10重仓股进行风险审计
        """
        print("\n" + "=" * 80)
        print("🛡️ 架构师风险审计报告")
        print("=" * 80)
        
        report = {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'total_assets': 504000,  # 50.4万元
            'top_holdings': top_holdings,
            'risk_findings': [],
            'recommendations': []
        }
        
        # 分析创业板依赖症
        gemini_stocks = []
        gemini_total_value = 0
        
        for holding in top_holdings:
            stock_code = holding['stock_code']
            stock_value = holding['stock_value']
            
            # 判断是否为创业板股票 (300开头)
            if stock_code.startswith('300'):
                gemini_stocks.append({
                    'code': stock_code,
                    'name': holding['stock_name'],
                    'value': stock_value,
                    'percentage': holding['ratio_in_portfolio']
                })
                gemini_total_value += stock_value
        
        # 计算创业板占比
        if gemini_stocks:
            gemini_percentage = (gemini_total_value / 504000) * 100
            
            report['risk_findings'].append({
                'type': '创业板依赖症 (Gem-Dependency)',
                'description': f'前10大重仓股中，{len(gemini_stocks)}只为创业板股票',
                'details': [
                    f'创业板股票总价值: {gemini_total_value:,.0f} 元',
                    f'占总资产比例: {gemini_percentage:.1f}%',
                    f'这意味着您的50.4万总资产，有超过{gemini_percentage:.1f}%的命运绑定在创业板指数的波动上'
                ],
                'stocks': gemini_stocks,
                'severity': '高' if gemini_percentage > 20 else '中'
            })
            
            print(f"📊 创业板依赖症分析:")
            print(f"   创业板股票数量: {len(gemini_stocks)} 只")
            print(f"   创业板总价值: {gemini_total_value:,.0f} 元")
            print(f"   占总资产: {gemini_percentage:.1f}%")
            print(f"   ⚠️ 风险等级: {'高' if gemini_percentage > 20 else '中'}")
        
        # 分析算力与半导体集中度
        computing_stocks = []
        computing_total_value = 0
        
        # 算力与半导体相关股票 (简化判断)
        computing_keywords = ['中际旭创', '新易盛', '中芯国际', '宁德时代', '东方财富']
        
        for holding in top_holdings:
            stock_name = holding['stock_name']
            stock_value = holding['stock_value']
            
            if any(keyword in stock_name for keyword in computing_keywords):
                computing_stocks.append({
                    'code': holding['stock_code'],
                    'name': stock_name,
                    'value': stock_value,
                    'percentage': holding['ratio_in_portfolio']
                })
                computing_total_value += stock_value
        
        # 计算算力板块占比
        if computing_stocks:
            computing_percentage = (computing_total_value / 504000) * 100
            
            report['risk_findings'].append({
                'type': '算力与半导体集中 (Cpm-Concentration)',
                'description': '底层持仓过于拥挤在AI算力赛道',
                'details': [
                    f'算力/半导体股票总价值: {computing_total_value:,.0f} 元',
                    f'占总资产比例: {computing_percentage:.1f}%',
                    f'系统应产生一条内部备注："主编，底层持仓过于拥挤在AI算力赛道，需留意板块轮动风险。"'
                ],
                'stocks': computing_stocks,
                'severity': '高' if computing_percentage > 30 else '中'
            })
            
            print(f"\n📊 算力与半导体集中度分析:")
            print(f"   相关股票数量: {len(computing_stocks)} 只")
            print(f"   相关股票总价值: {computing_total_value:,.0f} 元")
            print(f"   占总资产: {computing_percentage:.1f}%")
            print(f"   ⚠️ 风险等级: {'高' if computing_percentage > 30 else '中'}")
            print(f"   📝 内部备注: 主编，底层持仓过于拥挤在AI算力赛道，需留意板块轮动风险。")
        
        # 生成建议
        if gemini_stocks and gemini_percentage > 20:
            report['recommendations'].append({
                'priority': '高',
                'action': '降低创业板暴露',
                'description': f'当前创业板占比{gemini_percentage:.1f}%，建议降至20%以下',
                'suggested_actions': [
                    '考虑增加主板蓝筹股配置',
                    '分散到其他板块如消费、医药',
                    '设置创业板指数止损位'
                ]
            })
        
        if computing_stocks and computing_percentage > 30:
            report['recommendations'].append({
                'priority': '高',
                'action': '分散算力赛道集中度',
                'description': f'当前算力/半导体占比{computing_percentage:.1f}%，建议降至30%以下',
                'suggested_actions': [
                    '考虑配置部分消费电子或传统半导体',
                    '增加非科技板块的防御性配置',
                    '设置板块轮动监控机制'
                ]
            })
        
        # 如果没有高风险，给出正面反馈
        if not report['risk_findings']:
            report['risk_findings'].append({
                'type': '风险分散良好',
                'description': '持仓分散度良好，无明显集中风险',
                'details': ['当前持仓分散在多个板块和行业', '风险控制措施有效'],
                'severity': '低'
            })
        
        print("\n" + "=" * 80)
        print("📋 风险审计报告生成完成")
        print("=" * 80)
        
        # 保存报告
        self.save_risk_report(report)
        
        return report
    
    def save_risk_report(self, report):
        """保存风险审计报告"""
        try:
            report_dir = os.path.join(BASE_DIR, "reports", "risk_audit")
            os.makedirs(report_dir, exist_ok=True)
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M')
            report_file = os.path.join(report_dir, f"risk_audit_{timestamp}.md")
            
            # 生成Markdown报告
            report_content = f"""# 🛡️ 架构师风险审计报告

## 报告信息
- **审计时间**: {report['timestamp']}
- **总资产规模**: {report['total_assets']:,.0f} 元 (50.4万元)
- **审计对象**: 前10大重仓股穿透分析

## 📊 审计概览

### 总资产构成
- **总金额**: {report['total_assets']:,.0f} 元
- **审计股票**: {len(report['top_holdings'])} 只
- **审计范围**: 前10大重仓股穿透分析

## 🔍 风险发现

"""
            
            for i, finding in enumerate(report['risk_findings'], 1):
                report_content += f"""### {i}. {finding['type']}

**风险等级**: {finding.get('severity', '未知')}
**描述**: {finding['description']}

**详细分析**:
"""
                
                for detail in finding.get('details', []):
                    report_content += f"- {detail}\n"
                
                if 'stocks' in finding and finding['stocks']:
                    report_content += f"""
**相关股票**:
| 股票代码 | 股票名称 | 持仓价值 | 占比 |
|----------|----------|----------|------|
"""
                    for stock in finding['stocks']:
                        report_content += f"| {stock['code']} | {stock['name']} | {stock['value']:,.0f}元 | {stock['percentage']:.2f}% |\n"
                
                report_content += "\n"
            
            if report['recommendations']:
                report_content += """## 🎯 风险缓解建议

"""
                for i, rec in enumerate(report['recommendations'], 1):
                    report_content += f"""### {i}. {rec['action']} (优先级: {rec['priority']})

**建议原因**: {rec['description']}

**具体行动**:
"""
                    for action in rec.get('suggested_actions', []):
                        report_content += f"- {action}\n"
                    
                    report_content += "\n"
            
            report_content += f"""## 📈 后续监控计划

### 短期监控 (1周)
1. **创业板指数监控**: 每日跟踪创业板指数波动
2. **算力板块监控**: 监控AI算力相关板块表现
3. **持仓集中度**: 每周更新持仓穿透分析

### 中期调整 (1月)
1. **配置优化**: 基于风险审计结果调整基金配置
2. **风险对冲**: 考虑增加防御性板块配置
3. **止损策略**: 设置关键板块的止损位

### 长期规划 (1季)
1. **资产再平衡**: 季度性的资产再平衡
2. **风险模型优化**: 基于穿透结果优化风险模型
3. **策略回顾**: 回顾投资策略的有效性

---
*报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
*琥珀引擎风险审计系统*
*数据来源: Tushare Pro Verified + 资产穿透分析*
"""

            with open(report_file, 'w', encoding='utf-8') as f:
                f.write(report_content)
            
            print(f"📋 风险审计报告已生成: {report_file}")
            
            # 生成HTML版本
            self.generate_risk_html_report(report, report_dir, timestamp)
            
            return True
            
        except Exception as e:
            print(f"❌ 风险报告保存失败: {e}")
            return False
    
    def generate_risk_html_report(self, report, report_dir, timestamp):
        """生成HTML版本的风险报告"""
        html_file = os.path.join(report_dir, f"risk_audit_{timestamp}.html")
        
        # 准备数据
        risk_items = []
        for finding in report['risk_findings']:
            risk_items.append({
                'type': finding['type'],
                'severity': finding.get('severity', '未知'),
                'description': finding['description']
            })
        
        html_content = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>架构师风险审计报告</title>
    <link rel="stylesheet" href="/static/css/amber-v2.2.min.css">
    <style>
        .risk-report {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 2rem;
        }}
        
        .risk-header {{
            background: linear-gradient(135deg, #1a237e 0%, #283593 100%);
            color: white;
            padding: 2rem;
            border-radius: 1rem;
            margin-bottom: 2rem;
            text-align: center;
        }}
        
        .risk-card {{
            background: white;
            border-radius: 0.75rem;
            padding: 1.5rem;
            margin: 1rem 0;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            border-left: 4px solid;
        }}
        
        .risk-high {{
            border-left-color: #f44336;
        }}
        
        .risk-medium {{
            border-left-color: #ff9800;
        }}
        
        .risk-low {{
            border-left-color: #4caf50;
        }}
        
        .severity-badge {{
            display: inline-block;
            padding: 0.25rem 0.75rem;
            border-radius: 1rem;
            font-size: 0.875rem;
            font-weight: 600;
            margin-right: 0.5rem;
        }}
        
        .severity-high {{
            background: #ffebee;
            color: #c62828;
        }}
        
        .severity-medium {{
            background: #fff3e0;
            color: #ef6c00;
        }}
        
        .severity-low {{
            background: #e8f5e9;
            color: #2e7d32;
        }}
        
        .recommendation-card {{
            background: #e3f2fd;
            border-radius: 0.75rem;
            padding: 1.5rem;
            margin: 1rem 0;
            border-left: 4px solid #2196f3;
        }}
    </style>
</head>
<body>
    <div class="risk-report">
        <div class="risk-header">
            <h1>🛡️ 架构师风险审计报告</h1>
            <p>审计时间: {report['timestamp']}</p>
            <p>总资产规模: {report['total_assets']:,.0f} 元 (50.4万元)</p>
        </div>
        
        <h2>📊 风险发现</h2>
"""
        
        for item in risk_items:
            severity_class = f"severity-{item['severity'].lower()}"
            risk_class = f"risk-{item['severity'].lower()}"
            
            html_content += f"""        <div class="risk-card {risk_class}">
            <div class="risk-title">
                <span class="severity-badge {severity_class}">{item['severity']}风险</span>
                <strong>{item['type']}</strong>
            </div>
            <p>{item['description']}</p>
        </div>
"""
        
        if report['recommendations']:
            html_content += f"""        <h2>🎯 风险缓解建议</h2>
"""
            
            for rec in report['recommendations']:
                html_content += f"""        <div class="recommendation-card">
            <div class="rec-title">
                <strong>{rec['action']}</strong> (优先级: {rec['priority']})
            </div>
            <p>{rec['description']}</p>
            <ul>
"""
                
                for action in rec.get('suggested_actions', []):
                    html_content += f"""                <li>{action}</li>
"""
                
                html_content += f"""            </ul>
        </div>
"""
        
        html_content += f"""        <div class="report-footer">
            <p>💡 数据来源: Tushare Pro Verified | 琥珀引擎风险审计系统</p>
            <p>📅 报告生成: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            <p>🔗 访问地址: https://finance.cheese.ai/my-wealth/risk-audit</p>
        </div>
    </div>
</body>
</html>"""
        
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"✅ HTML风险报告已生成: {html_file}")

def main():
    """主函数"""
    print("🚀 启动琥珀引擎估值引擎...")
    
    # 创建估值引擎
    engine = ValuationEngine()
    
    if not engine.pro:
        print("❌ Tushare初始化失败，无法执行估值计算")
        return False
    
    # 测试PE百分位计算 (沪深300)
    print("\n" + "=" * 80)
    print("🧪 测试PE百分位计算")
    print("=" * 80)
    
    # 获取当前PE值 (示例值)
    current_pe = 14.75
    
    # 计算百分位
    result = engine.calculate_pe_percentile('000300.SH', current_pe)
    
    # 生成HTML显示代码
    html_display = engine.get_valuation_display_html('000300.SH', current_pe, result)
    
    print("\n" + "=" * 80)
    print("🎨 估值显示HTML代码:")
    print("=" * 80)
    print(html_display)
    
    # 测试风险审计报告
    print("\n" + "=" * 80)
    print("🛡️ 测试风险审计报告")
    print("=" * 80)
    
    # 模拟前10大重仓股数据
    top_holdings = [
        {'stock_code': '300750.SZ', 'stock_name': '宁德时代', 'stock_value': 35426, 'ratio_in_portfolio': 9.08},
        {'stock_code': '300308.SZ', 'stock_name': '中际旭创', 'stock_value': 23881, 'ratio_in_portfolio': 6.12},
        {'stock_code': '300059.SZ', 'stock_name': '东方财富', 'stock_value': 22127, 'ratio_in_portfolio': 5.67},
        {'stock_code': '300502.SZ', 'stock_name': '新易盛', 'stock_value': 16615, 'ratio_in_portfolio': 4.26},
        {'stock_code': '688981.SH', 'stock_name': '中芯国际', 'stock_value': 16329, 'ratio_in_portfolio': 4.19},
        {'stock_code': '600030.SH', 'stock_name': '中信证券', 'stock_value': 15487, 'ratio_in_portfolio': 3.97},
        {'stock_code': '600519.SH', 'stock_name': '贵州茅台', 'stock_value': 14806, 'ratio_in_portfolio': 3.80},
        {'stock_code': '688256.SH', 'stock_name': '寒武纪', 'stock_value': 14075, 'ratio_in_portfolio': 3.61},
        {'stock_code': '688041.SH', 'stock_name': '海光信息', 'stock_value': 13930, 'ratio_in_portfolio': 3.57},
        {'stock_code': '600036.SH', 'stock_name': '招商银行', 'stock_value': 13439, 'ratio_in_portfolio': 3.45}
    ]
    
    # 生成风险审计报告
    risk_report = engine.generate_risk_audit_report(top_holdings)
    
    print("\n" + "=" * 80)
    print("🏆 琥珀引擎估值引擎测试完成")
    print("=" * 80)
    print("✅ PE百分位计算: 算法实现完成")
    print("✅ 数据库缓存: amber_vault.db 本地化缓存")
    print("✅ 前端视觉语义化: HTML代码生成完成")
    print("✅ 风险审计报告: 架构师指令执行完成")
    print("📊 测试结果:")
    print(f"   当前PE: {current_pe:.2f}x")
    print(f"   历史百分位: {result.get('percentile', 'N/A')}%")
    print(f"   估值状态: {result.get('valuation_status', '未知')}")
    print(f"   风险发现: {len(risk_report['risk_findings'])} 项")
    print(f"   缓解建议: {len(risk_report['recommendations'])} 条")
    print("=" * 80)
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)