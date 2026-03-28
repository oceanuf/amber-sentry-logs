#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
琥珀引擎纠偏补丁：[M002-V4.1-PATCH] - 简化版
修正归一化溢出错误，对齐百分制评分逻辑
"""

import json
import numpy as np
from datetime import datetime
import os

print("="*60)
print("🚀 执行琥珀引擎纠偏补丁：[M002-V4.1-PATCH] - 简化版")
print("任务：修正归一化溢出错误，对齐百分制评分逻辑")
print("优先级：CRITICAL (紧急)")
print("执行者：工程师 Cheese")
print("="*60)

# 读取V4.0结果
v4_0_file = "etf_five_dimension_v4_0_results.json"
if not os.path.exists(v4_0_file):
    print(f"❌ 找不到V4.0结果文件: {v4_0_file}")
    exit(1)

with open(v4_0_file, 'r', encoding='utf-8') as f:
    v4_0_data = json.load(f)

print(f"✅ 加载V4.0结果: {len(v4_0_data.get('results', []))}只ETF")

# 修正逻辑
def fix_normalization_error(v4_0_results):
    """修正归一化溢出错误"""
    fixed_results = []
    
    for result in v4_0_results:
        # 提取10分制维度得分
        dimension_scores = result.get('dimension_scores', {})
        
        # V4.0错误逻辑: 直接加权求和 (0-10分)
        # V4.1修正逻辑: 加权求和后乘以10转换为百分制
        
        # 计算10分制加权原分
        weights = {
            "Performance": 0.50,
            "Liquidity": 0.15,
            "Cost": 0.15,
            "Correlation": 0.10,
            "Management": 0.10
        }
        
        raw_weighted_score = 0
        for dim, score in dimension_scores.items():
            weight = weights.get(dim, 0)
            raw_weighted_score += score * weight
        
        # V4.1关键修正：乘以10转换为百分制
        final_score_100 = round(raw_weighted_score * 10, 2)
        
        # 获取评级 (基于百分制)
        if final_score_100 >= 85.0:
            rating = "🏆 核心观察池"
            color = "#FFD700"
            color_name = "琥珀金"
        elif final_score_100 >= 70.0:
            rating = "🥈 备选观察池"
            color = "#F0E68C"
            color_name = "浅金"
        else:
            rating = "❌ 淘汰区"
            color = "#808080"
            color_name = "灰度"
        
        # 更新结果
        fixed_result = result.copy()
        fixed_result['total_score_100'] = final_score_100
        fixed_result['rating'] = rating
        fixed_result['color'] = color
        fixed_result['color_name'] = color_name
        fixed_result['patch_note'] = "V4.1归一化修正"
        
        fixed_results.append(fixed_result)
    
    return fixed_results

# 执行修正
v4_0_results = v4_0_data.get('results', [])
fixed_results = fix_normalization_error(v4_0_results)

# 统计
total_count = len(fixed_results)
core_count = len([r for r in fixed_results if r['total_score_100'] >= 85])
alternative_count = len([r for r in fixed_results if 70 <= r['total_score_100'] < 85])
rejected_count = len([r for r in fixed_results if r['total_score_100'] < 70])

print(f"\n📈 V4.1修正后统计结果:")
print(f"  分析ETF总数: {total_count}只")
print(f"  🏆 核心观察池: {core_count}只")
print(f"  🥈 备选观察池: {alternative_count}只")
print(f"  ❌ 淘汰区: {rejected_count}只")

# 显示Top 3
sorted_results = sorted(fixed_results, key=lambda x: x['total_score_100'], reverse=True)
print(f"\n🏆 Top 3 品种:")
for i, result in enumerate(sorted_results[:3], 1):
    etf_info = result.get('etf_info', {})
    print(f"  {i}. {etf_info.get('name', '未知')} ({etf_info.get('code', '未知')})")
    print(f"     主题: {etf_info.get('theme', '未知')} | 总分: {result['total_score_100']} | 评级: {result['rating']}")

# 验证华夏5G (515050)
for result in fixed_results:
    etf_info = result.get('etf_info', {})
    if etf_info.get('code') == "515050":
        score = result['total_score_100']
        print(f"\n🎯 华夏5G (515050) 验证:")
        print(f"  修正后得分: {score}")
        print(f"  预期范围: 94.0左右")
        print(f"  验证结果: {'✅ 通过' if 93 <= score <= 95 else '⚠️ 需检查'}")
        break

# 保存V4.1结果
v4_1_file = "etf_five_dimension_v4_1_results.json"
v4_1_data = {
    "analysis_time": datetime.now().isoformat(),
    "version": "V4.1-PATCH",
    "executor": "工程师 Cheese",
    "patch_note": "修正归一化溢出错误，对齐百分制评分逻辑",
    "correction_formula": "final_score_100 = round((S_D×0.50 + S_A×0.15 + S_C×0.15 + S_B×0.10 + S_E×0.10) × 10, 2)",
    "rating_system": {
        "琥珀金 (核心)": "总分 ≥ 85.0",
        "浅金 (备选)": "70.0 ≤ 总分 < 85.0",
        "灰度 (淘汰)": "总分 < 70.0"
    },
    "target_count": total_count,
    "summary": {
        "core_count": core_count,
        "alternative_count": alternative_count,
        "rejected_count": rejected_count
    },
    "results": fixed_results
}

with open(v4_1_file, 'w', encoding='utf-8') as f:
    json.dump(v4_1_data, f, ensure_ascii=False, indent=2)

print(f"\n✅ V4.1结果已保存到: {v4_1_file}")

# 生成简化的HTML报告
def generate_simple_html(fixed_results, output_path):
    """生成简化的HTML报告"""
    sorted_results = sorted(fixed_results, key=lambda x: x['total_score_100'], reverse=True)
    
    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>琥珀引擎 - ETF五维加权体检报告 (V4.1修正版)</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 5px 15px rgba(0,0,0,0.1); }}
        .header {{ text-align: center; margin-bottom: 30px; border-bottom: 3px solid #FFD700; padding-bottom: 20px; }}
        .patch-badge {{ background: #ff6b6b; color: white; padding: 10px 20px; border-radius: 20px; display: inline-block; margin-top: 10px; font-weight: bold; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
        th {{ background: #1a1a2e; color: white; padding: 15px; text-align: left; }}
        td {{ padding: 12px; border-bottom: 1px solid #ddd; }}
        tr:hover {{ background: #f9f9f9; }}
        .rating-core {{ background: #FFD700; color: #000; padding: 5px 10px; border-radius: 15px; font-weight: bold; }}
        .rating-alternative {{ background: #F0E68C; color: #000; padding: 5px 10px; border-radius: 15px; font-weight: bold; }}
        .rating-rejected {{ background: #808080; color: white; padding: 5px 10px; border-radius: 15px; font-weight: bold; }}
        .correction-note {{ background: #fff3cd; border-left: 5px solid #ffc107; padding: 15px; margin: 20px 0; border-radius: 5px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>琥珀引擎 - 十五五主题ETF五维加权体检报告</h1>
            <div class="subtitle">V4.1修正版 | 归一化溢出错误修复 | {datetime.now().strftime('%Y年%m月%d日 %H:%M')}</div>
            <div class="patch-badge">🚨 紧急纠偏补丁：[M002-V4.1-PATCH]</div>
        </div>
        
        <div class="correction-note">
            <h3>📝 V4.1归一化修正说明</h3>
            <p><strong>V4.0 BUG</strong>: 加权计算后结果在[0-10]区间，但评级标准在[0-100]区间，导致全员误判为"淘汰"</p>
            <p><strong>V4.1 FIX</strong>: 计算10分制加权原分后，强制乘以10转换为百分制</p>
            <p><strong>修正公式</strong>: final_score_100 = round((S_D×0.50 + S_A×0.15 + S_C×0.15 + S_B×0.10 + S_E×0.10) × 10, 2)</p>
        </div>
        
        <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px; margin: 30px 0;">
            <div style="text-align: center; padding: 20px; background: #FFD700; border-radius: 10px;">
                <div style="font-size: 2.5rem; font-weight: bold;">{core_count}</div>
                <div>🏆 核心观察池</div>
                <div style="font-size: 0.9rem;">总分 ≥ 85.0</div>
            </div>
            <div style="text-align: center; padding: 20px; background: #F0E68C; border-radius: 10px;">
                <div style="font-size: 2.5rem; font-weight: bold;">{alternative_count}</div>
                <div>🥈 备选观察池</div>
                <div style="font-size: 0.9rem;">70.0 ≤ 总分 < 85.0</div>
            </div>
            <div style="text-align: center; padding: 20px; background: #808080; color: white; border-radius: 10px;">
                <div style="font-size: 2.5rem; font-weight: bold;">{rejected_count}</div>
                <div>❌ 淘汰区</div>
                <div style="font-size: 0.9rem;">总分 < 70.0</div>
            </div>
            <div style="text-align: center; padding: 20px; background: #1a1a2e; color: white; border-radius: 10px;">
                <div style="font-size: 2.5rem; font-weight: bold;">{total_count}</div>
                <div>📊 分析总数</div>
                <div style="font-size: 0.9rem;">十五五主题ETF</div>
            </div>
        </div>
        
        <h2>📋 ETF五维加权体检表 (V4.1修正版)</h2>
        <table>
            <thead>
                <tr>
                    <th>排名</th>
                    <th>ETF名称</th>
                    <th>代码</th>
                    <th>主题</th>
                    <th>总分</th>
                    <th>评级</th>
                </tr>
            </thead>
            <tbody>
"""
    
    for i, result in enumerate(sorted_results, 1):
        etf_info = result.get('etf_info', {})
        rating_class = result['rating'].split()[0].replace('🏆', 'core').replace('🥈', 'alternative').replace('❌', 'rejected')
        
        html += f"""                <tr>
                    <td>{i}</td>
                    <td><strong>{etf_info.get('name', '未知')}</strong></td>
                    <td>{etf_info.get('code', '未知')}</td>
                    <td>{etf_info.get('theme', '未知')}</td>
                    <td style="font-weight: bold; color: {result['color']};">{result['total_score_100']}</td>
                    <td><span class="rating-{rating_class}">{result['rating']}</span></td>
                </tr>
"""
    
    html += f"""            </tbody>
        </table>
        
        <div style="margin-top: 40px; padding: 20px; background: #f8f9fa; border-radius: 10px;">
            <h3>📊 五维加权算法</h3>
            <div style="display: grid; grid-template-columns: repeat(5, 1fr); gap: 10px; margin-top: 15px;">
                <div style="text-align: center; padding: 15px; background: white; border-radius: 8px; border-top: 4px solid #FFD700;">
                    <div style="font-weight: bold;">表现</div>
                    <div style="font-size: 1.5rem; font-weight: bold;">50%</div>
                </div>
                <div style="text-align: center; padding: 15px; background: white; border-radius: 8px; border-top: 4px solid #2196F3;">
                    <div style="font-weight: bold;">流动性</div>
                    <div style="font-size: 1.5rem; font-weight: bold;">15%</div>
                </div>
                <div style="text-align: center; padding: 15px; background: white; border-radius: 8px; border-top: 4px solid #4CAF50;">
                    <div style="font-weight: bold;">费率</div>
                    <div style="font-size: 1.5rem; font-weight: bold;">15%</div>
                </div>
                <div style="text-align: center; padding: 15px; background: white; border-radius: 8px; border-top: 4px solid #FF9800;">
                    <div style="font-weight: bold;">相关性</div>
                    <div style="font-size: 1.5rem; font-weight: bold;">10%</div>
                </div>
                <div style="text-align: center; padding: 15px; background: white; border-radius: 8px; border-top: 4px solid #9C27B0;">
                    <div style="font-weight: bold;">管理</div>
                    <div style="font-size: 1.5rem; font-weight: bold;">10%</div>
                </div>
            </div>
        </div>
        
        <div style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #ddd; text-align: center; color: #666; font-size: 0.9rem;">
            <p>📅 报告生成时间: {datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}</p>
            <p>🏢 琥珀引擎团队 | 工程师: Cheese | 架构师: Gemini | 主编: Haiyang</p>
            <p>📊 数据源: AkShare (主要) + Tushare Pro (校准) | 基准锚点: 沪深300ETF (510300)</p>
            <p>⚠️ 风险提示: 本报告基于模拟数据，投资决策请结合实际情况</p>
        </div>
    </div>
</body>
</html>"""
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)
    
    return output_path

# 生成HTML报告
output_dir = "/home/luckyelite/.openclaw/workspace/amber-engine/output/etf/report"
os.makedirs(output_dir, exist_ok=True)
output_path = os.path.join(output_dir, "etf-health-check-v4.html")

html_path = generate_simple_html(fixed_results, output_path)
print(f"✅ HTML报告已保存到: {html_path}")
print(f"🌐 在线访问: https://amber.googlemanager.cn:10123/etf/report/etf-health-check-v4.html")

print("\n" + "="*60)
print("🎉 [M002-V4.1-PATCH] 归一化修正补丁执行完成!")
print("="*60)

print(f"\n🏢 团队协作:")
print(f"  主编掌舵: 等待验收V4.1修正结果")
print(f"  架构师谋略: 提供[M002-V4.1-PATCH]纠偏补丁")
print(f"  工程师实干: 完成归一化溢出错误修正")

print(f"\n🔧 关键修正验证:")
print(f"  ✅ 评分逻辑对齐: 10分制 → 百分制")
print(f"  ✅ 视觉系统重置: 琥珀金(≥85), 浅金(70-85), 灰度(<70)")
print(f"  ✅ 报告覆盖更新: HTML报告成功覆盖")

print(f"\n📄 交付物:")
print(f"  1. V4.1修正结果: {v4_1_file}")
print(f"  2. HTML报告: {html_path}")
print(f"  3. 在线访问: https://amber.googlemanager.cn:10123/etf/report/etf-health-check-v4.html")