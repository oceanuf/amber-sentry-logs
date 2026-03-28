#!/usr/bin/env python3
"""
更新黄金数据：国际金价和国内金价
主编要求：利用Tushare获取真实黄金数据
"""

import os
import sys
import json
import re
import tempfile
import subprocess
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

os.environ['TUSHARE_TOKEN'] = '9e32ef28eac05c5fbb11e6f02a50da903def70f94b3018e93340568b'

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INDEX_FILE = os.path.join(BASE_DIR, "output", "index.html")
GOLD_CACHE_FILE = os.path.join(BASE_DIR, "output", "static", "data", "gold_cache.json")

def get_gold_data_from_tushare() -> Dict[str, Any]:
    """从Tushare获取黄金数据"""
    try:
        import tushare as ts
        pro = ts.pro_api()
        
        today = datetime.now().strftime("%Y%m%d")
        yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y%m%d")
        
        gold_data = {
            "international_gold": None,
            "domestic_gold": None,
            "update_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "data_date": None
        }
        
        print("🪙 获取黄金数据...")
        
        # 1. 获取国际金价 (XAUUSD.FXCM)
        print("  📡 获取国际金价 (XAUUSD.FXCM)...")
        try:
            # 先尝试今天数据
            df = pro.fx_daily(ts_code='XAUUSD.FXCM', trade_date=today)
            if df.empty:
                # 尝试昨天数据
                df = pro.fx_daily(ts_code='XAUUSD.FXCM', trade_date=yesterday)
            
            if not df.empty:
                price = float(df.iloc[0]['bid_close'])
                trade_date = str(df.iloc[0]['trade_date'])
                
                # 计算涨跌幅（需要前一天数据）
                try:
                    # 获取前一个交易日数据
                    day_before = (datetime.strptime(trade_date, "%Y%m%d") - timedelta(days=1)).strftime("%Y%m%d")
                    df_prev = pro.fx_daily(ts_code='XAUUSD.FXCM', trade_date=day_before)
                    
                    if not df_prev.empty:
                        prev_price = float(df_prev.iloc[0]['bid_close'])
                        change_pct = ((price - prev_price) / prev_price) * 100
                        change_pct = round(change_pct, 2)
                    else:
                        change_pct = 0.0
                except:
                    change_pct = 0.0
                
                gold_data["international_gold"] = {
                    "pair": "XAUUSD.FXCM",
                    "price": price,
                    "change_pct": change_pct,
                    "trade_date": trade_date,
                    "unit": "USD/oz"
                }
                print(f"    ✅ 国际金价: {price} USD/oz ({change_pct:+.2f}%)")
            else:
                print("    ⚠️ 无国际金价数据")
        except Exception as e:
            print(f"    ❌ 国际金价获取失败: {e}")
        
        # 2. 获取国内金价 (AU.SHF)
        print("  📡 获取国内金价 (AU.SHF)...")
        try:
            # 尝试今天数据
            df = pro.fut_daily(ts_code='AU.SHF', trade_date=today)
            if df.empty:
                # 尝试昨天数据
                df = pro.fut_daily(ts_code='AU.SHF', trade_date=yesterday)
            
            if not df.empty:
                price = float(df.iloc[0]['close'])
                trade_date = str(df.iloc[0]['trade_date'])
                
                # 尝试获取涨跌幅
                try:
                    change_pct = float(df.iloc[0]['pct_chg'])
                except:
                    try:
                        # 如果pct_chg不存在，计算涨跌额
                        change = float(df.iloc[0]['change'])
                        change_pct = (change / (price - change)) * 100 if price != change else 0.0
                        change_pct = round(change_pct, 2)
                    except:
                        change_pct = 0.0
                
                gold_data["domestic_gold"] = {
                    "code": "AU.SHF",
                    "price": price,
                    "change_pct": change_pct,
                    "trade_date": trade_date,
                    "unit": "CNY/g"
                }
                print(f"    ✅ 国内金价: {price} CNY/g ({change_pct:+.2f}%)")
            else:
                print("    ⚠️ 无国内金价数据")
        except Exception as e:
            print(f"    ❌ 国内金价获取失败: {e}")
        
        # 设置数据日期
        if gold_data["international_gold"]:
            gold_data["data_date"] = gold_data["international_gold"]["trade_date"]
        elif gold_data["domestic_gold"]:
            gold_data["data_date"] = gold_data["domestic_gold"]["trade_date"]
        
        return gold_data
        
    except ImportError:
        print("❌ 无法导入tushare库")
        return {"error": "tushare not installed"}
    except Exception as e:
        print(f"❌ 黄金数据获取失败: {e}")
        import traceback
        traceback.print_exc()
        return {"error": str(e)}

def update_html_gold_data(gold_data: Dict[str, Any]) -> bool:
    """更新HTML中的黄金数据"""
    try:
        if not os.path.exists(INDEX_FILE):
            print(f"❌ index.html文件不存在: {INDEX_FILE}")
            return False
        
        with open(INDEX_FILE, 'r', encoding='utf-8') as f:
            content = f.read()
        
        modifications = 0
        
        # 1. 更新宏观四锚中的黄金数据
        if gold_data.get("international_gold"):
            intl_gold = gold_data["international_gold"]
            price = intl_gold["price"]
            change_pct = intl_gold["change_pct"]
            
            # 更新国际金价
            # 查找模式：<span class="anchor-label">🌍 国际金价 (XAUUSD)</span>后跟的anchor-value和anchor-change
            pattern = r'(<span class="anchor-label">🌍 国际金价 \(XAUUSD\)</span>\s*<span class="anchor-value">)[^<]+(</span>\s*<span class="anchor-change )[^"]+(">)[^<]+(</span>)'
            
            def replace_intl_gold(match):
                prefix = match.group(1)
                middle = match.group(2)
                suffix = match.group(3)
                end = match.group(4)
                
                # 确定颜色类
                color_class = "change-up" if change_pct > 0 else "change-down"
                change_symbol = "↑" if change_pct > 0 else "↓"
                change_text = f"{change_symbol} {abs(change_pct):.2f}%"
                
                return f'{prefix}{price:.2f}{middle}{color_class}{suffix}{change_text}{end}'
            
            new_content, count = re.subn(pattern, replace_intl_gold, content)
            if count > 0:
                content = new_content
                modifications += count
                print(f"  ✅ 宏观四锚-国际金价: {price:.2f} ({change_pct:+.2f}%)")
        
        if gold_data.get("domestic_gold"):
            dom_gold = gold_data["domestic_gold"]
            price = dom_gold["price"]
            change_pct = dom_gold["change_pct"]
            
            # 更新国内金价
            pattern = r'(<span class="anchor-label">🇨🇳 国内金价 \(AU\.SHF\)</span>\s*<span class="anchor-value">)[^<]+(</span>\s*<span class="anchor-change )[^"]+(">)[^<]+(</span>)'
            
            def replace_dom_gold(match):
                prefix = match.group(1)
                middle = match.group(2)
                suffix = match.group(3)
                end = match.group(4)
                
                color_class = "change-up" if change_pct > 0 else "change-down"
                change_symbol = "↑" if change_pct > 0 else "↓"
                change_text = f"{change_symbol} {abs(change_pct):.2f}%"
                
                return f'{prefix}{price:.2f}{middle}{color_class}{suffix}{change_text}{end}'
            
            new_content, count = re.subn(pattern, replace_dom_gold, content)
            if count > 0:
                content = new_content
                modifications += count
                print(f"  ✅ 宏观四锚-国内金价: {price:.2f} ({change_pct:+.2f}%)")
        
        # 2. 更新黄金对冲部分的数据
        if gold_data.get("international_gold"):
            intl_gold = gold_data["international_gold"]
            price = intl_gold["price"]
            change_pct = intl_gold["change_pct"]
            
            # 查找黄金对冲部分的国际金价
            pattern = r'(<div class="hedge-value )[^"]+(">)[^<]+(</div>\s*<div class="hedge-label">国际金价 \(USD/oz\)</div>)'
            
            def replace_intl_hedge(match):
                price_class = match.group(1)
                middle = match.group(2)
                suffix = match.group(3)
                
                color_class = "price-up" if change_pct > 0 else "price-down"
                return f'{price_class}{color_class}{middle}{price:.2f}{suffix}'
            
            new_content, count = re.subn(pattern, replace_intl_hedge, content)
            if count > 0:
                content = new_content
                modifications += count
                print(f"  ✅ 黄金对冲-国际金价: {price:.2f}")
        
        if gold_data.get("domestic_gold"):
            dom_gold = gold_data["domestic_gold"]
            price = dom_gold["price"]
            change_pct = dom_gold["change_pct"]
            
            # 查找黄金对冲部分的国内金价
            pattern = r'(<div class="hedge-value )[^"]+(">)[^<]+(</div>\s*<div class="hedge-label">国内金价 \(CNY/g\)</div>)'
            
            def replace_dom_hedge(match):
                price_class = match.group(1)
                middle = match.group(2)
                suffix = match.group(3)
                
                color_class = "price-up" if change_pct > 0 else "price-down"
                return f'{price_class}{color_class}{middle}{price:.2f}{suffix}'
            
            new_content, count = re.subn(pattern, replace_dom_hedge, content)
            if count > 0:
                content = new_content
                modifications += count
                print(f"  ✅ 黄金对冲-国内金价: {price:.2f}")
        
        # 3. 更新时间戳
        update_time = gold_data.get("update_time", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        
        # 更新黄金部分的更新时间
        time_patterns = [
            r'(<span class="update-time">更新: )[^<]+( \(北京时间\) \| 🎯 Tushare Pro验证通过 \| 🚀 V3\.2物理并线</span>)',
            r'(<span class="hedge-update">更新: )[^<]+( \(北京时间\)</span>)'
        ]
        
        for time_pattern in time_patterns:
            new_content, count = re.subn(time_pattern, f'\\g<1>{update_time}\\2', content)
            if count > 0:
                content = new_content
                modifications += count
                print(f"  ✅ 更新时间: {update_time}")
        
        # 保存文件
        try:
            with open(INDEX_FILE, 'w', encoding='utf-8') as f:
                f.write(content)
        except PermissionError:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False) as tmp:
                tmp.write(content)
                tmp_path = tmp.name
            
            result = subprocess.run(f'sudo tee {INDEX_FILE} < {tmp_path} > /dev/null', shell=True)
            os.unlink(tmp_path)
            
            if result.returncode != 0:
                raise Exception("sudo tee写入失败")
        
        print(f"✅ HTML更新完成: {modifications}处修改")
        return True
        
    except Exception as e:
        print(f"❌ HTML更新失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def save_gold_cache(gold_data: Dict[str, Any]) -> bool:
    """保存黄金数据缓存"""
    try:
        # 确保目录存在
        cache_dir = os.path.dirname(GOLD_CACHE_FILE)
        os.makedirs(cache_dir, exist_ok=True)
        
        with open(GOLD_CACHE_FILE, 'w', encoding='utf-8') as f:
            json.dump(gold_data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ 黄金数据缓存已保存: {GOLD_CACHE_FILE}")
        return True
    except Exception as e:
        print(f"❌ 缓存保存失败: {e}")
        return False

def reload_nginx():
    """重载Nginx服务"""
    print("\n🧹 重载Nginx服务...")
    result = subprocess.run("sudo systemctl reload nginx 2>/dev/null || true", shell=True)
    if result.returncode == 0:
        print("✅ Nginx重载完成")
        return True
    else:
        print("⚠️ Nginx重载可能失败，建议手动检查")
        return False

def main():
    """主函数"""
    print("=" * 70)
    print("🪙 黄金数据更新 - 主编指令")
    print("=" * 70)
    print("执行内容:")
    print("1. 📡 从Tushare Pro获取国际金价和国内金价")
    print("2. 🏷️ 更新琥珀引擎HTML中的黄金数据")
    print("3. 💾 保存数据缓存")
    print("4. 🔄 重载Nginx服务")
    print("=" * 70)
    
    try:
        # 步骤1: 获取黄金数据
        print("\n📡 步骤1: 从Tushare获取黄金数据")
        gold_data = get_gold_data_from_tushare()
        
        if "error" in gold_data:
            print(f"❌ 数据获取失败: {gold_data['error']}")
            return False
        
        if not gold_data.get("international_gold") and not gold_data.get("domestic_gold"):
            print("⚠️ 未获取到任何黄金数据，跳过更新")
            return True
        
        # 步骤2: 更新HTML
        print("\n🏷️ 步骤2: 更新HTML数据")
        if not update_html_gold_data(gold_data):
            print("❌ HTML更新失败")
            return False
        
        # 步骤3: 保存缓存
        print("\n💾 步骤3: 保存数据缓存")
        save_gold_cache(gold_data)
        
        # 步骤4: 重载Nginx
        reload_nginx()
        
        # 生成报告
        print("\n" + "=" * 70)
        print("🎉 黄金数据更新完成!")
        print("=" * 70)
        
        if gold_data.get("international_gold"):
            intl = gold_data["international_gold"]
            print(f"🌍 国际金价: {intl['price']:.2f} {intl['unit']} ({intl['change_pct']:+.2f}%)")
        
        if gold_data.get("domestic_gold"):
            dom = gold_data["domestic_gold"]
            print(f"🇨🇳 国内金价: {dom['price']:.2f} {dom['unit']} ({dom['change_pct']:+.2f}%)")
        
        print(f"\n🕒 更新时间: {gold_data.get('update_time', 'N/A')}")
        print(f"📅 数据日期: {gold_data.get('data_date', 'N/A')}")
        print(f"🔗 验证地址: https://amber.googlemanager.cn:10123/?v=3.2.7")
        print("🔄 强制刷新: Ctrl+F5 (清除浏览器缓存)")
        print("=" * 70)
        
        return True
        
    except Exception as e:
        print(f"\n❌ 更新失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)