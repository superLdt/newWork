#!/usr/bin/env python3
"""
车辆数据迁移脚本
将vehicles表中无task_id的数据迁移到vehicle_capacity_reference表
"""

import sys
import os
from datetime import datetime
import json

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app import create_app
from app.extensions import db
from app.models.vehicle.vehicle import Vehicle
from app.models.vehicle.vehicle_capacity_reference import VehicleCapacityReference
from sqlalchemy.exc import SQLAlchemyError


def migrate_vehicle_data():
    """
    执行车辆数据迁移
    """
    app = create_app('development')
    
    with app.app_context():
        try:
            print("开始车辆数据迁移...")
            
            # 查找vehicles表中task_id为空的记录
            vehicles_to_migrate = Vehicle.query.filter(
                db.or_(
                    Vehicle.task_id.is_(None),
                    Vehicle.task_id == ''
                )
            ).all()
            
            print(f"找到 {len(vehicles_to_migrate)} 条需要迁移的车辆记录")
            
            migrated_count = 0
            skipped_count = 0
            error_count = 0
            
            for vehicle in vehicles_to_migrate:
                try:
                    # 检查是否已经存在相同的记录
                    existing_record = None
                    if vehicle.license_plate:
                        existing_record = VehicleCapacityReference.query.filter_by(
                            license_plate=vehicle.license_plate
                        ).first()
                    elif vehicle.carriage_number:
                        existing_record = VehicleCapacityReference.query.filter_by(
                            carriage_number=vehicle.carriage_number
                        ).first()
                    
                    if existing_record:
                        print(f"跳过重复记录: {vehicle.license_plate or vehicle.carriage_number}")
                        skipped_count += 1
                        continue
                    
                    # 处理常用公司列表
                    frequent_companies_json = '[]'
                    if vehicle.frequent_companies:
                        try:
                            # 如果已经是JSON格式，直接使用
                            if isinstance(vehicle.frequent_companies, str):
                                json.loads(vehicle.frequent_companies)  # 验证JSON格式
                                frequent_companies_json = vehicle.frequent_companies
                            else:
                                frequent_companies_json = json.dumps(vehicle.frequent_companies, ensure_ascii=False)
                        except (json.JSONDecodeError, TypeError):
                            frequent_companies_json = '[]'
                    
                    # 自动设置车辆分类
                    vehicle_category = '单车'
                    if vehicle.carriage_number and '挂' in vehicle.carriage_number:
                        vehicle_category = '挂车'
                    
                    # 创建新的车辆容积参考记录
                    new_record = VehicleCapacityReference(
                        vehicle_type=vehicle.vehicle_type,
                        standard_volume=vehicle.actual_volume,  # 将actual_volume映射到standard_volume
                        license_plate=vehicle.license_plate,
                        carriage_number=vehicle.carriage_number,
                        vehicle_category=vehicle_category,
                        frequent_companies=frequent_companies_json,
                        status='active' if vehicle.status in ['active', '待确认', '已分配'] else 'inactive',
                        original_capacity=vehicle.original_capacity,
                        suppliers=vehicle.supplier_type or '',
                        created_at=vehicle.created_at or datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        updated_at=vehicle.updated_at or datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    )
                    
                    db.session.add(new_record)
                    migrated_count += 1
                    
                    print(f"迁移记录: {vehicle.license_plate or vehicle.carriage_number} -> vehicle_capacity_reference")
                    
                except Exception as e:
                    print(f"迁移记录失败 {vehicle.license_plate or vehicle.carriage_number}: {str(e)}")
                    error_count += 1
                    continue
            
            # 提交所有更改
            if migrated_count > 0:
                db.session.commit()
                print(f"成功迁移 {migrated_count} 条记录到 vehicle_capacity_reference 表")
            
            print(f"迁移完成统计:")
            print(f"  - 成功迁移: {migrated_count} 条")
            print(f"  - 跳过重复: {skipped_count} 条")
            print(f"  - 迁移失败: {error_count} 条")
            
            # 询问是否删除已迁移的记录
            if migrated_count > 0:
                print("\n注意: 迁移完成后，建议手动检查数据正确性")
                print("如果确认数据正确，可以考虑删除vehicles表中已迁移的记录")
                print("删除命令: DELETE FROM vehicles WHERE task_id IS NULL OR task_id = '';")
            
        except SQLAlchemyError as e:
            db.session.rollback()
            print(f"数据库操作失败: {str(e)}")
            return False
        except Exception as e:
            print(f"迁移过程中发生错误: {str(e)}")
            return False
    
    return True


def cleanup_migrated_data():
    """
    清理已迁移的数据（可选）
    """
    app = create_app('development')
    
    with app.app_context():
        try:
            print("开始清理已迁移的车辆数据...")
            
            # 删除vehicles表中task_id为空的记录
            deleted_count = Vehicle.query.filter(
                db.or_(
                    Vehicle.task_id.is_(None),
                    Vehicle.task_id == ''
                )
            ).delete(synchronize_session=False)
            
            db.session.commit()
            
            print(f"成功删除 {deleted_count} 条已迁移的记录")
            
        except SQLAlchemyError as e:
            db.session.rollback()
            print(f"清理数据失败: {str(e)}")
            return False
        except Exception as e:
            print(f"清理过程中发生错误: {str(e)}")
            return False
    
    return True


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='车辆数据迁移脚本')
    parser.add_argument('--migrate', action='store_true', help='执行数据迁移')
    parser.add_argument('--cleanup', action='store_true', help='清理已迁移的数据')
    
    args = parser.parse_args()
    
    if args.migrate:
        success = migrate_vehicle_data()
        if success:
            print("数据迁移完成")
        else:
            print("数据迁移失败")
            sys.exit(1)
    
    if args.cleanup:
        confirm = input("确认要删除vehicles表中已迁移的数据吗？(yes/no): ")
        if confirm.lower() == 'yes':
            success = cleanup_migrated_data()
            if success:
                print("数据清理完成")
            else:
                print("数据清理失败")
                sys.exit(1)
        else:
            print("取消数据清理")
    
    if not args.migrate and not args.cleanup:
        print("请指定操作: --migrate 或 --cleanup")
        parser.print_help()