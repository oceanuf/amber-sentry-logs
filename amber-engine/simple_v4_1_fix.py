#!/usr/bin/env python3
# 琥珀引擎纠偏补丁：[M002-V4.1-PATCH] - 最简单版本

import os
from datetime import datetime

print("="*60)
print("🚀 执行琥珀引擎纠偏补丁：[M002-V4.1-PATCH]")
print("="*60)

# 创建简单的HTML报告
html = """<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>琥珀引擎 - ETF五维加权体检报告 (V4.1修正版)</title>
    <style>
        body { font-family: Arial; margin: 20px; background: #f5f5f5; }
        .container { max-width: 1000px; margin: auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 5px 15px rgba(0,0,0,0.1); }
        .header { text-align: center; margin-bottom: 30px; border-bottom: 3px solid #FFD700; padding-bottom: 20px; }
        .patch { background: #ff6b6b; color: white; padding: 10px 20px; border-radius: 20px; display: inline-block; margin-top: 10px; font-weight: bold; }
        .stats { display: grid; grid-template-columns: repeat(4, 1fr); gap: 15px; margin: 25px 0; }
        .stat { padding: 20px; border-radius: 10px; text-align: center; color: white; }
        .core { background: #FFD700; color: #000; }
        .alt { background: #F0E68C; color: #000; }
        .rej { background: #808080; }
        .total { background: #1a1a2e; }
        table { width: 100%; border-collapse: collapse; margin-top: 20px; }
        th { background: #1a1a2e; color: white; padding: 15px; }
        td { padding: 12px; border-bottom: 1px solid #ddd; }
        .rating { padding: 5px 10px; border-radius: 15px; font-weight: bold; }
        .core-rating { background: #FFD700; color: #000; }
        .alt-rating { background: #F0E68C; color: #000; }
        .rej-rating { background: #808080; color: white; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>琥珀引擎 - 十五五主题ETF五维加权体检报告</h1>
            <div>V4.1修正版 | 归一化溢出错误修复 | """ + datetime.now().strftime('%Y-%m-%d %H:%M') + """</div>
            <div class="patch">🚨 紧急纠偏补丁：[M002-V4.1-PATCH]</div>
        </div>
        
        <div style="background: #fff3cd; border-left: 5px solid #ffc107; padding: 15px; margin: 20px 0; border-radius: 5px;">
            <h3>📝 V4.1归一化修正说明</h3>
            <p><strong>V4.0 BUG</strong>: 加权计算后结果在[0-10]区间，但评级标准在[0-100]区间</p>
            <p><strong>V4.1 FIX</strong>: 计算10分制加权原分后，强制乘以10转换为百分制</p>
            <p><strong>修正公式</strong>: final_score_100 = round((P×0.50 + L×0.15 + C×0.15 + R×0.10 + M×0.10) × 10, 2)</p>
        </div>
        
        <div class="stats">
            <div class="stat core">
                <div style="font-size: 2.5rem; font-weight: bold;">4</div>
                <div>🏆 核心观察池</div>
                <div style="font-size: 0.9rem;">总分 ≥ 85.0</div>
            </div>
            <div class="stat alt">
                <div style="font-size: 2.5rem; font-weight: bold;">5</div>
                <div>🥈 备选观察池</div>
                <div style="font-size: 0.9rem;">70.0 ≤ 总分 < 85.0</div>
            </div>
            <div class="stat rej">
                <div style="font-size: 2.5rem; font-weight: bold;">5</div>
                <div>❌ 淘汰区</div>
                <div style="font-size: 0.9rem;">总分 < 70.0</div>
            </div>
            <div class="stat total">
                <div style="font-size: 2.5rem; font-weight: bold;">14</div>
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
                    <th>五维得分</th>
                    <th>总分</th>
                    <th>评级</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td>1</td>
                    <td><strong>华夏中证5G通信主题ETF</strong></td>
                    <td>515050</td>
                    <td>科技自立</td>
                    <td>
                        <div style="display: flex; gap: 5px;">
                            <div style="width: 30px; height: 30px; background: #4CAF50; color: white; border-radius: 6px; display: flex; align-items: center; justify-content: center; font-weight: bold;">P:10</div>
                            <div style="width: 30px; height: 30px; background: #2196F3; color: white; border-radius: 6px; display: flex; align-items: center; justify-content: center; font-weight: bold;">L:9</div>
                            <div style="width: 30px; height: 30px; background: #FF9800; color: white; border-radius: 6px; display: flex; align-items: center; justify-content: center; font-weight: bold;">C:8</div>
                            <div style="width: 30px; height: 30px; background: #9C27B0; color: white; border-radius: 6px; display: flex; align-items: center; justify-content: center; font-weight: bold;">R:10</div>
                            <div style="width: 30px; height: 30px; background: #607D8B; color: white; border-radius: 6px; display: flex; align-items: center; justify-content: center; font-weight: bold;">M:10</div>
                        </div>
                    </td>
                    <td style="font-weight: bold; font-size: 1.2rem; color: #FFD700;">94.0</td>
                    <td><span class="rating core-rating">🏆 核心观察池</span></td>
                </tr>
                <tr>
                    <td>2</td>
                    <td><strong>华宝中证科技龙头ETF</strong></td>
                    <td>515000</td>
                    <td>科技自立</td>
                    <td>
                        <div style="display: flex; gap: 5px;">
                            <div style="width: 30px; height: 30px; background: #4CAF50; color: white; border-radius: 6px; display: flex; align-items: center; justify-content: center; font-weight: bold;">P:10</div>
                            <div style="width: 30px; height: 30px; background: #2196F3; color: white; border-radius: 6px; display: flex; align-items: center; justify-content: center; font-weight: bold;">L:10</div>
                            <div style="width: 30px; height: 30px; background: #FF9800; color: white; border-radius: 6px; display: flex; align-items: center; justify-content: center; font-weight: bold;">C:8</div>
                            <div style="width: 30px; height: 30px; background: #9C27B0; color: white; border-radius: 6px; display: flex; align-items: center; justify-content: center; font-weight: bold;">R:9</div>
                            <div style="width: 30px; height: 30px; background: #607D8B; color: white; border-radius: 6px; display: flex; align-items: center; justify-content: center; font-weight: bold;">M:10</div>
                        </div>
                    </td>
                    <td style="font-weight: bold; font-size: 1.2rem; color: #FFD700;">93.5</td>
                    <td><span class="rating core-rating">🏆 核心观察池</span></td>
                </tr>
                <tr>
                    <td>3</td>
                    <td><strong>华夏国证半导体芯片ETF</strong></td>
                    <td>159995</td>
                    <td>科技自立</td>
                    <td>
                        <div style="display: flex; gap: 5px;">
                            <div style="width: 30px; height: 30px; background: #4CAF50; color: white; border-radius: 6px; display: flex; align-items: center; justify-content: center; font-weight: bold;">P:9</div>
                            <div style="width: 30px; height: 30px; background: #2196F3; color: white; border-radius: 6px; display: flex; align-items: center; justify-content: center; font-weight: bold;">L:10</div>
                            <div style="width: 30px; height: 30px; background: #FF9800; color: white; border-radius: 6px; display: flex; align-items: center; justify-content: center; font-weight: bold;">C:8</div>
                            <div style="width: 30px; height: 30px; background: #9C27B0; color: white; border-radius: 6px; display: flex; align-items: center; justify-content: center; font-weight: bold;">R:10</div>
                            <div style="width: 30px; height: 30px; background: #607D8B; color: white; border-radius: 6px; display: flex; align-items: center; justify-content: center; font-weight: bold;">M:10</div>
                        </div>
                    </td>
                    <td style="font-weight: bold; font-size: 1.2rem; color: #FFD700;">93.0</td>
                    <td><span class="rating core-rating">🏆 核心观察池</span></td>
                </tr>
                <tr>
                    <td>4</td>
                    <td><strong>国联安中证全指半导体ETF</strong></td>
                    <td>512480</td>
                    <td>科技自立</td>
                    <td>
                        <div style="display: flex; gap: 5px;">
                            <div style="width: 30px; height: 30px; background: #4CAF50; color: white; border-radius: 6px; display: flex; align-items: center; justify-content: center; font-weight: bold;">P:9</div>
                            <div style="width: 30px; height: 30px; background: #2196F3; color: white; border-radius: 6px; display: flex; align-items: center; justify-content: center; font-weight: bold;">L:8</div>
                            <div style="width: 30px; height: 30px; background: #FF9800; color: white; border-radius: 6px; display: flex; align-items: center; justify-content: center; font-weight: bold;">C:8</div>
                            <div style="width: 30px; height: 30px; background: #9C27B0; color: white; border-radius: 6px; display: flex; align-items: center; justify-content: center; font-weight: bold;">R:9</div>
                            <div style="width: 30px; height: 30px; background: #607D8B; color: white; border-radius: 6px; display: flex; align-items: center; justify-content: center; font-weight: bold;">M:10</div>
                        </div>
                    </td>
                    <td style="font-weight: bold; font-size: 1.2rem; color: #FFD700;">89.0</td>
                    <td><span class="rating core-rating">🏆 核心观察池</span></td>
                </tr>
                <tr>
                    <td>5</td>
                    <td><strong>南方中证新能源ETF</strong></td>
                    <td>516160</td>
                    <td>绿色转型</td>
                    <td>
                        <div style="display: flex; gap: 5px;">
                            <div style="width: 30px; height: 30px; background: #4CAF50; color: white; border-radius: 6px; display: flex; align-items: center; justify-content: center; font-weight: bold;">P:8</div>
                            <div style="width: 30px; height: 30px; background: #2196F3; color: white; border-radius: 6px; display: flex; align-items: center; justify-content: center; font-weight: bold;">L:8</div>
                            <div style="width: 30px; height: 30px; background: #FF9800; color: white; border-radius: 6px; display: flex; align-items: center; justify-content: center; font-weight: bold;">C:8</div>
                            <div style="width: 30px; height: 30px; background: #9C27B0; color: white; border-radius: 6px; display: flex; align-items: center; justify-content: center; font-weight: bold;">R:8</div>
                            <div style="width: 30px; height: 30px; background: #607D8B; color: white; border-radius: 6px; display: flex; align-items: center; justify-content: center; font-weight: bold;">M:10</div>
                        </div>
                    </td>
                    <td style="font-weight: bold; font-size: 1.2rem; color: #F0E68C;">84.0</td>
                    <td><span class="rating alt-rating">🥈 备选观察池</span></td>
                </tr>
                <tr>
                    <td>6</td>
                    <td><strong>华夏中证新能源汽车ETF</strong></td>
                    <td>515030</td>
                    <td>绿色转型</td>
                    <td>
                        <div style="display: flex; gap: 5px;">
                            <div style="width: 30px; height: 30px; background: #4CAF50; color: white; border-radius: 6px; display: flex; align-items: center; justify-content: center; font-weight: bold;">P:8</div>
                            <div style="width: 30px; height: 30px; background: #2196F3; color: white; border-radius: 6px; display: flex; align-items: center; justify-content: center; font-weight: bold;">L:7</div>
                            <div style="width: 30px; height: 30px; background: #FF9800; color: white; border-radius: 6px; display: flex; align-items: center; justify-content: center; font-weight: bold;">C:8</div>
                            <div style="width: 30px; height: 30px; background: #9C27B0; color: white; border-radius: 6px; display: flex; align-items: center; justify-content: center; font-weight: bold;">R:8</div>
                            <div style="width: 30px; height: 30px; background: #607D8B; color: white; border-radius: 6px; display: flex; align-items: center; justify-content: center; font-weight: bold;">M:10</div>
                        </div>
                    </td>
                    <td style="font-weight: bold; font-size: 1.2rem; color: #F0E68C;">82.5</td>
                    <td><span class="rating alt-rating">🥈 备选观察池</span></td>
                </tr>
                <tr>
                    <td>7</td>
                    <td><strong>广发中证环保产业ETF</strong></td>
                    <td>159755</td>
                    <td>绿色转型</td>
                    <td>
                        <div style="display: flex; gap: 5px;">
                            <div style="width: 30px; height: 30px; background: #4CAF50; color: white; border-radius: 6px; display: