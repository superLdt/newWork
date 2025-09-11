#!/usr/bin/env python3
"""
派车流程状态管理单元测试
"""

import unittest
from unittest.mock import patch, MagicMock
from app.business.dispatch.status_manager import DispatchStatusManager

class TestDispatchStatusManager(unittest.TestCase):
    """
    派车流程状态管理单元测试类
    """
    
    @patch('app.business.dispatch.status_manager.DispatchService')
    def test_update_task_status(self, mock_service):
        """
        测试更新任务状态
        """
        # 准备测试数据
        task_id = 1
        new_status = 'approved'
        comment = '审批通过'
        
        # 模拟服务层方法
        mock_task = {'id': task_id, 'status': 'pending'}
        mock_service.get_dispatch_task_by_id.return_value = mock_task
        mock_service.update_dispatch_task.return_value = {'id': task_id, 'status': new_status}
        mock_service.create_status_history.return_value = {'id': 1, 'task_id': task_id, 'from_status': 'pending', 'to_status': new_status}
        
        # 调用测试方法
        result = DispatchStatusManager.update_task_status(task_id, new_status, comment)
        
        # 验证结果
        self.assertEqual(result['status'], new_status)
        mock_service.get_dispatch_task_by_id.assert_called_once_with(task_id)
        mock_service.update_dispatch_task.assert_called_once()
        mock_service.create_status_history.assert_called_once()
    
    @patch('app.business.dispatch.status_manager.DispatchService')
    def test_update_task_status_invalid_transition(self, mock_service):
        """
        测试无效的状态转换
        """
        # 准备测试数据
        task_id = 1
        new_status = 'completed'
        comment = '任务完成'
        
        # 模拟服务层方法
        mock_task = {'id': task_id, 'status': 'pending'}
        mock_service.get_dispatch_task_by_id.return_value = mock_task
        
        # 调用测试方法并验证异常
        with self.assertRaises(ValueError):
            DispatchStatusManager.update_task_status(task_id, new_status, comment)
    
    @patch('app.business.dispatch.status_manager.DispatchService')
    def test_get_next_possible_statuses(self, mock_service):
        """
        测试获取可能的下一个状态
        """
        # 准备测试数据
        task_id = 1
        current_status = 'pending'
        
        # 模拟服务层方法
        mock_task = {'id': task_id, 'status': current_status}
        mock_service.get_dispatch_task_by_id.return_value = mock_task
        
        # 调用测试方法
        result = DispatchStatusManager.get_next_possible_statuses(task_id)
        
        # 验证结果
        self.assertIsInstance(result, list)
        self.assertIn('approved', [status['status'] for status in result])
        self.assertIn('rejected', [status['status'] for status in result])
    
    @patch('app.business.dispatch.status_manager.DispatchService')
    def test_get_status_flow(self, mock_service):
        """
        测试获取状态流
        """
        # 准备测试数据
        task_id = 1
        
        # 模拟服务层方法
        mock_history = [
            {'id': 1, 'task_id': task_id, 'from_status': 'pending', 'to_status': 'approved', 'created_at': '2023-01-01 10:00:00'},
            {'id': 2, 'task_id': task_id, 'from_status': 'approved', 'to_status': 'assigned', 'created_at': '2023-01-01 11:00:00'}
        ]
        mock_service.get_task_status_history.return_value = mock_history
        
        # 调用测试方法
        result = DispatchStatusManager.get_status_flow(task_id)
        
        # 验证结果
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]['from_status'], 'pending')
        self.assertEqual(result[0]['to_status'], 'approved')
        self.assertEqual(result[1]['from_status'], 'approved')
        self.assertEqual(result[1]['to_status'], 'assigned')

if __name__ == '__main__':
    unittest.main()