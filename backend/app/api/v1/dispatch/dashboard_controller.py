from flask import jsonify
from app.services.dispatch.dashboard_service import DashboardService
from app.auth.decorators import permission_required
from app.common.response import success_response, error_response
import logging

logger = logging.getLogger(__name__)


class DashboardController:
    """
    调度仪表盘控制器类，处理仪表盘相关的API请求
    """

    @staticmethod
    @permission_required('dispatch:read')
    def get_dashboard_statistics():
        """
        获取仪表盘统计概览数据
        ---
        tags:
          - 调度仪表盘
        responses:
          200:
            description: 成功获取统计概览数据
            schema:
              type: object
              properties:
                total_tasks:
                  type: integer
                  description: 总任务数
                today_new_tasks:
                  type: integer
                  description: 今日新增任务数
                expiring_tasks:
                  type: integer
                  description: 即将超时任务数
          500:
            description: 服务器错误
        """
        try:
            statistics = DashboardService.get_task_statistics()
            return success_response(statistics)
        except Exception as e:
            logger.error(f"获取仪表盘统计数据失败: {str(e)}")
            return error_response(str(e), 500)

    @staticmethod
    @permission_required('dispatch:read')
    def get_dashboard_distributions():
        """
        获取状态和轨道分布数据
        ---
        tags:
          - 调度仪表盘
        responses:
          200:
            description: 成功获取分布数据
            schema:
              type: object
              properties:
                status_distribution:
                  type: array
                  items:
                    type: object
                    properties:
                      status:
                        type: string
                        description: 状态名称
                      count:
                        type: integer
                        description: 数量
                track_distribution:
                  type: array
                  items:
                    type: object
                    properties:
                      track:
                        type: string
                        description: 轨道名称
                      count:
                        type: integer
                        description: 数量
          500:
            description: 服务器错误
        """
        try:
            status_distribution = DashboardService.get_status_distribution()
            track_distribution = DashboardService.get_track_distribution()
            
            return success_response({
                'status_distribution': status_distribution,
                'track_distribution': track_distribution
            })
        except Exception as e:
            logger.error(f"获取分布数据失败: {str(e)}")
            return error_response(str(e), 500)

    @staticmethod
    @permission_required('dispatch:read')
    def get_urgent_tasks():
        """
        获取紧急任务列表
        ---
        tags:
          - 调度仪表盘
        responses:
          200:
            description: 成功获取紧急任务列表
            schema:
              type: array
              items:
                type: object
                properties:
                  task_id:
                    type: string
                    description: 任务ID
                  mail_route_name:
                    type: string
                    description: 邮路名称
                  status:
                    type: string
                    description: 任务状态
                  created_at:
                    type: string
                    description: 创建时间
                  urgency_level:
                    type: string
                    description: 紧急程度
          500:
            description: 服务器错误
        """
        try:
            urgent_tasks = DashboardService.get_urgent_tasks()
            return success_response(urgent_tasks)
        except Exception as e:
            logger.error(f"获取紧急任务列表失败: {str(e)}")
            return error_response(str(e), 500)

    @staticmethod
    @permission_required('dispatch:read')
    def get_complete_dashboard():
        """
        获取完整的仪表盘数据
        ---
        tags:
          - 调度仪表盘
        responses:
          200:
            description: 成功获取完整仪表盘数据
            schema:
              type: object
              properties:
                statistics:
                  type: object
                  description: 统计概览数据
                status_distribution:
                  type: array
                  description: 状态分布数据
                track_distribution:
                  type: array
                  description: 轨道分布数据
                urgent_tasks:
                  type: array
                  description: 紧急任务列表
          500:
            description: 服务器错误
        """
        try:
            dashboard_data = DashboardService.get_dashboard_data()
            return success_response(dashboard_data)
        except Exception as e:
            logger.error(f"获取完整仪表盘数据失败: {str(e)}")
            return error_response(str(e), 500)