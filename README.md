---
AIGC:
    Label: "1"
    ContentProducer: 001191440300708461136T1XGW3
    ProduceID: 5f5d0d7d01d6b3ad9ac6682f0b4a2afd_0f69299a72f811f1897e5254002afed2
    ReservedCode1: Ij9aeZU6WDQKfdE+htO3SNQF7J+su7M/dLzLh3GAaT1MCV3edwOOfrZWbZo7aiV54DIwi5EVKtiqq1TQpxzYGTpv3IYMEqIPy9wCtd+Ikuk5KPF+T4Z2CH4tnvbZ0IqRREfZeLvi7JZxmsZdjAc6S/Thk3znitoSfW2TzzIHceV0hIHDhTOKrIiFwNQ=
    ContentPropagator: 001191440300708461136T1XGW3
    PropagateID: 5f5d0d7d01d6b3ad9ac6682f0b4a2afd_0f69299a72f811f1897e5254002afed2
    ReservedCode2: Ij9aeZU6WDQKfdE+htO3SNQF7J+su7M/dLzLh3GAaT1MCV3edwOOfrZWbZo7aiV54DIwi5EVKtiqq1TQpxzYGTpv3IYMEqIPy9wCtd+Ikuk5KPF+T4Z2CH4tnvbZ0IqRREfZeLvi7JZxmsZdjAc6S/Thk3znitoSfW2TzzIHceV0hIHDhTOKrIiFwNQ=
---

# PersonalManager - 个人财务管理与时间管理应用

## 📱 应用简介

PersonalManager 是一款功能全面的个人管理安卓应用，集成了**财务记账**、**任务管理**和**时间监控**三大核心功能模块，帮助用户高效管理个人生活、提升工作效率。

**版本**: 1.0.0  
**开发框架**: Python + Kivy (跨平台移动开发框架)  
**数据库**: SQLite (本地存储，保护隐私)  
**目标平台**: Android 5.0+ (API 21+)

---

## ✨ 核心功能

### 1. 💸 花销记录模块
- **收支记录**: 快速记录日常收入和支出
- **分类管理**: 支持餐饮、交通、购物、娱乐等8大支出类别，以及工资、奖金、投资收益等6大收入类别
- **备注说明**: 每笔交易可添加详细备注
- **历史查询**: 查看最近20条交易记录，按时间倒序排列
- **实时余额**: 首页展示当前账户余额（初始余额+总收入-总支出）

### 2. 📝 待办任务模块
- **任务创建**: 添加待办事项，支持标题、描述、优先级设置
- **优先级管理**: 4级优先级系统 - 紧急(urgent) > 高(high) > 中(medium) > 低(low)
- **状态跟踪**: 待处理 → 进行中 → 已完成/已取消
- **截止日期**: 为每个任务设置截止日期，自动识别逾期任务
- **提醒功能**: 支持设置自定义提醒时间（需配合系统通知权限）
- **智能筛选**: 按状态筛选任务（全部/待处理/进行中/已完成）
- **逾期预警**: 自动标记并高亮显示已过期未完成任务

### 3. 📈 余额统计模块
- **财务总览卡片**: 直观展示当前余额、总收入、总支出
- **月度统计**: 本月收入/支出/净收支明细
- **分类分析**: 支出按类别汇总统计，支持查看各分类的金额和笔数
- **趋势对比**: 收支数据可视化呈现（颜色区分：绿色=收入，红色=支出）
- **净结余计算**: 自动计算每月结余金额，正负值用颜色区分

### 4. ⏰ 时间管理模块
- **屏幕时间追踪**: 记录每日手机使用时长（精确到分钟）
- **使用进度条**: 可视化展示今日使用量占设定限额的百分比
- **时间限制设置**: 自定义每日屏幕时间限制（0.5-12小时，可调）
- **超额警告**: 使用量超过70%黄色警告，超过90%红色告警
- **应用排行**: Top 10 应用使用时长排行榜（显示名称、时长、启动次数）
- **生产力分析**: 区分高效/低效应用使用时间，计算生产力占比
- **分类统计**: 按社交/娱乐/工具/学习/工作/游戏/购物等类别分析时间分配
- **模拟演示**: 内置示例数据生成功能，方便体验完整功能

### 5. 🏠 主仪表盘
- **快速概览**: 4宫格卡片展示关键指标（余额、待办数、月支出、屏幕时间）
- **快捷入口**: 一键跳转到各功能模块
- **功能导航**: 清晰的功能列表及说明文字
- **版本信息**: 显示当前应用版本号

---

## 🛠️ 技术架构

### 技术栈
```
前端UI: Kivy Framework (Python)
    ├── 响应式布局 (BoxLayout, GridLayout, ScrollView)
    ├── 自定义组件 (StyledButton, StyledLabel)
    └── 主题配色系统 (Material Design风格)

数据层: SQLite3 数据库
    ├── expenses 表 (花销记录)
    ├── tasks 表 (待办任务)
    ├── time_logs 表 (时间日志)
    └── settings 表 (用户设置)

业务逻辑: DatabaseManager 类
    ├── CRUD 操作封装
    ├── 统计聚合查询
    └── 数据校验与异常处理
```

### 数据库设计

#### expenses (花销表)
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键自增 |
| amount | REAL | 金额 |
| category | TEXT | 分类 |
| description | TEXT | 备注 |
| type | TEXT | 类型(income/expense) |
| date | TEXT | 日期时间 |
| created_at | TEXT | 创建时间 |

#### tasks (任务表)
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键自增 |
| title | TEXT | 任务标题 |
| description | TEXT | 任务描述 |
| priority | TEXT | 优先级(low/medium/high/urgent) |
| status | TEXT | 状态(pending/in_progress/completed/cancelled) |
| due_date | TEXT | 截止日期 |
| reminder_time | TEXT | 提醒时间 |
| created_at | TEXT | 创建时间 |
| completed_at | TEXT | 完成时间 |

#### time_logs (时间日志表)
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键自增 |
| app_name | TEXT | 应用名称 |
| category | TEXT | 应用分类 |
| duration_seconds | INTEGER | 使用时长(秒) |
| date | TEXT | 日期 |
| start_time | TEXT | 开始时间 |
| end_time | TEXT | 结束时间 |
| is_productive | BOOLEAN | 是否高效(0/1) |

#### settings (设置表)
| 字段 | 类型 | 说明 |
|------|------|------|
| key | TEXT | 设置键名(主键) |
| value | TEXT | 设置值 |
| updated_at | TEXT | 更新时间 |

---

## 🚀 安装与运行

### 方式一：直接运行源码（Windows/Linux/macOS）

#### 前置要求
- Python 3.8+
- pip 包管理器

#### 安装步骤

```bash
# 1. 克隆或下载项目到本地
cd PersonalManagerApp

# 2. 创建虚拟环境（推荐）
python -m venv venv

# 3. 激活虚拟环境
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# 4. 安装依赖
pip install -r requirements.txt

# 5. 运行应用
python main.py
```

#### 运行效果
应用将在桌面窗口中启动，可通过鼠标/触摸操作。所有界面均采用响应式设计，适配不同分辨率。

---

### 方式二：打包为 Android APK

#### 前置要求
- Python 3.8+
- Buildozer (Kivy官方打包工具)
- Android SDK / NDK (Buildozer会自动下载)
- Java JDK 8+

#### 安装 Buildozer

```bash
pip install buildozer
```

#### 打包命令

```bash
cd PersonalManagerApp

# 调试模式打包（速度快，体积大）
buildozer android debug

# 发布模式打包（需要签名密钥）
buildozer android release

# 仅构建不安装
buildozer android debug deploy run
```

#### 打包输出位置
```
PersonalManagerApp/
├── build/
│   └── android/
│       └── app/
│           └── debug.apk   # 或 release.aab (Android App Bundle)
```

#### 注意事项
1. **首次打包**会自动下载 Android SDK、NDK 等依赖（约2-4GB），请确保网络畅通
2. **打包时间**: 首次约30-60分钟，后续增量构建约5-15分钟
3. **架构选择**: 默认同时编译 arm64-v8a 和 armeabi-v7a，覆盖99%以上Android设备
4. **权限说明**: 应用需要以下权限：
   - `INTERNET`: 未来扩展云同步功能预留
   - `WRITE_EXTERNAL_STORAGE` / `READ_EXTERNAL_STORAGE`: 备份/恢复数据库
   - `PACKAGE_USAGE_STATS`: 读取应用使用统计（时间管理核心功能）
   - `SYSTEM_ALERT_WINDOW`: 浮窗提醒（可选）

---

## 📖 使用指南

### 初次使用流程

1. **打开应用** → 进入主仪表盘
2. **设置初始余额**（可选）: 点击"余额统计"页面，修改"初始余额"设置
3. **开始记账**: 
   - 点击"花销记录" → "+"按钮添加收入/支出
   - 选择分类 → 输入金额 → 添加备注 → 保存
4. **管理任务**:
   - 点击"待办任务" → "添加新任务"
   - 填写标题 → 设定优先级和截止日期 → 保存
   - 任务完成后点击 ✓ 按钮
5. **监控时间**:
   - 进入"时间管理"页面查看今日屏幕时间
   - 拖动滑块设置每日时间限制
   - 点击"添加示例数据"体验完整功能

### 功能特色

#### 💡 智能提示
- 逾期任务自动标红并显示"(已逾期)"标签
- 屏幕时间超限时进度条变色警告
- 余额为负时以红色醒目显示

#### 🎨 视觉设计
- Material Design 配色方案
- 优先级用颜色区分（红=紧急，橙=高，黄=中，绿=低）
- 卡片式布局，信息层次清晰

#### 🔒 隐私保护
- 所有数据存储在设备本地 SQLite 数据库
- 无需联网，无云端上传
- 用户完全掌控自己的数据

---

## 🎯 适用场景

- **个人理财**: 记录日常开销，控制消费欲望
- **学生党**: 管理生活费，规划学习任务
- **上班族**: 平衡工作与生活，减少无效刷屏时间
- **自由职业者**: 追踪项目进度，管理多个待办事项
- **家庭主妇/夫**: 记录家庭开支，安排家务任务

---

## 🔧 开发计划

### V1.1 (即将推出)
- [ ] 导出报表功能（CSV/PDF格式）
- [ ] 图表可视化（月度收支折线图、饼图）
- [ ] 数据备份与恢复（导出/导入SQLite文件）
- [ ] 多币种支持

### V1.2 (规划中)
- [ ] 云端同步（可选加密备份）
- [ ] 小组件（桌面Widget显示余额/待办数）
- [ ] 深色模式
- [ ] 多语言支持（英文/日文等）

### V2.0 (远期愿景)
- [ ] AI 智能分析（消费习惯建议、时间优化建议）
- [ ] 家庭共享账本（多人协作记账）
- [ ] 与系统日历深度集成
- [ ] 语音输入记账

---

## 📄 许可证

MIT License

Copyright (c) 2026 PersonalManager Team

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

---

## 🤝 贡献指南

欢迎提交 Issue 和 Pull Request！

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

---

## 📞 联系方式

- **问题反馈**: 请在 GitHub Issues 提交
- **功能建议**: 欢迎 Pull Request 或讨论
- **商业合作**: 请通过邮件联系

---

## 🙏 致谢

- [Kivy](https://kivy.org/) - 强大的Python跨平台UI框架
- [Buildozer](https://buildozer.readthedocs.io/) - Android打包工具
- [Plyer](https://plyer.org/) - 跨平台API接口库
- [Material Design](https://material.io/design) - 设计规范参考

---

**Made with ❤️ using Python & Kivy**

*最后更新: 2026-06-28*
*（内容由AI生成，仅供参考）*
