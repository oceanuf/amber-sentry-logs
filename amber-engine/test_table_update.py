#!/usr/bin/env python3
"""
测试表格更新正则表达式
"""

import re

# 模拟表格行
test_html = '''<tr class="index-row" data-index="沪深300" data-code="000300.SH">
                                    <td class="col-index">
                                        <span class="index-name">沪深300</span>
                                    </td>
                                    <td class="col-code">000300.SH</td>
                                    <td class="col-market">A股</td>
                                    <td class="col-price">4567.02</td>
                                    <td class="col-change price-down price-down">-0.35%</td>
                                    <td class="col-status">
                                        <span class="status-badge verified">已验证</span>
                                    </td>
                                    <td class="col-source">Tushare Pro</td>
                                </tr>'''

# 测试正则表达式
pattern1 = r'(<tr class="index-row" data-index="沪深300"[^>]*>.*?<td class="col-price">)[^<]*(</td>.*?<td class="col-change[^"]*">)[^<]*(</td>)'

match1 = re.search(pattern1, test_html, re.DOTALL)
print("模式1匹配结果:", "成功" if match1 else "失败")
if match1:
    print("  组1:", match1.group(1)[:50] + "...")
    print("  组2:", match1.group(2))
    print("  组3:", match1.group(3))

# 更简单的模式
pattern2 = r'data-index="沪深300".*?<td class="col-price">([^<]*)</td>.*?<td class="col-change[^"]*">([^<]*)</td>'

match2 = re.search(pattern2, test_html, re.DOTALL)
print("\n模式2匹配结果:", "成功" if match2 else "失败")
if match2:
    print("  价格:", match2.group(1))
    print("  涨跌幅:", match2.group(2))

# 测试替换
def replace_func(match):
    return match.group(0).replace(match.group(1), "TEST_PRICE").replace(match.group(2), "TEST_CHANGE")

new_html = re.sub(pattern2, replace_func, test_html, flags=re.DOTALL)
print("\n替换结果:", new_html[:100] + "...")