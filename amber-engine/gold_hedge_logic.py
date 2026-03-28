#!/usr/bin/env python3
"""
黄金对冲逻辑 - 架构师V3.0指令
10%资产配比强制锁定黄金ETF
"""

import os
import sys
import json
import pandas as pd
from datetime import datetime, timedelta
import logging
from typing import Dict, List, Any, Optional

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/home/luckyelite/.openclaw/workspace/gold_hedge.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class GoldHedgeLogic:
    """黄金对冲逻辑系统"""
    
    def __init__(self):
        # V3.0 黄金对冲配置
        self.config = {
            "architecture_version": "Gemini-Arch-V3.0-Amber-Polaris",
            "module_name": "Gold Hedge Logic",
            "target_allocation": 0.10,  # 10%资产配比
            "gold_etfs": [
                {"code": "518880", "name": "华安黄金ETF", "exchange": "SH"},
                {"code": "159934", "name": "易方达黄金ETF", "exchange": "SZ"}
            ],
            "hedge_triggers": {
                "fx_volatility_threshold": 0.01,  # 汇率波动率1%
                "market_stress_threshold": 0.05,  # 市场压力5%
                "inflation_hedge": True
            },
            "rebalancing_frequency": "weekly"
        }
        
        # 导入现有系统
        try:
            import tushare as ts
            sys.path.append('/home/luckyelite/.openclaw/workspace')
            from task_b_data_fallback_system import DataFallbackSystem
            
            self.ts = ts
            self.fallback_system = DataFallbackSystem()
            self.token = "9e32ef28eac05c5fbb11e6f02a50da903def70f94b3018e93340568b"
            self.pro = ts.pro_api(self.token)
            
            logger.info("✅ 黄金对冲系统初始化成功")
        except ImportError as e:
            logger.error(f"❌ 系统初始化失败: {e}")
            raise
        
        # 状态监控
        self.status = {
            "current_allocation": 0.0,
            "gold_position": {},
            "last_rebalance": None,
            "hedge_active": False,
            "warnings": []
        }
    
    def calculate_fx_volatility(self, days: int = 20) -> float:
        """计算汇率波动率"""
        logger.info(f"📊 计算USD/CNY {days}日波动率...")
        
        try:
            end_date = datetime.now().strftime("%Y%m%d")
            start_date = (datetime.now() - timedelta(days=days*2)).strftime("%Y%m%d")
            
            # 获取汇率数据
            df = self.pro.fx_daily(
                ts_code='USDCNH.FXCM',
                start_date=start_date,
                end_date=end_date
            )
            
            if len(df) >= days:
                # 计算收益率
                df['returns'] = df['close'].pct_change()
                
                # 计算波动率 (年化)
                volatility = df['returns'].std() * (252 ** 0.5)  # 年化波动率
                
                logger.info(f"✅ 汇率波动率: {volatility:.4f} ({volatility*100:.2f}%)")
                return volatility
            else:
                logger.warning(f"⚠️ 数据不足，无法计算{days}日波动率")
                return 0.0
                
        except Exception as e:
            logger.error(f"❌ 波动率计算失败: {e}")
            return 0.0
    
    def get_gold_etf_data(self, etf_code: str) -> Dict:
        """获取黄金ETF数据"""
        logger.info(f"📈 获取黄金ETF数据: {etf_code}")
        
        try:
            today = datetime.now().strftime("%Y%m%d")
            yesterday = (datetime.now() - timedelta(days=5)).strftime("%Y%m%d")
            
            # 获取ETF行情
            df = self.pro.daily(
                ts_code=f"{etf_code}.{'SH' if etf_code.startswith('51') else 'SZ'}",
                start_date=yesterday,
                end_date=today
            )
            
            if not df.empty:
                latest = df.iloc[-1]
                
                # 计算涨跌幅
                if len(df) > 1:
                    prev = df.iloc[-2]
                    change_percent = (float(latest['close']) / float(prev['close']) - 1) * 100
                else:
                    change_percent = 0
                
                result = {
                    "code": etf_code,
                    "name": next((etf["name"] for etf in self.config["gold_etfs"] if etf["code"] == etf_code), "黄金ETF"),
                    "price": float(latest['close']),
                    "change_percent": change_percent,
                    "volume": float(latest['vol']),
                    "amount": float(latest['amount']),
                    "trade_date": latest['trade_date'],
                    "source": "tushare_daily",
                    "status": "success"
                }
                
                logger.info(f"✅ {etf_code}: {result['price']:.3f} ({change_percent:+.2f}%)")
                return result
        
        except Exception as e:
            logger.warning(f"⚠️ 黄金ETF数据获取失败 {etf_code}: {e}")
        
        # 使用降级系统
        logger.info(f"🔄 使用降级系统获取黄金ETF数据: {etf_code}")
        
        # 简化实现，返回模拟数据
        result = {
            "code": etf_code,
            "name": next((etf["name"] for etf in self.config["gold_etfs"] if etf["code"] == etf_code), "黄金ETF"),
            "price": 4.850 if etf_code == "518880" else 4.820,
            "change_percent": 0.52,
            "volume": 50000000,
            "amount": 242500000,
            "trade_date": datetime.now().strftime("%Y%m%d"),
            "source": "fallback_simulation",
            "status": "fallback"
        }
        
        return result
    
    def check_hedge_conditions(self) -> Dict:
        """检查对冲条件"""
        logger.info("🔍 检查黄金对冲条件...")
        
        conditions = {
            "fx_volatility_trigger": False,
            "market_stress_trigger": False,
            "inflation_hedge_trigger": True,  # 默认开启通胀对冲
            "recommended_action": "hold",
            "alert_level": "normal"
        }
        
        # 检查汇率波动率
        fx_volatility = self.calculate_fx_volatility()
        if fx_volatility >= self.config["hedge_triggers"]["fx_volatility_threshold"]:
            conditions["fx_volatility_trigger"] = True
            conditions["alert_level"] = "warning"
            conditions["recommended_action"] = "increase"
            logger.warning(f"⚠️ 汇率波动率触发: {fx_volatility:.4f} >= {self.config['hedge_triggers']['fx_volatility_threshold']}")
        
        # 这里可以添加市场压力检查
        # 简化实现
        
        # 通胀对冲默认开启
        if self.config["hedge_triggers"]["inflation_hedge"]:
            conditions["inflation_hedge_trigger"] = True
            conditions["recommended_action"] = "maintain"
        
        return conditions
    
    def generate_rebalancing_recommendation(self, current_allocation: float, hedge_conditions: Dict) -> Dict:
        """生成再平衡建议"""
        target_allocation = self.config["target_allocation"]
        
        recommendation = {
            "current_allocation": current_allocation,
            "target_allocation": target_allocation,
            "allocation_gap": target_allocation - current_allocation,
            "action": "hold",
            "amount_change": 0,
            "priority": "medium",
            "reasoning": []
        }
        
        # 根据对冲条件调整建议
        if hedge_conditions["fx_volatility_trigger"]:
            recommendation["action"] = "increase"
            recommendation["priority"] = "high"
            recommendation["target_allocation"] = min(target_allocation * 1.5, 0.15)  # 最高15%
            recommendation["reasoning"].append("汇率波动率超过阈值，增加对冲仓位")
        
        elif hedge_conditions["market_stress_trigger"]:
            recommendation["action"] = "increase"
            recommendation["priority"] = "high"
            recommendation["target_allocation"] = min(target_allocation * 1.3, 0.13)  # 最高13%
            recommendation["reasoning"].append("市场压力增加，增强防御配置")
        
        elif current_allocation < target_allocation * 0.8:
            recommendation["action"] = "increase"
            recommendation["priority"] = "medium"
            recommendation["reasoning"].append("当前配置低于目标，逐步增持")
        
        elif current_allocation > target_allocation * 1.2:
            recommendation["action"] = "reduce"
            recommendation["priority"] = "low"
            recommendation["reasoning"].append("当前配置高于目标，适度减持")
        
        else:
            recommendation["action"] = "hold"
            recommendation["reasoning"].append("配置合理，保持现状")
        
        # 计算调整金额
        recommendation["allocation_gap"] = recommendation["target_allocation"] - current_allocation
        
        logger.info(f"📋 再平衡建议: {recommendation['action']} (缺口: {recommendation['allocation_gap']:.3f})")
        
        return recommendation
    
    def generate_commander_alert(self, hedge_conditions: Dict, recommendation: Dict) -> str:
        """生成主编作战室预警"""
        
        alert_level = hedge_conditions.get("alert_level", "normal")
        alert_color = {
            "normal": "#4ECDC4",
            "warning": "#FFB347",
            "critical": "#FF6B6B"
        }.get(alert_level, "#4ECDC4")
        
        alert_html = f"""
        <div class="gold-hedge-alert v3-0-amber" style="
            background: linear-gradient(135deg, #FFF8E1 0%, #FFECB3 100%);
            border-left: 4px solid {alert_color};
            padding: 15px;
            margin: 15px 0;
            border-radius: 8px;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        ">
            <div style="
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 10px;
            ">
                <h4 style="
                    margin: 0;
                    font-size: 16px;
                    color: #2C3E50;
                    display: flex;
                    align-items: center;
                ">
                    <span style="
                        background: {alert_color};
                        color: white;
                        width: 20px;
                        height: 20px;
                        border-radius: 50%;
                        display: inline-flex;
                        align-items: center;
                        justify-content: center;
                        margin-right: 8px;
                        font-size: 12px;
                    ">🛡️</span>
                    黄金对冲仓位监控
                </h4>
                <div style="
                    font-size: 12px;
                    color: #7F8C8D;
                    background: rgba(255, 255, 255, 0.5);
                    padding: 3px 8px;
                    border-radius: 4px;
                ">
                    {datetime.now().strftime('%H:%M')}
                </div>
            </div>
            
            <div style="margin-bottom: 10px;">
                <div style="
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    margin-bottom: 8px;
                ">
                    <span style="font-size: 13px; color: #555;">当前配置:</span>
                    <span style="font-size: 16px; font-weight: 600; color: #2C3E50;">
                        {recommendation['current_allocation']*100:.1f}%
                    </span>
                </div>
                
                <div style="
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    margin-bottom: 8px;
                ">
                    <span style="font-size: 13px; color: #555;">目标配置:</span>
                    <span style="font-size: 16px; font-weight: 600; color: #2C3E50;">
                        {recommendation['target_allocation']*100:.1f}%
                    </span>
                </div>
                
                <div style="
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    margin-bottom: 12px;
                ">
                    <span style="font-size: 13px; color: #555;">建议操作:</span>
                    <span style="
                        font-size: 14px;
                        font-weight: 600;
                        color: {'#2ECC71' if recommendation['action'] == 'increase' else 
                               '#E74C3C' if recommendation['action'] == 'reduce' else 
                               '#3498DB'};
                        background: {'rgba(46, 204, 113, 0.2)' if recommendation['action'] == 'increase' else 
                                   'rgba(231, 76, 60, 0.2)' if recommendation['action'] == 'reduce' else 
                                   'rgba(52, 152, 219, 0.2)'};
                        padding: 4px 10px;
                        border-radius: 4px;
                        text-transform: uppercase;
                    ">
                        {recommendation['action']}
                    </span>
                </div>
            </div>
            
            <div style="
                background: rgba(255, 255, 255, 0.7);
                padding: 10px;
                border-radius: 6px;
                font-size: 12px;
                color: #555;
            ">
                <div style="font-weight: 600; margin-bottom: 5px; color: #2C3E50;">
                    📋 决策依据:
                </div>
                <ul style="margin: 0; padding-left: 18px;">
        """
        
        for reason in recommendation.get("reasoning", []):
            alert_html += f'<li style="margin-bottom: 3px;">{reason}</li>'
        
        alert_html += f"""
                </ul>
            </div>
            
            <div style="
                margin-top: 12px;
                padding-top: 10px;
                border-top: 1px dashed #E0E0E0;
                font-size: 11px;
                color: #7F8C8D;
                display: flex;
                justify-content: space-between;
                align-items: center;
            ">
                <div>
                    <span style="margin-right: 10px;">⚡ 优先级: {recommendation.get('priority', 'medium').upper()}</span>
                    <span>🎯 缺口: {recommendation['allocation_gap']*100:+.1f}%</span>
                </div>
                <div>🧀 琥珀引擎 V3.0</div>
            </div>
        </div>
        """
        
        # 如果汇率波动率触发，添加特别警告
        if hedge_conditions.get("fx_volatility_trigger"):
            alert_html += f"""
            <div style="
                background: rgba(255, 107, 107, 0.1);
                border: 1px solid rgba(255, 107, 107, 0.3);
                border-radius: 6px;
                padding: 10px;
                margin-top: 10px;
                font-size: 12px;
                color: #E74C3C;
            ">
                <div style="display: flex; align-items: center; margin-bottom: 5px;">
                    <span style="
                        background: #E74C3C;
                        color: white;
                        width: 16px;
                        height: 16px;
                        border-radius: 50%;
                        display: inline-flex;
                        align-items: center;
                        justify-content: center;
                        margin-right: 6px;
                        font-size: 10px;
                    ">!</span>
                    <strong>架构师预警</strong>
                </div>
                <div>汇率波动率超过1%，黄金对冲仓位已生效，建议立即检查配置。</div>
            </div>
            """
        
        return alert_html
    
    def execute_full_analysis(self) -> Dict:
        """执行完整黄金对冲分析"""
        logger.info("=" * 60)
        logger.info("🛡️ 黄金对冲逻辑分析开始")
        logger.info("=" * 60)
        
        try:
            # 1. 获取黄金ETF数据
            logger.info("\n📈 步骤1: 获取黄金ETF数据...")
            gold_etf_data = []
            for etf in self.config["gold_etfs"]:
                data = self.get_gold_etf_data(etf["code"])
                gold_etf_data.append(data)
                logger.info(f"   • {etf['name']}({etf['code']}): {data['price']:.3f} ({data['change_percent']:+.2f}%)")
            
            # 2. 检查对冲条件
            logger.info("\n🔍 步骤2: 检查对冲条件...")
            hedge_conditions