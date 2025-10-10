#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试任务与车辆/车厢唯一性约束的单元测试
"""

import unittest
from unittest.mock import patch, MagicMock
from app import create_app
from app.extensions import db
from app.models import Vehicle, ManualDispatchTask
from app.business.dispatch.dispatch_business import DispatchBusiness
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError


class TestVehicleUniquenessConstraint(unittest.TestCase):
    """测试车辆唯一性约束"""

    def setUp(self):
        """测试前准备"""
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        """测试后清理"""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_database_unique_constraint_exists(self):
        """测试数据库唯一性约束是否存在"""
        # 检查task_id字段是否存在且为NOT NULL
        result = db.session.execute(text('PRAGMA table_info(vehicles)'))
        columns = result.fetchall()
        
        task_id_column = None
        for row in columns:
            if row[1] == 'task_id':
                task_id_column = row
                break
        
        self.assertIsNotNone(task_id_column, "task_id字段应该存在")
        self.assertEqual(task_id_column[3], 1, "task_id字段应该是NOT NULL")

        # 检查唯一性约束是否存在
        result = db.session.execute(text('PRAGMA index_list(vehicles)'))
        indexes = result.fetchall()
        
        unique_constraint_exists = False
        for row in indexes:
            if row[2] == 1:  # unique index
                result2 = db.session.execute(text(f'PRAGMA index_info({row[1]})'))
                index_info = result2.fetchall()
                for info in index_info:
                    if info[2] == 'task_id':
                        unique_constraint_exists = True
                        break
        
        self.assertTrue(unique_constraint_exists, "应该存在task_id的唯一性约束")

    def test_database_prevents_duplicate_task_id(self):
        """测试数据库层面阻止重复的task_id"""
        test_task_id = "TEST_UNIQUE_DB_001"
        
        # 插入第一条记录
        db.session.execute(text(f"""
            INSERT INTO vehicles (task_id, license_plate, vehicle_type) 
            VALUES ('{test_task_id}', 'TEST001', '大货车')
        """))
        db.session.commit()
        
        # 尝试插入重复的task_id，应该失败
        with self.assertRaises(IntegrityError):
            db.session.execute(text(f"""
                INSERT INTO vehicles (task_id, license_plate, vehicle_type) 
                VALUES ('{test_task_id}', 'TEST002', '小货车')
            """))
            db.session.commit()

    def test_vehicle_assignment_validation_single_vehicle(self):
        """测试派车验证：单辆车应该通过"""
        test_task_id = 'TEST_ASSIGNMENT_001'
        test_data = {
            'license_plate': 'TEST001',
            'driver_name': '张三',
            'driver_phone': '13800138001'
        }
        
        result = DispatchBusiness.validate_vehicle_assignment(test_task_id, test_data)
        self.assertTrue(result.get('valid', False), "单辆车派车应该通过验证")

    def test_vehicle_assignment_validation_missing_required_fields(self):
        """测试派车验证：缺少必填字段应该被阻止"""
        test_task_id = 'TEST_ASSIGNMENT_002'
        test_data = {
            'driver_name': '张三'
            # 缺少license_plate和driver_phone
        }
        
        result = DispatchBusiness.validate_vehicle_assignment(test_task_id, test_data)
        self.assertFalse(result.get('valid', True), "缺少必填字段的派车应该被阻止")
        self.assertIn('缺少必填字段', result.get('message', ''))

    def test_supplier_response_validation_single_vehicle(self):
        """测试供应商响应验证：单辆车应该通过"""
        test_data = {
            'task_id': 'TEST_SUPPLIER_001',
            'manifest_number': 'MN001',
            'dispatch_number': 'DN001',
            'vehicles': [
                {'license_plate': 'TEST001', 'vehicle_type': '大货车'}
            ]
        }
        
        result = DispatchBusiness.validate_supplier_response_data(test_data)
        self.assertTrue(result.get('valid', False), "单辆车供应商响应应该通过验证")

    def test_supplier_response_validation_single_carriage(self):
        """测试供应商响应验证：单个车厢应该通过"""
        test_data = {
            'task_id': 'TEST_SUPPLIER_002',
            'manifest_number': 'MN002',
            'dispatch_number': 'DN002',
            'vehicles': [],
            'carriages': [
                {'carriage_number': 'C001', 'vehicle_type': '车厢'}
            ]
        }
        
        result = DispatchBusiness.validate_supplier_response_data(test_data)
        self.assertTrue(result.get('valid', False), "单个车厢供应商响应应该通过验证")

    def test_supplier_response_validation_vehicle_and_carriage(self):
        """测试供应商响应验证：车辆+车厢应该被阻止"""
        test_data = {
            'task_id': 'TEST_SUPPLIER_003',
            'manifest_number': 'MN003',
            'dispatch_number': 'DN003',
            'vehicles': [
                {'license_plate': 'TEST001', 'vehicle_type': '大货车'}
            ],
            'carriages': [
                {'carriage_number': 'C001', 'vehicle_type': '车厢'}
            ]
        }
        
        result = DispatchBusiness.validate_supplier_response_data(test_data)
        self.assertFalse(result.get('valid', True), "车辆+车厢供应商响应应该被阻止")
        self.assertIn('只能派遣一辆车或一个车厢', result.get('message', ''))

    def test_supplier_response_validation_multiple_vehicles(self):
        """测试供应商响应验证：多辆车应该被阻止"""
        test_data = {
            'task_id': 'TEST_SUPPLIER_004',
            'manifest_number': 'MN004',
            'dispatch_number': 'DN004',
            'vehicles': [
                {'license_plate': 'TEST001', 'vehicle_type': '大货车'},
                {'license_plate': 'TEST002', 'vehicle_type': '小货车'}
            ]
        }
        
        result = DispatchBusiness.validate_supplier_response_data(test_data)
        self.assertFalse(result.get('valid', True), "多辆车供应商响应应该被阻止")
        self.assertIn('只能派遣一辆车或一个车厢', result.get('message', ''))

    def test_supplier_response_validation_multiple_carriages(self):
        """测试供应商响应验证：多个车厢应该被阻止"""
        test_data = {
            'task_id': 'TEST_SUPPLIER_005',
            'manifest_number': 'MN005',
            'dispatch_number': 'DN005',
            'vehicles': [],
            'carriages': [
                {'carriage_number': 'C001', 'vehicle_type': '车厢'},
                {'carriage_number': 'C002', 'vehicle_type': '车厢'}
            ]
        }
        
        result = DispatchBusiness.validate_supplier_response_data(test_data)
        self.assertFalse(result.get('valid', True), "多个车厢供应商响应应该被阻止")
        self.assertIn('只能派遣一辆车或一个车厢', result.get('message', ''))

    def test_supplier_response_validation_missing_required_fields(self):
        """测试供应商响应验证：缺少必填字段应该被阻止"""
        test_data = {
            'task_id': 'TEST_SUPPLIER_006'
            # 缺少manifest_number、dispatch_number和车辆信息
        }
        
        result = DispatchBusiness.validate_supplier_response_data(test_data)
        self.assertFalse(result.get('valid', True), "缺少必填字段的供应商响应应该被阻止")

    def test_empty_vehicles_and_carriages(self):
        """测试供应商响应验证：空的车辆和车厢列表应该被阻止"""
        test_data = {
            'task_id': 'TEST_SUPPLIER_007',
            'manifest_number': 'MN007',
            'dispatch_number': 'DN007',
            'vehicles': [],
            'carriages': []
        }
        
        result = DispatchBusiness.validate_supplier_response_data(test_data)
        self.assertFalse(result.get('valid', True), "空的车辆和车厢列表应该被阻止")


class TestVehicleUniquenessIntegration(unittest.TestCase):
    """集成测试：测试完整的唯一性约束流程"""

    def setUp(self):
        """测试前准备"""
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        """测试后清理"""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    @patch('app.business.dispatch.dispatch_business.DispatchService')
    def test_complete_vehicle_assignment_flow(self, mock_service):
        """测试完整的车辆分配流程"""
        # 模拟服务层返回
        mock_service.assign_vehicles_to_task.return_value = {
            'success': True,
            'message': '车辆分配成功'
        }
        mock_service.get_vehicles_by_task_id.return_value = []  # 模拟任务未分配车辆
        
        test_task_id = 'TEST_INTEGRATION_001'
        test_data = {
            'license_plate': 'TEST001',
            'driver_name': '张三',
            'driver_phone': '13800138001'
        }
        
        # 验证通过
        validation_result = DispatchBusiness.validate_vehicle_assignment(test_task_id, test_data)
        self.assertTrue(validation_result.get('valid', False))
        
        # 处理分配
        assignment_result = DispatchBusiness.process_vehicle_assignment(test_task_id, test_data)
        self.assertTrue(assignment_result.get('success', False))

    @patch('app.business.dispatch.dispatch_business.DispatchService')
    def test_complete_supplier_response_flow(self, mock_service):
        """测试完整的供应商响应流程"""
        # 模拟服务层返回
        mock_service.process_supplier_response.return_value = {
            'success': True,
            'message': '供应商响应处理成功'
        }
        
        test_data = {
            'task_id': 'TEST_INTEGRATION_002',
            'manifest_number': 'MN002',
            'dispatch_number': 'DN002',
            'vehicles': [
                {'license_plate': 'TEST001', 'vehicle_type': '大货车'}
            ]
        }
        
        # 验证通过
        validation_result = DispatchBusiness.validate_supplier_response_data(test_data)
        self.assertTrue(validation_result.get('valid', False))
        
        # 处理响应
        response_result = DispatchBusiness.process_supplier_response(test_data)
        self.assertTrue(response_result.get('success', False))


if __name__ == '__main__':
    unittest.main()