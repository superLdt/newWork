#!/usr/bin/env python3
"""
派车流程操作日志管理单元测试
"""

import unittest
from unittest.mock import patch, MagicMock
from app.business.dispatch.log_manager import DispatchLogManager

class TestDispatchLogManager(unittest.TestCase):
    """
    派车流程操作日志管理单元测试类
    """
    
    @patch('app.business.dispatch.log_manager.DispatchService')
    @patch('app.business.dispatch.log_manager.g')
    def test_log_action(self, mock_g, mock_service):
        """
        测试记录操作日志
        """
        # 准备测试数据
        task_id = 1
        action_type = 'create'
        details = {'task_data': {'title': '测试任务'}}
        
        # 模拟当前用户
        mock_g.current_user = MagicMock(id=100)
        
        # 模拟服务层方法
        mock_service.create_operation_log.return_value = {'id': 1, 'task_id': task_id, 'action_type': action_type}
        
        # 调用测试方法
        result = DispatchLogManager.log_action(task_id, action_type, details)
        
        # 验证结果
        self.assertIsNotNone(result)
        mock_service.create_operation_log.assert_called_once()
        call_args = mock_service.create_operation_log.call_args[0][0]
        self.assertEqual(call_args['task_id'], task_id)
        self.assertEqual(call_args['action_type'], action_type)
        self.assertEqual(call_args['operator_id'], 100)
        self.assertEqual(call_args['details'], details)
    
    @patch('app.business.dispatch.log_manager.DispatchService')
    def test_get_task_logs(self, mock_service):
        """
        测试获取任务操作日志
        """
        # 准备测试数据
        task_id = 1
        
        # 模拟服务层方法
        mock_logs = [
            {'id': 1, 'task_id': task_id, 'action_type': 'create', 'created_at': '2023-01-01 10:00:00'},
            {'id': 2, 'task_id': task_id, 'action_type': 'update', 'created_at': '2023-01-01 11:00:00'}
        ]
        mock_service.get_task_operation_logs.return_value = mock_logs
        
        # 调用测试方法
        result = DispatchLogManager.get_task_logs(task_id)
        
        # 验证结果
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]['action_type'], 'create')
        self.assertEqual(result[1]['action_type'], 'update')
        mock_service.get_task_operation_logs.assert_called_once_with(task_id)
    
    @patch('app.business.dispatch.log_manager.DispatchService')
    def test_get_action_type_display(self, mock_service):
        """
        测试获取操作类型显示名称
        """
        # 测试已定义的操作类型
        self.assertEqual(DispatchLogManager.get_action_type_display('create'), '创建任务')
        self.assertEqual(DispatchLogManager.get_action_type_display('update'), '更新任务')
        self.assertEqual(DispatchLogManager.get_action_type_display('approve'), '审批通过')
        self.assertEqual(DispatchLogManager.get_action_type_display('reject'), '审批拒绝')
        self.assertEqual(DispatchLogManager.get_action_type_display('assign'), '分配车辆')
        self.assertEqual(DispatchLogManager.get_action_type_display('complete'), '完成任务')
        self.assertEqual(DispatchLogManager.get_action_type_display('cancel'), '取消任务')
        self.assertEqual(DispatchLogManager.get_action_type_display('merge'), '合并车辆')
        self.assertEqual(DispatchLogManager.get_action_type_display('downgrade'), '车辆降档')
        
        # 测试未定义的操作类型
        self.assertEqual(DispatchLogManager.get_action_type_display('unknown'), '未知操作')

if __name__ == '__main__':
    unittest.main()