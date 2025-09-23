#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试任务与车辆/车厢的唯一性约束功能
"""

from app import create_app
from app.extensions import db
from app.models import Vehicle, ManualDispatchTask
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
import sys

def test_database_constraint():
    """测试数据库层面的唯一性约束"""
    print("=== 测试数据库唯一性约束 ===")
    
    app = create_app()
    with app.app_context():
        try:
            # 检查表结构
            result = db.session.execute(text('PRAGMA table_info(vehicles)'))
            columns = result.fetchall()
            task_id_column = None
            for row in columns:
                if row[1] == 'task_id':
                    task_id_column = row
                    break
            
            if task_id_column:
                print(f"✅ task_id字段存在: {task_id_column[1]} {task_id_column[2]} {'NOT NULL' if task_id_column[3] else 'NULL'}")
            else:
                print("❌ task_id字段不存在")
                return False
            
            # 检查唯一性约束
            result = db.session.execute(text('PRAGMA index_list(vehicles)'))
            indexes = result.fetchall()
            unique_constraint_exists = False
            for row in indexes:
                if row[2] == 1:  # unique index
                    # 检查索引详情
                    result2 = db.session.execute(text(f'PRAGMA index_info({row[1]})'))
                    index_info = result2.fetchall()
                    for info in index_info:
                        if info[2] == 'task_id':
                            unique_constraint_exists = True
                            print(f"✅ 找到task_id唯一性约束: {row[1]}")
                            break
            
            if not unique_constraint_exists:
                print("❌ 未找到task_id唯一性约束")
                return False
            
            # 测试插入重复数据
            print("\n--- 测试插入重复task_id ---")
            test_task_id = "TEST_UNIQUE_001"
            
            # 清理可能存在的测试数据
            db.session.execute(text(f"DELETE FROM vehicles WHERE task_id = '{test_task_id}'"))
            db.session.commit()
            
            # 插入第一条记录
            try:
                db.session.execute(text(f"""
                    INSERT INTO vehicles (task_id, license_plate, vehicle_type) 
                    VALUES ('{test_task_id}', 'TEST001', '大货车')
                """))
                db.session.commit()
                print("✅ 第一条记录插入成功")
            except Exception as e:
                print(f"❌ 第一条记录插入失败: {e}")
                return False
            
            # 尝试插入重复的task_id
            try:
                db.session.execute(text(f"""
                    INSERT INTO vehicles (task_id, license_plate, vehicle_type) 
                    VALUES ('{test_task_id}', 'TEST002', '小货车')
                """))
                db.session.commit()
                print("❌ 重复记录插入成功，约束未生效")
                return False
            except IntegrityError as e:
                print("✅ 重复记录插入被阻止，约束生效")
                db.session.rollback()
            except Exception as e:
                print(f"❌ 意外错误: {e}")
                db.session.rollback()
                return False
            
            # 清理测试数据
            db.session.execute(text(f"DELETE FROM vehicles WHERE task_id = '{test_task_id}'"))
            db.session.commit()
            
            return True
            
        except Exception as e:
            print(f"❌ 测试过程中发生错误: {e}")
            return False

def test_business_logic():
    """测试业务逻辑层面的验证"""
    print("\n=== 测试业务逻辑验证 ===")
    
    from app.business.dispatch.dispatch_business import DispatchBusiness
    
    # 测试派车验证
    print("--- 测试派车验证逻辑 ---")
    test_task_id = 'TEST_BUSINESS_001'
    test_data = {
        'vehicles': [
            {'license_plate': 'TEST001', 'vehicle_type': '大货车', 'driver_name': '张三', 'driver_phone': '13800138001'},
            {'license_plate': 'TEST002', 'vehicle_type': '小货车', 'driver_name': '李四', 'driver_phone': '13800138002'}
        ]
    }
    
    try:
        result = DispatchBusiness.validate_vehicle_assignment(test_task_id, test_data)
        if result.get('valid', True):  # 如果valid为True或不存在，说明验证通过
            print("❌ 多车辆验证通过，业务逻辑未生效")
            return False
        else:
            print(f"✅ 多车辆验证被阻止: {result.get('message', '未知错误')}")
    except Exception as e:
        print(f"❌ 派车验证测试失败: {e}")
        return False
    
    # 测试供应商响应验证
    print("--- 测试供应商响应验证逻辑 ---")
    test_response_data = {
        'task_id': 'TEST_BUSINESS_002',
        'manifest_number': 'MN001',
        'vehicles': [
            {'license_plate': 'TEST001', 'vehicle_type': '大货车'}
        ],
        'carriages': [
            {'carriage_number': 'C001', 'vehicle_type': '车厢'}
        ]
    }
    
    try:
        result = DispatchBusiness.validate_supplier_response_data(test_response_data)
        if result.get('success', False):  # 如果success为True，说明验证通过
            print("❌ 车辆+车厢验证通过，业务逻辑未生效")
            return False
        else:
            print(f"✅ 车辆+车厢验证被阻止: {result.get('error', '未知错误')}")
    except Exception as e:
        print(f"❌ 供应商响应验证测试失败: {e}")
        return False
    
    return True

def main():
    """主测试函数"""
    print("开始测试任务与车辆/车厢唯一性约束功能\n")
    
    # 测试数据库约束
    db_test_passed = test_database_constraint()
    
    # 测试业务逻辑
    business_test_passed = test_business_logic()
    
    print("\n=== 测试结果汇总 ===")
    print(f"数据库约束测试: {'✅ 通过' if db_test_passed else '❌ 失败'}")
    print(f"业务逻辑测试: {'✅ 通过' if business_test_passed else '❌ 失败'}")
    
    if db_test_passed and business_test_passed:
        print("\n🎉 所有测试通过！唯一性约束功能正常工作")
        return 0
    else:
        print("\n⚠️ 部分测试失败，请检查相关功能")
        return 1

if __name__ == '__main__':
    sys.exit(main())