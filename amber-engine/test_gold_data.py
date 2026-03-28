#!/usr/bin/env python3
"""
测试Tushare黄金数据接口
检查是否支持国际金价和国内金价
"""

import os
import sys
from datetime import datetime, timedelta

os.environ['TUSHARE_TOKEN'] = '9e32ef28eac05c5fbb11e6f02a50da903def70f94b3018e93340568b'

def test_tushare_gold():
    """测试Tushare黄金数据"""
    try:
        import tushare as ts
        pro = ts.pro_api()
        
        today = datetime.now().strftime("%Y%m%d")
        yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y%m%d")
        
        print("=" * 70)
        print("🧪 Tushare黄金数据接口测试")
        print("=" * 70)
        print(f"测试日期: {today}")
        print("=" * 70)
        
        # 1. 测试外汇接口中的黄金 (XAUUSD - 国际金价)
        print("\n1. 测试国际金价 (XAUUSD):")
        gold_pairs = ['XAUUSD', 'XAUUSD.FXCM', 'XAU', 'GOLD', 'XAUUSD.OTC', 'XAUUSD.SPOT']
        
        for pair in gold_pairs:
            try:
                print(f"  尝试 {pair}...")
                df = pro.fx_daily(ts_code=pair, trade_date=today)
                if not df.empty:
                    print(f"    ✅ 找到数据!")
                    print(f"      最新价: {df.iloc[0]['bid_close']}")
                    print(f"      交易日期: {df.iloc[0]['trade_date']}")
                    print(f"      数据列: {list(df.columns)}")
                    return {
                        "international_gold": True,
                        "pair": pair,
                        "price": float(df.iloc[0]['bid_close']),
                        "trade_date": df.iloc[0]['trade_date']
                    }
                else:
                    # 尝试昨天数据
                    df = pro.fx_daily(ts_code=pair, trade_date=yesterday)
                    if not df.empty:
                        print(f"    ✅ 找到昨日数据!")
                        print(f"      昨日价: {df.iloc[0]['bid_close']}")
                        print(f"      交易日期: {df.iloc[0]['trade_date']}")
                        return {
                            "international_gold": True,
                            "pair": pair,
                            "price": float(df.iloc[0]['bid_close']),
                            "trade_date": df.iloc[0]['trade_date'],
                            "note": "昨日数据"
                        }
            except Exception as e:
                print(f"    ❌ 错误: {e}")
                continue
        
        print("    ⚠️ 未找到XAUUSD数据")
        
        # 2. 测试期货黄金 (国内黄金期货)
        print("\n2. 测试国内金价 (黄金期货):")
        domestic_codes = ['AU0', 'AU', 'AU.SHF', 'AU9999', 'SGE', 'SHAU']
        
        for code in domestic_codes:
            try:
                print(f"  尝试 {code}...")
                df = pro.fut_daily(ts_code=code, trade_date=today)
                if not df.empty:
                    print(f"    ✅ 找到数据!")
                    print(f"      最新价: {df.iloc[0]['close']}")
                    print(f"      交易日期: {df.iloc[0]['trade_date']}")
                    print(f"      数据列: {list(df.columns)}")
                    return {
                        "domestic_gold": True,
                        "code": code,
                        "price": float(df.iloc[0]['close']),
                        "trade_date": df.iloc[0]['trade_date']
                    }
            except Exception as e:
                print(f"    ❌ 错误: {e}")
                continue
        
        # 3. 测试其他可能的黄金接口
        print("\n3. 测试其他黄金接口:")
        
        # 测试gold_daily接口（需要正确参数）
        try:
            print("  尝试gold_daily接口...")
            # 查看接口需要的参数
            print("  💡 gold_daily可能需要exchange参数: SGE, SHFE等")
            
            # 测试上海黄金交易所
            df = pro.gold_daily(exchange='SGE', trade_date=today)
            if not df.empty:
                print(f"    ✅ SGE黄金数据找到!")
                print(f"      数据: {df.head()}")
                return {"sge_gold": True, "data": df.head().to_dict()}
        except Exception as e:
            print(f"    ❌ gold_daily错误: {e}")
        
        # 测试期权黄金
        try:
            print("  尝试opt_gold接口...")
            # 可能需要不同参数
            pass
        except Exception as e:
            print(f"    ❌ opt_gold错误: {e}")
        
        # 4. 查看可用的外汇品种
        print("\n4. 查看可用外汇品种:")
        try:
            # 获取今天有数据的外汇品种
            df = pro.fx_daily(trade_date=today)
            if not df.empty:
                print(f"    ✅ 今天有{len(df)}个外汇品种")
                print("    前10个品种:")
                for i, row in df.head(10).iterrows():
                    print(f"      {row['ts_code']}: {row['bid_close']}")
                
                # 检查是否有黄金相关
                gold_related = df[df['ts_code'].str.contains('XAU|GOLD', case=False, na=False)]
                if not gold_related.empty:
                    print(f"\n    🎯 找到黄金相关品种:")
                    for i, row in gold_related.iterrows():
                        print(f"      {row['ts_code']}: {row['bid_close']}")
                    return {"found_gold": True, "pairs": gold_related['ts_code'].tolist()}
        except Exception as e:
            print(f"    ❌ 获取外汇品种失败: {e}")
        
        print("\n" + "=" * 70)
        print("📊 测试总结:")
        print("=" * 70)
        print("❌ 未直接找到黄金数据接口")
        print("\n💡 建议:")
        print("1. 查看Tushare官方文档确认黄金接口")
        print("2. 可能需要特定权限或参数")
        print("3. 可考虑其他数据源如:")
        print("   - 东方财富黄金数据")
        print("   - 新浪财经黄金数据")
        print("   - 专门的黄金API")
        print("=" * 70)
        
        return {"gold_supported": False}
        
    except ImportError:
        print("❌ 无法导入tushare库")
        return {"error": "tushare not installed"}
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return {"error": str(e)}

def test_alternative_gold_sources():
    """测试替代黄金数据源"""
    print("\n" + "=" * 70)
    print("🔍 测试替代黄金数据源")
    print("=" * 70)
    
    try:
        import akshare as ak
        print("✅ AkShare库已安装")
        
        # 测试国际金价
        print("\n1. 测试国际金价 (AkShare):")
        try:
            # 现货黄金
            df = ak.spot_gold()
            if not df.empty:
                print(f"   ✅ 找到现货黄金数据: {len(df)}行")
                print(f"     最新数据: {df.iloc[0].to_dict() if len(df) > 0 else '无数据'}")
                return {"akshare_gold": True, "data": df.head().to_dict()}
        except Exception as e:
            print(f"   ❌ 现货黄金错误: {e}")
        
        # 测试国内金价
        print("\n2. 测试国内金价 (AkShare):")
        try:
            # 上海黄金交易所
            df = ak.futures_shfe_spot(trade_date="20260319", symbol="au")
            if not df.empty:
                print(f"   ✅ 找到上海黄金数据: {len(df)}行")
                print(f"     最新数据: {df.head()}")
                return {"akshare_sge": True, "data": df.head().to_dict()}
        except Exception as e:
            print(f"   ❌ 上海黄金错误: {e}")
        
        print("⚠️ AkShare黄金数据获取有限")
        
    except ImportError:
        print("❌ AkShare未安装")
        print("   安装: pip install akshare")
    except Exception as e:
        print(f"❌ AkShare测试失败: {e}")
    
    return {"alternative_tested": True}

if __name__ == "__main__":
    print("开始测试黄金数据接口...")
    
    # 测试Tushare
    tushare_result = test_tushare_gold()
    
    # 如果Tushare不支持，测试其他数据源
    if not tushare_result.get("gold_supported", True):
        test_alternative_gold_sources()
    
    print("\n" + "=" * 70)
    print("🎯 实施建议:")
    print("=" * 70)
    print("基于测试结果，建议:")
    
    if tushare_result.get("international_gold") or tushare_result.get("domestic_gold"):
        print("✅ 使用Tushare Pro获取黄金数据")
        print("   需要确认正确的接口参数")
    else:
        print("❌ Tushare标准权限可能不支持黄金数据")
        print("✅ 考虑:")
        print("   1. 升级Tushare会员权限")
        print("   2. 集成AkShare获取黄金数据")
        print("   3. 使用专门的黄金API")
        print("   4. 暂时不添加黄金指标")
    
    print("=" * 70)