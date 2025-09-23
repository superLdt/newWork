#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化版车辆唯一性约束测试
专注于核心业务逻辑验证
"""

import unittest
from unittest.mock import patch, MagicMock
from app.business.dispatch.dispatch_business import DispatchBusiness


class TestVehicleUniquenessConstraintSimple(unittest.TestCase):
    """简化版车辆唯一性约束测试"""

    def test_vehicle_assignment_validation_success(self):
        """测试派车验证：正确数据应该通过"""
        with patch('app.business.dispatch.dispatch_business.DispatchService') as mock_service:
            # 模拟任务未分配车辆
            mock_service.get_vehicles_by_task_id.return_value = []
            
            test_task_id = 'TEST_001'
            test_data = {
                'license_plate': 'TEST001',
                'driver_name': '张三',
                'driver_phone': '13800138001'
            }
            
            result = DispatchBusiness.validate_vehicle_assignment(test_task_id, test_data)
            self.assertTrue(result.get('valid', False), "正确的派车数据应该通过验证")

    def test_vehicle_assignment_validation_missing_license_plate(self):
        """测试派车验证：缺少车牌号应该失败"""
        test_task_id = 'TEST_002'
        test_data = {
            'driver_name': '张三',
            'driver_phone': '13800138001'
        }
        
        result = DispatchBusiness.validate_vehicle_assignment(test_task_id, test_data)
        self.assertFalse(result.get('valid', True), "缺少车牌号的派车应该被阻止")
        self.assertIn('缺少必填字段', result.get('message', ''))

    def test_vehicle_assignment_validation_missing_driver_info(self):
        """测试派车验证：缺少司机信息应该失败"""
        test_task_id = 'TEST_003'
        test_data = {
            'license_plate': 'TEST001'
        }
        
        result = DispatchBusiness.validate_vehicle_assignment(test_task_id, test_data)
        self.assertFalse(result.get('valid', True), "缺少司机信息的派车应该被阻止")
        self.assertIn('缺少必填字段', result.get('message', ''))

    def test_vehicle_assignment_validation_already_assigned(self):
        """测试派车验证：已分配车辆的任务应该失败"""
        with patch('app.business.dispatch.dispatch_business.DispatchService') as mock_service:
            # 模拟任务已分配车辆
            mock_service.get_vehicles_by_task_id.return_value = [{'id': 1, 'license_plate': 'EXISTING001'}]
            
            test_task_id = 'TEST_004'
            test_data = {
                'license_plate': 'TEST001',
                'driver_name': '张三',
                'driver_phone': '13800138001'
            }
            
            result = DispatchBusiness.validate_vehicle_assignment(test_task_id, test_data)
            self.assertFalse(result.get('valid', True), "已分配车辆的任务应该被阻止")
            self.assertIn('已经分配了车辆', result.get('message', ''))

    def test_supplier_response_validation_single_vehicle_success(self):
        """测试供应商响应验证：单辆车应该通过"""
        test_data = {
            'task_id': 'TEST_005',
            'manifest_number': 'MN005',
            'dispatch_number': 'DN005',
            'vehicles': [
                {'license_plate': 'TEST001', 'vehicle_type': '大货车'}
            ]
        }
        
        result = DispatchBusiness.validate_supplier_response_data(test_data)
        self.assertTrue(result.get('valid', False), "单辆车供应商响应应该通过验证")

    def test_supplier_response_validation_carriage_without_vehicle_invalid(self):
        """测试只有车厢没有车辆的供应商响应验证 - 应该失败"""
        test_data = {
            'task_id': 1,
            'manifest_number': 'MN006',
            'dispatch_number': 'DN006',
            'vehicles': [],  # 空车辆列表
            'carriages': [
                {
                    'carriage_number': 'C001',
                    'carriage_type': 'container',
                    'capacity': 20
                }
            ]
        }
        
        # 车厢必须依附于车辆，只有车厢没有车辆应该被拒绝
        result = DispatchBusiness.validate_supplier_response_data(test_data)
        self.assertFalse(result['valid'])
        self.assertIn('vehicles 不能为空', result['message'])

    def test_supplier_response_validation_vehicle_and_carriage_invalid(self):
        """测试车辆+车厢组合的供应商响应验证 - 应该失败（违反唯一性约束）"""
        test_data = {
            'task_id': 1,
            'manifest_number': 'MN007',
            'dispatch_number': 'DN007',
            'vehicles': [
                {
                    'license_plate': 'V001',
                    'vehicle_type': 'truck',
                    'driver_name': 'Driver1',
                    'driver_phone': '12345678901'
                }
            ],
            'carriages': [
                {
                    'carriage_number': 'C001',
                    'carriage_type': 'container',
                    'capacity': 20
                }
            ]
        }
        
        # 一个任务只能派遣一辆车或一个车厢，不能同时派遣多个
        result = DispatchBusiness.validate_supplier_response_data(test_data)
        self.assertFalse(result['valid'])
        self.assertIn('一个任务只能派遣一辆车或一个车厢，不能同时派遣多个', result['message'])

    def test_supplier_response_validation_multiple_vehicles_fail(self):
        """测试供应商响应验证：多辆车应该失败"""
        test_data = {
            'task_id': 'TEST_007',
            'manifest_number': 'MN007',
            'dispatch_number': 'DN007',
            'vehicles': [
                {'license_plate': 'TEST001', 'vehicle_type': '大货车'},
                {'license_plate': 'TEST002', 'vehicle_type': '小货车'}
            ]
        }
        
        result = DispatchBusiness.validate_supplier_response_data(test_data)
        self.assertFalse(result.get('valid', True), "多辆车供应商响应应该被阻止")
        self.assertIn('只能派遣一辆车或一个车厢', result.get('message', ''))

    def test_supplier_response_validation_vehicle_and_carriage_fail(self):
        """测试供应商响应验证：车辆+车厢应该失败"""
        test_data = {
            'task_id': 'TEST_008',
            'manifest_number': 'MN008',
            'dispatch_number': 'DN008',
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

    def test_supplier_response_validation_missing_required_fields(self):
        """测试供应商响应验证：缺少必填字段应该失败"""
        test_data = {
            'task_id': 'TEST_009'
            # 缺少manifest_number、dispatch_number和vehicles
        }
        
        result = DispatchBusiness.validate_supplier_response_data(test_data)
        self.assertFalse(result.get('valid', True), "缺少必填字段的供应商响应应该被阻止")

    def test_supplier_response_validation_empty_vehicles_and_carriages(self):
        """测试供应商响应验证：空的车辆和车厢列表应该失败"""
        test_data = {
            'task_id': 'TEST_010',
            'manifest_number': 'MN010',
            'dispatch_number': 'DN010',
            'vehicles': [],
            'carriages': []
        }
        
        result = DispatchBusiness.validate_supplier_response_data(test_data)
        self.assertFalse(result.get('valid', True), "空的车辆和车厢列表应该被阻止")


if __name__ == '__main__':
    unittest.main()