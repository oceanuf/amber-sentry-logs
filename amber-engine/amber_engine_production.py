#!/usr/bin/env python3
"""
琥珀引擎实时生产任务 - 架构师投产指令
Ref: Gemini-Arch-V2.8-Live-Stream
执行时间: 立即
"""

import os
import sys
import json
import time
import pandas as pd
from datetime import datetime, timedelta
import logging
from typing import Dict, List, Any, Optional

# 添加当前目录到路径
sys.path.append('/home/luckyelite/.openclaw/workspace')

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/home/luckyelite/.openclaw/workspace/amber_engine.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class AmberEngineProduction:
    """琥珀引擎实时生产系统"""
    
    def __init__(self):
        # V2.8 生产配置
        self.config = {
            "architecture_version": "Gemini-Arch-V2.8-Live-Stream",
            "execution_mode": "real_time_production",
            "launch_time": datetime.now().isoformat(),
            "data_bridge": {
                "pe_window_years": 10,  # 架构师指令: 10年计算窗口
                "top_sectors_count": 3,
                "confidence_scoring": True
            },
            "visual_standards": {
                "primary_color": "#FFB347",  # 琥珀金
                "secondary_color": "#2C3E50",  # 深石墨灰
                "accent_color": "#FFA500",
                "chart_style": "v2_2_amber"
            },
            "wordpress_integration": {
                "section_name": "架构师内参",
                "auto_inject": True,
                "format": "html5_enhanced"
            }
        }
        
        # 导入任务A和任务B的系统
        try:
            from task_a_data_content_bridge import DataContentBridge
            from task_b_data_fallback_system import DataFallbackSystem
            
            self.data_bridge = DataContentBridge()
            self.fallback_system = DataFallbackSystem()
            
            logger.info("✅ 数据桥接与降级系统加载成功")
        except ImportError as e:
            logger.error(f"❌ 系统加载失败: {e}")
            raise
        
        # 生产状态
        self.production_status = {
            "start_time": datetime.now(),
            "steps_completed": [],
            "data_quality": {},
            "outputs_generated": []
        }
    
    def calculate_data_confidence(self, pe_data: Dict, data_points: int) -> float:
        """计算数据置信度评分"""
        base_score = 0.5  # 基础分
        
        # PE数据质量
        if pe_data.get("current_pe") is not None:
            base_score += 0.2
        
        if pe_data.get("percentile") is not None:
            base_score += 0.2
        
        # 数据点数量
        if data_points >= 2000:  # 10年数据约2500个交易日
            base_score += 0.1
        elif data_points >= 1000:
            base_score += 0.05
        
        # 限制在0-1之间
        confidence = min(max(base_score, 0), 1)
        
        # 转换为星级 (0-5星)
        stars = round(confidence * 5, 1)
        
        return {
            "score": confidence,
            "stars": stars,
            "rating": self._confidence_rating(confidence),
            "factors": {
                "pe_data_available": pe_data.get("current_pe") is not None,
                "percentile_available": pe_data.get("percentile") is not None,
                "data_points": data_points,
                "data_sufficiency": data_points >= 1000
            }
        }
    
    def _confidence_rating(self, score: float) -> str:
        """置信度评级"""
        if score >= 0.9:
            return "极高置信度"
        elif score >= 0.7:
            return "高置信度"
        elif score >= 0.5:
            return "中等置信度"
        elif score >= 0.3:
            return "较低置信度"
        else:
            return "低置信度"
    
    def generate_amber_chart(self, sector_data: pd.DataFrame, pe_data_list: List[Dict]) -> Dict:
        """生成琥珀金标准图表"""
        charts = []
        
        # 涨幅图表
        if not sector_data.empty:
            rising_chart = {
                "type": "vertical_bar",
                "title": "📈 当日涨幅领先板块",
                "data": [],
                "style": {
                    "color_scheme": "amber_gold_gradient",
                    "primary_color": self.config["visual_standards"]["primary_color"],
                    "background": "#FFFFFF",
                    "border_radius": "8px"
                }
            }
            
            for idx, row in sector_data.iterrows():
                color_intensity = 1.0 - (idx * 0.2)  # 递减颜色强度
                rising_chart["data"].append({
                    "label": row.get('name', row['ts_code']),
                    "value": float(row['pct_chg']),
                    "color": self.config["visual_standards"]["primary_color"],
                    "color_intensity": color_intensity,
                    "display_value": f"{row['pct_chg']:.2f}%"
                })
            
            charts.append(rising_chart)
        
        # PE分位点图表
        pe_chart_data = []
        for i, pe_data in enumerate(pe_data_list):
            if i < len(sector_data) and pe_data.get("percentile"):
                sector_name = sector_data.iloc[i].get('name', sector_data.iloc[i]['ts_code'])
                pe_chart_data.append({
                    "sector": sector_name,
                    "pe": pe_data.get("current_pe"),
                    "percentile": pe_data.get("percentile"),
                    "data_points": pe_data.get("data_points", 0)
                })
        
        if pe_chart_data:
            pe_chart = {
                "type": "radial_gauge",
                "title": "🎯 PE历史分位点 (10年窗口)",
                "data": pe_chart_data,
                "style": {
                    "color_scheme": "graphite_amber",
                    "primary_color": self.config["visual_standards"]["secondary_color"],
                    "accent_color": self.config["visual_standards"]["accent_color"],
                    "show_confidence": True
                }
            }
            charts.append(pe_chart)
        
        return {
            "charts": charts,
            "generated_at": datetime.now().isoformat(),
            "visual_version": "v2_2_amber",
            "compliance": "strict"
        }
    
    def generate_architect_insights(self, sector_data: pd.DataFrame, pe_data_list: List[Dict]) -> str:
        """生成架构师内参HTML内容"""
        if sector_data.empty:
            return "<p>⚠️ 今日板块数据暂不可用</p>"
        
        html_content = f"""
        <div class="architect-insights v2-8-amber" style="
            background: linear-gradient(135deg, #FFF8E1 0%, #FFECB3 100%);
            border-left: 4px solid {self.config['visual_standards']['primary_color']};
            padding: 20px;
            margin: 20px 0;
            border-radius: 8px;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        ">
            <h3 style="
                color: {self.config['visual_standards']['secondary_color']};
                margin-top: 0;
                font-size: 18px;
                font-weight: 600;
            ">
                🛡️ 架构师内参 | 估值支撑分析
            </h3>
        """
        
        # 添加板块分析
        html_content += """
            <div style="margin: 15px 0;">
                <h4 style="color: #555; font-size: 16px; margin-bottom: 10px;">
                    📊 今日涨幅前三板块估值分析
                </h4>
        """
        
        for i, (_, row) in enumerate(sector_data.iterrows()):
            pe_data = pe_data_list[i] if i < len(pe_data_list) else {}
            
            sector_name = row.get('name', row['ts_code'])
            change = row['pct_chg']
            
            # 置信度计算
            confidence = self.calculate_data_confidence(pe_data, pe_data.get("data_points", 0))
            
            html_content += f"""
                <div style="
                    background: white;
                    padding: 12px;
                    margin: 8px 0;
                    border-radius: 6px;
                    border: 1px solid #E0E0E0;
                ">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <strong style="color: {self.config['visual_standards']['secondary_color']};">
                                {sector_name}
                            </strong>
                            <span style="color: {'#4CAF50' if change > 0 else '#F44336'}; margin-left: 10px;">
                                {change:+.2f}%
                            </span>
                        </div>
                        <div style="
                            background: {self.config['visual_standards']['primary_color']}20;
                            color: {self.config['visual_standards']['primary_color']};
                            padding: 4px 8px;
                            border-radius: 4px;
                            font-size: 12px;
                            font-weight: 500;
                        ">
                            {'⭐' * int(confidence['stars'])}{'☆' * (5 - int(confidence['stars']))}
                        </div>
                    </div>
            """
            
            if pe_data.get("percentile"):
                percentile = pe_data["percentile"]
                current_pe = pe_data.get("current_pe", "N/A")
                
                # 估值判断
                if percentile < 30:
                    valuation_judgment = "🔵 处于历史低位，具备安全边际"
                    judgment_color = "#2196F3"
                elif percentile < 50:
                    valuation_judgment = "🟢 估值合理，具备投资价值"
                    judgment_color = "#4CAF50"
                elif percentile < 70:
                    valuation_judgment = "🟡 估值偏高，需谨慎对待"
                    judgment_color = "#FF9800"
                else:
                    valuation_judgment = "🔴 处于历史高位，注意风险"
                    judgment_color = "#F44336"
                
                html_content += f"""
                    <div style="margin-top: 8px; font-size: 13px; color: #666;">
                        <div>PE倍数: <strong>{current_pe:.2f}</strong></div>
                        <div>10年历史分位点: <strong>{percentile:.1f}%</strong></div>
                        <div style="color: {judgment_color}; margin-top: 4px;">
                            {valuation_judgment}
                        </div>
                    </div>
                """
            else:
                html_content += """
                    <div style="margin-top: 8px; font-size: 13px; color: #999;">
                        ⚠️ 估值数据暂不可用
                    </div>
                """
            
            html_content += "</div>"  # 结束板块div
        
        # 添加总结
        html_content += """
            </div>
            
            <div style="
                background: #F5F5F5;
                padding: 12px;
                border-radius: 6px;
                margin-top: 15px;
                font-size: 13px;
                color: #555;
            ">
                <div style="display: flex; align-items: center; margin-bottom: 5px;">
                    <span style="
                        background: #FFB347;
                        color: white;
                        width: 20px;
                        height: 20px;
                        border-radius: 50%;
                        display: inline-flex;
                        align-items: center;
                        justify-content: center;
                        margin-right: 8px;
                        font-size: 12px;
                    ">i</span>
                    <strong>数据说明</strong>
                </div>
                <ul style="margin: 5px 0 0 20px; padding: 0;">
                    <li>PE历史分位点基于10年窗口计算</li>
                    <li>置信度评分综合考虑数据完整性与质量</li>
                    <li>分析仅供参考，不构成投资建议</li>
                </ul>
            </div>
            
            <div style="
                margin-top: 15px;
                padding-top: 10px;
                border-top: 1px dashed #E0E0E0;
                font-size: 11px;
                color: #888;
                text-align: right;
            ">
                🧀 琥珀引擎 v2.8 | 生成时间: """ + datetime.now().strftime("%Y-%m-%d %H:%M") + """
            </div>
        </div>
        """
        
        return html_content
    
    def execute_production_pipeline(self):
        """执行实时生产管道"""
        logger.info("=" * 60)
        logger.info("🚀 琥珀引擎实时生产管道启动")
        logger.info("=" * 60)
        logger.info(f"架构版本: {self.config['architecture_version']}")
        logger.info(f"执行模式: {self.config['execution_mode']}")
        logger.info(f"启动时间: {self.config['launch_time']}")
        logger.info("=" * 60)
        
        try:
            # 步骤1: 获取当日涨幅前三板块
            logger.info("\n📡 步骤1: 激活数据桥接器...")
            today = datetime.now().strftime("%Y%m%d")
            top_sectors = self.data_bridge.get_top_rising_sectors(today)
            
            if top_sectors.empty:
                logger.warning("⚠️ 未获取到板块数据，尝试使用降级系统")
                # 使用降级系统获取数据
                top_sectors, source = self.fallback_system.get_data_with_fallback(
                    "sw_daily", 
                    trade_date=today
                )
                logger.info(f"使用降级数据源: {source}")
            
            if top_sectors.empty:
                raise Exception("无法获取板块数据，生产管道终止")
            
            logger.info(f"✅ 获取到{len(top_sectors)}个涨幅领先板块")
            for _, row in top_sectors.iterrows():
                logger.info(f"   • {row.get('name', row['ts_code'])}: {row['pct_chg']:.2f}%")
            
            self.production_status["steps_completed"].append("data_bridge_activated")
            
            # 步骤2: 提取PE倍数与10年历史位置
            logger.info("\n📊 步骤2: 数据萃取 - PE倍数与10年历史位置...")
            pe_data_list = []
            for _, row in top_sectors.iterrows():
                sector_code = row['ts_code']
                pe_data = self.data_bridge.get_sector_pe_percentile(
                    sector_code, 
                    lookback_days=3650  # 10年
                )
                pe_data_list.append(pe_data)
                
                if pe_data.get("percentile"):
                    logger.info(f"   • {row.get('name', sector_code)}: PE={pe_data['current_pe']:.2f}, 10年分位点={pe_data['percentile']:.1f}%")
                else:
                    logger.warning(f"   ⚠️  {row.get('name', sector_code)}: PE数据不可用")
            
            self.production_status["steps_completed"].append("pe_analysis_completed")
            
            # 步骤3: 生成琥珀金标准图表
            logger.info("\n🎨 步骤3: 视觉渲染 - 琥珀金标准图表...")
            amber_charts = self.generate_amber_chart(top_sectors, pe_data_list)
            
            # 计算总体置信度
            overall_confidence = 0
            confidence_count = 0
            for pe_data in pe_data_list:
                confidence = self.calculate_data_confidence(pe_data, pe_data.get("data_points", 0))
                overall_confidence += confidence["score"]
                confidence_count += 1
            
            if confidence_count > 0:
                overall_confidence /= confidence_count
            
            logger.info(f"✅ 图表生成完成: {len(amber_charts['charts'])}个图表")
            logger.info(f"📈 总体数据置信度: {overall_confidence:.2f} ({self._confidence_rating(overall_confidence)})")
            
            self.production_status["steps_completed"].append("visual_rendering_completed")
            self.production_status["data_quality"]["overall_confidence"] = overall_confidence
            
            # 步骤4: 生成架构师内参内容
            logger.info("\n📝 步骤4: 生成架构师内参区块...")
            architect_insights = self.generate_architect_insights(top_sectors, pe_data_list)
            
            # 保存内容到文件
            insights_file = f"/home/luckyelite/.openclaw/workspace/architect_insights_{today}.html"
            with open(insights_file, 'w', encoding='utf-8') as f:
                f.write(architect_insights)
            
            logger.info(f"✅ 内参内容已生成: {insights_file}")
            self.production_status["steps_completed"].append("architect_insights_generated")
            self.production_status["outputs_generated"].append(insights_file)
            
            # 步骤5: 生成完整生产报告
            logger.info("\n📋 步骤5: 生成生产报告...")
            production_report = {
                "production_run": {
                    "architecture_version": self.config["architecture_version