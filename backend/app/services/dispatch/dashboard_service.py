#!/usr/bin/env python3
"""
仪表盘数据统计服务

提供调度管理仪表盘所需的统计数据查询功能
"""

from datetime import datetime, timedelta
from app.extensions import db
from app.models.task import ManualDispatchTask


class DashboardService:
    """仪表盘数据统计服务类"""

    @staticmethod
    def get_task_statistics():
        """
        获取任务统计概览数据
        
        Returns:
            dict: 包含总任务数、今日新增任务数、即将超时任务数的字典
        """
        # 获取总任务数
        total_tasks = ManualDispatchTask.query.count()
        
        # 获取今日新增任务数
        today_start = datetime.now().strftime('%Y-%m-%d 00:00:00')
        today_new_tasks = ManualDispatchTask.query.filter(
            ManualDispatchTask.created_at >= today_start
        ).count()
        
        # 获取即将超时任务数（创建时间超过24小时未处理的任务）
        expire_time = (datetime.now() - timedelta(hours=24)).strftime('%Y-%m-%d %H:%M:%S')
        expiring_tasks = ManualDispatchTask.query.filter(
            ManualDispatchTask.created_at <= expire_time,
            ManualDispatchTask.status.in_(['待审核', '待供应商响应'])
        ).count()
        
        return {
            'total_tasks': total_tasks,
            'today_new_tasks': today_new_tasks,
            'expiring_tasks': expiring_tasks
        }

    @staticmethod
    def get_status_distribution():
        """
        获取任务状态分布数据
        
        Returns:
            list: 包含状态名称和对应数量的字典列表
        """
        from sqlalchemy import func
        
        status_distribution = db.session.query(
            ManualDispatchTask.status,
            func.count(ManualDispatchTask.task_id).label('count')
        ).group_by(ManualDispatchTask.status).all()
        
        return [
            {'status': status, 'count': count}
            for status, count in status_distribution
        ]

    @staticmethod
    def get_track_distribution():
        """
        获取派车轨道分布数据
        
        Returns:
            list: 包含轨道名称和对应数量的字典列表
        """
        from sqlalchemy import func
        
        track_distribution = db.session.query(
            ManualDispatchTask.dispatch_track,
            func.count(ManualDispatchTask.task_id).label('count')
        ).group_by(ManualDispatchTask.dispatch_track).all()
        
        return [
            {'track': track, 'count': count}
            for track, count in track_distribution
            if track is not None  # 过滤掉空值
        ]

    @staticmethod
    def get_urgent_tasks():
        """
        获取紧急任务列表
        
        Returns:
            list: 紧急任务信息字典列表
        """
        # 定义紧急任务条件：状态为待审核或待供应商响应，且创建时间超过12小时
        urgent_time = (datetime.now() - timedelta(hours=12)).strftime('%Y-%m-%d %H:%M:%S')
        
        urgent_tasks = ManualDispatchTask.query.filter(
            ManualDispatchTask.created_at <= urgent_time,
            ManualDispatchTask.status.in_(['待审核', '待供应商响应'])
        ).order_by(ManualDispatchTask.created_at.asc()).limit(10).all()
        
        return [
            {
                'task_id': task.task_id,
                'mail_route_name': task.mail_route_name,
                'status': task.status,
                'created_at': task.created_at,
                'urgency_level': 'high' if task.status == '待审核' else 'medium'
            }
            for task in urgent_tasks
        ]

    @staticmethod
    def get_dashboard_data():
        """
        获取完整的仪表盘数据
        
        Returns:
            dict: 包含所有仪表盘数据的字典
        """
        return {
            'statistics': DashboardService.get_task_statistics(),
            'status_distribution': DashboardService.get_status_distribution(),
            'track_distribution': DashboardService.get_track_distribution(),
            'urgent_tasks': DashboardService.get_urgent_tasks()
        }