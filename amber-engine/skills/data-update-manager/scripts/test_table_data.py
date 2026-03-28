#!/usr/bin/env python3
"""
测试表格数据更新
"""

import json
import os

# 读取缓存数据
cache_file = "output/static/data/unified_data_cache.json"
with open(cache_file, 'r') as f:
    cache_data = json.load(f)

print("缓存中的数据:")
print(f"沪深300: {cache_data['indices']['沪深300']['close']} ({cache_data['indices']['沪深300']['pct_chg']}%)")
print(f"创业板指: {cache_data['indices']['创业板指']['close']} ({cache_data['indices']['创业板指']['pct_chg']}%)")

# 读取页面中的数据
with open("output/index.html", 'r', encoding='utf-8') as f:
    content = f.read()

import re

# 提取沪深300数据
hs300_pattern = r'data-index="沪深300".*?<td class="col-price">([^<]*)</td>.*?<td class="col-change[^"]*">([^<]*)</td>'
hs300_match = re.search(hs300_pattern, content, re.DOTALL)
if hs300_match:
    print(f"\n页面中的沪深300:")
    print(f"  价格: {hs300_match.group(1)}")
    print(f"  涨跌幅: {hs300_match.group(2)}")

# 提取创业板指数据
cybz_pattern = r'data-index="创业板指".*?<td class="col-price">([^<]*)</td>.*?<td class="col-change[^"]*">([^<]*)</td>'
cybz_match = re.search(cybz_pattern, content, re.DOTALL)
if cybz_match:
    print(f"\n页面中的创业板指:")
    print(f"  价格: {cybz_match.group(1)}")
    print(f"  涨跌幅: {cybz_match.group(2)}")

# 检查表格更新时间
time_pattern = r'table-update-time">更新: ([^<]*)</span>'
time_match = re.search(time_pattern, content)
if time_match:
    print(f"\n表格更新时间: {time_match.group(1)}")