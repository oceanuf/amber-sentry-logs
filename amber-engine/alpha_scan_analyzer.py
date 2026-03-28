#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
琥珀引擎Alpha扫描分析器 - Gist_00127号任务
执行50支ETF净值历史智能挖掘，识别Alpha机会
"""

import json
import os
import pandas as pd
import numpy as np
from datetime import datetime
import glob

class AlphaScanAnalyzer:
    """Alpha扫描分析器 - 基于Gist_00127指令"""
    
    def __init__(self):
        """初始化分析器"""
        print("="*60)
        print("🚀 启动琥珀引擎Alpha扫描分析器 - Gist_00127")
        print("="*60)
        
        # 配置参数
        self.data_dir = "/home/luckyelite/.openclaw/workspace/amber-engine/data/nav_history/"
        self.output_dir = "/home/luckyelite/.openclaw/workspace/amber-engine/schedule/gist_report/insights/"
        self.etf_seeds_path = "/home/luckyelite/.openclaw/workspace/amber-engine/etf_50_seeds.json"
        
        # 加载ETF种子数据
        with open(self.etf_seeds_path, 'r', encoding='utf-8') as f:
            seeds_data = json.load(f)
            self.etf_seeds = seeds_data['etf_data']
        
        print(f"✅ 加载ETF种子数据: {len(self.etf_seeds)} 支ETF")
        print(f"✅ 数据目录: {self.data_dir}")
        print(f"✅ 输出目录: {self.output_dir}")
    
    def load_nav_history(self, etf_code):
        """加载单只ETF的净值历史数据"""
        file_path = os.path.join(self.data_dir, f"{etf_code}.json")
        if not os.path.exists(file_path):
            print(f"   ⚠️  文件不存在: {file_path}")
            return None
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return data
        except Exception as e:
            print(f"   ❌ 加载数据失败 {etf_code}: {e}")
            return None
    
    def calculate_ma20(self, nav_data):
        """计算20日移动平均线"""
        if not nav_data or len(nav_data) < 20:
            return None
        
        # 提取最近20个交易日的净值
        recent_navs = []
        for item in nav_data[:20]:  # 数据是按日期倒序排列的
            if 'unit_nav' in item:
                recent_navs.append(float(item['unit_nav']))
            elif 'nav' in item:
                recent_navs.append(float(item['nav']))
        
        if len(recent_navs) < 20:
            return None
        
        return np.mean(recent_navs)
    
    def calculate_volatility(self, nav_data):
        """计算波动率排名"""
        if not nav_data or len(nav_data) < 20:
            return None
        
        # 提取最近20个交易日的净值
        nav_values = []
        for item in nav_data[:20]:
            if 'unit_nav' in item:
                nav_values.append(float(item['unit_nav']))
            elif 'nav' in item:
                nav_values.append(float(item['nav']))
        
        if len(nav_values) < 2:
            return None
        
        # 计算日收益率
        returns = []
        for i in range(1, len(nav_values)):
            if nav_values[i-1] > 0:
                daily_return = (nav_values[i] - nav_values[i-1]) / nav_values[i-1]
                returns.append(daily_return)
        
        if len(returns) < 1:
            return None
        
        # 计算年化波动率 (假设252个交易日)
        volatility = np.std(returns) * np.sqrt(252)
        return volatility
    
    def analyze_etf(self, etf_code, etf_name):
        """分析单只ETF"""
        print(f"\n🔍 分析ETF: {etf_name} ({etf_code})")
        
        # 加载净值历史
        nav_data = self.load_nav_history(etf_code)
        if not nav_data:
            return None
        
        # 获取最新净值
        latest_nav = None
        if nav_data and len(nav_data) > 0:
            latest_item = nav_data[0]  # 最新数据
            if 'unit_nav' in latest_item:
                latest_nav = float(latest_item['unit_nav'])
            elif 'nav' in latest_item:
                latest_nav = float(latest_item['nav'])
        
        if latest_nav is None:
            print(f"   ⚠️  无法获取最新净值")
            return None
        
        # 计算MA20
        ma20 = self.calculate_ma20(nav_data)
        if ma20 is None:
            print(f"   ⚠️  无法计算MA20")
            return None
        
        # 计算波动率
        volatility = self.calculate_volatility(nav_data)
        
        # 计算MA20偏离度
        ma20_deviation = (latest_nav - ma20) / ma20 * 100
        
        # 判断Alpha机会 (根据Gist指令: IF current_nav < MA20 * 0.97 THEN FLAG_AS_ALPHA)
        is_alpha_opportunity = latest_nav < ma20 * 0.97
        
        # 准备结果 (确保所有值都是Python原生类型)
        result = {
            'code': etf_code,
            'name': etf_name,
            'latest_nav': float(latest_nav),
            'ma20': float(ma20),
            'ma20_deviation_percent': float(round(ma20_deviation, 2)),
            'volatility': float(round(volatility, 4)) if volatility else None,
            'is_alpha_opportunity': bool(is_alpha_opportunity),
            'alpha_score': float(self.calculate_alpha_score(ma20_deviation, volatility)) if volatility else 0.0
        }
        
        print(f"   📊 最新净值: {latest_nav:.4f}")
        print(f"   📈 MA20: {ma20:.4f}")
        print(f"   📉 MA20偏离度: {ma20_deviation:.2f}%")
        if volatility:
            print(f"   📊 年化波动率: {volatility:.4f}")
        print(f"   🎯 Alpha机会: {'✅ 是' if is_alpha_opportunity else '❌ 否'}")
        
        return result
    
    def calculate_alpha_score(self, ma20_deviation, volatility):
        """计算Alpha得分 (负偏离度越大，波动率越低，得分越高)"""
        # 偏离度得分 (负偏离度越大得分越高)
        deviation_score = max(0, -ma20_deviation) * 2  # 每1%负偏离得2分
        
        # 波动率得分 (波动率越低得分越高)
        if volatility:
            volatility_score = max(0, 10 - volatility * 100)  # 波动率每1%扣1分，基础10分
        else:
            volatility_score = 5  # 默认分
        
        # 综合得分
        total_score = deviation_score + volatility_score
        return min(100, total_score)  # 上限100分
    
    def run_analysis(self):
        """执行全量分析"""
        print("\n" + "="*60)
        print("🎯 开始50支ETF Alpha扫描分析")
        print("="*60)
        
        all_results = []
        
        # 分析所有ETF
        for etf in self.etf_seeds:
            result = self.analyze_etf(etf['code'], etf['name'])
            if result:
                all_results.append(result)
        
        print(f"\n✅ 分析完成: {len(all_results)}/{len(self.etf_seeds)} 支ETF分析成功")
        
        # 筛选Alpha机会
        alpha_opportunities = [r for r in all_results if r['is_alpha_opportunity']]
        print(f"🎯 发现Alpha机会: {len(alpha_opportunities)} 支ETF")
        
        # 按Alpha得分排序
        alpha_opportunities.sort(key=lambda x: x['alpha_score'], reverse=True)
        
        # 生成TOP_3_OPPORTUNITY_DASHBOARD
        self.generate_dashboard(alpha_opportunities[:3], all_results)
        
        # 生成详细报告
        self.generate_detailed_report(all_results, alpha_opportunities)
        
        return all_results, alpha_opportunities
    
    def generate_dashboard(self, top_3_opportunities, all_results):
        """生成TOP_3_OPPORTUNITY_DASHBOARD"""
        print("\n" + "="*60)
        print("📊 生成TOP_3_OPPORTUNITY_DASHBOARD")
        print("="*60)
        
        dashboard_data = {
            'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'gist_instruction': 'ALPHA_SCAN_AND_ALERT_00127',
            'total_etfs_analyzed': len(all_results),
            'alpha_opportunities_found': len([r for r in all_results if r['is_alpha_opportunity']]),
            'top_3_opportunities': top_3_opportunities,
            'summary_stats': {
                'avg_ma20_deviation': round(np.mean([r['ma20_deviation_percent'] for r in all_results]), 2),
                'avg_volatility': round(np.mean([r['volatility'] for r in all_results if r['volatility']]), 4),
                'max_alpha_score': max([r['alpha_score'] for r in all_results]),
                'min_ma20_deviation': min([r['ma20_deviation_percent'] for r in all_results])
            }
        }
        
        # 保存JSON文件
        output_path = os.path.join(self.output_dir, 'top_3_opportunity_dashboard.json')
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(dashboard_data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ 仪表板已保存: {output_path}")
        
        # 生成HTML可视化
        self.generate_html_dashboard(dashboard_data)
    
    def generate_html_dashboard(self, dashboard_data):
        """生成HTML可视化仪表板"""
        html_content = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>琥珀引擎Alpha机会仪表板 - Gist_00127</title>
    <style>
        body {{ font-family: 'Segoe UI', Arial, sans-serif; margin: 0; padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: #333; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; border-radius: 15px; padding: 30px; box-shadow: 0 20px 60px rgba(0,0,0,0.3); }}
        .header {{ text-align: center; margin-bottom: 40px; }}
        .header h1 {{ color: #2c3e50; font-size: 2.5em; margin-bottom: 10px; }}
        .header .subtitle {{ color: #7f8c8d; font-size: 1.2em; }}
        .stats-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin-bottom: 40px; }}
        .stat-card {{ background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%); padding: 20px; border-radius: 10px; text-align: center; }}
        .stat-card h3 {{ margin: 0 0 10px 0; color: #2c3e50; }}
        .stat-value {{ font-size: 2.5em; font-weight: bold; color: #3498db; }}
        .opportunities-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(350px, 1fr)); gap: 30px; }}
        .opportunity-card {{ background: linear-gradient(135deg, #fdfcfb 0%, #e2d1c3 100%); border-radius: 15px; padding: 25px; box-shadow: 0 10px 30px rgba(0,0,0,0.1); }}
        .opportunity-card.top {{ border: 3px solid #f39c12; }}
        .opportunity-card h3 {{ color: #2c3e50; margin-top: 0; }}
        .opportunity-metrics {{ display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin: 20px 0; }}
        .metric {{ text-align: center; }}
        .metric-label {{ font-size: 0.9em; color: #7f8c8d; }}
        .metric-value {{ font-size: 1.5em; font-weight: bold; }}
        .alpha-score {{ font-size: 3em; font-weight: bold; text-align: center; margin: 20px 0; }}
        .score-excellent {{ color: #27ae60; }}
        .score-good {{ color: #f39c12; }}
        .score-fair {{ color: #e74c3c; }}
        .footer {{ margin-top: 40px; text-align: center; color: #7f8c8d; font-size: 0.9em; }}
        .timestamp {{ background: #f8f9fa; padding: 10px; border-radius: 5px; margin-top: 20px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🏛️ 琥珀引擎Alpha机会仪表板</h1>
            <div class="subtitle">Gist_00127号任务 - 数据智能挖掘结果</div>
            <div class="timestamp">生成时间: {dashboard_data['generated_at']}</div>
        </div>
        
        <div class="stats-grid">
            <div class="stat-card">
                <h3>📊 分析ETF总数</h3>
                <div class="stat-value">{dashboard_data['total_etfs_analyzed']}</div>
            </div>
            <div class="stat-card">
                <h3>🎯 Alpha机会发现</h3>
                <div class="stat-value">{dashboard_data['alpha_opportunities_found']}</div>
            </div>
            <div class="stat-card">
                <h3>📉 平均MA20偏离度</h3>
                <div class="stat-value">{dashboard_data['summary_stats']['avg_ma20_deviation']}%</div>
            </div>
            <div class="stat-card">
                <h3>📊 平均波动率</h3>
                <div class="stat-value">{dashboard_data['summary_stats']['avg_volatility']}</div>
            </div>
        </div>
        
        <h2 style="color: #2c3e50; text-align: center; margin-bottom: 30px;">🏆 TOP 3 Alpha机会</h2>
        
        <div class="opportunities-grid">
"""
        
        # 添加TOP 3机会卡片
        for i, opp in enumerate(dashboard_data['top_3_opportunities']):
            score_class = "score-excellent" if opp['alpha_score'] >= 80 else "score-good" if opp['alpha_score'] >= 60 else "score-fair"
            
            html_content += f"""
            <div class="opportunity-card {'top' if i == 0 else ''}">
                <h3>#{i+1} {opp['name']} ({opp['code']})</h3>
                <div class="alpha-score {score_class}">{opp['alpha_score']}分</div>
                <div class="opportunity-metrics">
                    <div class="metric">
                        <div class="metric-label">最新净值</div>
                        <div class="metric-value">{opp['latest_nav']:.4f}</div>
                    </div>
                    <div class="metric">
                        <div class="metric-label">MA20</div>
                        <div class="metric-value">{opp['ma20']:.4f}</div>
                    </div>
                    <div class="metric">
                        <div class="metric-label">MA20偏离度</div>
                        <div class="metric-value">{opp['ma20_deviation_percent']}%</div>
                    </div>
                    <div class="metric">
                        <div class="metric-label">波动率</div>
                        <div class="metric-value">{opp['volatility'] if opp['volatility'] else 'N/A'}</div>
                    </div>
                </div>
                <div style="text-align: center; margin-top: 20px;">
                    <div style="background: #27ae60; color: white; padding: 10px 20px; border-radius: 25px; display: inline-block; font-weight: bold;">
                        ✅ Alpha机会确认
                    </div>
                </div>
            </div>
"""
        
        html_content += f"""
        </div>
        
        <div class="footer">
            <p>🏛️ 琥珀引擎 · 青铜法典 · Gist_00127号任务执行报告</p>
            <p>执行引擎: 工程师 Cheese | 架构指导: 首席架构师 Gemini | 最终审批: 主编 Haiyang</p>
            <p>访问地址: <a href="https://localhost:10168/schedule/gist_report/insights/top_3_opportunity_dashboard.html" target="_blank">https://localhost:10168/schedule/gist_report/insights/top_3_opportunity_dashboard.html</a></p>
        </div>
    </div>
</body>
</html>"""
        
        # 保存HTML文件
        output_path = os.path.join(self.output_dir, 'top_3_opportunity_dashboard.html')
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"✅ HTML仪表板已保存: {output_path}")
    
    def generate_detailed_report(self, all_results, alpha_opportunities):
        """生成详细报告"""
        print("\n" + "="*60)
        print("📋 生成详细分析报告")
        print("="*60)
        
        # 按Alpha得分排序
        sorted_results = sorted(all_results, key=lambda x: x['alpha_score'], reverse=True)
        
        report_data = {
            'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'gist_instruction': 'ALPHA_SCAN_AND_ALERT_00127',
            'analysis_scope': '50_ETF_NAV_HISTORY',
            'alpha_logic': 'IF current_nav < MA20 * 0.97 THEN FLAG_AS_ALPHA',
            'total_etfs': len(all_results),
            'alpha_opportunities_count': len(alpha_opportunities),
            'etf_analysis': sorted_results,
            'summary': {
                'top_3_codes': [r['code'] for r in sorted_results[:3]],
                'top_3_names': [r['name'] for r in sorted_results[:3]],
                'top_3_scores': [r['alpha_score'] for r in sorted_results[:3]],
                'worst_3_codes': [r['code'] for r in sorted_results[-3:]],
                'worst_3_names': [r['name'] for r in sorted_results[-3:]],
                'worst_3_scores': [r['alpha_score'] for r in sorted_results[-3:]]
            }
        }
        
        # 保存JSON报告
        output_path = os.path.join(self.output_dir, 'detailed_alpha_analysis.json')
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ 详细报告已保存: {output_path}")
        
        # 生成Markdown报告
        self.generate_markdown_report(report_data)
    
    def generate_markdown_report(self, report_data):
        """生成Markdown报告"""
        md_content = f"""# 🏛️ 琥珀引擎Alpha扫描分析报告 - Gist_00127

## 📋 报告摘要

- **生成时间**: {report_data['generated_at']}
- **指令编号**: {report_data['gist_instruction']}
- **分析范围**: {report_data['analysis_scope']}
- **Alpha逻辑**: `{report_data['alpha_logic']}`
- **分析ETF总数**: {report_data['total_etfs']} 支
- **发现Alpha机会**: {report_data['alpha_opportunities_count']} 支

## 🏆 TOP 3 Alpha机会

| 排名 | ETF代码 | ETF名称 | Alpha得分 | 最新净值 | MA20 | MA20偏离度 | 波动率 |
|------|---------|---------|-----------|----------|------|------------|--------|
"""
        
        # 添加TOP 3表格
        for i, etf in enumerate(report_data['etf_analysis'][:3]):
            md_content += f"""| #{i+1} | `{etf['code']}` | {etf['name']} | **{etf['alpha_score']}分** | {etf['latest_nav']:.4f} | {etf['ma20']:.4f} | {etf['ma20_deviation_percent']}% | {etf['volatility'] if etf['volatility'] else 'N/A'} |
"""
        
        md_content += f"""
## 📊 完整分析结果

| ETF代码 | ETF名称 | Alpha得分 | 最新净值 | MA20 | MA20偏离度 | 波动率 | Alpha机会 |
|---------|---------|-----------|----------|------|------------|--------|-----------|
"""
        
        # 添加完整表格
        for etf in report_data['etf_analysis']:
            alpha_flag = "✅" if etf['is_alpha_opportunity'] else "❌"
            md_content += f"""| `{etf['code']}` | {etf['name']} | {etf['alpha_score']}分 | {etf['latest_nav']:.4f} | {etf['ma20']:.4f} | {etf['ma20_deviation_percent']}% | {etf['volatility'] if etf['volatility'] else 'N/A'} | {alpha_flag} |
"""
        
        md_content += f"""
## 📈 统计分析

### 最佳表现
- **TOP 3 ETF**: {', '.join([f"{name}({code})" for name, code in zip(report_data['summary']['top_3_names'], report_data['summary']['top_3_codes'])])}
- **TOP 3 得分**: {', '.join([str(score) for score in report_data['summary']['top_3_scores']])}

### 最差表现  
- **BOTTOM 3 ETF**: {', '.join([f"{name}({code})" for name, code in zip(report_data['summary']['worst_3_names'], report_data['summary']['worst_3_codes'])])}
- **BOTTOM 3 得分**: {', '.join([str(score) for score in report_data['summary']['worst_3_scores']])}

## 🎯 投资建议

基于Gist_00127指令的Alpha扫描逻辑，建议重点关注以下ETF：

"""
        
        # 添加投资建议
        for i, etf in enumerate(report_data['etf_analysis'][:3]):
            md_content += f"""### {i+1}. {etf['name']} (`{etf['code']}`)
- **Alpha得分**: {etf['alpha_score']}分 (排名第{i+1})
- **核心优势**: 当前净值({etf['latest_nav']:.4f})显著低于MA20({etf['ma20']:.4f})，偏离度{etf['ma20_deviation_percent']}%
- **风险提示**: 波动率{etf['volatility'] if etf['volatility'] else 'N/A'}
- **建议**: 符合Alpha机会标准，建议进一步分析基本面

"""
        
        md_content += f"""
## 🔧 技术说明

### 算法逻辑
1. **数据源**: 50支ETF的30日净值历史数据
2. **MA20计算**: 最近20个交易日的净值移动平均
3. **偏离度计算**: (最新净值 - MA20) / MA20 × 100%
4. **波动率计算**: 基于日收益率的年化标准差
5. **Alpha得分**: 偏离度得分 + 波动率得分 (负偏离度越大、波动率越低，得分越高)

### 执行参数
- **Alpha阈值**: 最新净值 < MA20 × 0.97
- **分析时间**: {report_data['generated_at']}
- **数据版本**: 最新可用数据

---

**生成系统**: 琥珀引擎青铜法典  
**执行引擎**: 工程师 Cheese  
**架构指导**: 首席架构师 Gemini (基于Gist_00127指令)  
**最终审批**: 主编 Haiyang  
**数据版本**: V2.0 (档案成果馆时代)  

**访问地址**: `https://localhost:10168/schedule/gist_report/insights/top_3_opportunity_dashboard.html`  
**详细数据**: `https://localhost:10168/schedule/gist_report/insights/detailed_alpha_analysis.json`  

**🏛️ 琥珀引擎 · 青铜法典 · Gist_00127号任务执行完成**
"""
        
        # 保存Markdown报告
        output_path = os.path.join(self.output_dir, 'REPORT_Gist_00127.md')
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(md_content)
        
        print(f"✅ Markdown报告已保存: {output_path}")

def main():
    """主函数"""
    analyzer = AlphaScanAnalyzer()
    all_results, alpha_opportunities = analyzer.run_analysis()
    
    print("\n" + "="*60)
    print("🎉 Gist_00127号任务执行完成!")
    print("="*60)
    print(f"📊 分析ETF总数: {len(all_results)}")
    print(f"🎯 发现Alpha机会: {len(alpha_opportunities)}")
    print(f"📁 输出目录: {analyzer.output_dir}")
    print(f"📄 生成文件:")
    print(f"   - top_3_opportunity_dashboard.json")
    print(f"   - top_3_opportunity_dashboard.html")
    print(f"   - detailed_alpha_analysis.json")
    print(f"   - REPORT_Gist_00127.md")
    print("="*60)

if __name__ == "__main__":
    main()