#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
个人财务管理与时间管理应用 - PersonalManager
功能模块：
1. 花销记录：日常支出/收入记账
2. 待办任务：添加、管理待办事项
3. 任务期限：为任务设置截止日期和提醒
4. 余额剩余：展示当前余额、收支统计
5. 时间管理：手机使用时间监控与管理功能
"""

import os
import json
import sqlite3
from datetime import datetime, timedelta
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelItem
from kivy.uix.spinner import Spinner
from kivy.uix.checkbox import CheckBox
from kivy.uix.slider import Slider
from kivy.uix.progressbar import ProgressBar
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.metrics import dp, sp
from kivy.graphics import Color, Rectangle, Line
from kivy.utils import get_color_from_hex
from kivy.properties import (
    NumericProperty, StringProperty, ListProperty,
    BooleanProperty, ObjectProperty
)
import platform

# 应用配置
APP_NAME = "PersonalManager"
APP_VERSION = "1.0.0"
DB_NAME = "personal_manager.db"

# 颜色主题
THEME_COLORS = {
    'primary': '#2196F3',      # 主色调-蓝色
    'secondary': '#FFC107',    # 辅助色-黄色
    'success': '#4CAF50',      # 成功-绿色
    'danger': '#F44336',       # 危险-红色
    'warning': '#FF9800',      # 警告-橙色
    'background': '#FAFAFA',   # 背景色
    'surface': '#FFFFFF',      # 表面色
    'text_primary': '#212121', # 主文本色
    'text_secondary': '#757575'# 次要文本色
}


class DatabaseManager:
    """数据库管理类 - 负责所有数据持久化操作"""
    
    def __init__(self, db_path=None):
        if db_path is None:
            # 根据平台确定数据库路径
            if platform.system() == 'Android':
                from android.storage import primary_external_storage_path
                db_path = os.path.join(primary_external_storage_path(), APP_NAME, DB_NAME)
            else:
                db_path = os.path.join(os.path.dirname(__file__), DB_NAME)
        
        self.db_path = db_path
        self.conn = None
        self._init_database()
    
    def _get_connection(self):
        """获取数据库连接"""
        if self.conn is None:
            self.conn = sqlite3.connect(self.db_path)
            self.conn.row_factory = sqlite3.Row
        return self.conn
    
    def _init_database(self):
        """初始化数据库表结构"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # 1. 花销记录表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                amount REAL NOT NULL,
                category TEXT NOT NULL,
                description TEXT,
                type TEXT CHECK(type IN ('income', 'expense')) DEFAULT 'expense',
                date TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 2. 待办任务表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                priority TEXT CHECK(priority IN ('low', 'medium', 'high', 'urgent')) DEFAULT 'medium',
                status TEXT CHECK(status IN ('pending', 'in_progress', 'completed', 'cancelled')) DEFAULT 'pending',
                due_date TEXT,
                reminder_time TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                completed_at TEXT
            )
        ''')
        
        # 3. 时间管理记录表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS time_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                app_name TEXT,
                category TEXT,
                duration_seconds INTEGER DEFAULT 0,
                date TEXT NOT NULL,
                start_time TEXT,
                end_time TEXT,
                is_productive BOOLEAN DEFAULT 0,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 4. 用户设置表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        
        # 初始化默认设置
        self._init_default_settings(cursor, conn)
    
    def _init_default_settings(self, cursor, conn):
        """初始化默认设置"""
        default_settings = {
            'initial_balance': '0',
            'daily_time_limit': '3600',  # 默认1小时
            'currency': 'CNY',
            'reminder_enabled': 'true'
        }
        
        for key, value in default_settings.items():
            cursor.execute('INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)', (key, value))
        
        conn.commit()
    
    # ==================== 花销记录相关方法 ====================
    
    def add_expense(self, amount, category, description='', expense_type='expense', date=None):
        """添加花销/收入记录"""
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO expenses (amount, category, description, type, date)
            VALUES (?, ?, ?, ?, ?)
        ''', (float(amount), category, description, expense_type, date))
        conn.commit()
        return cursor.lastrowid
    
    def get_expenses(self, start_date=None, end_date=None, expense_type=None):
        """获取花销记录列表"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        query = 'SELECT * FROM expenses WHERE 1=1'
        params = []
        
        if start_date:
            query += ' AND date >= ?'
            params.append(start_date)
        if end_date:
            query += ' AND date <= ?'
            params.append(end_date)
        if expense_type:
            query += ' AND type = ?'
            params.append(expense_type)
        
        query += ' ORDER BY date DESC'
        cursor.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]
    
    def get_balance_summary(self):
        """获取收支汇总"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # 总收入
        cursor.execute('SELECT COALESCE(SUM(amount), 0) as total FROM expenses WHERE type = \'income\'')
        total_income = cursor.fetchone()['total']
        
        # 总支出
        cursor.execute('SELECT COALESCE(SUM(amount), 0) as total FROM expenses WHERE type = \'expense\'')
        total_expense = cursor.fetchone()['total']
        
        # 初始余额
        initial_balance = float(self.get_setting('initial_balance'))
        
        # 当前余额
        current_balance = initial_balance + total_income - total_expense
        
        # 本月收支
        current_month = datetime.now().strftime('%Y-%m')
        cursor.execute(
            'SELECT COALESCE(SUM(amount), 0) as total FROM expenses WHERE type = \'income\' AND date LIKE ?',
            (f'{current_month}%',)
        )
        month_income = cursor.fetchone()['total']
        
        cursor.execute(
            'SELECT COALESCE(SUM(amount), 0) as total FROM expenses WHERE type = \'expense\' AND date LIKE ?',
            (f'{current_month}%',)
        )
        month_expense = cursor.fetchone()['total']
        
        return {
            'total_income': round(total_income, 2),
            'total_expense': round(total_expense, 2),
            'current_balance': round(current_balance, 2),
            'month_income': round(month_income, 2),
            'month_expense': round(month_expense, 2),
            'month_net': round(month_income - month_expense, 2)
        }
    
    def get_category_summary(self):
        """获取分类统计"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT category, 
                   SUM(CASE WHEN type = 'expense' THEN amount ELSE 0 END) as expense_sum,
                   SUM(CASE WHEN type = 'income' THEN amount ELSE 0 END) as income_sum,
                   COUNT(*) as count
            FROM expenses 
            GROUP BY category
            ORDER BY expense_sum DESC
        ''')
        
        return [dict(row) for row in cursor.fetchall()]
    
    def delete_expense(self, expense_id):
        """删除花销记录"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM expenses WHERE id = ?', (expense_id,))
        conn.commit()
        return cursor.rowcount > 0
    
    # ==================== 待办任务相关方法 ====================
    
    def add_task(self, title, description='', priority='medium', due_date=None, reminder_time=None):
        """添加待办任务"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO tasks (title, description, priority, due_date, reminder_time)
            VALUES (?, ?, ?, ?, ?)
        ''', (title, description, priority, due_date, reminder_time))
        conn.commit()
        return cursor.lastrowid
    
    def get_tasks(self, status=None):
        """获取任务列表"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        query = 'SELECT * FROM tasks WHERE 1=1'
        params = []
        
        if status:
            query += ' AND status = ?'
            params.append(status)
        
        query += ' ORDER BY CASE priority WHEN \'urgent\' THEN 1 WHEN \'high\' THEN 2 WHEN \'medium\' THEN 3 ELSE 4 END, due_date ASC'
        cursor.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]
    
    def update_task_status(self, task_id, status):
        """更新任务状态"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        completed_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S') if status == 'completed' else None
        cursor.execute('''
            UPDATE tasks SET status = ?, completed_at = ? WHERE id = ?
        ''', (status, completed_at, task_id))
        conn.commit()
        return cursor.rowcount > 0
    
    def update_task(self, task_id, **kwargs):
        """更新任务信息"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        set_clause = ', '.join([f'{k} = ?' for k in kwargs.keys()])
        values = list(kwargs.values()) + [task_id]
        
        cursor.execute(f'UPDATE tasks SET {set_clause} WHERE id = ?', values)
        conn.commit()
        return cursor.rowcount > 0
    
    def delete_task(self, task_id):
        """删除任务"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM tasks WHERE id = ?', (task_id,))
        conn.commit()
        return cursor.rowcount > 0
    
    def get_overdue_tasks(self):
        """获取已过期未完成任务"""
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM tasks 
            WHERE status IN ('pending', 'in_progress') 
            AND due_date < ? 
            AND due_date IS NOT NULL
            ORDER BY due_date ASC
        ''', (now,))
        return [dict(row) for row in cursor.fetchall()]
    
    def get_today_tasks(self):
        """获取今日任务"""
        today = datetime.now().strftime('%Y-%m-%d')
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM tasks 
            WHERE date(due_date) = date(?)
            ORDER BY priority DESC, due_date ASC
        ''', (today,))
        return [dict(row) for row in cursor.fetchall()]
    
    # ==================== 时间管理相关方法 ====================
    
    def add_time_log(self, app_name, category, duration_seconds, date=None, is_productive=False):
        """添加时间使用记录"""
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')
        
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO time_logs (app_name, category, duration_seconds, date, is_productive)
            VALUES (?, ?, ?, ?, ?)
        ''', (app_name, category, duration_seconds, date, int(is_productive)))
        conn.commit()
        return cursor.lastrowid
    
    def get_time_stats(self, date=None, period='today'):
        """获取时间使用统计"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # 确定日期范围
        if period == 'today':
            date_filter = f"date = '{datetime.now().strftime('%Y-%m-%d')}'"
        elif period == 'week':
            week_ago = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
            date_filter = f"date >= '{week_ago}'"
        elif period == 'month':
            month_start = datetime.now().replace(day=1).strftime('%Y-%m-%d')
            date_filter = f"date >= '{month_start}'"
        else:
            date_filter = '1=1'
        
        # 总时间
        cursor.execute(f'''
            SELECT COALESCE(SUM(duration_seconds), 0) as total_seconds,
                   COUNT(*) as session_count
            FROM time_logs WHERE {date_filter}
        ''')
        result = cursor.fetchone()
        total_seconds = result['total_seconds']
        session_count = result['session_count']
        
        # 按分类统计
        cursor.execute(f'''
            SELECT category, 
                   SUM(duration_seconds) as total_seconds,
                   COUNT(*) as count,
                   ROUND(AVG(duration_seconds), 0) as avg_seconds
            FROM time_logs 
            WHERE {date_filter}
            GROUP BY category
            ORDER BY total_seconds DESC
        ''')
        category_stats = [dict(row) for row in cursor.fetchall()]
        
        # 按应用统计
        cursor.execute(f'''
            SELECT app_name, 
                   SUM(duration_seconds) as total_seconds,
                   COUNT(*) as count
            FROM time_logs 
            WHERE {date_filter}
            GROUP BY app_name
            ORDER BY total_seconds DESC
            LIMIT 10
        ''')
        app_stats = [dict(row) for row in cursor.fetchall()]
        
        # 生产力分析
        cursor.execute(f'''
            SELECT 
                SUM(CASE WHEN is_productive = 1 THEN duration_seconds ELSE 0 END) as productive_seconds,
                SUM(CASE WHEN is_productive = 0 THEN duration_seconds ELSE 0 END) as non_productive_seconds
            FROM time_logs WHERE {date_filter}
        ''')
        productivity = dict(cursor.fetchone())
        
        return {
            'total_seconds': total_seconds,
            'total_hours': round(total_seconds / 3600, 2),
            'session_count': session_count,
            'category_stats': category_stats,
            'app_stats': app_stats,
            'productivity': productivity,
            'productive_percentage': round(
                (productivity['productive_seconds'] / total_seconds * 100) if total_seconds > 0 else 0, 1
            ) if productivity else 0
        }
    
    # ==================== 设置相关方法 ====================
    
    def get_setting(self, key, default=None):
        """获取设置值"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT value FROM settings WHERE key = ?', (key,))
        result = cursor.fetchone()
        return result['value'] if result else default
    
    def set_setting(self, key, value):
        """设置值"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO settings (key, value, updated_at) 
            VALUES (?, ?, CURRENT_TIMESTAMP)
        ''', (key, str(value)))
        conn.commit()
    
    def close(self):
        """关闭数据库连接"""
        if self.conn:
            self.conn.close()
            self.conn = None


# 全局数据库实例
db_manager = DatabaseManager()


class StyledButton(Button):
    """自定义样式按钮"""
    pass


class StyledLabel(Label):
    """自定义样式标签"""
    pass


class ExpenseScreen(Screen):
    """花销记录界面"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'expense'
        self._build_ui()
    
    def _build_ui(self):
        layout = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))
        
        # 顶部余额显示
        balance_box = BoxLayout(size_hint_y=None, height=dp(120), padding=dp(15))
        with balance_box.canvas.before:
            Color(*get_color_from_hex(THEME_COLORS['primary']))
            Rectangle(pos=balance_box.pos, size=balance_box.size)
        
        balance_data = db_manager.get_balance_summary()
        balance_label = Label(
            text=f'[b]当前余额[/b]\n¥{balance_data["current_balance"]:,.2f}',
            markup=True,
            halign='center',
            valign='center',
            color=(1, 1, 1, 1),
            font_size=sp(24)
        )
        balance_box.add_widget(balance_label)
        layout.add_widget(balance_box)
        
        # 快捷操作按钮
        btn_layout = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(10))
        
        income_btn = Button(
            text='+ 收入',
            background_color=get_color_from_hex(THEME_COLORS['success']),
            on_press=self._show_add_income_dialog
        )
        expense_btn = Button(
            text='- 支出',
            background_color=get_color_from_hex(THEME_COLORS['danger']),
            on_press=self._show_add_expense_dialog
        )
        
        btn_layout.add_widget(income_btn)
        btn_layout.add_widget(expense_btn)
        layout.add_widget(btn_layout)
        
        # 本月统计
        stats_box = BoxLayout(size_hint_y=None, height=dp(80), padding=dp(10))
        stats_text = f"本月收入: ¥{balance_data['month_income']:,.2f}\n本月支出: ¥{balance_data['month_expense']:,.2f}"
        stats_label = Label(text=stats_text, halign='center', valign='center', markup=True)
        stats_box.add_widget(stats_label)
        layout.add_widget(stats_box)
        
        # 最近记录标题
        header = Label(
            text='[b]最近交易记录[/b]',
            size_hint_y=None,
            height=dp(40),
            markup=True
        )
        layout.add_widget(header)
        
        # 记录列表
        scroll = ScrollView()
        records_layout = BoxLayout(orientation='vertical', size_hint_y=None, spacing=dp(5))
        records_layout.bind(minimum_height=records_layout.setter('height'))
        
        recent_expenses = db_manager.get_expenses()[:20]
        if recent_expenses:
            for exp in recent_expenses:
                record_item = self._create_record_item(exp)
                records_layout.add_widget(record_item)
        else:
            empty_label = Label(text='暂无记录', size_hint_y=None, height=dp(50))
            records_layout.add_widget(empty_label)
        
        scroll.add_widget(records_layout)
        layout.add_widget(scroll)
        
        self.add_widget(layout)
    
    def _create_record_item(self, exp):
        """创建单条记录项"""
        item = BoxLayout(
            size_hint_y=None,
            height=dp(70),
            padding=dp(10),
            spacing=dp(10)
        )
        
        # 类型图标和颜色
        if exp['type'] == 'income':
            color = THEME_COLORS['success']
            prefix = '+'
        else:
            color = THEME_COLORS['danger']
            prefix = '-'
        
        # 金额显示
        amount_text = f"{prefix}¥{exp['amount']:,.2f}"
        info_text = f"[b]{exp['category']}[/b]\n{exp.get('description', '') or '无描述'}\n{exp['date'][:10]}"
        
        amount_label = Label(
            text=amount_text,
            size_hint_x=0.3,
            halign='right',
            valign='center',
            color=get_color_from_hex(color),
            bold=True,
            font_size=sp(18)
        )
        
        info_label = Label(
            text=info_text,
            size_hint_x=0.7,
            halign='left',
            valign='center',
            markup=True,
            font_size=sp(14)
        )
        
        item.add_widget(info_label)
        item.add_widget(amount_label)
        
        return item
    
    def _show_add_expense_dialog(self, instance):
        """显示添加支出对话框"""
        self._show_add_record_dialog('expense')
    
    def _show_add_income_dialog(self, instance):
        """显示添加收入对话框"""
        self._show_add_record_dialog('income')
    
    def _show_add_record_dialog(self, record_type):
        """显示添加记录对话框"""
        content = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(15))
        
        # 金额输入
        amount_input = TextInput(
            hint_text='输入金额',
            multiline=False,
            input_filter='float',
            size_hint_y=None,
            height=dp(45)
        )
        content.add_widget(amount_input)
        
        # 分类选择
        categories = ['餐饮', '交通', '购物', '娱乐', '医疗', '教育', '居住', '通讯', '其他']
        if record_type == 'income':
            categories = ['工资', '奖金', '投资收益', '兼职', '红包', '其他']
        
        category_spinner = Spinner(
            text='选择分类',
            values=categories,
            size_hint_y=None,
            height=dp(45)
        )
        content.add_widget(category_spinner)
        
        # 描述输入
        desc_input = TextInput(
            hint_text='备注说明（可选）',
            multiline=False,
            size_hint_y=None,
            height=dp(45)
        )
        content.add_widget(desc_input)
        
        # 按钮行
        btn_row = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(10))
        
        def save_record(btn):
            try:
                amount = float(amount_input.text)
                category = category_spinner.text
                description = desc_input.text
                
                if not amount or amount <= 0:
                    return
                
                if category == '选择分类':
                    return
                
                db_manager.add_expense(amount, category, description, record_type)
                popup.dismiss()
                
                # 刷新界面
                self.clear_widgets()
                self._build_ui()
                
            except ValueError:
                pass
        
        save_btn = Button(text='保存', on_press=save_record)
        cancel_btn = Button(text='取消', on_press=lambda x: popup.dismiss())
        
        btn_row.add_widget(save_btn)
        btn_row.add_widget(cancel_row)
        content.add_widget(btn_row)
        
        popup = Popup(
            title=f'添加{"支出" if record_type == "expense" else "收入"}',
            content=content,
            size=(dp(350), dp(350)),
            auto_dismiss=False
        )
        popup.open()


class TaskScreen(Screen):
    """待办任务界面"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'task'
        self._build_ui()
    
    def _build_ui(self):
        layout = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))
        
        # 顶部统计
        stats_box = BoxLayout(size_hint_y=None, height=dp(80), spacing=dp(10), padding=dp(10))
        
        all_tasks = db_manager.get_tasks()
        pending_count = len([t for t in all_tasks if t['status'] in ('pending', 'in_progress')])
        completed_count = len([t for t in all_tasks if t['status'] == 'completed'])
        overdue_count = len(db_manager.get_overdue_tasks())
        
        pending_label = Label(
            text=f'[b]{pending_count}[/b]\n待处理',
            markup=True,
            halign='center'
        )
        completed_label = Label(
            text=f'[b]{completed_count}[/b]\n已完成',
            markup=True,
            halign='center'
        )
        overdue_label = Label(
            text=f'[b]{overdue_count}[/b]\n已逾期',
            markup=True,
            halign='center',
            color=get_color_from_hex(THEME_COLORS['danger'])
        )
        
        stats_box.add_widget(pending_label)
        stats_box.add_widget(completed_label)
        stats_box.add_widget(overdue_label)
        layout.add_widget(stats_box)
        
        # 添加任务按钮
        add_btn = Button(
            text='+ 添加新任务',
            size_hint_y=None,
            height=dp(50),
            background_color=get_color_from_hex(THEME_COLORS['primary']),
            on_press=self._show_add_task_dialog
        )
        layout.add_widget(add_btn)
        
        # 任务筛选标签
        filter_layout = BoxLayout(size_hint_y=None, height=dp(40), spacing=dp(5))
        filters = [('全部', None), ('待处理', 'pending'), ('进行中', 'in_progress'), ('已完成', 'completed')]
        
        for filter_name, filter_value in filters:
            btn = Button(
                text=filter_name,
                size_hint_x=1,
                on_press=lambda x, fv=filter_value: self._filter_tasks(fv)
            )
            filter_layout.add_widget(btn)
        
        layout.add_widget(filter_layout)
        
        # 任务列表
        scroll = ScrollView()
        self.tasks_layout = BoxLayout(orientation='vertical', size_hint_y=None, spacing=dp(5))
        self.tasks_layout.bind(minimum_height=self.tasks_layout.setter('height'))
        
        self._load_tasks(None)
        
        scroll.add_widget(self.tasks_layout)
        layout.add_widget(scroll)
        
        self.add_widget(layout)
    
    def _load_tasks(self, status):
        """加载任务列表"""
        self.tasks_layout.clear_widgets()
        
        tasks = db_manager.get_tasks(status)
        
        if tasks:
            for task in tasks:
                task_item = self._create_task_item(task)
                self.tasks_layout.add_widget(task_item)
        else:
            empty_label = Label(
                text='暂无任务\n点击上方按钮添加新任务',
                size_hint_y=None,
                height=dp(80),
                halign='center',
                valign='center'
            )
            self.tasks_layout.add_widget(empty_label)
    
    def _create_task_item(self, task):
        """创建任务项"""
        item = BoxLayout(
            size_hint_y=None,
            height=dp(90),
            padding=dp(10),
            spacing=dp(10)
        )
        
        # 优先级颜色映射
        priority_colors = {
            'urgent': THEME_COLORS['danger'],
            'high': THEME_COLORS['warning'],
            'medium': THEME_COLORS['secondary'],
            'low': THEME_COLORS['success']
        }
        
        # 状态颜色映射
        status_colors = {
            'pending': THEME_COLORS['text_secondary'],
            'in_progress': THEME_COLORS['primary'],
            'completed': THEME_COLORS['success'],
            'cancelled': THEME_COLORS['text_secondary']
        }
        
        priority_color = priority_colors.get(task['priority'], THEME_COLORS['text_secondary'])
        status_color = status_colors.get(task['status'], THEME_COLORS['text_secondary'])
        
        # 左侧优先级指示条
        priority_indicator = BoxLayout(size_hint_x=None, width=dp(5))
        with priority_indicator.canvas.before:
            Color(*get_color_from_hex(priority_color))
            Rectangle(pos=priority_indicator.pos, size=priority_indicator.size)
        
        # 中间内容区
        content_box = BoxLayout(orientation='vertical', spacing=dp(3))
        
        title_text = task['title']
        if task['status'] == 'completed':
            title_text = f'✓ {title_text}'
        
        title_label = Label(
            text=f"[b]{title_text}[/b]",
            markup=True,
            halign='left',
            valign='top',
            size_hint_y=None,
            height=dp(25)
        )
        
        desc_text = task.get('description', '') or ''
        if len(desc_text) > 30:
            desc_text = desc_text[:30] + '...'
        
        desc_label = Label(
            text=desc_text,
            halign='left',
            size_hint_y=None,
            height=dp(20),
            font_size=sp(12),
            color=get_color_from_hex(THEME_COLORS['text_secondary'])
        )
        
        # 截止日期和状态
        meta_info = []
        if task['due_date']:
            due_date_str = task['due_date'][:10]
            # 检查是否逾期
            if task['status'] not in ('completed', 'cancelled'):
                due_datetime = datetime.strptime(task['due_date'], '%Y-%m-%d %H:%M:%S')
                if due_datetime < datetime.now():
                    due_date_str = f"[color={THEME_COLORS['danger']}]{due_date_str} (已逾期)[/color]"
            meta_info.append(f"截止: {due_date_str}")
        
        meta_info.append(f"状态: {self._get_status_text(task['status'])}")
        
        meta_label = Label(
            text='\n'.join(meta_info),
            markup=True,
            halign='left',
            size_hint_y=None,
            height=dp(35),
            font_size=sp(11),
            color=get_color_from_hex(status_color)
        )
        
        content_box.add_widget(title_label)
        content_box.add_widget(desc_label)
        content_box.add_widget(meta_label)
        
        # 右侧操作按钮
        action_box = BoxLayout(orientation='vertical', size_hint_x=None, width=dp(60), spacing=dp(5))
        
        if task['status'] != 'completed':
            complete_btn = Button(
                text='✓',
                size_hint_y=None,
                height=dp(35),
                font_size=sp(18),
                background_color=get_color_from_hex(THEME_COLORS['success']),
                on_press=lambda x, tid=task['id']: self._complete_task(tid)
            )
            action_box.add_widget(complete_btn)
        
        delete_btn = Button(
            text='×',
            size_hint_y=None,
            height=dp(35),
            font_size=sp(18),
            background_color=get_color_from_hex(THEME_COLORS['danger']),
            on_press=lambda x, tid=task['id']: self._delete_task(tid)
        )
        action_box.add_widget(delete_btn)
        
        item.add_widget(priority_indicator)
        item.add_widget(content_box)
        item.add_widget(action_box)
        
        return item
    
    def _get_status_text(self, status):
        """获取状态文本"""
        status_map = {
            'pending': '待处理',
            'in_progress': '进行中',
            'completed': '已完成',
            'cancelled': '已取消'
        }
        return status_map.get(status, status)
    
    def _filter_tasks(self, status):
        """筛选任务"""
        self._load_tasks(status)
    
    def _complete_task(self, task_id):
        """完成任务"""
        db_manager.update_task_status(task_id, 'completed')
        self._load_tasks(None)
    
    def _delete_task(self, task_id):
        """删除任务"""
        db_manager.delete_task(task_id)
        self._load_tasks(None)
    
    def _show_add_task_dialog(self, instance):
        """显示添加任务对话框"""
        content = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(15))
        
        # 任务标题
        title_input = TextInput(
            hint_text='输入任务标题',
            multiline=False,
            size_hint_y=None,
            height=dp(45)
        )
        content.add_widget(title_input)
        
        # 任务描述
        desc_input = TextInput(
            hint_text='任务描述（可选）',
            multiline=True,
            size_hint_y=None,
            height=dp(80)
        )
        content.add_widget(desc_input)
        
        # 优先级选择
        priority_layout = BoxLayout(size_hint_y=None, height=dp(45), spacing=dp(10))
        priority_label = Label(text='优先级:', size_hint_x=0.3, halign='right', valign='center')
        
        priority_spinner = Spinner(
            text='medium',
            values=['low', 'medium', 'high', 'urgent'],
            size_hint_x=0.7
        )
        priority_layout.add_widget(priority_label)
        priority_layout.add_widget(priority_spinner)
        content.add_widget(priority_layout)
        
        # 截止日期
        date_input = TextInput(
            hint_text='截止日期 (YYYY-MM-DD HH:MM:SS)',
            multiline=False,
            size_hint_y=None,
            height=dp(45),
            text=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        )
        content.add_widget(date_input)
        
        # 提醒时间
        reminder_input = TextInput(
            hint_text='提醒时间 (YYYY-MM-DD HH:MM:SS, 可选)',
            multiline=False,
            size_hint_y=None,
            height=dp(45)
        )
        content.add_widget(reminder_input)
        
        # 按钮行
        btn_row = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(10))
        
        def save_task(btn):
            try:
                title = title_input.text.strip()
                if not title:
                    return
                
                description = desc_input.text.strip()
                priority = priority_spinner.text
                due_date = date_input.text.strip()
                reminder_time = reminder_input.text.strip() or None
                
                db_manager.add_task(title, description, priority, due_date, reminder_time)
                popup.dismiss()
                
                # 刷新界面
                self.clear_widgets()
                self._build_ui()
                
            except Exception as e:
                print(f"Error saving task: {e}")
        
        save_btn = Button(text='保存任务', on_press=save_task)
        cancel_btn = Button(text='取消', on_press=lambda x: popup.dismiss())
        
        btn_row.add_widget(save_btn)
        btn_row.add_widget(cancel_btn)
        content.add_widget(btn_row)
        
        popup = Popup(
            title='添加新任务',
            content=content,
            size=(dp(400), dp(450)),
            auto_dismiss=False
        )
        popup.open()


class BalanceScreen(Screen):
    """余额统计界面"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'balance'
        self._build_ui()
    
    def _build_ui(self):
        layout = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(15))
        
        # 获取数据
        balance_data = db_manager.get_balance_summary()
        category_stats = db_manager.get_category_summary()
        
        # 总览卡片
        overview_box = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=dp(200),
            padding=dp(20),
            spacing=dp(10)
        )
        with overview_box.canvas.before:
            Color(*get_color_from_hex(THEME_COLORS['primary']))
            Rectangle(pos=overview_box.pos, size=overview_box.size)
        
        title_label = Label(
            text='[b][size=28]财务总览[/size][/b]',
            markup=True,
            halign='center',
            color=(1, 1, 1, 1),
            size_hint_y=None,
            height=dp(40)
        )
        
        balance_label = Label(
            text=f'[size=36]¥{balance_data["current_balance"]:,.2f}[/size]',
            markup=True,
            halign='center',
            color=(1, 1, 1, 1),
            size_hint_y=None,
            height=dp(50)
        )
        
        income_expense_label = Label(
            text=f'总收入: ¥{balance_data["total_income"]:,.2f}  |  总支出: ¥{balance_data["total_expense"]:,.2f}',
            markup=True,
            halign='center',
            color=(1, 1, 1, 0.9),
            size_hint_y=None,
            height=dp(30)
        )
        
        month_label = Label(
            text=f'本月净收支: {"+" if balance_data["month_net"] >= 0 else ""}¥{balance_data["month_net"]:,.2f}',
            markup=True,
            halign='center',
            color=(1, 1, 1, 0.8) if balance_data["month_net"] >= 0 else get_color_from_hex('#FFCDD2'),
            size_hint_y=None,
            height=dp(30)
        )
        
        overview_box.add_widget(title_label)
        overview_box.add_widget(balance_label)
        overview_box.add_widget(income_expense_label)
        overview_box.add_widget(month_label)
        layout.add_widget(overview_box)
        
        # 本月详情
        month_header = Label(
            text='[b]本月收支明细[/b]',
            size_hint_y=None,
            height=dp(40),
            markup=True
        )
        layout.add_widget(month_header)
        
        month_detail = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=dp(100),
            padding=dp(15),
            spacing=dp(10)
        )
        
        income_bar = BoxLayout(size_hint_y=None, height=dp(30))
        income_label = Label(text='收入:', size_hint_x=0.3, halign='left')
        income_value = Label(
            text=f'¥{balance_data["month_income"]:,.2f}',
            size_hint_x=0.7,
            halign='right',
            color=get_color_from_hex(THEME_COLORS['success'])
        )
        income_bar.add_widget(income_label)
        income_bar.add_widget(income_value)
        
        expense_bar = BoxLayout(size_hint_y=None, height=dp(30))
        expense_label = Label(text='支出:', size_hint_x=0.3, halign='left')
        expense_value = Label(
            text=f'¥{balance_data["month_expense"]:,.2f}',
            size_hint_x=0.7,
            halign='right',
            color=get_color_from_hex(THEME_COLORS['danger'])
        )
        expense_bar.add_widget(expense_label)
        expense_bar.add_widget(expense_value)
        
        net_bar = BoxLayout(size_hint_y=None, height=dp(30))
        net_label = Label(text='结余:', size_hint_x=0.3, halign='left')
        net_value = Label(
            text=f'{"+" if balance_data["month_net"] >= 0 else ""}¥{balance_data["month_net"]:,.2f}',
            size_hint_x=0.7,
            halign='right',
            bold=True
        )
        net_bar.add_widget(net_label)
        net_bar.add_widget(net_value)
        
        month_detail.add_widget(income_bar)
        month_detail.add_widget(expense_bar)
        month_detail.add_widget(net_bar)
        layout.add_widget(month_detail)
        
        # 分类统计
        category_header = Label(
            text='[b]支出分类统计[/b]',
            size_hint_y=None,
            height=dp(40),
            markup=True
        )
        layout.add_widget(category_header)
        
        scroll = ScrollView()
        category_layout = BoxLayout(orientation='vertical', size_hint_y=None, spacing=dp(5))
        category_layout.bind(minimum_height=category_layout.setter('height'))
        
        if category_stats:
            for cat in category_stats:
                if float(cat['expense_sum']) > 0:
                    cat_item = self._create_category_item(cat)
                    category_layout.add_widget(cat_item)
        else:
            empty_label = Label(text='暂无数据', size_hint_y=None, height=dp(50))
            category_layout.add_widget(empty_label)
        
        scroll.add_widget(category_layout)
        layout.add_widget(scroll)
        
        self.add_widget(layout)
    
    def _create_category_item(self, cat):
        """创建分类项"""
        item = BoxLayout(
            size_hint_y=None,
            height=dp(60),
            padding=dp(10),
            spacing=dp(10)
        )
        
        name_label = Label(
            text=f"[b]{cat['category']}[/b]",
            markup=True,
            size_hint_x=0.4,
            halign='left',
            valign='center'
        )
        
        amount_label = Label(
            text=f"¥{float(cat['expense_sum']):,.2f}",
            size_hint_x=0.3,
            halign='right',
            valign='center',
            color=get_color_from_hex(THEME_COLORS['danger'])
        )
        
        count_label = Label(
            text=f"{cat['count']}笔",
            size_hint_x=0.3,
            halign='right',
            valign='center',
            font_size=sp(12),
            color=get_color_from_hex(THEME_COLORS['text_secondary'])
        )
        
        item.add_widget(name_label)
        item.add_widget(amount_label)
        item.add_widget(count_label)
        
        return item


class TimeManagementScreen(Screen):
    """时间管理界面"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'time_management'
        self._update_event = None
        self._build_ui()
        # 启动定时更新（每分钟刷新一次）
        self._update_event = Clock.schedule_interval(self._update_time_display, 60)
    
    def _build_ui(self):
        layout = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))
        
        # 今日使用时间概览
        time_overview = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=dp(150),
            padding=dp(15),
            spacing=dp(10)
        )
        with time_overview.canvas.before:
            Color(*get_color_from_hex(THEME_COLORS['secondary']))
            Rectangle(pos=time_overview.pos, size=time_overview.size)
        
        time_stats = db_manager.get_time_stats(period='today')
        
        title_label = Label(
            text='[b]今日屏幕时间[/b]',
            markup=True,
            halign='center',
            size_hint_y=None,
            height=dp(35)
        )
        
        hours = int(time_stats['total_hours'])
        minutes = int((time_stats['total_hours'] - hours) * 60)
        time_display = Label(
            text=f'[size=42]{hours}小时{minutes:02d}分钟[/size]',
            markup=True,
            halign='center',
            size_hint_y=None,
            height=dp(55)
        )
        
        productivity_label = Label(
            text=f'生产力占比: {time_stats["productive_percentage"]}%',
            markup=True,
            halign='center',
            size_hint_y=None,
            height=dp(30)
        )
        
        time_overview.add_widget(title_label)
        time_overview.add_widget(time_display)
        time_overview.add_widget(productivity_label)
        layout.add_widget(time_overview)
        
        # 时间限制设置
        limit_section = BoxLayout(
            size_hint_y=None,
            height=dp(80),
            padding=dp(10),
            spacing=dp(10)
        )
        
        limit_label = Label(
            text='每日时间限制:',
            size_hint_x=0.4,
            halign='left',
            valign='center'
        )
        
        current_limit = int(db_manager.get_setting('daily_time_limit', 3600))
        current_hours = current_limit // 3600
        
        self.time_slider = Slider(
            min=0.5,
            max=12,
            value=current_hours,
            step=0.5,
            size_hint_x=0.5,
            on_value_change=self._update_time_limit
        )
        
        self.limit_value_label = Label(
            text=f'{current_hours}小时',
            size_hint_x=0.1,
            halign='center',
            valign='center'
        )
        
        limit_section.add_widget(limit_label)
        limit_section.add_widget(self.time_slider)
        limit_section.add_widget(self.limit_value_label)
        layout.add_widget(limit_section)
        
        # 使用进度条
        progress_section = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=dp(80),
            padding=dp(10),
            spacing=dp(10)
        )
        
        progress_label = Label(
            text='今日使用进度:',
            size_hint_y=None,
            height=dp(25),
            halign='left'
        )
        
        usage_ratio = min(time_stats['total_seconds'] / current_limit, 1.0) if current_limit > 0 else 0
        self.usage_progress = ProgressBar(
            max=1,
            value=usage_ratio,
            size_hint_y=None,
            height=dp(25)
        )
        
        # 根据使用量设置颜色
        if usage_ratio > 0.9:
            self.usage_progress.color = get_color_from_hex(THEME_COLORS['danger'])
        elif usage_ratio > 0.7:
            self.usage_progress.color = get_color_from_hex(THEME_COLORS['warning'])
        else:
            self.usage_progress.color = get_color_from_hex(THEME_COLORS['success'])
        
        usage_percent_label = Label(
            text=f'{usage_ratio * 100:.1f}% ({hours}h{minutes:02d}m / {current_hours}h)',
            size_hint_y=None,
            height=dp(25),
            halign='center'
        )
        
        progress_section.add_widget(progress_label)
        progress_section.add_widget(self.usage_progress)
        progress_section.add_widget(usage_percent_label)
        layout.add_widget(progress_section)
        
        # 应用使用排行
        app_header = Label(
            text='[b]应用使用排行 (Top 10)[/b]',
            size_hint_y=None,
            height=dp(40),
            markup=True
        )
        layout.add_widget(app_header)
        
        scroll = ScrollView()
        app_layout = BoxLayout(orientation='vertical', size_hint_y=None, spacing=dp(5))
        app_layout.bind(minimum_height=app_layout.setter('height'))
        
        if time_stats['app_stats']:
            for idx, app in enumerate(time_stats['app_stats'], 1):
                app_item = self._create_app_usage_item(idx, app)
                app_layout.add_widget(app_item)
        else:
            empty_label = Label(
                text='暂无使用记录\n开始使用手机后将自动记录',
                size_hint_y=None,
                height=dp(80),
                halign='center'
            )
            app_layout.add_widget(empty_label)
        
        scroll.add_widget(app_layout)
        layout.add_widget(scroll)
        
        # 添加模拟数据按钮（用于演示）
        demo_btn = Button(
            text='添加示例数据',
            size_hint_y=None,
            height=dp(45),
            background_color=get_color_from_hex(THEME_COLORS['primary']),
            on_press=self._add_demo_data
        )
        layout.add_widget(demo_btn)
        
        self.add_widget(layout)
    
    def _create_app_usage_item(self, rank, app):
        """创建应用使用项"""
        item = BoxLayout(
            size_hint_y=None,
            height=dp(50),
            padding=dp(8),
            spacing=dp(8)
        )
        
        rank_label = Label(
            text=f'[b]{rank}.[/b]',
            markup=True,
            size_hint_x=0.1,
            halign='center',
            valign='center'
        )
        
        name_label = Label(
            text=app['app_name'] or '未知应用',
            size_hint_x=0.5,
            halign='left',
            valign='center'
        )
        
        duration_seconds = app['total_seconds']
        duration_hours = duration_seconds // 3600
        duration_minutes = (duration_seconds % 3600) // 60
        
        if duration_hours > 0:
            duration_text = f"{duration_hours}h{duration_minutes:02d}m"
        else:
            duration_text = f"{duration_minutes}m"
        
        duration_label = Label(
            text=duration_text,
            size_hint_x=0.2,
            halign='right',
            valign='center',
            color=get_color_from_hex(THEME_COLORS['text_secondary'])
        )
        
        count_label = Label(
            text=f"{app['count']}次",
            size_hint_x=0.2,
            halign='right',
            valign='center',
            font_size=sp(12),
            color=get_color_from_hex(THEME_COLORS['text_secondary'])
        )
        
        item.add_widget(rank_label)
        item.add_widget(name_label)
        item.add_widget(duration_label)
        item.add_widget(count_label)
        
        return item
    
    def _update_time_limit(self, instance, value):
        """更新时间限制"""
        hours = int(value)
        minutes = int((value - hours) * 60)
        total_seconds = hours * 3600 + minutes * 60
        
        db_manager.set_setting('daily_time_limit', total_seconds)
        self.limit_value_label.text = f'{value:.1f}小时'
        
        # 更新进度条
        time_stats = db_manager.get_time_stats(period='today')
        usage_ratio = min(time_stats['total_seconds'] / total_seconds, 1.0) if total_seconds > 0 else 0
        self.usage_progress.value = usage_ratio
    
    def _update_time_display(self, dt):
        """定时更新时间显示"""
        try:
            self.clear_widgets()
            self._build_ui()
        except Exception as e:
            print(f"Update error: {e}")
    
    def _add_demo_data(self, instance):
        """添加示例数据用于演示"""
        import random
        
        apps = [
            ('微信', '社交', True),
            ('抖音', '娱乐', False),
            ('支付宝', '工具', True),
            ('淘宝', '购物', False),
            ('微博', '社交', False),
            ('知乎', '学习', True),
            ('王者荣耀', '游戏', False),
            ('钉钉', '工作', True),
            ('哔哩哔哩', '娱乐', False),
            ('网易云音乐', '娱乐', False)
        ]
        
        today = datetime.now().strftime('%Y-%m-%d')
        
        for app_name, category, is_productive in apps:
            # 随机生成使用时长（5分钟到3小时）
            duration = random.randint(300, 10800)
            db_manager.add_time_log(app_name, category, duration, today, is_productive)
        
        # 刷新界面
        self.clear_widgets()
        self._build_ui()


class MainScreen(Screen):
    """主界面/仪表盘"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'main'
        self._build_ui()
    
    def _build_ui(self):
        layout = BoxLayout(orientation='vertical', padding=dp(15), spacing=dp(15))
        
        # 应用标题
        header = BoxLayout(size_hint_y=None, height=dp(80))
        with header.canvas.before:
            Color(*get_color_from_hex(THEME_COLORS['primary']))
            Rectangle(pos=header.pos, size=header.size)
        
        title = Label(
            text=f'[b][size=24]Personal Manager[/size][/b]\n[size=14]个人财务与时间管理助手[/size]',
            markup=True,
            halign='center',
            valign='center',
            color=(1, 1, 1, 1)
        )
        header.add_widget(title)
        layout.add_widget(header)
        
        # 快速概览卡片
        overview_grid = GridLayout(cols=2, spacing=dp(10), size_hint_y=None, height=dp(200))
        
        # 余额卡片
        balance_card = self._create_quick_card(
            '💰 当前余额',
            f"¥{db_manager.get_balance_summary()['current_balance']:,.2f}",
            THEME_COLORS['success'],
            lambda x: self.manager.current = 'balance'
        )
        overview_grid.add_widget(balance_card)
        
        # 待办卡片
        tasks = db_manager.get_tasks()
        pending_count = len([t for t in tasks if t['status'] in ('pending', 'in_progress')])
        task_card = self._create_quick_card(
            '📋 待办任务',
            f"{pending_count}项",
            THEME_COLORS['warning'],
            lambda x: self.manager.current = 'task'
        )
        overview_grid.add_widget(task_card)
        
        # 本月支出卡片
        balance_data = db_manager.get_balance_summary()
        expense_card = self._create_quick_card(
            '📊 本月支出',
            f"¥{balance_data['month_expense']:,.2f}",
            THEME_COLORS['danger'],
            lambda x: self.manager.current = 'expense'
        )
        overview_grid.add_widget(expense_card)
        
        # 今日屏幕时间卡片
        time_stats = db_manager.get_time_stats(period='today')
        hours = int(time_stats['total_hours'])
        minutes = int((time_stats['total_hours'] - hours) * 60)
        time_card = self._create_quick_card(
            '⏱️ 屏幕时间',
            f"{hours}h{minutes:02d}m",
            THEME_COLORS['primary'],
            lambda x: self.manager.current = 'time_management'
        )
        overview_grid.add_widget(time_card)
        
        layout.add_widget(overview_grid)
        
        # 功能入口列表
        functions_label = Label(
            text='[b]功能模块[/b]',
            size_hint_y=None,
            height=dp(40),
            markup=True
        )
        layout.add_widget(functions_label)
        
        functions_list = [
            ('💸 花销记录', '记录日常收支，管理财务状况', 'expense'),
            ('📝 待办任务', '管理待办事项，提高工作效率', 'task'),
            ('📈 余额统计', '查看收支分析，掌握财务动态', 'balance'),
            ('⏰ 时间管理', '监控屏幕时间，提升专注力', 'time_management')
        ]
        
        for func_name, func_desc, screen_name in functions_list:
            func_item = self._create_function_item(func_name, func_desc, screen_name)
            layout.add_widget(func_item)
        
        # 底部提示
        footer = Label(
            text=f'版本 {APP_VERSION} | 数据存储于本地数据库',
            size_hint_y=None,
            height=dp(30),
            font_size=sp(11),
            color=get_color_from_hex(THEME_COLORS['text_secondary'])
        )
        layout.add_widget(footer)
        
        self.add_widget(layout)
    
    def _create_quick_card(self, title, value, color, on_press_callback):
        """创建快速概览卡片"""
        card = Button(
            orientation='vertical',
            background_normal='',
            background_color=(1, 1, 1, 1),
            border=dp(2),
            on_press=on_press_callback
        )
        
        card_content = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(5))
        
        title_lbl = Label(
            text=title,
            size_hint_y=None,
            height=dp(25),
            font_size=sp(13),
            color=get_color_from_hex(THEME_COLORS['text_secondary'])
        )
        
        value_lbl = Label(
            text=f"[b][size=22]{value}[/size][/b]",
            markup=True,
            size_hint_y=None,
            height=dp(40),
            color=get_color_from_hex(color)
        )
        
        card_content.add_widget(title_lbl)
        card_content.add_widget(value_lbl)
        card.add_widget(card_content)
        
        # 添加边框效果
        with card.canvas.after:
            Color(*get_color_from_hex(color), 0.3)
            Line(rounded_rectangle=(card.x, card.y, card.width, card.height, dp(10)), width=dp(2))
        
        return card
    
    def _create_function_item(self, name, description, screen_name):
        """创建功能入口项"""
        item = Button(
            size_hint_y=None,
            height=dp(70),
            background_normal='',
            background_color=(1, 1, 1, 0.9),
            on_press=lambda x, sn=screen_name: setattr(self.manager, 'current', sn)
        )
        
        item_content = BoxLayout(padding=dp(15))
        
        text_box = BoxLayout(orientation='vertical', spacing=dp(3))
        
        name_label = Label(
            text=f"[b]{name}[/b]",
            markup=True,
            halign='left',
            size_hint_y=None,
            height=dp(30)
        )
        
        desc_label = Label(
            text=description,
            halign='left',
            size_hint_y=None,
            height=dp(25),
            font_size=sp(12),
            color=get_color_from_hex(THEME_COLORS['text_secondary'])
        )
        
        arrow_label = Label(
            text='>',
            size_hint_x=None,
            width=dp(30),
            halign='center',
            valign='center',
            font_size=sp(20),
            color=get_color_from_hex(THEME_COLORS['text_secondary'])
        )
        
        text_box.add_widget(name_label)
        text_box.add_widget(desc_label)
        item_content.add_widget(text_box)
        item_content.add_widget(arrow_label)
        item.add_widget(item_content)
        
        # 底部分割线
        with item.canvas.after:
            Color(*get_color_from_hex('#E0E0E0'))
            Line(points=[item.x+dp(15), item.y, item.right-dp(15), item.y], width=dp(1))
        
        return item


class PersonalManagerApp(App):
    """PersonalManager 主应用类"""
    
    def build(self):
        """构建应用界面"""
        # 设置窗口背景色
        Window.clearcolor = get_color_from_hex(THEME_COLORS['background'])
        
        # 创建屏幕管理器
        sm = ScreenManager()
        
        # 添加各功能界面
        sm.add_widget(MainScreen())
        sm.add_widget(ExpenseScreen())
        sm.add_widget(TaskScreen())
        sm.add_widget(BalanceScreen())
        sm.add_widget(TimeManagementScreen())
        
        return sm
    
    def on_stop(self):
        """应用停止时清理资源"""
        if hasattr(self, '_update_event') and self._update_event:
            self._update_event.cancel()
        db_manager.close()
        return True


if __name__ == '__main__':
    PersonalManagerApp().run()