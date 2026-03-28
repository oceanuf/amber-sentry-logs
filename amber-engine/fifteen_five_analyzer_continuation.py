period}}</strong></p>
            <p>数据归一化基准：2026年3月19日收盘价</p>
        </div>
        
        <div class="hs300-benchmark">
            <h3>📊 沪深300基准表现</h3>
            <div class="hs300-value">{{hs300_start}} → {{hs300_end}} ({{hs300_change}}%)</div>
            <p>所有ETF的超额收益均以此基准计算</p>
        </div>
        
        <h2 class="section-title">📈 ETF主题表现分析</h2>
        <p>按超额收益排序，跑赢沪深300的ETF使用<span style="color:#f44336; font-weight:bold;">中国红</span>高亮显示</p>
        
        <table class="etf-table">
            <thead>
                <tr>
                    <th>ETF名称</th>
                    <th>代码</th>
                    <th>主要主题</th>
                    <th>星级</th>
                    <th>区间表现</th>
                    <th>超额收益</th>
                    <th>最新净值</th>
                </tr>
            </thead>
            <tbody>
                {% for etf in etfs %}
                <tr class="{% if etf.outperforms %}outperform-row{% endif %} {% if etf.main_theme == '科技自立' %}theme-tech{% elif etf.main_theme == '绿色转型' %}theme-green{% elif etf.main_theme == '安全韧性' %}theme-safety{% endif %}">
                    <td><strong>{{etf.name}}</strong></td>
                    <td><code>{{etf.ts_code}}</code></td>
                    <td>
                        <span style="color: {{theme_colors.get(etf.main_theme, '#666')}}; font-weight:600;">
                            {{etf.main_theme if etf.main_theme else '其他'}}
                        </span>
                    </td>
                    <td><span class="star-rating">{{etf.star_rating}}</span></td>
                    <td>
                        {{etf.start_price}} → {{etf.end_price}}<br>
                        <strong>{{etf.change_pct}}%</strong>
                    </td>
                    <td>
                        <span class="{% if etf.alpha > 0 %}positive-alpha{% else %}negative-alpha{% endif %}">
                            {{etf.alpha}}%
                        </span>
                        {% if etf.outperforms %}
                        <span style="color:#f44336; font-weight:bold;">✅ 跑赢</span>
                        {% endif %}
                    </td>
                    <td>{{etf.latest_nav}}</td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
        
        <div class="investment-advice">
            <h3 class="advice-title">🎯 投资建议</h3>
            <p>基于十五五规划三大主线，建议配置权重如下：</p>
            
            <div class="theme-weight">
                <div class="weight-card">
                    <h4>科技自立</h4>
                    <div class="weight-value">40%</div>
                    <p>核心驱动：自主可控、技术创新、产业升级</p>
                    <ul class="recommendation-list">
                        <li>重点关注：半导体、人工智能、量子科技</li>
                        <li>配置策略：核心+卫星，长期持有</li>
                    </ul>
                </div>
                
                <div class="weight-card">
                    <h4>绿色转型</h4>
                    <div class="weight-value">35%</div>
                    <p>核心驱动：碳中和、能源革命、可持续发展</p>
                    <ul class="recommendation-list">
                        <li>重点关注：新能源车、光伏、储能</li>
                        <li>配置策略：趋势跟踪，波段操作</li>
                    </ul>
                </div>
                
                <div class="weight-card">
                    <h4>安全韧性</h4>
                    <div class="weight-value">25%</div>
                    <p>核心驱动：国家安全、资源保障、应急能力</p>
                    <ul class="recommendation-list">
                        <li>重点关注：军工、粮食安全、关键矿产</li>
                        <li>配置策略：防御配置，对冲风险</li>
                    </ul>
                </div>
            </div>
            
            <h4>核心观察池（三星级ETF）</h4>
            <ul class="recommendation-list">
                {% for etf in etfs if etf.star_rating == '★★★' %}
                <li><strong>{{etf.name}}</strong> ({{etf.ts_code}}) - {{etf.main_theme}}主题，超额收益: {{etf.alpha}}%</li>
                {% endfor %}
            </ul>
        </div>
        
        <div class="footer">
            <p>© 2026 琥珀引擎 - 十五五规划主题ETF研究中心</p>
            <p>数据来源: Tushare Pro 实时接口 | 分析时间: {{analysis_date}}</p>
            <p>免责声明: 本报告仅供参考，不构成投资建议。投资有风险，入市需谨慎。</p>
        </div>
    </div>
</body>
</html>
"""
    
    # 准备数据
    hs300 = analysis_data['hs300_performance']
    
    # 计算主题分布
    theme_counts = {}
    for etf in analysis_data['etfs']:
        theme = etf['main_theme']
        if theme:
            theme_counts[theme] = theme_counts.get(theme, 0) + 1
    
    # 生成HTML
    html_content = template.replace('{{