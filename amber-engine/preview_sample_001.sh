#!/bin/bash
# 琥珀引擎 001号样板预览脚本

echo "========================================================"
echo "琥珀引擎 001号样板预览"
echo "中国人寿(601628.SH)专属页面"
echo "========================================================"

BASE_DIR="/home/luckyelite/.openclaw/workspace/amber-engine"
OUTPUT_DIR="$BASE_DIR/output"

echo ""
echo "📋 生成的文件:"
echo "  1. 股票详情页: $OUTPUT_DIR/stock/601628.html"
echo "  2. 数据库文件: $BASE_DIR/amber_cms.db"
echo "  3. 环境配置: $BASE_DIR/.env.amber"

echo ""
echo "🚀 预览方式:"
echo "  方法1: 使用Python HTTP服务器"
echo "    cd $OUTPUT_DIR && python3 -m http.server 8000"
echo "    然后在浏览器打开: http://localhost:8000/stock/601628.html"
echo ""
echo "  方法2: 直接查看文件"
echo "    firefox $OUTPUT_DIR/stock/601628.html"
echo "    或"
echo "    google-chrome $OUTPUT_DIR/stock/601628.html"

echo ""
echo "📊 数据验证:"
sqlite3 "$BASE_DIR/amber_cms.db" << 'SQL'
SELECT '✅ 中国人寿基本信息:' as '';
SELECT name, industry, list_date FROM stock_basic WHERE ts_code = '601628.SH';

SELECT '' as '';
SELECT '✅ 最近5日行情:' as '';
SELECT trade_date, close, pct_chg FROM stock_daily 
WHERE ts_code = '601628.SH' 
ORDER BY trade_date DESC 
LIMIT 5;

SELECT '' as '';
SELECT '✅ 关联文章:' as '';
SELECT a.title, a.total_score FROM articles a
JOIN stock_articles sa ON a.id = sa.article_id
WHERE sa.stock_id = '601628.SH';
SQL

echo ""
echo "🎉 预览准备完成!"
echo "运行以下命令启动预览服务器:"
echo "  cd $OUTPUT_DIR && python3 -m http.server 8000"
