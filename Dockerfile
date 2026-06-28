FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive
ENV JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
ENV PATH=$PATH:$JAVA_HOME/bin

# 安装系统依赖
RUN apt-get update && apt-get install -y \
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
    && rm -rf /var/lib/apt/lists/*

# 升级 pip 并安装 Python 依赖
RUN pip3 install --upgrade pip
RUN pip3 install buildozer cython
RUN pip3 install kivy==2.3.0 plyer==2.1.0

# 设置工作目录
WORKDIR /app

# 复制项目文件
COPY . .

# 执行打包命令
CMD ["buildozer", "android", "debug"]
