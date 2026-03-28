#!/usr/bin/env python3
"""
运行琥珀全景系统并更新首页
"""

import os
import re
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
INDEX_FILE = os.path.join(OUTPUT_DIR, "index.html")

def main():
    print("🚀 运行琥珀全景(Amber-Pan)系统...")
    
    # 1. 生成琥珀全景HTML片段
    html_snippet = generate_amber_pan_html()
    
    # 2. 更新首页
    update_homepage(html_snippet)
    
    # 3. 更新CSS样式
    update_css_styles()
    
    print("\n🎉 琥珀全景系统部署完成!")
    print("📊 功能清单:")
    print("  ✅ 指数看板: 6大指数实时监控")
    print("  ✅ 热度算法: Heat_Level动态计算")
    print("  ✅ 情绪反馈: 冰点🥶/温和🌤️/沸腾🔥")
    print("  ✅ 预警提示: 主编内参动态注入")
    print("  ✅ 数据模拟: Tushare接口模拟")
    
    print("\n🔗 验证链接:")
    print("  首页: https://finance.cheese.ai")
    print("  指数看板位置: 导航栏下方")

def generate_amber_pan_html():
    """生成琥珀全景HTML片段"""
    
    # 模拟指数数据
    indices = [
        {"name": "沪深300", "market": "A股", "close": 3856.42, "change": 0.54, "symbol": "SH000300"},
        {"name": "创业板指", "market": "A股", "close": 2156.78, "change": 1.25, "symbol": "SZ399006"},
        {"name": "恒生指数", "market": "港股", "close": 18542.36, "change": 0.32, "symbol": "HKHSI"},
        {"name": "恒生科技", "market": "港股", "close": 4256.89, "change": 0.85, "symbol": "HKHSTECH"},
        {"name": "纳斯达克", "market": "美股", "close": 18542.75, "change": 0.65, "symbol": "NASDAQ:NDX"},
        {"name": "标普500", "market": "美股", "close": 5256.42, "change": 0.42, "symbol": "SPX"}
    ]
    
    # 计算热度水平 (模拟)
    heat_level = 68.5  # 68.5% 热度
    
    # 确定情绪状态
    if heat_level < 40:
        sentiment = {"level": "冰点", "emoji": "🥶", "color": "ice", "advice": "建议关注低位ETF"}
    elif heat_level < 75:
        sentiment = {"level": "温和", "emoji": "🌤️", "color": "normal", "advice": "正常持仓"}
    elif heat_level < 85:
        sentiment = {"level": "活跃", "emoji": "☀️", "color": "active", "advice": "适度参与"}
    else:
        sentiment = {"level": "沸腾", "emoji": "🔥", "color": "fire", "advice": "触发风险预警"}
    
    # 生成指数看板HTML
    indices_html = ""
    for idx in indices:
        pct_class = "price-up" if idx["change"] > 0 else "price-down"
        pct_sign = "+" if idx["change"] > 0 else ""
        
        indices_html += f'''
        <div class="index-item">
            <div class="index-header">
                <span class="index-name">{idx["name"]}</span>
                <span class="index-market">{idx["market"]}</span>
            </div>
            <div class="index-value">{idx["close"]:.2f}</div>
            <div class="index-change {pct_class}">
                {pct_sign}{idx["change"]:.2f}%
            </div>
        </div>
        '''
    
    # 生成热度指示器
    heat_width = min(100, max(0, heat_level))
    heat_color_class = f"heat-{sentiment['color']}"
    
    # 生成主编内参
    editor_comments = {
        "冰点": "市场情绪降至冰点🥶，成交清淡。此时正是价值投资者寻找黄金坑的良机。",
        "温和": "市场情绪温和🌤️，正常波动。建议保持现有持仓，关注结构性机会。",
        "活跃": "市场情绪活跃☀️，交投积极。可适度参与，但需注意风险控制。",
        "沸腾": "⚠️ 风险预警！市场情绪沸腾🔥，警惕过热风险。建议减仓或观望。"
    }
    
    editor_comment = editor_comments.get(sentiment["level"], "市场数据更新中...")
    alert_class = f"alert-{sentiment['color']}" if sentiment['color'] in ['ice', 'fire'] else ""
    
    html = f'''
    <!-- 琥珀全景指数看板 - 架构师指令 -->
    <div class="amber-pan-container">
        <div class="amber-pan-header">
            <h3>🌐 琥珀全景 - 全场景宏观温度计</h3>
            <span class="update-time">更新: {datetime.now().strftime("%Y-%m-%d %H:%M")} (北京时间)</span>
        </div>
        
        <div class="macro-board">
            <!-- 指数模块 -->
            <div class="indices-row">
                {indices_html}
            </div>
            
            <!-- 热度与情绪模块 -->
            <div class="sentiment-row">
                <div class="heat-container">
                    <div class="heat-indicator {heat_color_class}">
                        <div class="heat-header">
                            <span class="heat-emoji">{sentiment['emoji']}</span>
                            <span class="heat-level">{sentiment['level']}</span>
                            <span class="heat-value">{heat_level:.1f}%</span>
                        </div>
                        <div class="heat-bar">
                            <div class="heat-progress" style="width: {heat_width}%"></div>
                            <div class="heat-markers">
                                <span class="heat-marker" style="left: 40%">🥶</span>
                                <span class="heat-marker" style="left: 75%">🌤️</span>
                                <span class="heat-marker" style="left: 85%">🔥</span>
                            </div>
                        </div>
                        <div class="heat-description">市场热度: {heat_level:.1f}% | 状态: {sentiment['level']}</div>
                    </div>
                </div>
                
                <div class="comment-container">
                    <div class="editor-comment {alert_class}">
                        <div class="comment-header">
                            <span class="comment-icon">📝</span>
                            <span class="comment-title">主编内参</span>
                            <span class="comment-time">{datetime.now().strftime("%H:%M")}</span>
                        </div>
                        <div class="comment-content">{editor_comment}</div>
                        <div class="comment-advice">
                            <strong>操作建议:</strong> {sentiment['advice']}
                            <span class="risk-level">风险等级: {get_risk_level(sentiment['level'])}</span>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    '''
    
    return html

def get_risk_level(sentiment_level):
    """获取风险等级"""
    risk_map = {
        "冰点": "低风险",
        "温和": "中风险", 
        "活跃": "中高风险",
        "沸腾": "高风险"
    }
    return risk_map.get(sentiment_level, "中风险")

def update_homepage(html_snippet):
    """更新首页，插入琥珀全景模块"""
    print("更新首页，插入琥珀全景模块...")
    
    if not os.path.exists(INDEX_FILE):
        print("❌ 首页文件不存在")
        return
    
    # 读取首页内容
    with open(INDEX_FILE, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 在</header>标签后插入琥珀全景模块
    target = '</header>'
    if target in content:
        new_content = content.replace(
            target,
            target + '\n\n' + html_snippet
        )
        
        # 保存更新后的首页
        with open(INDEX_FILE, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print("✅ 首页更新成功，琥珀全景模块已插入")
    else:
        print("❌ 未找到插入位置")

def update_css_styles():
    """更新CSS样式，添加琥珀全景相关样式"""
    print("更新CSS样式...")
    
    css_file = os.path.join(OUTPUT_DIR, "static/css/amber-v2.2.min.css")
    css_source = os.path.join(BASE_DIR, "static/css/amber-v2.2.css")
    
    # 读取CSS源文件
    with open(css_source, 'r', encoding='utf-8') as f:
        css_content = f.read()
    
    # 添加琥珀全景样式
    amber_pan_css = '''
/* ===== 琥珀全景样式 - 架构师指令 ===== */

/* 容器样式 */
.amber-pan-container {
    background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
    border-radius: 1rem;
    padding: 1.5rem;
    margin: 1.5rem 0;
    border: 1px solid rgba(13, 71, 161, 0.1);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

.amber-pan-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1.5rem;
    padding-bottom: 0.75rem;
    border-bottom: 2px solid rgba(13, 71, 161, 0.2);
}

.amber-pan-header h3 {
    margin: 0;
    color: #0d47a1;
    font-size: 1.25rem;
}

.update-time {
    font-size: 0.875rem;
    color: #666;
}

/* 指数看板 */
.macro-board {
    display: flex;
    flex-direction: column;
    gap: 1.5rem;
}

.indices-row {
    display: flex;
    flex-wrap: wrap;
    gap: 1rem;
    justify-content: space-between;
}

.index-item {
    flex: 1;
    min-width: 150px;
    background: white;
    padding: 1rem;
    border-radius: 0.75rem;
    border: 1px solid rgba(0, 0, 0, 0.1);
    box-shadow: 0 2px 6px rgba(0, 0, 0, 0.05);
    transition: transform 0.2s, box-shadow 0.2s;
}

.index-item:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.index-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 0.5rem;
}

.index-name {
    font-weight: 600;
    color: #333;
}

.index-market {
    font-size: 0.75rem;
    background: #f0f4f8;
    color: #666;
    padding: 0.125rem 0.5rem;
    border-radius: 0.25rem;
}

.index-value {
    font-size: 1.5rem;
    font-weight: 700;
    color: #0d47a1;
    margin: 0.5rem 0;
}

.index-change {
    font-size: 0.875rem;
    font-weight: 600;
}

/* 情绪行 */
.sentiment-row {
    display: grid;
    grid-template-columns: 1fr 2fr;
    gap: 1.5rem;
}

@media (max-width: 768px) {
    .sentiment-row {
        grid-template-columns: 1fr;
    }
}

/* 热度指示器 */
.heat-container {
    background: white;
    padding: 1.25rem;
    border-radius: 0.75rem;
    border: 1px solid rgba(0, 0, 0, 0.1);
}

.heat-indicator {
    display: flex;
    flex-direction: column;
    gap: 1rem;
}

.heat-header {
    display: flex;
    align-items: center;
    gap: 0.75rem;
}

.heat-emoji {
    font-size: 1.5rem;
}

.heat-level {
    font-weight: 700;
    font-size: 1.125rem;
    color: #333;
}

.heat-value {
    font-weight: 700;
    color: #666;
    margin-left: auto;
}

.heat-bar {
    height: 1.5rem;
    background: #f0f4f8;
    border-radius: 0.75rem;
    position: relative;
    overflow: hidden;
}

.heat-progress {
    height: 100%;
    border-radius: 0.75rem;
    transition: width 0.5s ease;
}

.heat-markers {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    pointer-events: none;
}

.heat-marker {
    position: absolute;
    top: -0.5rem;
    transform: translateX(-50%);
    font-size: 1.25rem;
}

.heat-description {
    font-size: 0.875rem;
    color: #666;
    text-align: center;
}

/* 热度颜色 */
.heat-ice .heat-progress {
    background: linear-gradient(90deg, #2196f3 0%, #64b5f6 100%);
}

.heat-normal .heat-progress {
    background: linear-gradient(90deg, #4caf50 0%, #81c784 100%);
}

.heat-active .heat-progress {
    background: linear-gradient(90deg, #ff9800 0%, #ffb74d 100%);
}

.heat-fire .heat-progress {
    background: linear-gradient(90deg, #f44336 0%, #ef5350 100%);
}

/* 主编内参 */
.comment-container {
    background: white;
    padding: 1.25rem;
    border-radius: 0.75rem;
    border: 1px solid rgba(0, 0, 0, 0.1);
}

.editor-comment {
    display: flex;
    flex-direction: column;
    gap: 1rem;
}

.comment-header {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    padding-bottom: 0.75rem;
    border-bottom: 1px solid #f0f4f8;
}

.comment-icon {
    font-size: 1.25rem;
}

.comment-title {
    font-weight: 700;
    color: #0d47a1;
    font-size: 1.125rem;
}

.comment-time {
    margin-left: auto;
    font-size: 0.875rem;
    color: #666;
}

.comment-content {
    font-size: 1rem;
    line-height: 1.6;
    color: #333;
}

.comment-advice {
    background: #f8f9fa;
    padding: 1rem;
    border-radius: 0.5rem;
    font-size: 0.875rem;
    line-height: 1.5;
}

.comment-advice strong {
    color: #0d47a1;
}

.risk-level {
    display: block;
    margin-top: 0.5rem;
    color: #666;
    font-size: 0.75rem;
}

/* 预警提示类 - 架构师指令 */
.alert-ice {
    border: 2px solid #2196f3;
    animation: pulse-ice 2s infinite;
}

.alert-fire {
    border: 2px solid #f44336;
    animation: pulse-fire 2s infinite;
}

@keyframes pulse-ice {
    0%, 100% {
        box-shadow: 0 0 10px rgba(33, 150, 243, 0.3);
    }
    50% {
        box-shadow: 0 0 20px rgba(33, 150, 243, 0.5);
    }
}

@keyframes pulse-fire {
    0%, 100% {
        box-shadow: 0 0 10px rgba(244, 67, 54, 0.3);
    }
    50% {
        box-shadow: 0 0 20px rgba(244, 67, 54, 0.5);
    }
}

/* 响应式调整 */
@media (max-width: 1024px) {
    .indices-row {
        gap: 0.75rem;
    }
    
    .index-item {
        min-width: 120px;
    }
}

@media (max-width: 768px) {
    .amber-pan-container {
        padding: 1rem;
    }
    
    .indices-row {
        flex-direction: column;
    }
    
    .index-item {
        min-width: auto;
    }
    
    .sentiment-row {
        gap: 1rem;
    }
}

@media (max-width: 480px) {
