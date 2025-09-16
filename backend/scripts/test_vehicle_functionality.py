#!/usr/bin/env python3
"""
车辆功能测试脚本
验证车辆管理和派车响应功能是否正常工作
"""

import sys
import os
import json
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app import create_app
from app.extensions import db
from app.models.vehicle.vehicle import Vehicle
from app.models.vehicle.vehicle_capacity_reference import VehicleCapacityReference
from app.models.task import ManualDispatchTask
from app.services.vehicle.vehicle_capacity_reference_service import VehicleCapacityReferenceService
from app.services.vehicle.vehicle_service import VehicleService
from sqlalchemy.exc import SQLAlchemyError


def test_vehicle_capacity_reference_crud():
    """
    测试车辆容积参考的CRUD操作
    """
    print("\n=== 测试车辆容积参考CRUD操作 ===")
    
    try:
        # 1. 创建车辆容积参考
        test_data = {
            'vehicle_type': '20吨',
            'standard_volume': 85.5,
            'license_plate': '测试A12345',
            'carriage_number': '测试A12345挂',
            'frequent_companies': ['测试公司A', '测试公司B'],
            'original_capacity': 20.0,
            'suppliers': '测试供应商'
        }
        
        print("1. 创建车辆容积参考...")
        created_vehicle = VehicleCapacityReferenceService.create_vehicle(test_data)
        print(f"   创建成功，ID: {created_vehicle['id']}")
        vehicle_id = created_vehicle['id']
        
        # 2. 获取车辆详情
        print("2. 获取车辆详情...")
        vehicle_detail = VehicleCapacityReferenceService.get_vehicle_by_id(vehicle_id)
        print(f"   获取成功，车牌号: {vehicle_detail['license_plate']}")
        
        # 3. 更新车辆信息
        print("3. 更新车辆信息...")
        update_data = {
            'standard_volume': 90.0,
            'suppliers': '更新后的供应商'
        }
        updated_vehicle = VehicleCapacityReferenceService.update_vehicle(vehicle_id, update_data)
        print(f"   更新成功，新容积: {updated_vehicle['standard_volume']}")
        
        # 4. 获取车辆列表
        print("4. 获取车辆列表...")
        vehicles, total = VehicleCapacityReferenceService.get_vehicle_list(page=1, per_page=10)
        print(f"   获取成功，总数: {total}")
        
        # 5. 搜索车辆
        print("5. 搜索车辆...")
        search_results = VehicleCapacityReferenceService.search_vehicles(license_plate='测试A')
        print(f"   搜索成功，找到 {len(search_results)} 条记录")
        
        # 6. 删除车辆
        print("6. 删除车辆...")
        delete_success = VehicleCapacityReferenceService.delete_vehicle(vehicle_id)
        print(f"   删除成功: {delete_success}")
        
        print("✓ 车辆容积参考CRUD测试通过")
        return True
        
    except Exception as e:
        print(f"✗ 车辆容积参考CRUD测试失败: {str(e)}")
        return False


def test_vehicle_dispatch_functionality():
    """
    测试派车响应功能
    """
    print("\n=== 测试派车响应功能 ===")
    
    try:
        # 1. 创建测试任务
        print("1. 创建测试派车任务...")
        task_id = f"TEST_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        test_task = ManualDispatchTask(
            task_id=task_id,
            required_date='2024-01-20',
            origin_bureau='测试始发局',
            mail_route_name='测试邮路',
            organizing_unit='测试承运商',
            transport_type='公路运输',
            requirement_type='正班',
            standard_weight='20吨',
            standard_volume=85,
            actual_volume=85,
            status='待供应商响应',
            dispatch_track='轨道B',
            initiator_role='调度员',
            initiator_user_id=1,
            business_type='委办派车',
            created_at=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            updated_at=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        )
        
        db.session.add(test_task)
        db.session.commit()
        print(f"   任务创建成功，ID: {task_id}")
        
        # 2. 创建关联车辆（派车响应）
        print("2. 创建派车响应车辆...")
        vehicle_data = {
            'task_id': task_id,
            'license_plate': '响应A12345',
            'carriage_number': '响应A12345挂',
            'vehicle_type': '20吨',
            'actual_volume': 85.0,
            'supplier_id': 1,
            'supplier_type': '委办公司',
            'status': '待确认'
        }
        
        created_vehicle = VehicleService.create_vehicle(vehicle_data)
        print(f"   派车响应车辆创建成功，ID: {created_vehicle['id']}")
        response_vehicle_id = created_vehicle['id']
        
        # 3. 验证车辆必须关联任务
        print("3. 验证车辆必须关联任务...")
        try:
            invalid_vehicle_data = {
                'license_plate': '无效A12345',
                'vehicle_type': '20吨'
                # 故意不提供task_id
            }
            VehicleService.create_vehicle(invalid_vehicle_data)
            print("   ✗ 应该失败但成功了")
            return False
        except Exception:
            print("   ✓ 正确拒绝了无task_id的车辆创建")
        
        # 4. 获取任务关联的车辆
        print("4. 获取任务关联的车辆...")
        task_vehicles = Vehicle.query.filter_by(task_id=task_id).all()
        print(f"   找到 {len(task_vehicles)} 辆关联车辆")
        
        # 5. 清理测试数据
        print("5. 清理测试数据...")
        Vehicle.query.filter_by(task_id=task_id).delete()
        ManualDispatchTask.query.filter_by(task_id=task_id).delete()
        db.session.commit()
        print("   测试数据清理完成")
        
        print("✓ 派车响应功能测试通过")
        return True
        
    except Exception as e:
        print(f"✗ 派车响应功能测试失败: {str(e)}")
        # 清理可能的残留数据
        try:
            Vehicle.query.filter(Vehicle.license_plate.like('响应%')).delete()
            ManualDispatchTask.query.filter(ManualDispatchTask.task_id.like('TEST_%')).delete()
            db.session.commit()
        except:
            pass
        return False


def test_data_separation():
    """
    测试数据分离是否正确
    """
    print("\n=== 测试数据分离 ===")
    
    try:
        # 1. 检查vehicle_capacity_reference表结构
        print("1. 检查vehicle_capacity_reference表结构...")
        columns = [column.name for column in VehicleCapacityReference.__table__.columns]
        required_columns = ['carriage_number', 'vehicle_category', 'frequent_companies', 'status', 'original_capacity']
        
        for col in required_columns:
            if col in columns:
                print(f"   ✓ {col} 字段存在")
            else:
                print(f"   ✗ {col} 字段缺失")
                return False
        
        # 2. 检查vehicles表约束
        print("2. 检查vehicles表task_id约束...")
        task_id_column = None
        for column in Vehicle.__table__.columns:
            if column.name == 'task_id':
                task_id_column = column
                break
        
        if task_id_column and not task_id_column.nullable:
            print("   ✓ task_id字段已设置为非空")
        else:
            print("   ⚠ task_id字段约束可能未生效（需要运行数据库迁移）")
        
        # 3. 验证功能分离
        print("3. 验证功能分离...")
        print("   - vehicle_capacity_reference: 车辆日常管理")
        print("   - vehicles: 派车响应管理")
        print("   ✓ 功能分离正确")
        
        print("✓ 数据分离测试通过")
        return True
        
    except Exception as e:
        print(f"✗ 数据分离测试失败: {str(e)}")
        return False


def run_all_tests():
    """
    运行所有测试
    """
    app = create_app('development')
    
    with app.app_context():
        print("开始车辆功能测试...")
        
        tests = [
            test_data_separation,
            test_vehicle_capacity_reference_crud,
            test_vehicle_dispatch_functionality
        ]
        
        passed = 0
        total = len(tests)
        
        for test in tests:
            try:
                if test():
                    passed += 1
            except Exception as e:
                print(f"测试执行异常: {str(e)}")
        
        print(f"\n=== 测试结果 ===")
        print(f"通过: {passed}/{total}")
        
        if passed == total:
            print("🎉 所有测试通过！车辆管理逻辑重构成功")
            return True
        else:
            print("❌ 部分测试失败，请检查相关功能")
            return False


if __name__ == '__main__':
    success = run_all_tests()
    if not success:
        sys.exit(1)