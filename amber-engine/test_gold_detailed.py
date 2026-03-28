#!/usr/bin/env python3
"""
详细测试Tushare黄金数据
检查国际金价和国内金价支持情况
"""

import os
import sys
from datetime import datetime, timedelta

os.environ['TUSHARE_TOKEN'] = '9e32ef28eac05c5fbb11e6f02a50da903def70f94b3018e93340568b'

def get_all_gold_data():
    """获取所有黄金数据"""
    try:
        import tushare as ts
        pro = ts.pro_api()
        
        today = datetime.now().strftime("%Y%m%d")
        yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y%m%d")
        
        results = {
            "international_gold": None,
            "domestic_gold": None,
            "available_pairs": [],
            "test_date": today
        }
        
        print("=" * 70)
        print("🔍 Tushare黄金数据详细测试")
        print("=" * 70)
        
        # 1. 查看今天所有外汇数据，寻找黄金
        print("\n1. 扫描今天的外汇数据:")
        try:
            df_fx = pro.fx_daily(trade_date=today)
            if not df_fx.empty:
                print(f"   ✅ 今天有{len(df_fx)}个外汇品种")
                
                # 寻找黄金相关
                gold_keywords = ['XAU', 'GOLD', '黄金']
                gold_pairs = []
                
                for keyword in gold_keywords:
                    matches = df_fx[df_fx['ts_code'].str.contains(keyword, case=False, na=False)]
                    if not matches.empty:
                        gold_pairs.extend(matches['ts_code'].tolist())
                        print(f"   🎯 找到'{keyword}'相关品种:")
                        for _, row in matches.iterrows():
                            print(f"      {row['ts_code']}: {row['bid_close']} (日期: {row['trade_date']})")
                            results["available_pairs"].append({
                                "pair": row['ts_code'],
                                "price": float(row['bid_close']),
                                "date": row['trade_date']
                            })
                
                if gold_pairs:
                    results["international_gold"] = {
                        "supported": True,
                        "pairs": gold_pairs,
                        "note": "从fx_daily接口获取"
                    }
                else:
                    print("   ⚠️ 今天无黄金相关外汇数据")
            else:
                print("   ⚠️ 今天无外汇数据")
                
        except Exception as e:
            print(f"   ❌ 外汇数据扫描失败: {e}")
        
        # 2. 测试国内黄金期货
        print("\n2. 测试国内黄金期货:")
        try:
            # 常见国内黄金期货代码
            domestic_codes = ['AU0', 'AU', 'AU.SHF', 'AU9999', 'SGE', 'SHAU', 'AU88']
            
            for code in domestic_codes:
                try:
                    df = pro.fut_daily(ts_code=code, trade_date=today)
                    if not df.empty:
                        print(f"   ✅ 找到{code}数据:")
                        print(f"      最新价: {df.iloc[0]['close']}")
                        print(f"      涨跌幅: {df.iloc[0]['pct_chg']}%")
                        print(f"      交易日期: {df.iloc[0]['trade_date']}")
                        
                        results["domestic_gold"] = {
                            "supported": True,
                            "code": code,
                            "price": float(df.iloc[0]['close']),
                            "change_pct": float(df.iloc[0]['pct_chg']),
                            "date": df.iloc[0]['trade_date']
                        }
                        break
                except Exception as e:
                    continue
            
            if not results["domestic_gold"]:
                print("   ⚠️ 未找到国内黄金期货数据")
                
        except Exception as e:
            print(f"   ❌ 国内黄金测试失败: {e}")
        
        # 3. 测试黄金专门接口
        print("\n3. 测试黄金专门接口:")
        try:
            # 尝试不同交易所
            exchanges = ['SGE', 'SHFE', 'INE', 'CZCE', 'DCE']
            
            for exchange in exchanges:
                try:
                    # 可能需要正确参数格式
                    if exchange == 'SGE':
                        # 上海黄金交易所
                        print(f"  测试{exchange}...")
                        # 这里需要正确的参数格式
                        pass
                except:
                    continue
                    
        except Exception as e:
            print(f"   ❌ 黄金专门接口测试失败: {e}")
        
        # 4. 查看可用期货品种
        print("\n4. 查看期货市场黄金品种:")
        try:
            df_fut = pro.fut_basic(exchange='SHFE')
            if not df_fut.empty:
                print(f"   ✅ 上期所有{len(df_fut)}个期货品种")
                
                # 寻找黄金相关
                gold_futures = df_fut[df_fut['name'].str.contains('黄金|金|AU', case=False, na=False)]
                if not gold_futures.empty:
                    print(f"   🎯 找到黄金期货品种:")
                    for _, row in gold_futures.head(5).iterrows():
                        print(f"      {row['ts_code']}: {row['name']}")
                        
                    # 测试其中一个品种的数据
                    test_code = gold_futures.iloc[0]['ts_code']
                    print(f"\n  测试{test_code}数据...")
                    try:
                        df_data = pro.fut_daily(ts_code=test_code, trade_date=yesterday)
                        if not df_data.empty:
                            print(f"     昨日收盘: {df_data.iloc[0]['close']}")
                            print(f"     涨跌幅: {df_data.iloc[0]['pct_chg']}%")
                            
                            if not results["domestic_gold"]:
                                results["domestic_gold"] = {
                                    "supported": True,
                                    "code": test_code,
                                    "price": float(df_data.iloc[0]['close']),
                                    "change_pct": float(df_data.iloc[0]['pct_chg']),
                                    "date": df_data.iloc[0]['trade_date'],
                                    "name": gold_futures.iloc[0]['name']
                                }
                    except Exception as e:
                        print(f"     数据获取失败: {e}")
                else:
                    print("   ⚠️ 未找到黄金期货品种")
            else:
                print("   ⚠️ 无期货品种数据")
                
        except Exception as e:
            print(f"   ❌ 期货品种查询失败: {e}")
        
        print("\n" + "=" * 70)
        print("📊 测试结果总结")
        print("=" * 70)
        
        if results["international_gold"]:
            print("✅ 国际金价: 支持")
            pairs = results["international_gold"].get("pairs", [])
            for pair in pairs:
                print(f"   可用品种: {pair}")
        else:
            print("❌ 国际金价: 未找到支持数据")
            
        if results["domestic_gold"]:
            print("✅ 国内金价: 支持")
            print(f"   代码: {results['domestic_gold']['code']}")
            print(f"   价格: {results['domestic_gold']['price']}")
            print(f"   日期: {results['domestic_gold']['date']}")
        else:
            print("❌ 国内金价: 未找到支持数据")
            
        print("\n💡 实施建议:")
        if results["international_gold"] and results["domestic_gold"]:
            print("✅ 可以添加国际金价和国内金价指标")
            print("   国际: 使用fx_daily接口 (如XAUUSD.FXCM)")
            print("   国内: 使用fut_daily接口 (黄金期货)")
        elif results["international_gold"]:
            print("✅ 可以添加国际金价指标")
            print("❌ 国内金价需其他数据源")
        elif results["domestic_gold"]:
            print("✅ 可以添加国内金价指标")
            print("❌ 国际金价需其他数据源")
        else:
            print("❌ Tushare标准权限可能不支持黄金数据")
            print("   考虑AkShare或其他数据源")
        
        print("=" * 70)
        return results
        
    except ImportError:
        print("❌ 无法导入tushare库")
        return {"error": "tushare not installed"}
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return {"error": str(e)}

if __name__ == "__main__":
    get_all_gold_data()