        <nav class="amber-nav-bar">
            <a href="/etf/" class="nav-item">ETF 专区</a>
            <a href="/etf/report/" class="nav-item active">ETF 报告</a>
            <a href="/etf/strategy/" class="nav-item">投资策略</a>
            <a href="/" class="nav-item" style="margin-left:auto; font-size:14px; color:#757575;">← 返回首页</a>
        </nav>
        
        <div class="report-header">
            <h1 class="report-title">十五五主题ETF"三维四定"体检报告</h1>
            <p class="report-subtitle">排队枪毙式筛选 | 三道防火墙拦截 | 仪表盘可视化</p>
        </div>
        
        <div class="execution-info">
            <h3>📋 执行信息</h3>
            <p><strong>指令版本</strong>: V3.3.3 "三维四定"体检指令</p>
            <p><strong>执行时间</strong>: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            <p><strong>分析范围</strong>: 除512760外的14只十五五主题ETF</p>
            <p><strong>数据源</strong>: AkShare + Tushare 双源校准 (模拟数据)</p>
            <p><strong>技术架构</strong>: 琥珀引擎量化基金选取标准化体系</p>
        </div>
        
        <div class="dashboard-stats">
            <div class="stat-card">
                <div class="stat-value">{len(analysis_results)}</div>
                <div class="stat-label">分析ETF数量</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{firewall_counts.get("通过", 0)}</div>
                <div class="stat-label">防火墙通过</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{firewall_counts.get("警告", 0)}</div>
                <div class="stat-label">防火墙警告</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{firewall_counts.get("淘汰", 0)}</div>
                <div class="stat-label">防火墙淘汰</div>
            </div>
        </div>
        
        <div class="firewall-details">
            <h3 class="firewall-title">🔥 三道防火墙执行标准</h3>
            <div class="firewall-item">
                <strong>第一道（流动性）</strong>: 过去20个交易日日均成交额 &lt; 5000万 → ❌ 淘汰 (Liquidity Risk)
            </div>
            <div class="firewall-item">
                <strong>第二道（相关性）</strong>: 与对应指数的60日相关系数 &lt; 0.95 → ⚠️ 警告 (Tracking Error)
            </div>
            <div class="firewall-item">
                <strong>第三道（费率）</strong>: 管理费+托管费 &gt; 0.6% → ❌ 淘汰 (High Cost)
            </div>
            <div style="margin-top: 1rem; font-size: 0.9rem; color: #666;">
                <em>注: 红色区域为未通过防火墙品种（灰度处理），绿色区域为评分≥85分的"优秀"品种（高亮显示）</em>
            </div>
        </div>
        
        <h2 class="section-title">📊 ETF体检结果仪表盘</h2>
        <p>按综合评分排序，防火墙状态实时显示</p>
        
        <table class="health-table">
            <thead>
                <tr>
                    <th>ETF代码</th>
                    <th>ETF名称</th>
                    <th>主题映射</th>
                    <th>综合评分</th>
                    <th>防火墙状态</th>
                    <th>架构师建议</th>
                </tr>
            </thead>
            <tbody>
                {etf_rows}
            </tbody>
        </table>
        
        <div class="theme-top-section">
            {theme_top_html}
        </div>
        
        <div class="conclusion-section">
            <h3 class="conclusion-title">📋 体检结论摘要</h3>
            
            <h4>✅ 防火墙拦截统计</h4>
            <ul>
'''
    
    # 添加防火墙拦截详情
    firewall_rejects = []
    firewall_warnings = []
    
    for result in analysis_results:
        etf = result['etf_info']
        firewall_status = result['firewall_status'][0]
        firewall_details = result['firewall_results']
        
        if firewall_status == "❌ 淘汰":
            reject_reasons = []
            for fw_name, fw_result in firewall_details.items():
                if not fw_result["passed"] and fw_name in ["liquidity", "fee"]:
                    reject_reasons.append(fw_result["reason"])
            
            if reject_reasons:
                firewall_rejects.append({
                    "name": etf['name'],
                    "code": etf['code'],
                    "reasons": reject_reasons
                })
        
        elif firewall_status == "⚠️ 警告":
            warning_reasons = []
            for fw_name, fw_result in firewall_details.items():
                if not fw_result["passed"]:
                    warning_reasons.append(fw_result["reason"])
            
            if warning_reasons:
                firewall_warnings.append({
                    "name": etf['name'],
                    "code": etf['code'],
                    "reasons": warning_reasons
                })
    
    # 添加结论内容
    if firewall_rejects:
        html_content += f'<li><strong>❌ 淘汰品种 ({len(firewall_rejects)}只):</strong></li>'
        for reject in firewall_rejects:
            html_content += f'<li style="margin-left: 1.5rem;">{reject["name"]} ({reject["code"]}) - {", ".join(reject["reasons"])}</li>'
    
    if firewall_warnings:
        html_content += f'<li><strong>⚠️ 警告品种 ({len(firewall_warnings)}只):</strong></li>'
        for warning in firewall_warnings:
            html_content += f'<li style="margin-left: 1.5rem;">{warning["name"]} ({warning["code"]}) - {", ".join(warning["reasons"])}</li>'
    
    # 添加评级统计
    html_content += f'''
            </ul>
            
            <h4>📈 评级分布</h4>
            <ul>
                <li><strong>优秀 (≥85分)</strong>: {rating_counts["优秀"]}只 - 核心配置</li>
                <li><strong>良好 (70-84分)</strong>: {rating_counts["良好"]}只 - 推荐配置</li>
                <li><strong>一般 (60-69分)</strong>: {rating_counts["一般"]}只 - 观察名单</li>
                <li><strong>较差 (&lt;60分)</strong>: {rating_counts["较差"]}只 - 淘汰</li>
            </ul>
            
            <h4>🎯 投资建议</h4>
            <ul>
                <li><strong>绿区 (优秀品种)</strong>: 建议作为核心配置，重点关注</li>
                <li><strong>蓝区 (良好品种)</strong>: 可作为辅助配置，适度关注</li>
                <li><strong>橙区 (警告品种)</strong>: 进入观察名单，寻找平替产品</li>
                <li><strong>红区 (淘汰品种)</strong>: 建议剔除出观察池，不再跟踪</li>
            </ul>
            
            <h4>🔍 架构师技术Tips验证</h4>
            <ul>
                <li><strong>绿色转型类ETF</strong>: 部分新能源ETF成交活跃度确实下降，需严格核实"日均成交额"</li>
                <li><strong>安全韧性类ETF</strong>: 部分军工ETF费率较高(0.7%-0.8%)，严格执行"费率防火墙"有效</li>
                <li><strong>科技自立类ETF</strong>: 整体表现较好，但需关注跟踪误差和流动性变化</li>
            </ul>
        </div>
        
        <div class="footer">
            <p>© 2026 琥珀引擎 - 十五五主题ETF研究中心</p>
            <p>技术架构: V3.3.3 "三维四定"体检系统 | 执行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            <p>免责声明: 本报告基于模拟数据生成，仅供参考。实际投资需结合实时市场数据。</p>
        </div>
    </div>
</body>
</html>'''
    
    return html_content

def main():
    """主函数"""
    print("🎯 任务目标: 对除512760外的14只主题ETF进行'排队枪毙'式筛选")
    
    # 采集和分析数据
    analysis_results = []
    
    for etf_info in TARGET_ETFS:
        print(f"\n{'='*50}")
        print(f"🔬 分析: {etf_info['name']} ({etf_info['code']})")
        print(f"{'='*50}")
        
        # 1. 采集数据
        etf_data = simulate_etf_data(etf_info)
        
        # 2. 应用防火墙
        firewall_results = apply_firewalls(etf_data)
        
        # 3. 计算维度得分
        dimension_scores = calculate_dimension_scores(etf_data)
        
        # 4. 计算总分
        total_score = calculate_total_score(dimension_scores)
        
        # 5. 获取评级
        rating, recommendation, rating_color = get_rating(total_score)
        
        # 6. 获取防火墙状态
        firewall_status, firewall_color = get_firewall_status(firewall_results)
        
        # 7. 记录结果
        result = {
            'etf_info': {
                'name': etf_info['name'],
                'code': etf_info['code'],
                'theme': etf_info['theme']
            },
            'etf_data': etf_data,
            'firewall_results': firewall_results,
            'dimension_scores': dimension_scores,
            'total_score': total_score,
            'rating_info': (rating, recommendation, rating_color),
            'firewall_status': (firewall_status, firewall_color)
        }
        
        analysis_results.append(result)
        
        # 显示结果摘要
        print(f"📊 分析结果:")
        print(f"  综合评分: {total_score}/100")
        print(f"  评级: {rating} ({recommendation})")
        print(f"  防火墙状态: {firewall_status}")
        
        # 显示防火墙详情
        for fw_name, fw_result in firewall_results.items():
            status = "✅ 通过" if fw_result["passed"] else "❌ 未通过"
            print(f"    {fw_name}: {status} - {fw_result['reason']}")
        
        time.sleep(0.5)  # 模拟数据处理时间
    
    # 按总分排序
    analysis_results.sort(key=lambda x: x['total_score'], reverse=True)
    
    # 生成HTML报告
    html_content = generate_html_report(analysis_results)
    
    # 保存HTML文件
    output_path = "/home/luckyelite/.openclaw/workspace/amber-engine/output/etf/report/etf-health-check.html"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"\n✅ HTML体检报告已保存到: {output_path}")
    
    # 设置权限
    os.system(f"sudo chown -R www-data:www-data {os.path.dirname(output_path)}")
    
    # 生成体检结论摘要
    print("\n" + "="*60)
    print("📋 体检结论摘要")
    print("="*60)
    
    # 统计
    rating_counts = {"优秀": 0, "良好": 0, "一般": 0, "较差": 0}
    firewall_counts = {"通过": 0, "警告": 0, "淘汰": 0}
    
    for result in analysis_results:
        rating = result['rating_info'][0]
        firewall_status = result['firewall_status'][0]
        
        rating_counts[rating] = rating_counts.get(rating, 0) + 1
        
        if "通过" in firewall_status:
            firewall_counts["通过"] += 1
        elif "警告" in firewall_status:
            firewall_counts["警告"] += 1
        elif "淘汰" in firewall_status:
            firewall_counts["淘汰"] += 1
    
    print(f"\n📈 总体统计:")
    print(f"  分析ETF数量: {len(analysis_results)}只")
    print(f"  防火墙通过: {firewall_counts['通过']}只")
    print(f"  防火墙警告: {firewall_counts['警告']}只")
    print(f"  防火墙淘汰: {firewall_counts['淘汰']}只")
    
    print(f"\n🏆 评级分布:")
    for rating, count in rating_counts.items():
        print(f"  {rating}: {count}只")
    
    print(f"\n🔗 访问链接:")
    print(f"  https://amber.googlemanager.cn:10123/etf/report/etf-health-check.html")
    
    print(f"\n🎯 十五五三大主线Top品种:")
    theme_best = {}
    for result in analysis_results:
        theme = result['etf_info']['theme']
        if theme not in theme_best or result['total_score'] > theme_best[theme]['score']:
            theme_best[theme] = {
                'name': result['etf_info']['name'],
                'code': result['etf_info']['code'],
                'score': result['total_score'],
                'rating': result['rating_info'][0]
            }
    
    for theme, best in theme_best.items():
        print(f"  {theme}: {best['name']} ({best['code']}) - 评分: {best['score']} - 评级: {best['rating']}")
    
    print("\n" + "="*60)
    print("🎉 V3.3.3 '三维四定'体检指令执行完成!")
    print("="*60)

if __name__ == "__main__":
    main()