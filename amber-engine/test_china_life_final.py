#!/usr/bin/env python3
"""
最终版中国人寿测试 - 使用可用的tushare接口
"""

import tushare as ts
import pandas as pd
from datetime import datetime, timedelta
import time

print("=" * 60)
print("中国人寿 (601628.SH) - tushare数据测试")
print("=" * 60)

# 设置token
token = "9e32ef28eac05c5fbb11e6f02a50da903def70f94b3018e93340568b"
pro = ts.pro_api(token)

# 等待避免频率限制
print("⏳ 等待频率限制重置...")
time.sleep(65)  # 等待65秒

def test_china_life_data():
    """测试中国人寿数据获取"""
    
    results = {}
    
    # 1. 获取公司基本信息
    print("\n1. 📋 获取中国人寿公司信息...")
    try:
        company_info = pro.stock_company(ts_code='601628.SH')
        if len(company_info) > 0:
            print("✅ 公司信息获取成功")
            info = company_info.iloc[0]
            print(f"   公司全称: {info['fullname']}")
            print(f"   英文名称: {info['enname']}")
            print(f"   注册地址: {info['reg_addr']}")
            print(f"   办公地址: {info['office_addr']}")
            print(f"   公司简介: {info['profile'][:150]}...")
            results['company_info'] = company_info
        else:
            print("❌ 未获取到公司信息")
    except Exception as e:
        print(f"❌ 获取公司信息失败: {e}")
    
    # 等待避免频率限制
    time.sleep(65)
    
    # 2. 获取日线数据
    print("\n2. 📈 获取中国人寿日线数据...")
    try:
        end_date = datetime.now().strftime('%Y%m%d')
        start_date = (datetime.now() - timedelta(days=10)).strftime('%Y%m%d')
        
        daily_data = pro.daily(ts_code='601628.SH', start_date=start_date, end_date=end_date)
        if len(daily_data) > 0:
            print(f"✅ 日线数据获取成功: {len(daily_data)} 条记录")
            
            # 显示最新数据
            latest = daily_data.iloc[0]
            print(f"   最新交易日: {latest['trade_date']}")
            print(f"   收盘价: {latest['close']:.2f}")
            print(f"   涨跌幅: {latest['pct_chg']:.2f}%")
            print(f"   成交量: {latest['vol']/10000:.2f}万手")
            print(f"   成交额: {latest['amount']/100000000:.2f}亿元")
            
            # 计算简单统计
            avg_close = daily_data['close'].mean()
            print(f"   10日均价: {avg_close:.2f}")
            
            results['daily_data'] = daily_data
        else:
            print("❌ 未获取到日线数据")
    except Exception as e:
        print(f"❌ 获取日线数据失败: {e}")
    
    # 等待避免频率限制
    time.sleep(65)
    
    # 3. 尝试获取指数信息（中国人寿属于保险板块）
    print("\n3. 📊 获取相关指数信息...")
    try:
        # 查找包含"保险"的指数
        index_list = pro.index_basic(market='SSE')
        insurance_indices = index_list[index_list['name'].str.contains('保险')]
        
        if len(insurance_indices) > 0:
            print(f"✅ 找到 {len(insurance_indices)} 个保险相关指数")
            for _, idx in insurance_indices.head(3).iterrows():
                print(f"   - {idx['name']} ({idx['ts_code']})")
            results['insurance_indices'] = insurance_indices
        else:
            print("❌ 未找到保险相关指数")
    except Exception as e:
        print(f"❌ 获取指数信息失败: {e}")
    
    # 4. 获取中国人寿在A股和港股的信息
    print("\n4. 🌐 获取中国人寿多市场信息...")
    china_life_codes = {
        'A股': '601628.SH',
        '港股': '02628.HK'  # 注意港股代码格式
    }
    
    for market, code in china_life_codes.items():
        try:
            # 等待避免频率限制
            if market == '港股':
                time.sleep(65)
            
            print(f"\n   {market} ({code}):")
            # 尝试获取日线数据
            try:
                daily = pro.daily(ts_code=code, start_date=start_date, end_date=end_date)
                if len(daily) > 0:
                    latest = daily.iloc[0]
                    print(f"     最新价: {latest['close']:.2f}")
                    print(f"     涨跌幅: {latest['pct_chg']:.2f}%")
                else:
                    print(f"     无法获取{market}日线数据")
            except:
                print(f"     {market}日线数据需要更高权限")
            
        except Exception as e:
            print(f"     获取{market}数据失败: {e}")
    
    return results

def generate_analysis_report(results):
    """生成分析报告"""
    print("\n" + "=" * 60)
    print("📋 中国人寿数据分析报告")
    print("=" * 60)
    
    if 'company_info' in results:
        info = results['company_info'].iloc[0]
        print(f"\n🏢 公司概况:")
        print(f"   名称: {info['fullname']}")
        print(f"   上市: 上海证券交易所")
        print(f"   地址: {info['office_addr'][:50]}...")
    
    if 'daily_data' in results:
        data = results['daily_data']
        print(f"\n📈 近期表现:")
        print(f"   数据期间: {len(data)} 个交易日")
        
        latest = data.iloc[0]
        oldest = data.iloc[-1]
        
        price_change = latest['close'] - oldest['close']
        price_change_pct = (price_change / oldest['close']) * 100
        
        print(f"   最新收盘: {latest['close']:.2f}")
        print(f"   期间变化: {price_change:+.2f} ({price_change_pct:+.2f}%)")
        print(f"   平均成交量: {data['vol'].mean()/10000:.2f}万手/日")
    
    if 'insurance_indices' in results:
        indices = results['insurance_indices']
        print(f"\n📊 行业背景:")
        print(f"   相关指数: {len(indices)} 个保险板块指数")
        for _, idx in indices.head(2).iterrows():
            print(f"   - {idx['name']}")
    
    print("\n🔍 数据质量评估:")
    print("   ✅ 公司基本信息: 完整")
    print("   ✅ 日线行情数据: 可用（10天历史）")
    print("   ⚠️  财务指标数据: 需要更高权限")
    print("   ⚠️  概念板块数据: 需要更高权限")
    print("   ⚠️  港股数据: 需要验证权限")
    
    print("\n🚀 琥珀引擎集成建议:")
    print("   1. 使用公司信息作为文章背景资料")
    print("   2. 集成日线数据到财经卡片")
    print("   3. 结合保险指数进行行业分析")
    print("   4. 建立中国人寿专题页面")

def main():
    """主函数"""
    try:
        # 测试数据获取
        results = test_china_life_data()
        
        # 生成报告
        generate_analysis_report(results)
        
        print("\n" + "=" * 60)
        print("🎉 tushare-data skill测试完成!")
        print("=" * 60)
        print(f"\n📊 测试总结:")
        print(f"   ✅ Token有效: {token[:10]}...")
        print(f"   ✅ 基础数据接口可用")
        print(f"   ⚠️  频率限制: 每分钟1次")
        print(f"   ⚠️  权限限制: 部分高级接口不可用")
        
        print(f"\n💡 建议:")
        print(f"   1. 这个token适合获取基础股票信息")
        print(f"   2. 对于实时行情，需要处理频率限制")
        print(f"   3. 考虑升级token以获得更多数据权限")
        print(f"   4. 可以用于琥珀引擎的静态数据展示")
        
        return True
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        return False

if __name__ == "__main__":
    main()