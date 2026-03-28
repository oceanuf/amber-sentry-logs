#!/usr/bin/env python3
"""
琥珀全景(Amber-Pan)指数与热度系统
架构师最高指令: 全场景宏观温度计
"""

import os
import json
import random
from datetime import datetime, timedelta
import sqlite3

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
DB_PATH = os.path.join(BASE_DIR, "amber_cms.db")
INDEX_DATA_FILE = os.path.join(OUTPUT_DIR, "static/data/macro_index.json")

class AmberPanSystem:
    """琥珀全景指数与热度系统"""
    
    def __init__(self):
        self.indices = self.get_indices_config()
        self.heat_level = None
        self.market_sentiment = None
        
    def get_indices_config(self):
        """获取指数配置"""
        return {
            "A股": [
                {"code": "000300", "name": "沪深300", "symbol": "SH000300", "weight": 0.30},
                {"code": "399006", "name": "创业板指", "symbol": "SZ399006", "weight": 0.20}
            ],
            "港股": [
                {"code": "HSI", "name": "恒生指数", "symbol": "HKHSI", "weight": 0.15},
                {"code": "HSTECH", "name": "恒生科技", "symbol": "HKHSTECH", "weight": 0.15}
            ],
            "美股": [
                {"code": "NDX", "name": "纳斯达克100", "symbol": "NASDAQ:NDX", "weight": 0.10},
                {"code": "SPX", "name": "标普500", "symbol": "SPX", "weight": 0.10}
            ]
        }
    
    def generate_index_data(self):
        """生成指数数据（模拟Tushare接口）"""
        index_data = {}
        today = datetime.now().strftime("%Y-%m-%d")
        
        # 模拟A股数据
        for market in self.indices:
            for index in self.indices[market]:
                # 基础价格
                base_price = random.uniform(3000, 5000) if market == "A股" else random.uniform(15000, 35000)
                
                # 生成日线数据
                daily_data = []
                for days_ago in range(20, -1, -1):
                    date = (datetime.now() - timedelta(days=days_ago)).strftime("%Y-%m-%d")
                    
                    if days_ago == 0:  # 今日数据
                        pct_chg = random.uniform(-0.03, 0.03)
                        volume = random.uniform(100, 500)  # 亿元
                    else:  # 历史数据
                        pct_chg = random.uniform(-0.02, 0.02)
                        volume = random.uniform(80, 400)
                    
                    close = base_price * (1 + pct_chg)
                    
                    daily_data.append({
                        "trade_date": date,
                        "close": round(close, 2),
                        "pct_chg": round(pct_chg * 100, 2),
                        "volume": round(volume, 1),
                        "amount": round(volume * 1.2, 1)  # 模拟成交额
                    })
                
                index_data[index["code"]] = {
                    "name": index["name"],
                    "market": market,
                    "symbol": index["symbol"],
                    "weight": index["weight"],
                    "latest": daily_data[0],  # 最新数据
                    "history": daily_data[1:],  # 历史数据
                    "update_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
        
        return index_data
    
    def calculate_heat_level(self, index_data):
        """
        计算市场热度水平
        Heat_Level = (今日成交额 / 近20日均值) * 权重A + (上涨家数比例) * 权重B
        """
        
        # 权重配置
        weight_a = 0.6  # 成交额权重
        weight_b = 0.4  # 上涨家数权重
        
        total_turnover_ratio = 0
        up_count_ratio = 0
        total_weight = 0
        
        for index_code, data in index_data.items():
            latest = data["latest"]
            history = data["history"]
            
            # 计算近20日平均成交额
            avg_amount_20d = sum([d["amount"] for d in history]) / len(history)
            
            # 今日成交额与均值的比率
            if avg_amount_20d > 0:
                turnover_ratio = latest["amount"] / avg_amount_20d
            else:
                turnover_ratio = 1.0
            
            # 判断涨跌
            is_up = latest["pct_chg"] > 0
            
            total_turnover_ratio += turnover_ratio * data["weight"]
            up_count_ratio += (1 if is_up else 0) * data["weight"]
            total_weight += data["weight"]
        
        # 归一化
        if total_weight > 0:
            avg_turnover_ratio = total_turnover_ratio / total_weight
            avg_up_ratio = up_count_ratio / total_weight
        else:
            avg_turnover_ratio = 1.0
            avg_up_ratio = 0.5
        
        # 计算热度水平
        heat_level = (avg_turnover_ratio * weight_a) + (avg_up_ratio * weight_b)
        
        # 转换为百分比
        heat_level_percent = heat_level * 100
        
        return heat_level_percent
    
    def get_market_sentiment(self, heat_level):
        """获取市场情绪状态"""
        if heat_level < 40:
            return {
                "level": "冰点",
                "emoji": "🥶",
                "color": "ice",
                "description": "市场情绪低迷，成交清淡",
                "advice": "建议关注低位ETF，分批布局优质资产",
                "risk_level": "低风险"
            }
        elif heat_level < 75:
            return {
                "level": "温和",
                "emoji": "🌤️",
                "color": "normal",
                "description": "市场情绪平稳，正常波动",
                "advice": "保持现有持仓，关注结构性机会",
                "risk_level": "中风险"
            }
        elif heat_level < 85:
            return {
                "level": "活跃",
                "emoji": "☀️",
                "color": "active",
                "description": "市场情绪活跃，交投积极",
                "advice": "适度参与，注意风险控制",
                "risk_level": "中高风险"
            }
        else:  # >= 85
            return {
                "level": "沸腾",
                "emoji": "🔥",
                "color": "fire",
                "description": "市场情绪过热，警惕风险",
                "advice": "触发风险管控预警，建议减仓或观望",
                "risk_level": "高风险"
            }
    
    def generate_editor_comment(self, sentiment):
        """生成主编内参简评"""
        today = datetime.now().strftime("%Y年%m月%d日")
        
        comments = {
            "冰点": [
                f"{today}，市场情绪降至冰点🥶，成交清淡。此时正是价值投资者寻找黄金坑的良机。",
                f"冰点时刻，保持冷静。{today}市场交投清淡，建议关注被错杀的优质ETF。",
                f"🥶 市场冰点，耐心等待。{today}建议控制仓位，分批布局宽基指数。"
            ],
            "温和": [
                f"{today}，市场情绪温和🌤️，正常波动。建议保持现有持仓，关注结构性机会。",
                f"🌤️ 温和市道，{today}市场平稳运行。可适度调整持仓结构，优化资产配置。",
                f"市场情绪平稳，{today}建议关注行业轮动机会，保持均衡配置。"
            ],
            "活跃": [
                f"{today}，市场情绪活跃☀️，交投积极。可适度参与，但需注意风险控制。",
                f"☀️ 活跃市场，{today}机会与风险并存。建议精选个股，控制仓位。",
                f"市场交投活跃，{today}建议关注成长性较好的ETF，但需设置止盈止损。"
            ],
            "沸腾": [
                f"⚠️ 风险预警！{today}市场情绪沸腾🔥，警惕过热风险。建议减仓或观望。",
                f"🔥 市场沸腾，风险积聚。{today}强烈建议控制仓位，等待回调机会。",
                f"极度狂热！{today}市场情绪达到沸点🔥，触发风险管控预警，建议谨慎操作。"
            ]
        }
        
        # 随机选择一条评论
        import random
        return random.choice(comments[sentiment["level"]])
    
    def update_database(self, index_data, heat_level, sentiment):
        """更新数据库"""
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            
            # 创建表
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS macro_indices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                index_code TEXT NOT NULL,
                index_name TEXT NOT NULL,
                market TEXT,
                latest_close REAL,
                latest_pct_chg REAL,
                trade_date TEXT,
                update_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(index_code, trade_date)
            )
            ''')
            
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS market_sentiment (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                trade_date TEXT UNIQUE NOT NULL,
                heat_level REAL,
                sentiment_level TEXT,
                sentiment_emoji TEXT,
                editor_comment TEXT,
                update_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            ''')
            
            # 插入指数数据
            today = datetime.now().strftime("%Y-%m-%d")
            for index_code, data in index_data.items():
                cursor.execute('''
                INSERT OR REPLACE INTO macro_indices 
                (index_code, index_name, market, latest_close, latest_pct_chg, trade_date)
                VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    index_code,
                    data["name"],
                    data["market"],
                    data["latest"]["close"],
                    data["latest"]["pct_chg"],
                    today
                ))
            
            # 插入市场情绪数据
            editor_comment = self.generate_editor_comment(sentiment)
            
            cursor.execute('''
            INSERT OR REPLACE INTO market_sentiment 
            (trade_date, heat_level, sentiment_level, sentiment_emoji, editor_comment)
            VALUES (?, ?, ?, ?, ?)
            ''', (
                today,
                heat_level,
                sentiment["level"],
                sentiment["emoji"],
                editor_comment
            ))
            
            conn.commit()
            conn.close()
            
            print("✅ 数据库更新成功")
            
        except Exception as e:
            print(f"❌ 数据库更新失败: {e}")
    
    def generate_html_snippet(self, index_data, heat_level, sentiment):
        """生成HTML代码片段"""
        
        # 生成指数看板HTML
        indices_html = ""
        for market in self.indices:
            for index in self.indices[market]:
                data = index_data[index["code"]]
                latest = data["latest"]
                
                pct_class = "price-up" if latest["pct_chg"] > 0 else "price-down"
                pct_sign = "+" if latest["pct_chg"] > 0 else ""
                
                indices_html += f'''
                <div class="index-item">
                    <div class="index-header">
                        <span class="index-name">{index["name"]}</span>
                        <span class="index-market">{market}</span>
                    </div>
                    <div class="index-value">{latest["close"]:.2f}</div>
                    <div class="index-change {pct_class}">
                        {pct_sign}{latest["pct_chg"]:.2f}%
                    </div>
                </div>
                '''
        
        # 生成热度指示器HTML
        heat_width = min(100, max(0, heat_level))
        heat_color_class = f"heat-{sentiment['color']}"
        
        heat_html = f'''
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
            <div class="heat-description">{sentiment['description']}</div>
        </div>
        '''
        
        # 生成主编内参HTML
        editor_comment = self.generate_editor_comment(sentiment)
        alert_class = f"alert-{sentiment['color']}" if sentiment['color'] in ['ice', 'fire'] else ""
        
        editor_html = f'''
        <div class="editor-comment {alert_class}">
            <div class="comment-header">
                <span class="comment-icon">📝</span>
                <span class="comment-title">主编内参</span>
                <span class="comment-time">{datetime.now().strftime("%H:%M")}</span>
            </div>
            <div class="comment-content">{editor_comment}</div>
            <div class="comment-advice">
                <strong>操作建议:</strong> {sentiment['advice']}
                <span class="risk-level">风险等级: {sentiment['risk_level']}</span>
            </div>
        </div>
        '''
        
        # 完整的HTML片段
        html_snippet = f'''
        <!-- 琥珀全景指数看板 - 架构师指令 -->
        <div class="amber-pan-container">
            <div class="amber-pan-header">
                <h3>🌐 琥珀全景 - 全场景宏观温度计</h3>
                <span class="update-time">更新: {datetime.now().strftime("%Y-%m-%d %H:%M")} (北京时间)</span>
            </div>
            
            <div class="macro-board">
                <div class="indices-row">
                    {indices_html}
                </div>
                
                <div class="sentiment-row">
                    <div class="heat-container">
                        {heat_html}
                    </div>
                    
                    <div class="comment-container">
                        {editor_html}
                    </div>
                </div>
            </div>
        </div>
        '''
        
        return html_snippet
    
    def save_to_file(self, data):
        """保存数据到文件"""
        os.makedirs(os.path.dirname(INDEX_DATA_FILE), exist_ok=True)
        
        with open(INDEX_DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ 指数数据保存到: {INDEX_DATA_FILE}")
    
    def run(self):
        """运行主程序"""
        print("=" * 70)
        print("琥珀全景(Amber-Pan)指数与热度系统")
        print("=" * 70)
        
        try:
            # 1. 生成指数数据
            print("\n1. 📊 生成指数数据...")
            index_data = self.generate_index_data()
            
            # 2. 计算热度水平
            print("2. 🔥 计算市场热度...")
            heat_level = self.calculate_heat_level(index_data)
            
            # 3. 获取市场情绪
            print("3. 🎭 分析市场情绪...")
            sentiment = self.get_market_sentiment(heat_level)
            
            # 4. 生成HTML片段
            print("4. 🎨 生成HTML代码...")
            html_snippet = self.generate_html_snippet(index_data, heat_level, sentiment)
            
            # 5. 更新数据库
            print("5. 💾 更新数据库...")
            self.update_database(index_data, heat_level, sentiment)
            
            # 6. 保存数据
            print("6. 💿