#!/bin/bash
# ============================================================
# PersonalManagerApp - WSL 环境自动配置脚本
# 用途：在 Ubuntu (WSL2) 中自动安装 buildozer 并打包 APK
# 使用方法：在 WSL 中执行: bash setup_wsl_build.sh
# ============================================================

set -e  # 遇到错误立即退出

echo "=========================================="
echo "  PersonalManagerApp - WSL 打包环境配置"
echo "=========================================="
echo ""

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${GREEN}[✓]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

print_error() {
    echo -e "${RED}[✗]${NC} $1"
}

# 检查是否在 WSL 中运行
if ! grep -q Microsoft /proc/version 2>/dev/null && ! grep -q microsoft /proc/version 2>/dev/null; then
    print_warning "警告：未检测到 WSL 环境，脚本可能无法正常工作"
    read -p "是否继续？(y/n): " confirm
    if [ "$confirm" != "y" ]; then
        exit 1
    fi
fi

echo "步骤 1/7：更新系统包..."
sudo apt-get update
sudo apt-get upgrade -y
print_status "系统更新完成"

echo ""
echo "步骤 2/7：安装系统依赖..."
sudo apt-get install -y \
    build-essential \
    git \
    python3 \
    python3-pip \
    python3-dev \
    openjdk-17-jdk \
    zlib1g-dev \
    libncurses5-dev \
    libstdc++6 \
    liblzma-dev \
    autoconf \
    libtool \
    pkg-config \
    libffi-dev \
    wget \
    unzip \
    zip
print_status "系统依赖安装完成"

echo ""
echo "步骤 3/7：配置 Java 环境..."
if grep -q "JAVA_HOME" ~/.bashrc; then
    print_warning "JAVA_HOME 已存在，跳过配置"
else
    echo '' >> ~/.bashrc
    echo '# Java environment' >> ~/.bashrc
    echo 'export JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64' >> ~/.bashrc
    echo 'export PATH=$PATH:$JAVA_HOME/bin' >> ~/.bashrc
fi
export JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
export PATH=$PATH:$JAVA_HOME/bin
print_status "Java 环境配置完成"

echo ""
echo "步骤 4/7：升级 pip 并安装 Python 包..."
python3 -m pip install --upgrade pip
pip3 install --upgrade cython
pip3 install buildozer
pip3 install kivy==2.3.0
pip3 install plyer==2.1.0
print_status "Python 依赖安装完成"

echo ""
echo "步骤 5/7：验证安装..."
java -version
python3 --version
buildozer --version
print_status "所有工具验证通过"

echo ""
echo "步骤 6/7：定位项目目录..."
# 尝试找到项目目录（Windows 路径）
PROJECT_DIR="/mnt/c/Users/JXGM/AppData/Roaming/Tencent/Marvis/User/oAN1i2Tn_pzTx4sNh59hSSLCXd_8/workspace/conv_19f0e5d64cf_b689032d9157/output/PersonalManagerApp"

if [ -d "$PROJECT_DIR" ]; then
    print_status "找到项目目录: $PROJECT_DIR"
else
    print_error "未找到项目目录: $PROJECT_DIR"
    echo ""
    echo "请手动指定项目路径（Windows 格式）："
    read -p "项目路径: " CUSTOM_PATH
    # 转换 Windows 路径为 WSL 路径
    PROJECT_DIR=$(echo "$CUSTOM_PATH" | sed 's|\\|/|g' | sed 's|C:|/mnt/c|' | sed 's|D:|/mnt/d|')
    
    if [ ! -d "$PROJECT_DIR" ]; then
        print_error "指定的路径不存在: $PROJECT_DIR"
        exit 1
    fi
fi

cd "$PROJECT_DIR"
print_status "已切换到项目目录"

echo ""
echo "步骤 7/7：开始打包 APK..."
echo ""
echo "=========================================="
echo "  重要提示"
echo "=========================================="
echo "首次打包需要下载以下组件（约 1-2 GB）："
echo "  - Android SDK (~1 GB)"
echo "  - Android NDK (~800 MB)"
echo "  - Python 依赖库"
echo ""
echo "预计耗时：30-60 分钟（取决于网络速度）"
echo "后续增量打包：5-10 分钟"
echo ""
echo "=========================================="
echo ""

read -p "确认开始打包？(y/n): " start_confirm
if [ "$start_confirm" != "y" ]; then
    echo "用户取消操作"
    exit 0
fi

echo ""
echo "正在执行 buildozer android debug..."
echo "日志将输出到控制台和文件 build_log.txt"
echo ""

# 执行打包并记录日志
if buildozer android debug 2>&1 | tee build_log.txt; then
    echo ""
    echo "=========================================="
    echo -e "${GREEN}🎉 APK 打包成功！${NC}"
    echo "=========================================="
    
    # 查找生成的 APK 文件
    APK_FILE=$(find ./bin -name "*.apk" -type f 2>/dev/null | head -1)
    
    if [ -n "$APK_FILE" ]; then
        echo ""
        echo "APK 文件位置:"
        echo "  Linux 路径: $APK_FILE"
        
        # 转换为 Windows 路径显示
        WIN_PATH=$(echo "$APK_FILE" | sed 's|/mnt/c|C:|' | sed 's|/|\\|g')
        echo "  Windows 路径: $WIN_PATH"
        
        echo ""
        echo "文件大小:"
        ls -lh "$APK_FILE" | awk '{print "  " $5}'
        
        echo ""
        echo "复制到桌面（可选）："
        DESKTOP_APK="$HOME/Desktop/personalmanager-debug.apk"
        cp "$APK_FILE" "$DESKTOP_APK"
        print_status "已复制到桌面: $DESKTOP_APK"
    fi
    
    echo ""
    echo "=========================================="
    echo "  后续操作建议"
    echo "=========================================="
    echo "1. 将 APK 传输到 Android 手机"
    echo "2. 在手机上允许安装未知来源应用"
    echo "3. 安装并测试应用功能"
    echo "4. 如需发布到应用商店，请使用 release 模式重新打包"
    echo "   命令: buildozer android release"
    echo "=========================================="
else
    echo ""
    print_error "打包失败！"
    echo ""
    echo "错误日志已保存到: build_log.txt"
    echo ""
    echo "常见问题排查："
    echo "1. 检查网络连接（可能需要代理）"
    echo "2. 查看错误日志最后 50 行：tail -n 50 build_log.txt"
    echo "3. 清理缓存重试：rm -rf .buildozer && buildozer android debug"
    echo ""
    echo "如需帮助，请提供错误日志"
    exit 1
fi

echo ""
print_status "脚本执行完成！"
