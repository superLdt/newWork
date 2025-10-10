#!/usr/bin/env python3
"""
数据库模型一致性检查工具
检查数据库表结构与模型定义是否一致
"""

import sqlite3
import os
import sys
from datetime import datetime
from typing import Dict, List, Set, Tuple

# 添加项目路径到Python路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

# 导入所有模型类
from app.models import *
from app.models.vehicle import *
from app.models.dispatch import *
from app.models.vehicle.vehicle_downgrade_record import VehicleDowngradeRecord
from app.models.vehicle.vehicle_merge_record import VehicleMergeRecord


class DatabaseModelChecker:
    """数据库模型一致性检查器"""
    
    def __init__(self, db_path: str):
        """
        初始化检查器
        
        Args:
            db_path: 数据库文件路径
        """
        self.db_path = db_path
        self.db_tables = {}
        self.model_classes = {}
        self.report = []
    
    def connect_db(self):
        """连接数据库"""
        try:
            conn = sqlite3.connect(self.db_path)
            return conn
        except Exception as e:
            self.report.append(f"连接数据库失败: {e}")
            return None
    
    def get_database_tables(self) -> Dict[str, List[str]]:
        """
        获取数据库中所有表及其字段信息
        
        Returns:
            Dict[str, List[str]]: 表名到字段列表的映射
        """
        conn = self.connect_db()
        if not conn:
            return {}
        
        tables = {}
        try:
            cursor = conn.cursor()
            
            # 获取所有表名
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            table_names = [row[0] for row in cursor.fetchall()]
            
            # 获取每个表的字段信息
            for table_name in table_names:
                cursor.execute(f"PRAGMA table_info({table_name});")
                columns = [row[1] for row in cursor.fetchall()]
                tables[table_name] = columns
                
        except Exception as e:
            self.report.append(f"获取数据库表信息失败: {e}")
        finally:
            conn.close()
            
        return tables
    
    def get_model_classes(self) -> Dict[str, type]:
        """
        获取所有模型类
        
        Returns:
            Dict[str, type]: 表名到模型类的映射
        """
        # 手动列出所有模型类
        model_classes = {
            'User': User,
            'Company': Company,
            'Role': Role,
            'ManualDispatchTask': ManualDispatchTask,
            'Vehicle': Vehicle,
            'DispatchStatusHistory': DispatchStatusHistory,
            'VehicleCapacityReference': VehicleCapacityReference,
            'Permission': Permission,
            'Menu': Menu,
            'RolePermission': RolePermission,
            'MenuPermission': MenuPermission,
            'OperationLog': OperationLog,
            'VehicleVolumeHistory': VehicleVolumeHistory,
            'VehicleDowngradeRecord': VehicleDowngradeRecord,
            'VehicleMergeRecord': VehicleMergeRecord
        }
        
        return model_classes
    
    def get_association_tables(self) -> Dict[str, type]:
        """
        获取所有关联表
        
        Returns:
            Dict[str, type]: 表名到关联表的映射
        """
        # 手动列出所有关联表
        association_tables = {
            'UserRole': user_role
        }
        
        return association_tables
    
    def get_model_columns(self, model_class: type) -> List[str]:
        """
        获取模型类对应的字段名列表
        
        Args:
            model_class: SQLAlchemy模型类
            
        Returns:
            List[str]: 字段名列表
        """
        if hasattr(model_class, '__table__'):
            return [column.name for column in model_class.__table__.columns]
        return []
    
    def get_association_table_columns(self, association_table) -> List[str]:
        """
        获取关联表的字段名列表
        
        Args:
            association_table: SQLAlchemy关联表
            
        Returns:
            List[str]: 字段名列表
        """
        if hasattr(association_table, 'columns'):
            return [column.name for column in association_table.columns]
        return []
    
    def compare_structure(self) -> List[str]:
        """
        比较数据库表结构与模型定义
        
        Returns:
            List[str]: 比较结果报告
        """
        comparison_report = []
        
        # 获取数据库表结构
        db_tables = self.get_database_tables()
        if not db_tables:
            comparison_report.append("无法获取数据库表结构信息")
            return comparison_report
            
        # 获取模型类
        model_classes = self.get_model_classes()
        
        # 获取关联表
        association_tables = self.get_association_tables()
        
        comparison_report.append("=== 数据库模型一致性检查报告 ===")
        comparison_report.append(f"检查时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        comparison_report.append("")
        
        # 检查每个模型类
        for table_name, model_class in model_classes.items():
            db_table_name = model_class.__tablename__ if hasattr(model_class, '__tablename__') else table_name
            
            comparison_report.append(f"检查模型: {table_name} (表名: {db_table_name})")
            
            # 检查表是否存在
            if db_table_name not in db_tables:
                comparison_report.append(f"  ❌ 数据库中缺少表: {db_table_name}")
                continue
                
            # 获取数据库字段和模型字段
            db_columns = set(db_tables[db_table_name])
            model_columns = set(self.get_model_columns(model_class))
            
            # 比较字段
            missing_in_db = model_columns - db_columns
            extra_in_db = db_columns - model_columns
            
            if missing_in_db:
                comparison_report.append(f"  ⚠️  模型中有但数据库中缺少的字段: {', '.join(missing_in_db)}")
            
            if extra_in_db:
                comparison_report.append(f"  ℹ️  数据库中有但模型中缺少的字段: {', '.join(extra_in_db)}")
            
            if not missing_in_db and not extra_in_db:
                comparison_report.append(f"  ✅ 表结构一致")
                
            comparison_report.append("")
        
        # 检查关联表
        for table_name, assoc_table in association_tables.items():
            db_table_name = table_name
            
            comparison_report.append(f"检查关联表: {table_name}")
            
            # 检查表是否存在
            if db_table_name not in db_tables:
                comparison_report.append(f"  ❌ 数据库中缺少表: {db_table_name}")
                continue
                
            # 获取数据库字段和关联表字段
            db_columns = set(db_tables[db_table_name])
            assoc_columns = set(self.get_association_table_columns(assoc_table))
            
            # 比较字段
            missing_in_db = assoc_columns - db_columns
            extra_in_db = db_columns - assoc_columns
            
            if missing_in_db:
                comparison_report.append(f"  ⚠️  关联表中有但数据库中缺少的字段: {', '.join(missing_in_db)}")
            
            if extra_in_db:
                comparison_report.append(f"  ℹ️  数据库中有但关联表中缺少的字段: {', '.join(extra_in_db)}")
            
            if not missing_in_db and not extra_in_db:
                comparison_report.append(f"  ✅ 表结构一致")
                
            comparison_report.append("")
        
        # 检查数据库中有但模型中没有的表
        model_table_names = [cls.__tablename__ if hasattr(cls, '__tablename__') else name 
                            for name, cls in model_classes.items()]
        assoc_table_names = list(association_tables.keys())
        all_model_table_names = model_table_names + assoc_table_names + ['alembic_version']  # alembic_version是迁移工具表
        
        extra_tables = set(db_tables.keys()) - set(all_model_table_names)
        
        if extra_tables:
            comparison_report.append("=== 数据库中有多余的表 ===")
            for table in extra_tables:
                comparison_report.append(f"  ℹ️  数据库中有但模型中缺少的表: {table}")
            comparison_report.append("")
        
        return comparison_report
    
    def generate_report(self) -> str:
        """
        生成完整的检查报告
        
        Returns:
            str: 检查报告内容
        """
        # 获取数据库信息
        db_tables = self.get_database_tables()
        
        # 添加数据库概览
        self.report.append("=== 数据库概览 ===")
        self.report.append(f"数据库路径: {self.db_path}")
        self.report.append(f"表数量: {len(db_tables)}")
        self.report.append("")
        
        for table_name, columns in db_tables.items():
            self.report.append(f"表: {table_name}")
            self.report.append(f"  字段: {', '.join(columns)}")
            self.report.append("")
        
        # 添加模型概览
        model_classes = self.get_model_classes()
        association_tables = self.get_association_tables()
        self.report.append("=== 模型概览 ===")
        self.report.append(f"模型数量: {len(model_classes)}")
        self.report.append(f"关联表数量: {len(association_tables)}")
        self.report.append("")
        
        for name, cls in model_classes.items():
            table_name = getattr(cls, '__tablename__', name)
            columns = self.get_model_columns(cls)
            self.report.append(f"模型: {name} (表名: {table_name})")
            self.report.append(f"  字段: {', '.join(columns)}")
            self.report.append("")
        
        for name, table in association_tables.items():
            columns = self.get_association_table_columns(table)
            self.report.append(f"关联表: {name}")
            self.report.append(f"  字段: {', '.join(columns)}")
            self.report.append("")
        
        # 添加结构比较结果
        comparison_results = self.compare_structure()
        self.report.extend(comparison_results)
        
        return "\n".join(self.report)


def main():
    """主函数"""
    # 数据库路径
    db_path = os.path.join(os.path.dirname(__file__), '..', '..', 'database.db')
    
    # 检查数据库文件是否存在
    if not os.path.exists(db_path):
        print(f"数据库文件不存在: {db_path}")
        return
    
    # 创建检查器并生成报告
    checker = DatabaseModelChecker(db_path)
    report_content = checker.generate_report()
    
    # 输出报告到控制台
    print(report_content)
    
    # 保存报告到docs目录
    docs_dir = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'docs')
    if not os.path.exists(docs_dir):
        os.makedirs(docs_dir)
    
    report_path = os.path.join(docs_dir, 'db_model_consistency_report.md')
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report_content)
    
    print(f"\n报告已保存到: {report_path}")


if __name__ == "__main__":
    main()