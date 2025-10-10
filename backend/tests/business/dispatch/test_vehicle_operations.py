#!/usr/bin/env python3
"""
车辆操作单元测试
"""

import unittest
from unittest.mock import patch, MagicMock
from app.business.dispatch.dispatch_business import DispatchBusiness
from app.business.vehicle.vehicle_downgrade_business import VehicleDowngradeBusiness

class TestVehicleOperations(unittest.TestCase):
    """
    车辆操作单元测试类
    """
    
    @patch('app.business.dispatch.dispatch_business.DispatchService')
    @patch('app.business.dispatch.dispatch_business.DispatchLogManager')
    @patch('app.business.dispatch.dispatch_business.g')
    def test_merge_vehicles_success(self, mock_g, mock_log_manager, mock_service):
        """
        测试成功合并车辆
        """
        # 准备测试数据
        source_vehicle_id = 1
        target_vehicle_id = 2
        
        # 模拟当前用户
        mock_g.current_user = MagicMock(id=100)
        
        # 模拟服务层方法
        mock_service.get_vehicle_by_id.side_effect = [
            {'id': source_vehicle_id, 'plate_number': 'A12345', 'vehicle_type': 'SUV'},
            {'id': target_vehicle_id, 'plate_number': 'B67890', 'vehicle_type': 'SUV'}
        ]
        mock_service.get_vehicle_active_tasks.return_value = []
        mock_service.get_vehicle_completed_tasks.return_value = [
            {'id': 10, 'vehicle_id': source_vehicle_id},
            {'id': 11, 'vehicle_id': source_vehicle_id}
        ]
        mock_service.create_vehicle_merge_record.return_value = {'id': 1, 'source_vehicle_id': source_vehicle_id, 'target_vehicle_id': target_vehicle_id}
        
        # 调用测试方法
        result = DispatchBusiness.merge_vehicles(source_vehicle_id, target_vehicle_id)
        
        # 验证结果
        self.assertTrue(result['success'])
        mock_service.get_vehicle_by_id.assert_any_call(source_vehicle_id)
        mock_service.get_vehicle_by_id.assert_any_call(target_vehicle_id)
        mock_service.get_vehicle_active_tasks.assert_called_once_with(source_vehicle_id)
        mock_service.get_vehicle_completed_tasks.assert_called_once_with(source_vehicle_id)
        self.assertEqual(mock_service.update_task_vehicle.call_count, 2)
        mock_service.create_vehicle_merge_record.assert_called_once()
        mock_service.update_vehicle.assert_called_once()
        mock_log_manager.log_action.assert_called_once()
    
    @patch('app.business.dispatch.dispatch_business.DispatchService')
    def test_merge_vehicles_same_vehicle(self, mock_service):
        """
        测试合并相同车辆的情况
        """
        # 准备测试数据
        vehicle_id = 1
        
        # 调用测试方法并验证异常
        with self.assertRaises(ValueError) as context:
            DispatchBusiness.merge_vehicles(vehicle_id, vehicle_id)
        
        self.assertIn("源车辆和目标车辆不能是同一辆车", str(context.exception))
    
    @patch('app.business.dispatch.dispatch_business.DispatchService')
    def test_merge_vehicles_with_active_tasks(self, mock_service):
        """
        测试源车辆有进行中任务的情况
        """
        # 准备测试数据
        source_vehicle_id = 1
        target_vehicle_id = 2
        
        # 模拟服务层方法
        mock_service.get_vehicle_by_id.side_effect = [
            {'id': source_vehicle_id, 'plate_number': 'A12345', 'vehicle_type': 'SUV'},
            {'id': target_vehicle_id, 'plate_number': 'B67890', 'vehicle_type': 'SUV'}
        ]
        mock_service.get_vehicle_active_tasks.return_value = [{'id': 10, 'vehicle_id': source_vehicle_id}]
        
        # 调用测试方法并验证异常
        with self.assertRaises(ValueError) as context:
            DispatchBusiness.merge_vehicles(source_vehicle_id, target_vehicle_id)
        
        self.assertIn("源车辆有1个进行中的任务，无法合并", str(context.exception))
    
    @patch('app.business.vehicle.vehicle_downgrade_business.VehicleService')
    @patch('app.business.vehicle.vehicle_downgrade_business.DispatchService')
    def test_downgrade_vehicle_success(self, mock_dispatch_service, mock_vehicle_service):
        """
        测试成功降档车辆
        """
        # 准备测试数据
        vehicle_id = 1
        downgrade_record = {
            'vehicle_id': vehicle_id,
            'previous_type': 'SUV',
            'new_type': 'SEDAN',
            'reason': '车辆老化',
            'downgraded_by': 100
        }
        
        # 模拟服务层方法
        mock_vehicle_service.get_vehicle_by_id.return_value = {'id': vehicle_id, 'plate_number': 'A12345', 'vehicle_type': 'SUV', 'status': 'available'}
        mock_dispatch_service.get_vehicle_active_tasks.return_value = []
        mock_vehicle_service.get_valid_vehicle_types.return_value = ['SUV', 'SEDAN', 'COMPACT']
        mock_vehicle_service.get_vehicle_type_level.side_effect = [3, 2]  # SUV级别高于SEDAN
        mock_vehicle_service.create_vehicle_downgrade_record.return_value = {'id': 1, 'vehicle_id': vehicle_id}
        
        # 调用测试方法
        result = VehicleDowngradeBusiness.process_vehicle_downgrade(vehicle_id, downgrade_record)
        
        # 验证结果
        self.assertTrue(result['success'])
        mock_vehicle_service.get_vehicle_by_id.assert_called_once_with(vehicle_id)
        mock_dispatch_service.get_vehicle_active_tasks.assert_called_once_with(vehicle_id)
        mock_vehicle_service.get_valid_vehicle_types.assert_called_once()
        self.assertEqual(mock_vehicle_service.get_vehicle_type_level.call_count, 2)
        mock_vehicle_service.create_vehicle_downgrade_record.assert_called_once_with(downgrade_record)
        mock_vehicle_service.update_vehicle.assert_called_once()
    
    @patch('app.business.vehicle.vehicle_downgrade_business.VehicleService')
    @patch('app.business.vehicle.vehicle_downgrade_business.DispatchService')
    def test_downgrade_vehicle_with_active_tasks(self, mock_dispatch_service, mock_vehicle_service):
        """
        测试车辆有进行中任务的情况
        """
        # 准备测试数据
        vehicle_id = 1
        downgrade_record = {
            'vehicle_id': vehicle_id,
            'previous_type': 'SUV',
            'new_type': 'SEDAN',
            'reason': '车辆老化',
            'downgraded_by': 100
        }
        
        # 模拟服务层方法
        mock_vehicle_service.get_vehicle_by_id.return_value = {'id': vehicle_id, 'plate_number': 'A12345', 'vehicle_type': 'SUV', 'status': 'available'}
        mock_dispatch_service.get_vehicle_active_tasks.return_value = [{'id': 10, 'vehicle_id': vehicle_id}]
        
        # 调用测试方法并验证异常
        with self.assertRaises(ValueError) as context:
            VehicleDowngradeBusiness.process_vehicle_downgrade(vehicle_id, downgrade_record)
        
        self.assertIn("车辆有1个进行中的任务，无法降档", str(context.exception))

if __name__ == '__main__':
    unittest.main()