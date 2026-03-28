#!/usr/bin/env python3
"""
快速测试Tushare Pro会员权限
"""

import os
import sys
from datetime import datetime, timedelta

# 设置Tushare Token
TUSHARE_TOKEN = "9e32ef28eac05c5fbb11e6f02a50da903def70f94b3018e93340568b"
os.environ['TUSHARE_TOKEN'] = TUSHARE_TOKEN

print("🚀 快速测试Tushare Pro会员权限...")

try:
    import tushare as ts
    print("✅ tushare库导入成功")
    
    # 初始化pro接口
    pro = ts.pro_api(TUSHARE_TOKEN)
    print("✅ tushare pro接口初始化成功")
    
    # 获取当前日期
    today = datetime.now().strftime("%Y%m%d")
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y%m%d")
    
    print(f"\n📅 查询日期: 今天={today}, 昨天={yesterday}")
    
    # 测试指数日线接口
    print("\n🔍 测试指数日线接口 (index_daily)...")
    
    try:
        df = pro.index_daily(ts_code='000300.SH', 
                            start_date=yesterday, 
                            end_date=today)
        
        if df is not None and not df.empty:
            print(f"✅ ✅ ✅ 会员升级成功！接口可用！")
            print(f"📊 返回数据: {len(df)} 条记录")
            
            # 显示数据
            df = df.sort_values('trade_date', ascending=False)
            latest = df.iloc[0]
            
            print(f"\n📈 沪深300最新数据:")
            print(f"   交易日期: {latest['trade_date']}")
            print(f"   收盘点位: {latest['close']:.2f}")
            print(f"   涨跌幅: {latest['pct_chg']:.2f}%")
            print(f"   成交量: {latest['vol']:,.0f} 手")
            print(f"   成交额: {latest['amount']:,.0f} 元")
            
            # 与东方财富数据对比
            ef_price = 4658.33  # 东方财富数据
            ef_change = 0.45
            
            print(f"\n🔍 数据对比:")
            print(f"   Tushare点位: {latest['close']:.2f}")
            print(f"   东方财富点位: {ef_price:.2f}")
            print(f"   差异: {abs(latest['close'] - ef_price):.2f} 点")
            
            # 判断数据一致性
            diff = abs(latest['close'] - ef_price)
            if diff < 10:
                print(f"✅ 数据一致性: 优秀 (差异 {diff:.2f} 点)")
            elif diff < 30:
                print(f"✅ 数据一致性: 良好 (差异 {diff:.2f} 点)")
            else:
                print(f"⚠️ 数据一致性: 差异较大 (差异 {diff:.2f} 点)")
            
            # 测试更多数据
            print("\n🔍 测试获取更多历史数据...")
            start_date = (datetime.now() - timedelta(days=30)).strftime("%Y%m%d")
            df_history = pro.index_daily(ts_code='000300.SH', 
                                        start_date=start_date, 
                                        end_date=today)
            
            if df_history is not None and not df_history.empty:
                print(f"✅ 历史数据获取成功: {len(df_history)} 个交易日")
                print(f"   时间范围: {df_history['trade_date'].min()} 至 {df_history['trade_date'].max()}")
                print(f"   点位范围: {df_history['close'].min():.2f} - {df_history['close'].max():.2f}")
                print(f"   平均点位: {df_history['close'].mean():.2f}")
            
            print("\n🎉 Tushare Pro会员升级验证完成！")
            print(f"📊 沪深300最新点位: {latest['close']:.2f}")
            print(f"📈 涨跌幅: {latest['pct_chg']:+.2f}%")
            print(f"⏰ 数据时间: {latest['trade_date']}")
            
        else:
            print("⚠️ 数据为空，可能今日未交易")
            print("💡 尝试获取昨日数据...")
            
            # 尝试获取更早的数据
            three_days_ago = (datetime.now() - timedelta(days=3)).strftime("%Y%m%d")
            df_earlier = pro.index_daily(ts_code='000300.SH', 
                                        start_date=three_days_ago, 
                                        end_date=today)
            
            if df_earlier is not None and not df_earlier.empty:
                print(f"✅ 获取到历史数据: {len(df_earlier)} 条记录")
                df_earlier = df_earlier.sort_values('trade_date', ascending=False)
                latest_earlier = df_earlier.iloc[0]
                
                print(f"\n📈 沪深300最新可用数据:")
                print(f"   交易日期: {latest_earlier['trade_date']}")
                print(f"   收盘点位: {latest_earlier['close']:.2f}")
                print(f"   涨跌幅: {latest_earlier['pct_chg']:.2f}%")
            else:
                print("❌ 无法获取任何数据")
                
    except Exception as e:
        print(f"❌ 接口调用错误: {e}")
        
except ImportError as e:
    print(f"❌ tushare库导入失败: {e}")
except Exception as e:
    print(f"❌ 测试过程发生错误: {e}")
    import traceback
    traceback.print_exc()