#!/usr/bin/env python3
"""
琥珀引擎 - 长周期量化策略库 (Strategy Pool)
功能: 封装10大量化交易公式，支持N=60天持有期胜率优化
版本: V1.0.0 (2613-173号指令)
创建时间: 2026-03-27 20:55
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple, Union
import math

class StrategyLibrary:
    """
    长周期量化策略库
    核心使命: 捕获季级均值回归，实现长胜不败
    持有期N值: 统一设定为60天 (主攻方向)
    """
    
    def __init__(self):
        """初始化策略库"""
        self.strategy_names = {
            1: "引力超跌模型 (Gravity-Dip)",
            2: "双重动能过滤 (Dual Momentum)",
            3: "波动率压缩捕捉 (Volatility Squeeze)",
            4: "股息率价值模型 (Dividend Alpha)",
            5: "RSI周线极值 (Weekly RSI)",
            6: "统计学Z-Score偏离 (Z-Score Bias)",
            7: "三重均线共振 (Triple Cross)",
            8: "缩量回踩支撑 (Low Volume Retrace)",
            9: "宏观对冲锚点 (Macro-Anchor)",
            10: "能量潮背离 (OBV Divergence)"
        }
        
        # N值胜率对齐参数
        self.n_days = 60  # 主攻方向
        self.win_rate_targets = {30: 0.65, 60: 0.78, 90: 0.85}
    
    # ==================== 1. 引力超跌模型 (Gravity-Dip) ====================
    def gravity_dip_score(self, 
                         current_price: float,
                         ma_200: float,
                         atr_14: float) -> float:
        """
        公式: Score = (MA_200 - Price) / ATR(14)
        核心: 猎杀偏离200日线极值的"橡皮筋"效应
        """
        if atr_14 <= 0:
            return 0.0
        
        score = (ma_200 - current_price) / atr_14
        return round(score, 4)
    
    def gravity_dip_signal(self,
                          score: float,
                          threshold: float = 2.0) -> Dict:
        """
        生成引力超跌信号
        threshold: 分数阈值，默认2.0表示2倍ATR偏离
        """
        signal = {
            "strategy_id": 1,
            "strategy_name": self.strategy_names[1],
            "score": score,
            "threshold": threshold,
            "signal": "BUY" if score >= threshold else "HOLD",
            "confidence": min(score / threshold, 1.0) if score >= threshold else 0.0,
            "reasoning": f"价格偏离200日均线{score:.2f}倍ATR，触发橡皮筋效应" if score >= threshold else "偏离不足"
        }
        return signal
    
    # ==================== 2. 双重动能过滤 (Dual Momentum) ====================
    def dual_momentum_check(self,
                           current_price: float,
                           ma_200: float,
                           price_90d_ago: float) -> Dict:
        """
        公式: (Price > MA_200) ∩ (Price > Price_90d_ago)
        核心: 仅在绝对动能与相对动能均为正时持仓
        """
        absolute_momentum = current_price > ma_200
        relative_momentum = current_price > price_90d_ago
        
        signal = {
            "strategy_id": 2,
            "strategy_name": self.strategy_names[2],
            "absolute_momentum": absolute_momentum,
            "relative_momentum": relative_momentum,
            "signal": "BUY" if (absolute_momentum and relative_momentum) else "HOLD",
            "confidence": 0.8 if (absolute_momentum and relative_momentum) else 0.0,
            "reasoning": "绝对动能与相对动能双重确认，趋势健康" if (absolute_momentum and relative_momentum) else "动能不足"
        }
        return signal
    
    # ==================== 3. 波动率压缩捕捉 (Volatility Squeeze) ====================
    def volatility_squeeze_score(self,
                                upper_bb: float,
                                lower_bb: float,
                                ma_20: float,
                                threshold: float = 0.1) -> Dict:
        """
        公式: (UpperBB - LowerBB) / MA_20 < Threshold
        核心: 寻找横盘30天以上的"火山喷发"前兆
        """
        if ma_20 <= 0:
            return {
                "strategy_id": 3,
                "strategy_name": self.strategy_names[3],
                "score": 0.0,
                "threshold": threshold,
                "signal": "HOLD",
                "confidence": 0.0,
                "reasoning": "MA20无效"
            }
        
        squeeze_ratio = (upper_bb - lower_bb) / ma_20
        is_squeeze = squeeze_ratio < threshold
        
        signal = {
            "strategy_id": 3,
            "strategy_name": self.strategy_names[3],
            "squeeze_ratio": round(squeeze_ratio, 4),
            "threshold": threshold,
            "signal": "BUY" if is_squeeze else "HOLD",
            "confidence": (threshold - squeeze_ratio) / threshold if is_squeeze else 0.0,
            "reasoning": f"波动率压缩至{squeeze_ratio:.4f}，低于阈值{threshold}" if is_squeeze else "波动率正常"
        }
        return signal
    
    # ==================== 4. 股息率价值模型 (Dividend Alpha) ====================
    def dividend_alpha_score(self,
                           dividend: float,
                           price: float,
                           risk_free_rate: float = 0.02) -> Dict:
        """
        公式: (Dividend / Price) - RiskFreeRate
        核心: 针对高股息ETF，建立长线收息保护垫
        """
        if price <= 0:
            return {
                "strategy_id": 4,
                "strategy_name": self.strategy_names[4],
                "score": 0.0,
                "signal": "HOLD",
                "confidence": 0.0,
                "reasoning": "价格无效"
            }
        
        dividend_yield = dividend / price
        alpha = dividend_yield - risk_free_rate
        
        signal = {
            "strategy_id": 4,
            "strategy_name": self.strategy_names[4],
            "dividend_yield": round(dividend_yield, 4),
            "risk_free_rate": risk_free_rate,
            "alpha": round(alpha, 4),
            "signal": "BUY" if alpha > 0 else "HOLD",
            "confidence": min(alpha / risk_free_rate, 1.0) if alpha > 0 else 0.0,
            "reasoning": f"股息率超越无风险利率{alpha:.4f}" if alpha > 0 else "股息率不足"
        }
        return signal
    
    # ==================== 5. RSI周线极值 (Weekly RSI) ====================
    def weekly_rsi_signal(self,
                         rsi_weekly: float,
                         oversold: float = 35,
                         overbought: float = 65) -> Dict:
        """
        公式: RSI_14(Weekly) < 35
        核心: 寻找大周期级别的"精疲力竭"卖点
        """
        is_oversold = rsi_weekly < oversold
        
        signal = {
            "strategy_id": 5,
            "strategy_name": self.strategy_names[5],
            "rsi_weekly": rsi_weekly,
            "oversold_threshold": oversold,
            "signal": "BUY" if is_oversold else "HOLD",
            "confidence": (oversold - rsi_weekly) / oversold if is_oversold else 0.0,
            "reasoning": f"周线RSI {rsi_weekly:.1f}进入超卖区" if is_oversold else "周线RSI正常"
        }
        return signal
    
    # ==================== 6. 统计学Z-Score偏离 (Z-Score Bias) ====================
    def z_score_bias(self,
                    current_price: float,
                    ma_60: float,
                    std_60: float,
                    threshold: float = 2.0) -> Dict:
        """
        公式: Z = (Price - MA_60) / StdDev(60)
        核心: 利用3倍标准差捕捉统计学意义上的"极端错价"
        """
        if std_60 <= 0:
            return {
                "strategy_id": 6,
                "strategy_name": self.strategy_names[6],
                "z_score": 0.0,
                "threshold": threshold,
                "signal": "HOLD",
                "confidence": 0.0,
                "reasoning": "标准差无效"
            }
        
        z_score = (current_price - ma_60) / std_60
        is_extreme = abs(z_score) >= threshold
        
        signal = {
            "strategy_id": 6,
            "strategy_name": self.strategy_names[6],
            "z_score": round(z_score, 4),
            "threshold": threshold,
            "signal": "BUY" if z_score <= -threshold else "SELL" if z_score >= threshold else "HOLD",
            "confidence": abs(z_score) / threshold if is_extreme else 0.0,
            "reasoning": f"Z-Score {z_score:.2f}超出{threshold}倍标准差" if is_extreme else "价格在统计正常范围内"
        }
        return signal
    
    # ==================== 7. 三重均线共振 (Triple Cross) ====================
    def triple_cross_signal(self,
                           ma_5: float,
                           ma_20: float,
                           ma_60: float) -> Dict:
        """
        公式: MA_5 > MA_20 > MA_60
        核心: 确认多头排列后的长持稳健收益
        """
        is_triple_bull = (ma_5 > ma_20) and (ma_20 > ma_60)
        
        signal = {
            "strategy_id": 7,
            "strategy_name": self.strategy_names[7],
            "ma_5": ma_5,
            "ma_20": ma_20,
            "ma_60": ma_60,
            "signal": "BUY" if is_triple_bull else "HOLD",
            "confidence": 0.7 if is_triple_bull else 0.0,
            "reasoning": "5日>20日>60日均线，三重多头排列" if is_triple_bull else "均线排列不完整"
        }
        return signal
    
    # ==================== 8. 缩量回踩支撑 (Low Volume Retrace) ====================
    def low_volume_retrace_signal(self,
                                 current_price: float,
                                 ma_60: float,
                                 current_volume: float,
                                 avg_volume_20: float,
                                 price_tolerance: float = 0.02,
                                 volume_threshold: float = 0.5) -> Dict:
        """
        公式: (Price ≈ MA_60) ∩ (Vol < 0.5 × AvgVol_20)
        核心: 确认上升趋势中的洗盘结束信号
        """
        price_near_ma = abs(current_price - ma_60) / ma_60 <= price_tolerance
        volume_low = current_volume < volume_threshold * avg_volume_20
        
        signal = {
            "strategy_id": 8,
            "strategy_name": self.strategy_names[8],
            "price_near_ma": price_near_ma,
            "volume_low": volume_low,
            "signal": "BUY" if (price_near_ma and volume_low) else "HOLD",
            "confidence": 0.6 if (price_near_ma and volume_low) else 0.0,
            "reasoning": "价格回踩60日均线且成交量萎缩，洗盘结束" if (price_near_ma and volume_low) else "条件不满足"
        }
        return signal
    
    # ==================== 9. 宏观对冲锚点 (Macro-Anchor) ====================
    def macro_anchor_score(self,
                          gold_price: float,
                          implied_real_rate: float,
                          current_gold_price: float) -> Dict:
        """
        公式: Real_Gold = Gold - Implied(Real_Rate)
        核心: 剥离利率噪音，寻找黄金ETF的真实引力点
        """
        real_gold = gold_price - implied_real_rate
        deviation = current_gold_price - real_gold
        deviation_pct = deviation / real_gold if real_gold != 0 else 0
        
        signal = {
            "strategy_id": 9,
            "strategy_name": self.strategy_names[9],
            "real_gold_anchor": round(real_gold, 4),
            "current_gold_price": current_gold_price,
            "deviation": round(deviation, 4),
            "deviation_pct": round(deviation_pct, 4),
            "signal": "BUY" if deviation_pct < -0.05 else "SELL" if deviation_pct > 0.05 else "HOLD",
            "confidence": abs(deviation_pct) / 0.1 if abs(deviation_pct) > 0.05 else 0.0,
            "reasoning": f"黄金价格偏离宏观锚点{deviation_pct:.2%}" if abs(deviation_pct) > 0.05 else "价格在锚点附近"
        }
        return signal
    
    # ==================== 10. 能量潮背离 (OBV Divergence) ====================
    def obv_divergence_signal(self,
                             price_trend: str,  # "horizontal", "up", "down"
                             obv_trend: str,    # "upward", "downward", "horizontal"
                             obv_strength: float) -> Dict:
        """
        公式: (Price → Horizontal) ∩ (OBV → Upward)
        核心: 发现主力资金在长周期内的悄然吸筹
        """
        is_divergence = (price_trend.lower() in ["horizontal", "down"]) and (obv_trend.lower() == "upward")
        
        signal = {
            "strategy_id": 10,
            "strategy_name": self.strategy_names[10],
            "price_trend": price_trend,
            "obv_trend": obv_trend,
            "is_divergence": is_divergence,
            "signal": "BUY" if is_divergence else "HOLD",
            "confidence": obv_strength if is_divergence else 0.0,
            "reasoning": "价格横盘/下跌但OBV上升，主力吸筹背离" if is_divergence else "无背离信号"
        }
        return signal
    
    # ==================== 策略综合评估 ====================
    def evaluate_all_strategies(self, 
                              symbol_data: Dict) -> Dict:
        """
        综合评估所有策略，生成交易建议
        symbol_data: 包含所有必要数据的字典
        """
        signals = []
        
        # 评估每个策略
        if "gravity_dip" in symbol_data:
            gd = symbol_data["gravity_dip"]
            signals.append(self.gravity_dip_score(gd["current_price"], gd["ma_200"], gd["atr_14"]))
        
        if "dual_momentum" in symbol_data:
            dm = symbol_data["dual_momentum"]
            signals.append(self.dual_momentum_check(dm["current_price"], dm["ma_200"], dm["price_90d_ago"]))
        
        if "volatility_squeeze" in symbol_data:
            vs = symbol_data["volatility_squeeze"]
            signals.append(self.volatility_squeeze_score(vs["upper_bb"], vs["lower_bb"], vs["ma_20"]))
        
        if "dividend_alpha" in symbol_data:
            da = symbol_data["dividend_alpha"]
            signals.append(self.dividend_alpha_score(da["dividend"], da["price"]))
        
        if "weekly_rsi" in symbol_data:
            wr = symbol_data["weekly_rsi"]
            signals.append(self.weekly_rsi_signal(wr["rsi_weekly"]))
        
        if "z_score" in symbol_data:
            zs = symbol_data["z_score"]
            signals.append(self.z_score_bias(zs["current_price"], zs["ma_60"], zs["std_60"]))
        
        if "triple_cross" in symbol_data:
            tc = symbol_data["triple_cross"]
            signals.append(self.triple_cross_signal(tc["ma_5"], tc["ma_20"], tc["ma_60"]))
        
        if "low_volume" in symbol_data:
            lv = symbol_data["low_volume"]
            signals.append(self.low_volume_retrace_signal(
                lv["current_price"], lv["ma_60"], lv["current_volume"], lv["avg_volume_20"]
            ))
        
        if "macro_anchor" in symbol_data:
            ma = symbol_data["macro_anchor"]
            signals.append(self.macro_anchor_score(ma["gold_price"], ma["implied_real_rate"], ma["current_gold_price"]))
        
        if "obv_divergence" in symbol_data:
            od = symbol_data["obv_divergence"]
            signals.append(self.obv_divergence_signal(od["price_trend"], od["obv_trend"], od["obv_strength"]))
        
        # 统计买入信号
        buy_signals = [s for s in signals if s.get("signal") == "BUY"]
        sell_signals = [s for s in signals if s.get("signal") == "SELL"]
        hold_signals = [s for s in signals if s.get("signal") == "HOLD"]
        
        # 计算综合置信度
        avg_confidence = np.mean([s.get("confidence", 0) for s in signals]) if signals else 0
        
        # 生成综合建议
        final_signal = "HOLD"
        if len(buy_signals) > len(sell_signals) and avg_confidence > 0.3:
            final_signal = "BUY"
        elif len(sell_signals) > len(buy_signals) and avg_confidence > 0.3:
            final_signal = "SELL"
        
        return {
            "symbol": symbol_data.get("symbol", "UNKNOWN"),
            "total_strategies": len(signals),
            "buy_signals": len(buy_signals),
            "sell_signals": len(sell_signals),
            "hold_signals": len(hold_signals),
            "avg_confidence": round(avg_confidence, 4),
            "final_signal": final_signal,
            "signals": signals,
            "n_day_hold": self.n_days,
            "win_rate_target": self.win_rate_targets[self.n_days]
        }
    
    # ==================== N天倒计时工具函数 ====================
    def calculate_hold_progress(self,
                               entry_date: str,
                               current_date: str,
                               n_days: int = 60) -> Dict:
        """
        计算持仓进度
        """
        try:
            entry = pd.to_datetime(entry_date)
            current = pd.to_datetime(current_date)
            days_held = (current - entry).days
            progress = min(days_held / n_days, 1.0)
            
            return {
                "entry_date": entry_date,
                "current_date": current_date,
                "days_held": days_held,
                "n_days": n_days,
                "progress": round(progress, 4),
                "days_remaining": max(n_days - days_held, 0),
                "hold_stage": "早期" if progress < 0.33 else "中期" if progress < 0.66 else "晚期"
            }
        except:
            return {
                "entry_date": entry_date,
                "current_date": current_date,
                "days_held": 0,
                "n_days": n_days,
                "progress": 0.0,
                "days_remaining": n_days,
                "hold_stage": "未知"
            }


# 全局实例化
strategy_lib = StrategyLibrary()

if __name__ == "__main__":
    # 测试代码
    lib = StrategyLibrary()
    print("✅ 琥珀引擎长周期量化策略库加载成功")
    print(f"📊 策略数量: {len(lib.strategy_names)}")
    print(f"⏳ 主攻持有期N值: {lib.n_days}天")
    print(f"🎯 胜率目标: {lib.win_rate_targets[lib.n_days]*100}%")
    
    # 测试引力超跌模型
    test_score = lib.gravity_dip_score(100, 120, 5)
    print(f"\n🔍 引力超跌模型测试:")
    print(f"   价格: 100, MA200: 120, ATR14: 5")
    print(f"   分数: {test_score}")
    
    test_signal = lib.gravity_dip_signal(test_score, 2.0)
    print(f"   信号: {test_signal['signal']}, 置信度: {test_signal['confidence']:.2%}")