#!/usr/bin/env python3
"""
主编持仓配置 - 50.4万专项雷达
"""

from datetime import datetime

# 主编持仓数据 - 真实支付宝持仓
PORTFOLIO = {
    "total_amount": 504000,  # 50.4万
    "funds": [
        {
            "code": "205856",
            "name": "电网设备",
            "full_name": "富国中证全指电力设备ETF联接A",
            "category": "行业主题",
            "amount": 75000,  # 7.5万
            "initial_weight": 14.88,  # 7.5/50.4
            "current_nav": 1.2345,
            "initial_nav": 1.2000,
            "daily_change": 0.85,  # 今日涨跌幅%
            "fee_rate": 0.15,  # 管理费率%
            "risk_level": "中高风险",
            "etf_mapping": "159611",  # 场内ETF映射
            "description": "跟踪中证全指电力设备指数，覆盖电网设备、新能源电力等"
        },
        {
            "code": "000051",
            "name": "沪深300",
            "full_name": "华夏沪深300ETF联接A",
            "category": "宽基指数",
            "amount": 70000,  # 7万
            "initial_weight": 13.89,
            "current_nav": 1.5678,
            "initial_nav": 1.5500,
            "daily_change": 0.42,
            "fee_rate": 0.10,
            "risk_level": "中风险",
            "etf_mapping": "510300",  # 沪深300ETF
            "description": "跟踪沪深300指数，A股核心资产代表"
        },
        {
            "code": "008142",
            "name": "黄金",
            "full_name": "华安黄金ETF联接A",
            "category": "商品",
            "amount": 52000,  # 5.2万
            "initial_weight": 10.32,
            "current_nav": 1.0890,
            "initial_nav": 1.0800,
            "daily_change": 0.28,
            "fee_rate": 0.10,
            "risk_level": "低风险",
            "etf_mapping": "518880",  # 黄金ETF
            "description": "跟踪黄金价格，抗通胀避险资产"
        },
        {
            "code": "019702",
            "name": "科创成长",
            "full_name": "易方达科创板50ETF联接A",
            "category": "科技创新",
            "amount": 52000,  # 5.2万
            "initial_weight": 10.32,
            "current_nav": 0.9567,
            "initial_nav": 0.9500,
            "daily_change": 1.25,
            "fee_rate": 0.15,
            "risk_level": "高风险",
            "etf_mapping": "588000",  # 科创50ETF
            "description": "跟踪科创板50指数，科技创新成长股"
        },
        {
            "code": "015061",
            "name": "300增强",
            "full_name": "易方达沪深300增强策略ETF联接A",
            "category": "增强指数",
            "amount": 30000,  # 3万
            "initial_weight": 5.95,
            "current_nav": 1.1234,
            "initial_nav": 1.1100,
            "daily_change": 0.65,
            "fee_rate": 0.60,  # 增强型费率较高
            "risk_level": "中风险",
            "etf_mapping": "510310",  # 沪深300增强ETF
            "description": "沪深300指数增强策略，追求超额收益"
        },
        {
            "code": "002251",
            "name": "军工安全",
            "full_name": "华夏军工安全混合A",
            "category": "行业主题",
            "amount": 30000,  # 3万
            "initial_weight": 5.95,
            "current_nav": 2.3456,
            "initial_nav": 2.3000,
            "daily_change": 0.92,
            "fee_rate": 1.50,  # 主动型费率最高
            "risk_level": "高风险",
            "etf_mapping": "512560",  # 军工ETF
            "description": "军工安全主题混合基金，主动管理"
        }
    ]
}

# 8%年化收益基准线配置
BENCHMARK_8_PERCENT = {
    "annual_return": 8.0,  # 年化8%
    "daily_return": 0.021,  # 日化收益率 (1.08^(1/365)-1)
    "line_color": "#FFD700",  # 金黄色
    "line_style": "dashed",
    "line_width": 2
}

# 风险再平衡配置
REBALANCING_CONFIG = {
    "deviation_threshold": 5.0,  # ±5%偏离度预警
    "warning_color": "#9C27B0",  # 紫色预警
    "fee_comparison": {
        "enhanced_fund": "015061",  # 300增强
        "passive_fund": "000051",   # 沪深300
        "fee_difference": 0.50,     # 费率差 0.6% - 0.1%
        "min_excess_return": 0.60   # 最小超额收益要求
    }
}

# T+0数据映射配置
T0_MAPPING = {
    "enabled": True,
    "update_interval": 60,  # 60秒更新一次
    "data_sources": {
        "etf_realtime": "模拟场内ETF实时价格",
        "nav_estimation": "基于ETF价格估算联接基金净值"
    }
}

def calculate_current_weights(portfolio):
    """计算当前权重"""
    total = portfolio["total_amount"]
    current_weights = {}
    
    for fund in portfolio["funds"]:
        current_value = fund["amount"] * (1 + fund["daily_change"]/100)
        current_weight = (current_value / total) * 100
        current_weights[fund["code"]] = {
            "current_weight": current_weight,
            "deviation": current_weight - fund["initial_weight"],
            "deviation_percent": ((current_weight - fund["initial_weight"]) / fund["initial_weight"]) * 100
        }
    
    return current_weights

def calculate_daily_contributions(portfolio):
    """计算每日盈亏贡献"""
    contributions = []
    
    for fund in portfolio["funds"]:
        daily_pnl = fund["amount"] * (fund["daily_change"] / 100)
        contributions.append({
            "code": fund["code"],
            "name": fund["name"],
            "daily_pnl": daily_pnl,
            "daily_change": fund["daily_change"]
        })
    
    # 按贡献度排序
    contributions.sort(key=lambda x: abs(x["daily_pnl"]), reverse=True)
    return contributions

def check_rebalancing_warnings(portfolio):
    """检查再平衡预警"""
    warnings = []
    current_weights = calculate_current_weights(portfolio)
    
    for fund in portfolio["funds"]:
        deviation = current_weights[fund["code"]]["deviation_percent"]
        
        if abs(deviation) > REBALANCING_CONFIG["deviation_threshold"]:
            warnings.append({
                "code": fund["code"],
                "name": fund["name"],
                "deviation": deviation,
                "message": f"权重偏离 {deviation:.1f}%，超过±5%阈值"
            })
    
    return warnings

def check_fee_optimization(portfolio):
    """检查费率优化建议"""
    enhanced_fund = None
    passive_fund = None
    
    for fund in portfolio["funds"]:
        if fund["code"] == REBALANCING_CONFIG["fee_comparison"]["enhanced_fund"]:
            enhanced_fund = fund
        elif fund["code"] == REBALANCING_CONFIG["fee_comparison"]["passive_fund"]:
            passive_fund = fund
    
    if enhanced_fund and passive_fund:
        excess_return = enhanced_fund["daily_change"] - passive_fund["daily_change"]
        fee_diff = REBALANCING_CONFIG["fee_comparison"]["fee_difference"]
        
        if excess_return < REBALANCING_CONFIG["fee_comparison"]["min_excess_return"]:
            return {
                "suggestion": "建议归并",
                "reason": f"超额收益{excess_return:.2f}%不足以覆盖费率差{fee_diff:.2f}%",
                "enhanced_fund": enhanced_fund["name"],
                "passive_fund": passive_fund["name"],
                "excess_return": excess_return
            }
    
    return None

def estimate_t0_pnl(portfolio):
    """估算T+0盈亏"""
    total_estimated_pnl = 0
    fund_estimates = []
    
    for fund in portfolio["funds"]:
        # 模拟场内ETF实时价格波动
        etf_volatility = 1.2  # ETF波动率因子
        estimated_daily_change = fund["daily_change"] * etf_volatility
        
        estimated_pnl = fund["amount"] * (estimated_daily_change / 100)
        total_estimated_pnl += estimated_pnl
        
        fund_estimates.append({
            "code": fund["code"],
            "name": fund["name"],
            "estimated_change": estimated_daily_change,
            "estimated_pnl": estimated_pnl,
            "etf_mapping": fund["etf_mapping"]
        })
    
    return {
        "total_estimated_pnl": total_estimated_pnl,
        "fund_estimates": fund_estimates,
        "update_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

if __name__ == "__main__":
    print("主编持仓配置加载成功")
    print(f"总持仓: {PORTFOLIO['total_amount']/10000:.1f}万")
    print(f"基金数量: {len(PORTFOLIO['funds'])}只")
    
    # 计算当前权重
    weights = calculate_current_weights(PORTFOLIO)
    print("\n当前权重分布:")
    for code, data in weights.items():
        print(f"  {code}: {data['current_weight']:.1f}% (偏离: {data['deviation_percent']:.1f}%)")
    
    # 计算盈亏贡献
    contributions = calculate_daily_contributions(PORTFOLIO)
    print("\n今日盈亏贡献榜:")
    for contrib in contributions[:3]:  # 显示前三名
        sign = "+" if contrib["daily_pnl"] > 0 else ""
        print(f"  {contrib['name']}: {sign}{contrib['daily_pnl']:.1f}元 ({contrib['daily_change']:.2f}%)")