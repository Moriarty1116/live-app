#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import os

# 切换到项目目录
os.chdir(r'C:\Users\JXGM\AppData\Roaming\Tencent\Marvis\User\oAN1i2Tn_pzTx4sNh59hSSLCXd_8\workspace\conv_19f0e5d64cf_b689032d9157\output\PersonalManagerApp')

# 导入 buildozer
from buildozer import Buildozer

try:
    # 创建 Buildozer 实例
    build = Buildozer(filename='buildozer.spec', target='android')
    
    # 执行 debug 打包
    print("开始打包 Android Debug APK...")
    build.prepare_for_build()
    build.build_package()
    
    print("\n✅ APK 打包成功！")
    
except Exception as e:
    print(f"\n❌ 打包失败: {str(e)}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
