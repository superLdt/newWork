from app.models.task import ManualDispatchTask
from app.models.dispatch_status_history import DispatchStatusHistory
from app.models.dispatch.operation_log import OperationLog
from app.models.vehicle.vehicle import Vehicle
from app.models.vehicle.vehicle_merge_record import VehicleMergeRecord
from app.models.vehicle.vehicle_downgrade_record import VehicleDowngradeRecord
from app.extensions import db
from datetime import datetime
from sqlalchemy.exc import SQLAlchemyError
from typing import Dict, List, Optional, Tuple, Any
import logging
import uuid

logger = logging.getLogger(__name__)


class DispatchService:
    """
    派车服务类，处理派车流程相关的数据操作
    """
    
    @staticmethod
    def _is_large_capacity_vehicle(standard_weight: str) -> bool:
        """
        判断是否为大容积车辆（标准吨位>=30吨）
        
        Args:
            standard_weight: 标准吨位字符串，如"30吨"
            
        Returns:
            bool: 是否为大容积车辆
        """
        if not standard_weight:
            return False
        
        # 提取数字部分
        try:
            weight_num = int(standard_weight.replace('吨', '').replace('A', '').replace('B', ''))
            return weight_num >= 30
        except (ValueError, AttributeError):
            return False
    
    @staticmethod
    def get_task_list(page: int = 1, per_page: int = 10, filters: Dict = None) -> Tuple[List[Dict], int]:
        """
        获取派车任务列表
        
        Args:
            page: 页码
            per_page: 每页数量
            filters: 过滤条件
            
        Returns:
            Tuple[List[Dict], int]: 任务列表和总数
        """
        try:
            from flask import g
            query_obj = ManualDispatchTask.query
            
            # 权限过滤：根据用户角色和关联单位过滤任务
            current_user = getattr(g, 'current_user', None)
            if current_user:
                user_roles = [role.name for role in current_user.roles] if current_user.roles else []
                
                # 超级管理员和区域调度员可以看到全部任务
                if not ('超级管理员' in user_roles or '区域调度员' in user_roles):
                    # 其他角色只能看到与自己关联单位的任务
                    if current_user.dispatch_unit_id:
                        query_obj = query_obj.filter(ManualDispatchTask.organizing_unit_id == current_user.dispatch_unit_id)
                    else:
                        # 如果用户没有关联单位，则看不到任何任务
                        query_obj = query_obj.filter(ManualDispatchTask.task_id == None)  # 返回空结果
            
            # 应用其他过滤条件
            if filters:
                if filters.get('status'):
                    query_obj = query_obj.filter(ManualDispatchTask.status == filters['status'])
                if filters.get('mail_route_name'):
                    query_obj = query_obj.filter(ManualDispatchTask.mail_route_name.ilike(f"%{filters['mail_route_name']}%"))
                if filters.get('origin_bureau'):
                    query_obj = query_obj.filter(ManualDispatchTask.origin_bureau.ilike(f"%{filters['origin_bureau']}%"))
                if filters.get('required_date_start') and filters.get('required_date_end'):
                    query_obj = query_obj.filter(
                        ManualDispatchTask.required_date >= filters['required_date_start'],
                        ManualDispatchTask.required_date <= filters['required_date_end']
                    )
                if filters.get('initiator_user_id'):
                    query_obj = query_obj.filter(ManualDispatchTask.initiator_user_id == filters['initiator_user_id'])
                if filters.get('current_handler_role'):
                    query_obj = query_obj.filter(ManualDispatchTask.current_handler_role == filters['current_handler_role'])
            
            # 按创建时间降序排序
            query_obj = query_obj.order_by(db.desc(ManualDispatchTask.created_at))
            
            # 分页
            pagination = query_obj.paginate(page=page, per_page=per_page, error_out=False)
            tasks = pagination.items
            total = pagination.total
            
            # 转换为字典列表
            task_list = [task.to_dict() for task in tasks]
            
            return task_list, total
        except SQLAlchemyError as e:
            logger.error(f"获取派车任务列表失败: {str(e)}")
            raise
    
    @staticmethod
    def get_task_by_id(task_id: str) -> Optional[Dict]:
        """
        根据ID获取派车任务信息
        
        Args:
            task_id: 任务ID
            
        Returns:
            Optional[Dict]: 任务信息字典，如果不存在则返回None
        """
        try:
            task = ManualDispatchTask.query.get(task_id)
            if not task:
                return None
            return task.to_dict()
        except SQLAlchemyError as e:
            logger.error(f"获取派车任务信息失败: {str(e)}")
            raise
    
    @staticmethod
    def create_task(task_data: Dict) -> Dict:
        """
        创建新派车任务
        
        Args:
            task_data: 任务数据
            
        Returns:
            Dict: 创建的任务信息
        """
        try:
            from flask import g
            
            # 生成任务ID
            task_id = f"T{datetime.now().strftime('%Y%m%d%H%M%S')}{uuid.uuid4().hex[:6].upper()}"
            
            # 获取当前用户信息
            current_user = getattr(g, 'current_user', None)
            current_user_id = current_user.id if current_user else task_data.get('initiator_user_id', 1)
            
            # 获取当前用户角色（取第一个角色作为主要角色）
            current_user_role = None
            if current_user and current_user.roles:
                current_user_role = current_user.roles[0].name
            else:
                current_user_role = task_data.get('initiator_role', '车间地调')
            
            # 确定派车轨道和初始状态
            dispatch_track = task_data.get('dispatch_track', '轨道A')
            requirement_type = task_data.get('requirement_type', '加班派车')
            
            # 获取业务类型和标准吨位
            business_type = task_data.get('business_type', '委办派车')
            standard_weight = task_data.get('standard_weight', '')
            
            # 根据用户角色和业务类型确定轨道和状态
            if current_user_role == '车间地调':
                # 车间地调只能使用轨道A，需要审核
                dispatch_track = '轨道A'
                initial_status = '待审核'
                audit_required = True
                current_handler_role = '区域调度员'
            elif current_user_role in ['超级管理员', '区域调度员']:
                # 管理员和区域调度员可以选择轨道
                if requirement_type == '正班派车':
                    # 正班派车直接下发，使用轨道B
                    dispatch_track = '轨道B'
                    if business_type == '自办派车':
                        # 自办派车根据标准吨位决定处理人
                        if DispatchService._is_large_capacity_vehicle(standard_weight):
                            initial_status = '待响应'
                            current_handler_role = '外包管理公司'
                        else:
                            initial_status = '待响应'
                            current_handler_role = '班组长'
                    else:
                        # 委办派车
                        initial_status = '待供应商响应'
                        current_handler_role = '供应商'
                    audit_required = False
                else:
                    # 加班派车根据选择的轨道确定流程
                    if dispatch_track == '轨道A':
                        initial_status = '待审核'
                        audit_required = True
                        current_handler_role = '区域调度员'
                    else:  # 轨道B
                        if business_type == '自办派车':
                            # 自办派车根据标准吨位决定处理人
                            if DispatchService._is_large_capacity_vehicle(standard_weight):
                                initial_status = '待响应'
                                current_handler_role = '外包管理公司'
                            else:
                                initial_status = '待响应'
                                current_handler_role = '班组长'
                        else:
                            # 委办派车
                            initial_status = '待供应商响应'
                            current_handler_role = '供应商'
                        audit_required = False
            else:
                # 其他角色默认使用轨道A
                dispatch_track = '轨道A'
                initial_status = '待审核'
                audit_required = True
                current_handler_role = '区域调度员'
            
            # 创建任务对象，确保所有字段都正确映射
            task = ManualDispatchTask(
                task_id=task_id,
                required_date=task_data.get('required_date'),
                origin_bureau=task_data.get('origin_bureau'),
                mail_route_name=task_data.get('mail_route_name'),
                organizing_unit=task_data.get('organizing_unit'),
                organizing_unit_id=task_data.get('organizing_unit_id'),
                transport_type=task_data.get('transport_type'),
                requirement_type=requirement_type,
                standard_weight=task_data.get('standard_weight'),
                standard_volume=task_data.get('standard_volume'),
                actual_volume=task_data.get('actual_volume'),
                special_requirements=task_data.get('special_requirements'),
                status=task_data.get('status', initial_status),
                dispatch_track=dispatch_track,
                initiator_role=current_user_role,
                initiator_user_id=current_user_id,
                initiator_department=task_data.get('initiator_department'),
                audit_required=audit_required,
                current_handler_role=current_handler_role,
                business_type=task_data.get('business_type', '委办派车'),
                created_at=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                updated_at=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            )
            
            # 保存到数据库
            db.session.add(task)
            
            # 创建状态历史记录
            status_history = DispatchStatusHistory(
                task_id=task_id,
                status_change='创建任务',
                operator=f"用户ID: {current_user_id}, 角色: {current_user_role}",
                timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                note=f'任务创建，轨道: {dispatch_track}，初始状态: {initial_status}'
            )
            db.session.add(status_history)
            
            # 创建操作日志
            operation_log = OperationLog(
                task_id=task_id,
                operation_type='创建任务',
                user_id=current_user_id,
                user_role=current_user_role,
                operation_time=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                operation_content='创建派车任务',
                ip_address=task_data.get('ip_address')
            )
            db.session.add(operation_log)
            
            db.session.commit()
            
            return task.to_dict()
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"创建派车任务失败: {str(e)}")
            raise
    
    @staticmethod
    def update_task(task_id: str, update_data: Dict) -> Dict:
        """
        更新派车任务信息
        
        Args:
            task_id: 任务ID
            update_data: 更新数据
            
        Returns:
            Dict: 更新后的任务信息
        """
        try:
            # 获取任务对象
            task = ManualDispatchTask.query.get(task_id)
            if not task:
                raise ValueError(f"任务ID {task_id} 不存在")
            
            # 记录原始状态
            old_status = task.status
            
            # 更新任务字段
            for key, value in update_data.items():
                if hasattr(task, key):
                    setattr(task, key, value)
            
            # 更新时间
            task.updated_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            # 如果状态发生变化，创建状态历史记录
            if 'status' in update_data and old_status != update_data['status']:
                status_history = DispatchStatusHistory(
                    task_id=task_id,
                    status_change=f"{old_status} -> {update_data['status']}",
                    operator=f"用户ID: {update_data.get('current_handler_user_id', '系统')}",
                    timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    note=update_data.get('note', '')
                )
                db.session.add(status_history)
                
                # 创建操作日志
                operation_log = OperationLog(
                    task_id=task_id,
                    operation_type='状态变更',
                    user_id=update_data.get('current_handler_user_id'),
                    user_role=update_data.get('current_handler_role'),
                    operation_time=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    operation_content=f"状态从 {old_status} 变更为 {update_data['status']}",
                    ip_address=update_data.get('ip_address')
                )
                db.session.add(operation_log)
            
            db.session.commit()
            
            return task.to_dict()
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"更新派车任务失败: {str(e)}")
            raise
    
    @staticmethod
    def delete_task(task_id: str) -> bool:
        """
        删除派车任务
        
        Args:
            task_id: 任务ID
            
        Returns:
            bool: 是否删除成功
        """
        try:
            # 获取任务对象
            task = ManualDispatchTask.query.get(task_id)
            if not task:
                return False
            
            # 删除任务
            db.session.delete(task)
            db.session.commit()
            
            return True
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"删除派车任务失败: {str(e)}")
            raise
    
    @staticmethod
    def create_vehicle(vehicle_data: Dict) -> Dict:
        """
        创建车辆信息
        
        Args:
            vehicle_data: 车辆数据
            
        Returns:
            Dict: 创建的车辆信息
        """
        try:
            # 创建车辆对象
            vehicle = Vehicle(
                task_id=vehicle_data.get('task_id'),
                license_plate=vehicle_data.get('license_plate'),
                carriage_number=vehicle_data.get('carriage_number'),
                driver_name=vehicle_data.get('driver_name'),
                driver_phone=vehicle_data.get('driver_phone'),
                driver_id_card=vehicle_data.get('driver_id_card'),
                vehicle_type=vehicle_data.get('vehicle_type'),
                supplier_id=vehicle_data.get('supplier_id'),
                status='已分配',
                created_at=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                updated_at=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            )
            
            # 保存到数据库
            db.session.add(vehicle)
            
            # 创建操作日志
            operation_log = OperationLog(
                task_id=vehicle.task_id,
                operation_type='分配车辆',
                user_id=vehicle_data.get('operator_id'),
                user_role=vehicle_data.get('operator_role'),
                operation_time=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                operation_content=f"分配车辆 {vehicle_data.get('license_plate')}",
                ip_address=vehicle_data.get('ip_address')
            )
            db.session.add(operation_log)
            
            db.session.commit()
            
            return vehicle.to_dict()
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"创建车辆信息失败: {str(e)}")
            raise
    
    @staticmethod
    def get_task_status_history(task_id: str) -> List[Dict]:
        """
        获取任务状态历史
        
        Args:
            task_id: 任务ID
            
        Returns:
            List[Dict]: 状态历史列表
        """
        try:
            # 查询状态历史记录
            history_records = DispatchStatusHistory.query.filter_by(task_id=task_id).order_by(DispatchStatusHistory.timestamp).all()
            
            # 转换为字典列表
            history_list = [record.to_dict() for record in history_records]
            
            return history_list
        except SQLAlchemyError as e:
            logger.error(f"获取任务状态历史失败: {str(e)}")
            raise
    
    @staticmethod
    def get_task_operation_logs(task_id: str) -> List[Dict]:
        """
        获取任务操作日志
        
        Args:
            task_id: 任务ID
            
        Returns:
            List[Dict]: 操作日志列表
        """
        try:
            # 查询操作日志记录
            log_records = OperationLog.query.filter_by(task_id=task_id).order_by(OperationLog.operation_time).all()
            
            # 转换为字典列表
            log_list = [record.to_dict() for record in log_records]
            
            return log_list
        except SQLAlchemyError as e:
            logger.error(f"获取任务操作日志失败: {str(e)}")
            raise
    
    @staticmethod
    def merge_vehicles(source_vehicle_id: int, target_vehicle_id: int, operator_id: int, operator_role: str) -> Dict:
        """
        合并车辆信息
        
        Args:
            source_vehicle_id: 源车辆ID
            target_vehicle_id: 目标车辆ID
            operator_id: 操作人ID
            operator_role: 操作人角色
            
        Returns:
            Dict: 合并结果
        """
        try:
            # 获取源车辆和目标车辆
            source_vehicle = Vehicle.query.get(source_vehicle_id)
            target_vehicle = Vehicle.query.get(target_vehicle_id)
            
            if not source_vehicle or not target_vehicle:
                raise ValueError("源车辆或目标车辆不存在")
            
            # 创建合并记录
            merge_record = VehicleMergeRecord(
                source_vehicle_id=source_vehicle_id,
                target_vehicle_id=target_vehicle_id,
                merge_time=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                operator_id=operator_id,
                operator_role=operator_role,
                source_license_plate=source_vehicle.license_plate,
                target_license_plate=target_vehicle.license_plate,
                source_data=source_vehicle.to_dict(),
                merge_reason="车辆信息合并"
            )
            
            # 保存合并记录
            db.session.add(merge_record)
            
            # 更新目标车辆信息
            if not target_vehicle.actual_volume and source_vehicle.actual_volume:
                target_vehicle.actual_volume = source_vehicle.actual_volume
            
            if not target_vehicle.driver_name and source_vehicle.driver_name:
                target_vehicle.driver_name = source_vehicle.driver_name
                target_vehicle.driver_phone = source_vehicle.driver_phone
                target_vehicle.driver_id_card = source_vehicle.driver_id_card
            
            # 标记源车辆为已合并状态
            source_vehicle.status = '已合并'
            source_vehicle.updated_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            # 创建操作日志
            operation_log = OperationLog(
                task_id=source_vehicle.task_id,
                operation_type='车辆合并',
                operator_id=operator_id,
                operator_role=operator_role,
                operation_time=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                operation_details=f"将车辆 {source_vehicle.license_plate} 合并到 {target_vehicle.license_plate}"
            )
            db.session.add(operation_log)
            
            db.session.commit()
            
            return merge_record.to_dict()
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"合并车辆信息失败: {str(e)}")
            raise
    
    @staticmethod
    def downgrade_vehicle(vehicle_id: int, new_type: str, reason: str, operator_id: int, operator_role: str) -> Dict:
        """
        车辆降档
        
        Args:
            vehicle_id: 车辆ID
            new_type: 新车型
            reason: 降档原因
            operator_id: 操作人ID
            operator_role: 操作人角色
            
        Returns:
            Dict: 降档结果
        """
        try:
            # 获取车辆
            vehicle = Vehicle.query.get(vehicle_id)
            
            if not vehicle:
                raise ValueError("车辆不存在")
            
            # 记录原车型
            old_type = vehicle.vehicle_type
            
            # 创建降档记录
            downgrade_record = VehicleDowngradeRecord(
                vehicle_id=vehicle_id,
                original_type=old_type,
                new_type=new_type,
                downgrade_time=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                operator_id=operator_id,
                operator_role=operator_role,
                license_plate=vehicle.license_plate,
                downgrade_reason=reason
            )
            
            # 保存降档记录
            db.session.add(downgrade_record)
            
            # 更新车辆类型
            vehicle.vehicle_type = new_type
            vehicle.updated_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            # 创建操作日志
            operation_log = OperationLog(
                task_id=vehicle.task_id,
                operation_type='车辆降档',
                operator_id=operator_id,
                operator_role=operator_role,
                operation_time=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                operation_details=f"将车辆 {vehicle.license_plate} 从 {old_type} 降档为 {new_type}"
            )
            db.session.add(operation_log)
            
            db.session.commit()
            
            return downgrade_record.to_dict()
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"车辆降档失败: {str(e)}")
            raise
    
    # 添加别名方法和缺失方法，用于与控制器及业务层命名对齐
    
    @staticmethod
    def get_dispatch_task_list(page: int = 1, per_page: int = 10, filters: Dict = None) -> Tuple[List[Dict], int]:
        """
        获取派车任务列表（控制器调用的别名方法）
        """
        return DispatchService.get_task_list(page, per_page, filters)
    
    @staticmethod
    def get_dispatch_task_by_id(task_id: str) -> Optional[Dict]:
        """
        根据ID获取派车任务信息（控制器调用的别名方法）
        """
        return DispatchService.get_task_by_id(task_id)
    
    @staticmethod
    def create_dispatch_task(task_data: Dict) -> Dict:
        """
        创建新派车任务（控制器调用的别名方法）
        """
        return DispatchService.create_task(task_data)
    
    @staticmethod
    def update_dispatch_task(task_id: str, update_data: Dict) -> Dict:
        """
        更新派车任务信息（控制器调用的别名方法）
        """
        return DispatchService.update_task(task_id, update_data)
    
    @staticmethod
    def assign_vehicle_to_task(task_id: str, vehicle_data: Dict) -> Dict:
        """
        为任务分配车辆
        
        Args:
            task_id: 任务ID
            vehicle_data: 车辆数据（包含车辆ID、司机信息等）
            
        Returns:
            Dict: 分配结果
        """
        try:
            # 检查任务是否存在
            task = ManualDispatchTask.query.get(task_id)
            if not task:
                raise ValueError(f"任务不存在: {task_id}")
            
            # 获取或创建车辆
            vehicle_id = vehicle_data.get('vehicle_id')
            if vehicle_id:
                # 使用已有车辆
                vehicle = Vehicle.query.get(vehicle_id)
                if not vehicle:
                    raise ValueError(f"车辆不存在: {vehicle_id}")
                
                # 更新车辆信息
                vehicle.task_id = task_id
                vehicle.driver_name = vehicle_data.get('driver_name', vehicle.driver_name)
                vehicle.driver_phone = vehicle_data.get('driver_phone', vehicle.driver_phone)
                vehicle.status = '已分配'
                vehicle.updated_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            else:
                # 创建新车辆
                vehicle_data['task_id'] = task_id
                vehicle = DispatchService.create_vehicle(vehicle_data)
                return vehicle
            
            # 记录操作日志
            operation_log = OperationLog(
                task_id=task_id,
                operation_type='分配车辆',
                operator_id=vehicle_data.get('operator_id'),
                operator_role=vehicle_data.get('operator_role'),
                operation_time=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                operation_details=f"为任务分配车辆 {vehicle.license_plate}",
                ip_address=vehicle_data.get('ip_address')
            )
            db.session.add(operation_log)
            
            db.session.commit()
            
            return vehicle.to_dict()
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"分配车辆失败: {str(e)}")
            raise
    
    @staticmethod
    def get_vehicle_by_id(vehicle_id: int) -> Optional[Dict]:
        """
        根据ID获取车辆信息
        
        Args:
            vehicle_id: 车辆ID
            
        Returns:
            Optional[Dict]: 车辆信息字典，如果不存在则返回None
        """
        try:
            vehicle = Vehicle.query.get(vehicle_id)
            if not vehicle:
                return None
            return vehicle.to_dict()
        except SQLAlchemyError as e:
            logger.error(f"获取车辆信息失败: {str(e)}")
            raise
    
    @staticmethod
    def update_task_status(task_id: str, new_status: str, status_history_data: Dict = None) -> Dict:
        """
        更新任务状态并记录历史
        
        Args:
            task_id: 任务ID
            new_status: 新状态
            status_history_data: 状态历史数据
            
        Returns:
            Dict: 更新结果
        """
        try:
            # 获取任务
            task = ManualDispatchTask.query.get(task_id)
            if not task:
                raise ValueError(f"任务不存在: {task_id}")
            
            # 更新任务状态
            old_status = task.status
            task.status = new_status
            task.updated_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            # 如果提供了状态历史数据，则创建历史记录
            if status_history_data:
                status_history = DispatchStatusHistory(
                    task_id=task_id,
                    status_change=f"{status_history_data.get('previous_status', old_status)} -> {new_status}",
                    operator=f"用户ID: {status_history_data.get('changed_by', '系统')}",
                    timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    note=status_history_data.get('comment', '')
                )
                db.session.add(status_history)
            
            db.session.commit()
            
            return {
                'task_id': task_id,
                'old_status': old_status,
                'new_status': new_status,
                'updated_at': task.updated_at
            }
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"更新任务状态失败: {str(e)}")
            raise