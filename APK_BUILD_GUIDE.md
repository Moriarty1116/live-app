# PersonalManagerApp - APK 打包指南

## ⚠️ 重要说明

**Buildozer 在 Windows 上不支持 Android 打包**（官方限制）。以下是 3 种可行方案：

---

## 方案一：WSL2 + Ubuntu（推荐）

### 前置要求
1. 启用 WSL2：以管理员身份运行 PowerShell
```powershell
wsl --install -d Ubuntu-22.04
```
2. 重启电脑，完成 Ubuntu 初始化（设置用户名/密码）

### 打包步骤

```bash
# 1. 进入 WSL
wsl

# 2. 更新系统
sudo apt update && sudo apt upgrade -y

# 3. 安装依赖
sudo apt install -y build-essential git python3 python3-pip \
    openjdk-17-jdk zlib1g-dev libncurses5-dev libstdc++6 \
    liblzma-dev autoconf libtool pkg-config libffi-dev

# 4. 设置 JAVA_HOME
echo 'export JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64' >> ~/.bashrc
echo 'export PATH=$PATH:$JAVA_HOME/bin' >> ~/.bashrc
source ~/.bashrc

# 5. 进入项目目录（Windows 路径转换为 WSL 路径）
cd /mnt/c/Users/JXGM/AppData/Roaming/Tencent/Marvis/User/oAN1i2Tn_pzTx4sNh59hSSLCXd_8/workspace/conv_19f0e5d64cf_b689032d9157/output/PersonalManagerApp

# 6. 安装 buildozer 和依赖
pip3 install --upgrade pip
pip3 install buildozer cython
pip3 install kivy==2.3.0 plyer==2.1.0

# 7. 执行打包（首次需下载 SDK/NDK，约 30-60 分钟）
buildozer android debug

# 8. 打包完成后，APK 文件位于：
# ./bin/personalmanager-1.0.0-debug.apk
```

### 复制 APK 到 Windows
```bash
# 在 WSL 中执行
cp ./bin/personalmanager-1.0.0-debug.apk /mnt/c/Users/JXGM/Desktop/
```

---

## 方案二：GitHub Actions 自动化打包（无需本地环境）

### 步骤

1. **将项目推送到 GitHub**
   ```bash
   git init
   git add .
   git commit -m "Initial commit: PersonalManager App"
   git remote add origin <你的GitHub仓库地址>
   git push -u origin main
   ```

2. **创建 GitHub Actions 工作流**

在项目中创建 `.github/workflows/build-apk.yml`：

```yaml
name: Build Android APK

on:
  push:
    branches: [ main ]
  workflow_dispatch:

jobs:
  build:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Setup Python
      uses: actions/setup-python@v5
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        sudo apt-get update
        sudo apt-get install -y build-essential git openjdk-17-jdk \
            zlib1g-dev libncurses5-dev libstdc++6 liblzma-dev \
            autoconf libtool pkg-config libffi-dev
        pip install --upgrade pip
        pip install buildozer cython
        pip install kivy==2.3.0 plyer==2.1.0
    
    - name: Build Debug APK
      run: |
        export JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
        buildozer android debug
    
    - name: Upload APK
      uses: actions/upload-artifact@v4
      with:
        name: debug-apk
        path: bin/*.apk
```

3. **触发构建**
   - 推送代码后自动触发
   - 或在 GitHub 仓库的 Actions 页面手动触发

4. **下载 APK**
   - 构建完成后在 Actions 页面下载 Artifact

---

## 方案三：Docker 容器打包

### 前置要求
安装 [Docker Desktop](https://www.docker.com/products/docker-desktop)

### 使用方法

1. **创建 Dockerfile**（已包含在项目中）

2. **构建并运行容器**
```bash
cd PersonalManagerApp
docker build -t personalmanager-builder .
docker run -v %cd%:/app -it personalmanager-builder
```

3. **APK 输出**
   - 容器完成后，APK 位于 `./bin/` 目录

---

## 当前状态

✅ **已完成的工作：**
- 应用名称已修改为"活着"
- buildozer.spec 配置文件已修复
- 项目代码完整（main.py、run.py 等）
- 所有依赖清单已准备（requirements.txt）

❌ **待执行：**
- 需要在 Linux 环境中运行 `buildozer android debug` 命令

---

## 技术细节

### 应用信息
- **名称**：活着
- **包名**：com.personalmanager
- **版本**：1.0.0
- **最低 Android 版本**：Android 5.0 (API 21)
- **目标架构**：arm64-v8a, armeabi-v7a

### 功能模块
1. ✅ 花销记录（收支分类、实时余额）
2. ✅ 待办任务（优先级管理、逾期提醒）
3. ✅ 任务期限（截止日期、智能排序）
4. ✅ 余额剩余（财务总览、月度报表）
5. ✅ 时间管理（屏幕监控、应用排行）

### 文件结构
```
PersonalManagerApp/
├── main.py              # 主程序源码（1700+ 行）
├── buildozer.spec       # 打包配置（已优化）
├── requirements.txt     # Python 依赖
├── run.py              # 启动脚本
├── README.md           # 项目文档
├── assets/             # 图标资源
│   └── icon.png
└── .gitignore          # Git 忽略规则
```

---

## 故障排除

### 常见问题

**Q1: WSL 安装失败**
```
解决方案：确保 Windows 版本 >= 2004，启用"适用于 Linux 的 Windows 子系统"功能
```

**Q2: buildozer 下载 SDK 超时**
```
解决方案：设置代理或使用国内镜像
export ANDROID_SDK_URL=https://mirrors.tuna.tsinghua.edu.cn/android/repository/
export ANDROID_NDK_URL=https://mirrors.tuna.tsinghua.edu.cn/android/repository/
```

**Q3: 编译错误：Cython 版本不兼容**
```
解决方案：pip install "cython<3.0"
```

**Q4: Java 版本错误**
```
解决方案：确保安装 JDK 17（不是 JDK 20/21）
sudo apt install openjdk-17-jdk
```

---

## 下一步操作建议

### 快速开始（预计时间：45-90 分钟）

1. **安装 WSL2**（10 分钟）
2. **配置 Ubuntu 环境**（15 分钟）
3. **首次打包**（30-60 分钟，含 SDK/NDK 下载）
4. **后续增量打包**（5-10 分钟）

### 自动化选项

如果需要频繁打包，建议设置 **GitHub Actions**，实现：
- 代码推送自动构建
- 多版本并行编译（debug/release）
- 自动发布到 GitHub Releases

---

## 联系与支持

如遇到问题，请提供以下信息以便排查：
1. 操作系统版本（`winver`）
2. Python 版本（`python --version`）
3. 完整的错误日志（`buildozer android debug` 的输出）
4. 使用的打包方案（WSL/Docker/GitHub Actions）

---

**最后更新时间**：2026-06-28  
**文档版本**：v1.0  
**适用系统**：Windows 11 (Build 26200)
