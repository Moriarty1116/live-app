#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PersonalManager 应用启动脚本
支持 Windows / Linux / macOS 多平台运行
"""

import sys
import os

# 确保项目根目录在 Python 路径中
script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.insert(0, script_dir)

# 检查依赖是否安装
def check_dependencies():
    """检查并提示缺失的依赖"""
    missing = []
    
    try:
        import kivy
    except ImportError:
        missing.append('kivy')
    
    try:
        import plyer
    except ImportError:
        missing.append('plyer')
    
    if missing:
        print("=" * 60)
        print("⚠️  缺少必要的依赖包，请先运行以下命令安装：")
        print("=" * 60)
        print(f"\npip install {' '.join(missing)}\n")
        print("或使用: pip install -r requirements.txt")
        print("=" * 60)
        return False
    
    return True


def main():
    """主函数"""
    print("=" * 60)
    print("🚀 正在启动 PersonalManager...")
    print("=" * 60)
    
    # 检查依赖
    if not check_dependencies():
        input("\n按回车键退出...")
        sys.exit(1)
    
    # 配置 Kivy 窗口
    os.environ['KIVY_TEXT'] = 'pil'  # 使用 PIL 文本渲染
    
    # 导入并启动应用
    from main import PersonalManagerApp
    
    try:
        app = PersonalManagerApp()
        app.run()
    except Exception as e:
        print(f"\n❌ 应用启动失败: {e}")
        import traceback
        traceback.print_exc()
        input("\n按回车键退出...")
        sys.exit(1)


if __name__ == '__main__':
    main()