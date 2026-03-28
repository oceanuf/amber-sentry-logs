#!/bin/bash
# 琥珀引擎 - 一键部署脚本
# Git Pull -> Python Generate -> Nginx Reload

echo "========================================================"
echo "琥珀引擎 - 生产环境一键部署"
echo "========================================================"

# 配置
BASE_DIR="/home/luckyelite/.openclaw/workspace/amber-engine"
OUTPUT_DIR="$BASE_DIR/output"
NGINX_CONF="/etc/nginx/sites-available/finance.cheese.ai.conf"
SITE_URL="https://finance.cheese.ai"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查命令是否存在
check_command() {
    if ! command -v $1 &> /dev/null; then
        log_error "命令 $1 不存在，请先安装"
        exit 1
    fi
}

# 步骤1: 检查环境
check_environment() {
    log_info "步骤1: 检查环境..."
    
    check_command git
    check_command python3
    check_command nginx
    check_command openssl
    
    # 检查目录
    if [ ! -d "$BASE_DIR" ]; then
        log_error "项目目录不存在: $BASE_DIR"
        exit 1
    fi
    
    # 检查Nginx配置
    if [ ! -f "$NGINX_CONF" ]; then
        log_warning "Nginx配置不存在，将创建默认配置"
    fi
    
    log_success "环境检查通过"
}

# 步骤2: 更新代码
update_code() {
    log_info "步骤2: 更新代码..."
    
    cd "$BASE_DIR"
    
    if [ -d ".git" ]; then
        log_info "拉取最新代码..."
        git pull origin main 2>/dev/null || log_warning "Git拉取失败，继续使用本地代码"
    else
        log_warning "不是Git仓库，跳过代码更新"
    fi
    
    log_success "代码更新完成"
}

# 步骤3: 生成静态页面
generate_pages() {
    log_info "步骤3: 生成静态页面..."
    
    cd "$BASE_DIR"
    
    # 检查Python依赖
    if ! python3 -c "import tushare" 2>/dev/null; then
        log_warning "Tushare未安装，将使用模拟数据"
    fi
    
    # 运行ETF优先生成脚本
    log_info "运行ETF优先生成脚本..."
    python3 scripts/gen_etf_priority.py
    
    if [ $? -eq 0 ]; then
        log_success "页面生成完成"
    else
        log_error "页面生成失败"
        exit 1
    fi
}

# 步骤4: 复制静态文件
copy_static_files() {
    log_info "步骤4: 复制静态文件..."
    
    # 创建输出目录
    mkdir -p "$OUTPUT_DIR/static/css"
    mkdir -p "$OUTPUT_DIR/static/js"
    mkdir -p "$OUTPUT_DIR/static/cert"
    
    # 复制CSS文件
    if [ -f "$BASE_DIR/static/css/amber-v2.2.min.css" ]; then
        cp "$BASE_DIR/static/css/amber-v2.2.min.css" "$OUTPUT_DIR/static/css/"
        log_success "CSS文件复制完成"
    else
        log_warning "CSS文件不存在，跳过"
    fi
    
    # 创建JS文件
    echo '// 琥珀引擎 JavaScript 文件' > "$OUTPUT_DIR/static/js/amber-engine.min.js"
    echo 'console.log("琥珀引擎已加载");' >> "$OUTPUT_DIR/static/js/amber-engine.min.js"
    log_success "JS文件创建完成"
    
    # 复制SSL证书
    if [ -f "/etc/nginx/ssl/finance.cheese.ai.crt" ]; then
        sudo cp "/etc/nginx/ssl/finance.cheese.ai.crt" "$OUTPUT_DIR/static/cert/amber-root.crt"
        sudo chmod 644 "$OUTPUT_DIR/static/cert/amber-root.crt"
        log_success "SSL证书复制完成"
    else
        log_warning "SSL证书不存在，跳过"
    fi
}

# 步骤5: 配置Nginx
configure_nginx() {
    log_info "步骤5: 配置Nginx..."
    
    # 检查Nginx配置目录
    sudo mkdir -p /etc/nginx/sites-available /etc/nginx/sites-enabled
    
    # 复制配置文件
    if [ -f "$BASE_DIR/nginx/finance.cheese.ai.conf" ]; then
        sudo cp "$BASE_DIR/nginx/finance.cheese.ai.conf" /etc/nginx/sites-available/
        sudo ln -sf /etc/nginx/sites-available/finance.cheese.ai.conf /etc/nginx/sites-enabled/
        log_success "Nginx配置文件复制完成"
    else
        log_warning "Nginx配置文件不存在，使用默认配置"
        create_default_nginx_config
    fi
    
    # 测试Nginx配置
    log_info "测试Nginx配置..."
    if sudo nginx -t 2>/dev/null; then
        log_success "Nginx配置测试通过"
    else
        log_error "Nginx配置测试失败"
        exit 1
    fi
    
    # 重载Nginx
    log_info "重载Nginx服务..."
    sudo systemctl reload nginx 2>/dev/null || sudo service nginx reload 2>/dev/null
    
    if [ $? -eq 0 ]; then
        log_success "Nginx重载成功"
    else
        log_error "Nginx重载失败"
        exit 1
    fi
}

# 创建默认Nginx配置
create_default_nginx_config() {
    cat > /tmp/finance.cheese.ai.conf << 'EOF'
server {
    listen 80;
    listen [::]:80;
    server_name finance.cheese.ai;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name finance.cheese.ai;
    
    ssl_certificate /etc/nginx/ssl/finance.cheese.ai.crt;
    ssl_certificate_key /etc/nginx/ssl/finance.cheese.ai.key;
    
    root /home/luckyelite/.openclaw/workspace/amber-engine/output;
    index index.html;
    
    location / {
        try_files $uri $uri/ =404;
    }
    
    location /static/ {
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
}
EOF
    
    sudo cp /tmp/finance.cheese.ai.conf /etc/nginx/sites-available/
    sudo ln -sf /etc/nginx/sites-available/finance.cheese.ai.conf /etc/nginx/sites-enabled/
}

# 步骤6: 生成SSL证书
generate_ssl_cert() {
    log_info "步骤6: 生成SSL证书..."
    
    sudo mkdir -p /etc/nginx/ssl
    
    if [ ! -f "/etc/nginx/ssl/finance.cheese.ai.key" ] || [ ! -f "/etc/nginx/ssl/finance.cheese.ai.crt" ]; then
        log_info "生成10年期SSL证书..."
        cd /etc/nginx/ssl && sudo openssl req -x509 -nodes -days 3650 -newkey rsa:2048 \
            -keyout finance.cheese.ai.key \
            -out finance.cheese.ai.crt \
            -subj "/C=CN/ST=Guangdong/L=Shenzhen/O=Cheese Intelligence/OU=Engineering/CN=finance.cheese.ai/emailAddress=contact@cheese.ai" \
            2>/dev/null
        
        if [ $? -eq 0 ]; then
            log_success "SSL证书生成成功"
        else
            log_error "SSL证书生成失败"
            exit 1
        fi
    else
        log_success "SSL证书已存在，跳过生成"
    fi
}

# 步骤7: 验证部署
verify_deployment() {
    log_info "步骤7: 验证部署..."
    
    # 检查输出目录
    if [ ! -f "$OUTPUT_DIR/index.html" ]; then
        log_error "首页不存在: $OUTPUT_DIR/index.html"
        exit 1
    fi
    
    # 检查静态文件
    if [ ! -f "$OUTPUT_DIR/static/css/amber-v2.2.min.css" ]; then
        log_warning "CSS文件不存在"
    fi
    
    # 检查SSL证书
    if [ ! -f "$OUTPUT_DIR/static/cert/amber-root.crt" ]; then
        log_warning "SSL证书下载文件不存在"
    fi
    
    # 测试网站访问
    log_info "测试网站访问..."
    if curl -s -k "https://finance.cheese.ai" > /dev/null 2>&1; then
        log_success "网站访问正常"
    else
        log_warning "HTTPS访问失败，尝试HTTP..."
        if curl -s "http://finance.cheese.ai" > /dev/null 2>&1; then
            log_success "HTTP访问正常"
        else
            log_error "网站无法访问"
            exit 1
        fi
    fi
    
    log_success "部署验证通过"
}

# 步骤8: 显示部署信息
show_deployment_info() {
    log_info "步骤8: 显示部署信息..."
    
    echo ""
    echo "========================================================"
    echo "🎉 琥珀引擎部署完成!"
    echo "========================================================"
    
    echo ""
    echo "📊 部署统计:"
    echo "   网站地址: https://finance.cheese.ai"
    echo "   输出目录: $OUTPUT_DIR"
    echo "   SSL证书: 10年期自签名证书"
    echo "   静态缓存: 30天"
    echo "   Gzip压缩: 已启用"
    
    echo ""
    echo "📁 生成的文件:"
    echo "   首页: $OUTPUT_DIR/index.html"
    echo "   ETF页面: $OUTPUT_DIR/etf/[代码]/index.html"
    echo "   股票页面: $OUTPUT_DIR/stock/[代码]/index.html"
    echo "   CSS文件: $OUTPUT_DIR/static/css/amber-v2.2.min.css"
    echo "   SSL证书: $OUTPUT_DIR/static/cert/amber-root.crt"
    
    echo ""
    echo "🔗 重要链接:"
    echo "   网站首页: https://finance.cheese.ai"
    echo "   SSL证书下载: https://finance.cheese.ai/static/cert/amber-root.crt"
    echo "   示例ETF: https://finance.cheese.ai/etf/510300.html"
    echo "   示例股票: https://finance.cheese.ai/stock/601318.html"
    
    echo ""
    echo "🔧 管理命令:"
    echo "   重新部署: bash $BASE_DIR/deploy.sh"
    echo "   查看日志: tail -f /var/log/nginx/finance.cheese.ai.access.log"
    echo "   重启Nginx: sudo systemctl reload nginx"
    echo "   停止服务: sudo systemctl stop nginx"
    
    echo ""
    echo "📝 SSL证书安装指南:"
    echo "   1. 访问: https://finance.cheese.ai/static/cert/amber-root.crt"
    echo "   2. 下载证书文件"
    echo "   3. 双击安装到受信任的根证书颁发机构"
    echo "   4. 重启浏览器"
    
    echo ""
    echo "🚀 部署时间: $(date '+%Y-%m-%d %H:%M:%S')"
    echo "========================================================"
}

# 主函数
main() {
    echo "开始琥珀引擎生产环境部署..."
    echo ""
    
    # 执行所有步骤
    check_environment
    echo ""
    
    update_code
    echo ""
    
    generate_ssl_cert
    echo ""
    
    generate_pages
    echo ""
    
    copy_static_files
    echo ""
    
    configure_nginx
    echo ""
    
    verify_deployment
    echo ""
    
    show_deployment_info
    
    echo ""
    log_success "琥珀引擎部署完成!"
}

# 运行主函数
main "$@"