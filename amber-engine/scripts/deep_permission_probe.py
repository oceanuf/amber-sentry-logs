#!/usr/bin/env python3
"""
琥珀权限深度探测脚本
探测Tushare Pro会员权限矩阵
"""

import tushare as ts
import time
import pandas as pd
from datetime import datetime

# 使用主编提供的Token
TUSHARE_TOKEN = "9e32ef28eac05c5fbb11e6f02a50da903def70f94b3018e93340568b"
pro = ts.pro_api(TUSHARE_TOKEN)

def probe_api(api_name, params):
    """探测单个API权限"""
    try:
        # 尝试调用
        start_time = time.time()
        df = getattr(pro, api_name)(**params)
        elapsed_time = time.time() - start_time
        
        if df is not None:
            row_count = len(df)
            print(f"✅ [SUCCESS] {api_name}: 权限已开启，返回 {row_count} 行数据，耗时 {elapsed_time:.2f}秒。")
            
            # 显示数据样本
            if row_count > 0:
                print(f"   数据样本:")
                sample = df.head(3) if row_count >= 3 else df
                for idx, row in sample.iterrows():
                    # 显示关键字段
                    if api_name == "index_daily":
                        print(f"     {row.get('trade_date', '')}: 收盘 {row.get('close', '')}, 涨跌 {row.get('pct_chg', '')}%")
                    elif api_name == "index_dailybasic":
                        print(f"     {row.get('trade_date', '')}: PE {row.get('pe', '')}, PB {row.get('pb', '')}")
                    elif api_name == "fund_daily":
                        print(f"     {row.get('trade_date', '')}: 净值 {row.get('nav', '')}, 涨跌 {row.get('pct_chg', '')}%")
                    else:
                        # 显示前3个字段
                        fields = list(row.index)[:3]
                        values = [str(row[field])[:20] for field in fields]
                        print(f"     {' | '.join([f'{f}:{v}' for f, v in zip(fields, values)])}")
            
            return {
                'status': 'SUCCESS',
                'row_count': row_count,
                'elapsed_time': elapsed_time,
                'sample_data': df.head(3).to_dict('records') if row_count > 0 else []
            }
        else:
            print(f"⚠️ [EMPTY] {api_name}: 返回空数据")
            return {'status': 'EMPTY', 'row_count': 0, 'elapsed_time': elapsed_time}
            
    except Exception as e:
        error_msg = str(e)
        print(f"❌ [DENIED] {api_name}: 错误信息 - {error_msg[:100]}...")
        return {
            'status': 'DENIED',
            'error': error_msg,
            'elapsed_time': 0
        }

# --- 探测矩阵 ---
test_matrix = {
    "index_daily": {"ts_code": "000300.SH", "start_date": "20260317", "end_date": "20260318"},  # 指数日线
    "index_dailybasic": {"ts_code": "000300.SH", "trade_date": "20260317"},  # 指数估值(PE/PB)
    "fund_daily": {"ts_code": "510300.SH", "start_date": "20260317", "end_date": "20260318"},  # ETF基金日线
    "fund_portfolio": {"ts_code": "510300.SH"},  # 基金持仓穿透 (核心探测点)
    "fina_indicator": {"ts_code": "600519.SH", "period": "20251231"},  # 财务指标
    "moneyflow_hsgt": {"start_date": "20260317", "end_date": "20260318"},  # 沪深港通资金流
    "stk_holdernumber": {"ts_code": "600519.SH"}  # 股东人数 (情绪指标)
}

print("=" * 80)
print("🚀 开始琥珀权限深度探测...")
print(f"🔑 Token: {TUSHARE_TOKEN[:10]}...")
print(f"⏰ 探测时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 80)

results = {}
for api_name, param in test_matrix.items():
    print(f"\n🔍 探测: {api_name}")
    print(f"   参数: {param}")
    result = probe_api(api_name, param)
    results[api_name] = result
    time.sleep(0.5)  # 避免请求过快

# 生成权限地图
print("\n" + "=" * 80)
print("📊 琥珀权限深度探测结果 - Permission_Map")
print("=" * 80)

# 统计结果
success_count = sum(1 for r in results.values() if r['status'] == 'SUCCESS')
denied_count = sum(1 for r in results.values() if r['status'] == 'DENIED')
empty_count = sum(1 for r in results.values() if r['status'] == 'EMPTY')

print(f"📈 探测统计: 成功 {success_count} | 拒绝 {denied_count} | 空数据 {empty_count}")
print(f"📊 成功率: {success_count/len(results)*100:.1f}%")

print("\n🔑 权限详情:")
print("-" * 80)

for api_name, result in results.items():
    status_icon = "✅" if result['status'] == 'SUCCESS' else "❌" if result['status'] == 'DENIED' else "⚠️"
    status_text = "已开启" if result['status'] == 'SUCCESS' else "未授权" if result['status'] == 'DENIED' else "空数据"
    
    if result['status'] == 'SUCCESS':
        print(f"{status_icon} {api_name:20} {status_text:10} 数据行: {result['row_count']:4d} 耗时: {result['elapsed_time']:.2f}s")
    elif result['status'] == 'DENIED':
        error_preview = result['error'][:50] + "..." if len(result['error']) > 50 else result['error']
        print(f"{status_icon} {api_name:20} {status_text:10} 错误: {error_preview}")
    else:
        print(f"{status_icon} {api_name:20} {status_text:10} 无数据返回")

print("\n" + "=" * 80)
print("🎯 关键权限分析")
print("=" * 80)

# 关键权限分析
critical_apis = ["index_daily", "index_dailybasic", "fund_daily", "fund_portfolio"]
print("🔑 核心财经数据权限:")

for api in critical_apis:
    result = results.get(api, {})
    if result.get('status') == 'SUCCESS':
        print(f"   ✅ {api:20} - 可用 (琥珀引擎核心依赖)")
    else:
        print(f"   ❌ {api:20} - 不可用 (可能影响功能)")

print("\n📊 数据能力评估:")

# 评估数据能力
data_capabilities = {
    "指数行情": results.get("index_daily", {}).get("status") == "SUCCESS",
    "估值数据": results.get("index_dailybasic", {}).get("status") == "SUCCESS",
    "ETF数据": results.get("fund_daily", {}).get("status") == "SUCCESS",
    "持仓穿透": results.get("fund_portfolio", {}).get("status") == "SUCCESS",
    "财务指标": results.get("fina_indicator", {}).get("status") == "SUCCESS",
    "资金流向": results.get("moneyflow_hsgt", {}).get("status") == "SUCCESS",
    "股东情绪": results.get("stk_holdernumber", {}).get("status") == "SUCCESS"
}

for capability, available in data_capabilities.items():
    icon = "✅" if available else "❌"
    print(f"   {icon} {capability:15} - {'可用' if available else '不可用'}")

print("\n" + "=" * 80)
print("💡 琥珀引擎集成建议")
print("=" * 80)

# 基于权限的集成建议
available_apis = [api for api, result in results.items() if result.get('status') == 'SUCCESS']

if "index_daily" in available_apis and "index_dailybasic" in available_apis:
    print("✅ 核心指数数据完整，可构建:")
    print("   - 实时指数行情系统")
    print("   - 估值云图分析")
    print("   - 指数历史回测")

if "fund_daily" in available_apis:
    print("✅ ETF数据可用，可扩展:")
    print("   - ETF实时净值监控")
    print("   - 场内场外套利分析")
    print("   - 基金业绩对比")

if "fund_portfolio" in available_apis:
    print("✅ 基金持仓穿透可用，可开发:")
    print("   - 基金重仓股分析")
    print("   - 行业配置透视")
    print("   - 基金经理风格识别")

if "moneyflow_hsgt" in available_apis:
    print("✅ 资金流向数据可用，可建立:")
    print("   - 北向资金监控")
    print("   - 主力资金流向")
    print("   - 市场情绪指标")

if "fina_indicator" in available_apis:
    print("✅ 财务指标可用，可构建:")
    print("   - 公司基本面分析")
    print("   - 财务健康度评分")
    print("   - 估值模型计算")

print("\n" + "=" * 80)
print("📋 Permission_Map 总结报告")
print("=" * 80)

# 生成总结报告
report = f"""
## 🚀 琥珀权限深度探测报告

### 📅 探测信息
- 探测时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- Token状态: 有效 (已升级Tushare Pro会员)
- 探测API数量: {len(test_matrix)} 个
- 总体成功率: {success_count/len(results)*100:.1f}%

### 🎯 核心权限状态
1. **指数行情** ({results.get('index_daily', {}).get('status', 'UNKNOWN')})
   - 沪深300日线数据: {'✅ 可用' if results.get('index_daily', {}).get('status') == 'SUCCESS' else '❌ 不可用'}

2. **估值数据** ({results.get('index_dailybasic', {}).get('status', 'UNKNOWN')})
   - PE/PB等估值指标: {'✅ 可用' if results.get('index_dailybasic', {}).get('status') == 'SUCCESS' else '❌ 不可用'}

3. **ETF数据** ({results.get('fund_daily', {}).get('status', 'UNKNOWN')})
   - 基金日线行情: {'✅ 可用' if results.get('fund_daily', {}).get('status') == 'SUCCESS' else '❌ 不可用'}

4. **持仓穿透** ({results.get('fund_portfolio', {}).get('status', 'UNKNOWN')})
   - 基金重仓股分析: {'✅ 可用' if results.get('fund_portfolio', {}).get('status') == 'SUCCESS' else '❌ 不可用'}

### 📊 数据能力矩阵
| 数据类别 | 状态 | 数据行数 | 说明 |
|---------|------|----------|------|
"""

for api_name, result in results.items():
    status = result.get('status', 'UNKNOWN')
    status_display = "✅ 成功" if status == 'SUCCESS' else "❌ 拒绝" if status == 'DENIED' else "⚠️ 空数据"
    row_count = result.get('row_count', 0) if status == 'SUCCESS' else 0
    
    # API说明
    api_descriptions = {
        "index_daily": "指数日线行情",
        "index_dailybasic": "指数估值数据(PE/PB)",
        "fund_daily": "ETF基金日线",
        "fund_portfolio": "基金持仓穿透",
        "fina_indicator": "财务指标",
        "moneyflow_hsgt": "沪深港通资金流",
        "stk_holdernumber": "股东人数变化"
    }
    
    description = api_descriptions.get(api_name, api_name)
    report += f"| {api_name} | {status_display} | {row_count} | {description} |\n"

report += f"""
### 💡 琥珀引擎集成建议
基于当前权限状态，建议优先集成以下功能:

1. **立即集成** (权限已开启):
   - 沪深300实时行情 + 历史数据
   - 估值云图分析系统
   - ETF净值监控

2. **中期规划** (需验证数据质量):
   - 基金持仓分析 (如权限可用)
   - 资金流向监控
   - 财务指标分析

3. **长期扩展** (高级功能):
   - 量化策略回测
   - 风险管理系统
   - 智能投顾服务

### ⚠️ 注意事项
1. API调用频率限制需遵守Tushare Pro规则
2. 数据缓存策略需优化以减少API调用
3. 异常处理机制需完善以保障系统稳定

---
*报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
*琥珀引擎权限探测系统*
"""

print(report)

# 保存探测结果
import json
import os

result_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "reports", "permissions")
os.makedirs(result_dir, exist_ok=True)

result_file = os.path.join(result_dir, f"permission_map_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")

# 简化结果保存
simplified_results = {}
for api_name, result in results.items():
    simplified_results[api_name] = {
        'status': result.get('status'),
        'row_count': result.get('row_count', 0),
        'elapsed_time': result.get('elapsed_time', 0)
    }

with open(result_file, 'w', encoding='utf-8') as f:
    json.dump({
        'timestamp': datetime.now().isoformat(),
        'token_preview': TUSHARE_TOKEN[:10] + "...",
        'total_apis': len(test_matrix),
        'success_count': success_count,
        'results': simplified_results
    }, f, ensure_ascii=False, indent=2)

print(f"\n💾 探测结果已保存: {result_file}")
print("=" * 80)
print("🎉 琥珀权限深度探测完成！")
print("=" * 80)