#!/usr/bin/env python3
"""
使用tushare基础接口获取沪深300数据
尝试所有可用接口
"""

import os
import sys
import pandas as pd
from datetime import datetime, timedelta

# 设置Tushare Token
TUSHARE_TOKEN = "9e32ef28eac05c5fbb11e6f02a50da903def70f94b3018e93340568b"
os.environ['TUSHARE_TOKEN'] = TUSHARE_TOKEN

def get_hs300_basic():
    """
    使用tushare基础接口获取沪深300数据
    """
    print("=" * 70)
    print("📊 tushare基础接口: 沪深300数据获取")
    print("=" * 70)
    
    try:
        import tushare as ts
        
        print(f"✅ tushare库导入成功")
        print(f"🔑 Token: {TUSHARE_TOKEN[:10]}...")
        
        # 初始化pro接口
        pro = ts.pro_api(TUSHARE_TOKEN)
        print("✅ tushare pro接口初始化成功")
        
        # 测试Token权限
        print("\n🔍 测试Token权限...")
        
        # 方法1: 尝试获取交易日历 (基础权限)
        try:
            cal_data = pro.trade_cal(exchange='SSE', start_date='20240301', end_date='20240310')
            if cal_data is not None:
                print(f"✅ 交易日历接口可用: 返回 {len(cal_data)} 条记录")
                print(f"   示例: {cal_data.iloc[0]['cal_date']} - {cal_data.iloc[0]['is_open']}")
            else:
                print("⚠️ 交易日历接口返回空数据")
        except Exception as e:
            print(f"❌ 交易日历接口错误: {e}")
        
        # 方法2: 尝试获取股票列表 (基础权限)
        try:
            stock_list = pro.stock_basic(exchange='', list_status='L', fields='ts_code,symbol,name,area,industry,list_date')
            if stock_list is not None:
                print(f"✅ 股票列表接口可用: 返回 {len(stock_list)} 只股票")
                # 查找沪深300
                hs300_in_list = stock_list[stock_list['symbol'] == '000300']
                if not hs300_in_list.empty:
                    print(f"✅ 在股票列表中找到沪深300: {hs300_in_list.iloc[0]['name']}")
                else:
                    print("⚠️ 在股票列表中未找到沪深300")
            else:
                print("⚠️ 股票列表接口返回空数据")
        except Exception as e:
            print(f"❌ 股票列表接口错误: {e}")
        
        # 方法3: 尝试获取指数基本信息
        try:
            index_info = pro.index_basic(market='SSE')
            if index_info is not None:
                print(f"✅ 指数基本信息接口可用: 返回 {len(index_info)} 个指数")
                # 查找沪深300
                hs300_info = index_info[index_info['ts_code'] == '000300.SH']
                if not hs300_info.empty:
                    print(f"✅ 在指数列表中找到沪深300:")
                    print(f"   代码: {hs300_info.iloc[0]['ts_code']}")
                    print(f"   名称: {hs300_info.iloc[0]['name']}")
                    print(f"   发布日: {hs300_info.iloc[0]['list_date']}")
                    print(f"   类型: {hs300_info.iloc[0]['market']}")
                else:
                    print("⚠️ 在指数列表中未找到沪深300")
            else:
                print("⚠️ 指数基本信息接口返回空数据")
        except Exception as e:
            print(f"❌ 指数基本信息接口错误: {e}")
        
        # 方法4: 尝试使用旧版tushare接口
        print("\n🔍 尝试使用旧版tushare接口...")
        try:
            # 使用旧版get_k_data
            import tushare as ts_old
            
            # 获取沪深300日线数据
            df_kdata = ts_old.get_k_data('000300', index=True, start='2024-03-01')
            if df_kdata is not None and not df_kdata.empty:
                print(f"✅ 旧版get_k_data接口可用: 返回 {len(df_kdata)} 条记录")
                
                # 获取最新数据
                latest_kdata = df_kdata.iloc[-1]
                print(f"\n📈 沪深300最新数据 (旧版接口):")
                print(f"   日期: {latest_kdata['date']}")
                print(f"   收盘: {latest_kdata['close']:.2f}")
                print(f"   开盘: {latest_kdata['open']:.2f}")
                print(f"   最高: {latest_kdata['high']:.2f}")
                print(f"   最低: {latest_kdata['low']:.2f}")
                print(f"   成交量: {latest_kdata['volume']:,.0f}")
                
                # 计算涨跌幅
                if len(df_kdata) > 1:
                    prev_close = df_kdata.iloc[-2]['close']
                    change_pct = (latest_kdata['close'] - prev_close) / prev_close * 100
                    print(f"   涨跌幅: {change_pct:+.2f}%")
                
                return {
                    'source': 'tushare_old_get_k_data',
                    'price': float(latest_kdata['close']),
                    'date': latest_kdata['date'],
                    'volume': float(latest_kdata['volume'])
                }
            else:
                print("⚠️ 旧版接口返回空数据")
        except Exception as e:
            print(f"❌ 旧版接口错误: {e}")
        
        # 方法5: 尝试使用get_hist_data
        try:
            df_hist = ts_old.get_hist_data('000300', start='2024-03-01')
            if df_hist is not None and not df_hist.empty:
                print(f"✅ get_hist_data接口可用: 返回 {len(df_hist)} 条记录")
                
                # 获取最新数据
                latest_date = df_hist.index[0]  # 按日期降序排列
                latest_hist = df_hist.loc[latest_date]
                
                print(f"\n📈 沪深300最新数据 (get_hist_data):")
                print(f"   日期: {latest_date}")
                print(f"   收盘: {latest_hist['close']:.2f}")
                print(f"   涨跌幅: {latest_hist['p_change']:.2f}%")
                print(f"   成交量: {latest_hist['volume']:,.0f}")
                print(f"   成交额: {latest_hist['amount']:,.0f}")
                
                return {
                    'source': 'tushare_old_get_hist_data',
                    'price': float(latest_hist['close']),
                    'change': float(latest_hist['p_change']),
                    'date': latest_date,
                    'volume': float(latest_hist['volume']),
                    'amount': float(latest_hist['amount'])
                }
            else:
                print("⚠️ get_hist_data返回空数据")
        except Exception as e:
            print(f"❌ get_hist_data接口错误: {e}")
        
        # 方法6: 尝试使用简单接口
        try:
            # 获取实时行情
            df_realtime = ts_old.get_realtime_quotes('000300')
            if df_realtime is not None and not df_realtime.empty:
                print(f"✅ get_realtime_quotes接口可用")
                
                realtime_data = df_realtime.iloc[0]
                print(f"\n📈 沪深300实时行情:")
                print(f"   名称: {realtime_data['name']}")
                print(f"   当前价: {realtime_data['price']}")
                print(f"   昨收: {realtime_data['pre_close']}")
                print(f"   今开: {realtime_data['open']}")
                print(f"   成交量: {realtime_data['volume']}")
                print(f"   成交额: {realtime_data['amount']}")
                
                # 计算涨跌幅
                if realtime_data['pre_close'] and float(realtime_data['pre_close']) > 0:
                    change_pct = (float(realtime_data['price']) - float(realtime_data['pre_close'])) / float(realtime_data['pre_close']) * 100
                    print(f"   涨跌幅: {change_pct:+.2f}%")
                
                return {
                    'source': 'tushare_get_realtime_quotes',
                    'price': float(realtime_data['price']),
                    'pre_close': float(realtime_data['pre_close']),
                    'name': realtime_data['name'],
                    'volume': realtime_data['volume'],
                    'amount': realtime_data['amount']
                }
            else:
                print("⚠️ 实时行情接口返回空数据")
        except Exception as e:
            print(f"❌ 实时行情接口错误: {e}")
        
        print("\n❌ 所有接口均无法获取沪深300实时数据")
        print("\n💡 建议:")
        print("1. 检查Token权限级别")
        print("2. 使用东方财富接口 (已通过首席架构师验证)")
        print("3. 考虑升级Tushare Pro会员")
        
        return None
        
    except ImportError as e:
        print(f"❌ tushare库导入失败: {e}")
        return None
        
    except Exception as e:
        print(f"❌ 数据获取过程发生错误: {e}")
        import traceback
        print("\n📋 错误详情:")
        print(traceback.format_exc())
        return None

def main():
    """主函数"""
    print("🚀 开始使用tushare基础接口获取沪深300数据...")
    
    result = get_hs300_basic()
    
    if result:
        print("\n" + "=" * 70)
        print("🏆 tushare基础接口执行完成")
        print("=" * 70)
        print(f"📊 沪深300数据获取成功:")
        print(f"   数据源: {result['source']}")
        
        if 'price' in result:
            print(f"   点位: {result['price']:.2f}")
        
        if 'change' in result:
            print(f"   涨跌: {result['change']:+.2f}%")
        
        if 'date' in result:
            print(f"   日期: {result['date']}")
        
        if 'name' in result:
            print(f"   名称: {result['name']}")
        
        # 与首席架构师验证数据对比
        if 'price' in result:
            architect_price = 4658.33
            price_diff = abs(result['price'] - architect_price)
            print(f"\n🔍 与首席架构师验证数据对比:")
            print(f"   tushare点位: {result['price']:.2f}")
            print(f"   架构师点位: {architect_price:.2f} (东方财富实时)")
            print(f"   点位差异: {price_diff:.2f}")
            
            if price_diff < 50:  # 50点以内差异可接受
                print(f"✅ 数据一致性: 可接受 (差异 < 50点)")
            else:
                print(f"⚠️ 数据一致性: 差异较大 ({price_diff:.2f}点)")
        
        print(f"\n⏰ 查询时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    else:
        print("\n❌ 数据获取失败")

if __name__ == "__main__":
    main()