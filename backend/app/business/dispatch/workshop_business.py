"""
车间地调相关业务逻辑模块

处理车间核实和相关业务逻辑

车间地调角色发起派车说明：
1. 当用户角色为"车间地调"时，系统会自动调用本模块的create_dispatch_task方法
2. 车间地调创建的任务走"轨道A流程"，需要经过审核阶段
3. 任务初始状态设置为"待审核"，由超级管理员/区域调度员进行审核
4. 审核通过后任务进入"待响应"状态，由供应商/班组长/大容积供应商等角色进行响应
5. 任务创建后会记录状态历史，便于追踪任务流转过程

业务流程：
车间地调创建任务 → 超级管理员/区域调度员审核 → 供应商/班组长/大容积供应商响应 → 车间地调核查 → 供应商/班组长/供应商确认 → 任务完成
"""

from datetime import datetime
from flask_jwt_extended import get_current_user
from app.models.task import ManualDispatchTask
from app.models.vehicle.vehicle import Vehicle
from app.models.dispatch_status_history import DispatchStatusHistory
from app.models.vehicle.vehicle_downgrade_record import VehicleDowngradeRecord
from app.models.vehicle.vehicle_merge_record import VehicleMergeRecord
from app.business.dispatch.status_manager import DispatchStatusManager
from app.business.vehicle.vehicle_downgrade_business import VehicleDowngradeBusiness
from app.business.dispatch.base_business import BaseDispatchBusiness
from app.services.dispatch.dispatch_service import DispatchService  # 修正导入路径
from typing import Dict, Any
import re
import logging

logger = logging.getLogger(__name__)

class WorkshopDispatchBusiness(BaseDispatchBusiness):
    """车间地调派车业务逻辑类"""
    
    @staticmethod
    def _save_operation_attachments(attachments: list, operation_type: str, operation_id: int, current_user) -> bool:
        """
        保存操作附件
        
        Args:
            attachments: 附件列表
            operation_type: 操作类型
            operation_id: 操作ID
            current_user: 当前用户
            
        Returns:
            bool: 保存是否成功
        """
        if not attachments or not operation_id:
            return True
        
        try:
            from app.services.common.upload_service import UploadService
            
            # 使用UploadService保存附件，设置业务类型和业务ID
            business_type = f"dispatch_{operation_type}"
            business_id = str(operation_id)
            
            for attachment in attachments:
                if isinstance(attachment, dict) and 'file' in attachment:
                    file = attachment['file']
                    success, result = UploadService.save_file(
                        file=file,
                        file_type='document',  # 默认为文档类型
                        business_type=business_type,
                        business_id=business_id,
                        user_id=current_user.id
                    )
                    if not success:
                        logger.warning(f'保存附件失败: {result}')
                        return False
            
            return True
            
        except Exception as e:
            logger.warning(f'保存操作附件失败: {e}')
            return False

    @staticmethod
    def create_dispatch_task(task_data):
        """
        车间地调创建派车任务（轨道A流程 - 需要审核）
        
        Args:
            task_data: 任务数据
            
        Returns:
            Dict: 创建结果
        """
        try:
            current_user = get_current_user()
            
            # 获取用户角色名称
            user_roles = [role.name for role in current_user.roles] if hasattr(current_user, 'roles') else []
            user_role = '车间地调' if '车间地调' in user_roles else (user_roles[0] if user_roles else '未知角色')
            
            # 生成任务ID
            import uuid
            task_id = f"T{datetime.now().strftime('%Y%m%d%H%M%S')}{str(uuid.uuid4())[:6]}"
            
            # 准备任务数据
            task_data_prepared = {
                'task_id': task_id,
                'mail_route_name': task_data.get('mail_route_name', ''),
                'required_date': task_data.get('required_date', ''),
                'origin_bureau': task_data.get('origin_bureau', ''),
                'organizing_unit': task_data.get('organizing_unit', ''),
                'organizing_unit_id': task_data.get('organizing_unit_id'),
                'transport_type': task_data.get('transport_type', ''),
                'requirement_type': task_data.get('requirement_type', ''),
                'required_weight': task_data.get('required_weight', ''),
                'required_volume': task_data.get('required_volume', 0),
                'special_requirements': task_data.get('special_requirements', ''),
                'status': '待审核',  # 车间地调创建的任务需要审核
                'dispatch_track': '轨道A',  # 车间地调创建的任务走轨道A
                'initiator_role': '车间地调',
                'initiator_user_id': current_user.id,
                'initiator_department': task_data.get('initiator_department') or BaseDispatchBusiness._get_user_department_name(current_user.id),
                'audit_required': True,  # 需要审核
                'current_handler_role': '超级管理员/区域调度员',  # 默认流转到管理员审核
                'current_handler_user_id': None,
                'business_type': task_data.get('business_type', '委办派车')  # 从传入参数读取业务类型
            }
            
            # 调用服务层创建任务
            result = DispatchService.create_dispatch_task(task_data_prepared)
            
            # 记录状态历史（使用服务层方法）
            operator_name = (getattr(current_user, 'full_name', None) or 
                           getattr(current_user, 'username', None) or 
                           f"ID:{getattr(current_user, 'id', '系统')}")
            
            status_history_data = {
                'task_id': task_id,
                'status_change': '任务创建',
                'operator': operator_name,
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'note': f'车间地调创建派车任务：{task_data.get("mail_route_name", "")}',
                'next_handler_role': '超级管理员/区域调度员'
            }
            
            # 调用服务层记录状态历史
            DispatchService.add_status_history(status_history_data)
            
            # 记录操作日志
            BaseDispatchBusiness._log_task_action(
                task_id=task_id,
                action_type='create',
                details={
                    'route_name': task_data.get('mail_route_name', ''),
                    'initiator_role': '车间地调',
                    'status': '待审核'
                }
            )
            
            return WorkshopDispatchBusiness._ok(f'车间地调创建派车任务成功，任务ID：{task_id}，当前状态：待审核')
            
        except Exception as e:
            return WorkshopDispatchBusiness._error(f'创建派车任务失败：{str(e)}')
    
    @staticmethod
    def process_workshop_verification(task_id: int, verification_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        处理车间核实操作（主入口方法）
        
        Args:
            task_id: 任务ID
            verification_data: 核实数据
            
        Returns:
            Dict: 处理结果
        """
        try:
            current_user = get_current_user()
            # 使用服务层获取任务信息
            task_dict = DispatchService.get_dispatch_task_by_id(str(task_id))
            if not task_dict:
                raise ValueError(f'未找到ID为{task_id}的派车任务')
            
            # 检查任务状态 - 支持多种状态
            valid_statuses = ['待车间核查', '待核查']
            if task_dict['status'] not in valid_statuses:
                raise ValueError(f'当前任务状态为{task_dict["status"]}，不能进行车间核实操作')
            
            # 根据操作类型调用对应的处理方法
            operation_type = verification_data.get('operation_type')
            
            if operation_type == 'confirm':
                return WorkshopDispatchBusiness._process_confirm_verification(task_id, task_dict, verification_data)
            elif operation_type == 'downgrade':
                return WorkshopDispatchBusiness._process_downgrade_verification(task_id, task_dict, verification_data)
            elif operation_type == 'merge':
                return WorkshopDispatchBusiness._process_merge_verification(task_id, task_dict, verification_data)
            else:
                raise ValueError(f'不支持的操作类型：{operation_type}')
                
        except Exception as e:
            return {
                'success': False,
                'message': f'处理车间核实失败：{str(e)}',
                'code': 'WORKSHOP_VERIFICATION_FAILED'
            }

    @staticmethod
    def _process_confirm_verification(task_id: int, task_dict: Dict[str, Any], verification_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        处理核实通过操作
        
        Args:
            task_id: 任务ID
            task_dict: 任务信息
            verification_data: 核实数据
            
        Returns:
            Dict: 处理结果
        """
        current_user = get_current_user()
        comment = verification_data.get('comment', '')
        
        # 图片附件信息
        attachments = verification_data.get('attachments', [])
        
        # 核实通过操作，更新实际吨位和实际容积
        supplier_info = verification_data.get('supplier_vehicle_info', {}) or {}
        actual_weight = supplier_info.get('actual_weight')
        actual_volume = supplier_info.get('actual_volume')

        # 若前端未提供supplier_vehicle_info，回退到数据库中已响应车辆记录
        if actual_weight is None or actual_volume is None:
            # 使用服务层获取车辆信息
            from app.services.vehicle.vehicle_downgrade_service import VehicleDowngradeService
            vehicle_dict = VehicleDowngradeService.get_vehicle_by_task_id(str(task_id))

            if vehicle_dict:
                # 回填实际容积
                if actual_volume is None:
                    actual_volume = int(vehicle_dict['actual_volume']) if vehicle_dict.get('actual_volume') is not None else None
                # 回填实际吨位，优先使用original_capacity，否则从vehicle_type解析数字
                if actual_weight is None:
                    weight_val = vehicle_dict.get('original_capacity')
                    if (weight_val is None) and vehicle_dict.get('vehicle_type'):
                        try:
                            m = re.search(r"(\d+)", str(vehicle_dict['vehicle_type']))
                            weight_val = int(m.group(1)) if m else None
                        except Exception:
                            weight_val = None
                    actual_weight = str(int(weight_val)) if (weight_val is not None) else None

        # 更新任务数据
        update_data = {
            'actual_weight': actual_weight,
            'actual_volume': actual_volume,
            'status': '待确认',
            'status_type': 0  # 0表示正常
        }
        DispatchService.update_dispatch_task(str(task_id), update_data)
        
        # 确定下一处理人角色
        next_handler_role = WorkshopDispatchBusiness._get_next_handler_role(task_id)
        
        # 更新处理人角色
        DispatchService.update_dispatch_task(str(task_id), {'current_handler_role': next_handler_role})
        
        # 记录状态历史
        WorkshopDispatchBusiness._record_status_history(
            task_id, '车间核实通过', comment, next_handler_role, 'confirm'
        )
        
        # 处理图片附件 - 对于核实通过操作，我们需要创建一个操作记录来关联附件
        confirm_record_id = None
        if attachments:
            # 为核实通过操作创建一个操作记录
            from app.services.common.upload_service import UploadService
            try:
                # 使用UploadService保存附件，设置业务类型和业务ID
                business_type = "dispatch_confirm"
                business_id = str(task_id)
                
                saved_files = []
                for attachment in attachments:
                    if isinstance(attachment, dict) and 'file' in attachment:
                        file = attachment['file']
                        success, result = UploadService.save_file(
                            file=file,
                            file_type='document',
                            business_type=business_type,
                            business_id=business_id,
                            user_id=current_user.id
                        )
                        if success:
                            saved_files.append(result)
                        else:
                            logger.warning(f'保存核实通过操作附件失败: {result}')
                
                # 返回第一个保存成功的文件ID作为confirm_record_id
                if saved_files:
                    confirm_record_id = saved_files[0].get('id')
                    
            except Exception as e:
                logger.warning(f'保存核实通过操作附件失败: {e}')
        
        return {
            'success': True,
            'data': {
                'task_id': task_id,
                'status': '待确认',
                'current_handler_role': next_handler_role,
                'operation_type': 'confirm',
                'confirm_record_id': confirm_record_id,
                'message': '车间地调核实操作（confirm）成功'
            }
        }

    @staticmethod
    def _process_downgrade_verification(task_id: int, task_dict: Dict[str, Any], verification_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        处理降档操作
        
        Args:
            task_id: 任务ID
            task_dict: 任务信息
            verification_data: 核实数据
            
        Returns:
            Dict: 处理结果
        """
        current_user = get_current_user()
        comment = verification_data.get('comment', '')
        tonnage = verification_data.get('tonnage')
        
        # 图片附件信息
        attachments = verification_data.get('attachments', [])
        
        if not tonnage:
            raise ValueError('降档操作需要提供吨位参数')
        
        # 统一将吨位转换为数字（支持字符串如"30吨/40吨A/40吨B"）
        def _parse_tonnage_to_float(val):
            try:
                if isinstance(val, (int, float)):
                    return float(val)
                # 从字符串中抽取第一个数字
                m = re.search(r"(\d+)", str(val))
                return float(m.group(1)) if m else None
            except Exception:
                return None

        # 使用服务层获取车辆信息
        from app.services.vehicle.vehicle_downgrade_service import VehicleDowngradeService
        vehicle_dict = VehicleDowngradeService.get_vehicle_by_task_id(str(task_id))
        
        # 获取供应商响应车辆信息中的派车单号
        dispatch_number = None
        if vehicle_dict:
            dispatch_number = vehicle_dict.get('dispatch_number') or vehicle_dict.get('manifest_number')
        
        # 准备降档记录数据
        downgrade_data = {
            'task_id': str(task_id),
            'vehicle_id': vehicle_dict.get('id') if vehicle_dict else None,
            'operation_type': 'downgrade',
            'operation_time': datetime.now(),
            'operator_id': current_user.id,
            'operator_name': (getattr(current_user, 'full_name', None) or getattr(current_user, 'username', None) or f"ID:{current_user.id}"),
            'operator_role': '车间地调',
            # 将原始吨位和降档后吨位写入数字，避免浮点字段写入字符串导致数据库错误
            'original_tonnage': _parse_tonnage_to_float(task_dict.get('required_weight')),
            'downgraded_tonnage': _parse_tonnage_to_float(tonnage),
            'operation_reason': comment or '车间核查降档处理',
            'dispatch_number': dispatch_number  # 记录派车单号
        }
        
        # 使用服务层创建降档记录
        downgrade_result = VehicleDowngradeService.create_downgrade_record(downgrade_data)
        if not downgrade_result:
            logger.warning(f'保存降档记录失败，继续处理任务更新')
        
        downgrade_record_id = downgrade_result.get('id') if isinstance(downgrade_result, dict) else downgrade_result.id if downgrade_result else None
        
        # 处理图片附件
        if attachments and downgrade_record_id:
            WorkshopDispatchBusiness._save_operation_attachments(
                attachments, 'downgrade', downgrade_record_id, current_user
            )
        
        # 仅更新实际吨位，不修改需求吨位
        update_data = {
            # 任务表"实际吨位"为字符串字段，统一以"X吨"写入，避免类型不一致
            'actual_weight': f"{int(_parse_tonnage_to_float(tonnage))}吨" if _parse_tonnage_to_float(tonnage) is not None else str(tonnage),
            'status': '待确认',
            'status_type': 1  # 1表示降档
        }
        DispatchService.update_dispatch_task(str(task_id), update_data)
        
        # 确定下一处理人角色
        next_handler_role = WorkshopDispatchBusiness._get_next_handler_role(task_id)
        
        # 更新处理人角色
        DispatchService.update_dispatch_task(str(task_id), {'current_handler_role': next_handler_role})
        
        # 记录状态历史
        WorkshopDispatchBusiness._record_status_history(
            task_id, f'车间核实降档至{tonnage}吨', comment, next_handler_role, 'downgrade'
        )
        
        return {
            'success': True,
            'data': {
                'task_id': task_id,
                'status': '待确认',
                'current_handler_role': next_handler_role,
                'operation_type': 'downgrade',
                'downgrade_record_id': downgrade_record_id,
                'message': '车间地调核实操作（downgrade）成功'
            }
        }

    @staticmethod
    def _process_merge_verification(task_id: int, task_dict: Dict[str, Any], verification_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        处理合并操作
        
        Args:
            task_id: 任务ID
            task_dict: 任务信息
            verification_data: 核实数据
            
        Returns:
            Dict: 处理结果
        """
        current_user = get_current_user()
        comment = verification_data.get('comment', '')
        
        # 合并操作 - 支持通过派车单号或任务ID查找目标任务
        merge_task_id = verification_data.get('merge_task_id')
        merge_dispatch_number = verification_data.get('merge_dispatch_number')
        
        # 新增车辆信息
        new_vehicle_info = verification_data.get('new_vehicle_info', {})
        
        # 图片附件信息
        attachments = verification_data.get('attachments', [])
        
        if not merge_task_id and not merge_dispatch_number:
            raise ValueError('合并操作需要提供目标任务ID或派车单号')
        
        # 获取源车辆信息
        from app.services.vehicle.vehicle_merge_service import VehicleMergeService
        source_vehicle_dict = VehicleMergeService.get_vehicle_by_task_id(str(task_id))
        source_dispatch_number = None
        if source_vehicle_dict:
            source_dispatch_number = source_vehicle_dict.get('dispatch_number') or source_vehicle_dict.get('manifest_number')
        
        # 处理目标派车单号信息
        target_dispatch_number = merge_dispatch_number  # 直接使用输入的派车单号
        
        # 优先使用前端传递的合并后实际重量，如果没有则计算
        merged_actual_weight = verification_data.get('actual_weight')
        
        if not merged_actual_weight:
            # 如果前端没有传递actual_weight，则使用原有逻辑计算
            # 获取源任务的实际重量信息
            source_actual_weight = task_dict.get('actual_weight')
            if not source_actual_weight and source_vehicle_dict:
                # 如果源任务没有实际重量，从车辆信息中获取
                weight_val = source_vehicle_dict.get('original_capacity')
                if weight_val is None and source_vehicle_dict.get('vehicle_type'):
                    try:
                        m = re.search(r"(\d+)", str(source_vehicle_dict['vehicle_type']))
                        weight_val = int(m.group(1)) if m else None
                    except Exception:
                        weight_val = None
                source_actual_weight = f"{int(weight_val)}吨" if weight_val is not None else None

            # 获取目标任务信息并计算合并后的总重量
            merged_actual_weight = source_actual_weight
            target_task_dict = None
            
            if merge_dispatch_number:
                # 通过派车单号获取目标任务信息
                target_task_dict = DispatchService.get_dispatch_task_by_dispatch_number(merge_dispatch_number)
            elif merge_task_id:
                # 通过任务ID获取目标任务信息
                target_task_dict = DispatchService.get_dispatch_task_by_id(str(merge_task_id))
            
            if target_task_dict:
                target_actual_weight = target_task_dict.get('actual_weight')
                
                # 解析源任务和目标任务的重量数值
                def parse_weight(weight_str):
                    if not weight_str:
                        return 0
                    try:
                        # 提取数字部分
                        match = re.search(r"(\d+(?:\.\d+)?)", str(weight_str))
                        return float(match.group(1)) if match else 0
                    except:
                        return 0
                
                source_weight_num = parse_weight(source_actual_weight)
                target_weight_num = parse_weight(target_actual_weight)
                
                # 计算合并后的总重量
                if source_weight_num > 0 or target_weight_num > 0:
                    total_weight = source_weight_num + target_weight_num
                    merged_actual_weight = f"{int(total_weight)}吨" if total_weight == int(total_weight) else f"{total_weight}吨"
        
        # 计算合并后的总容积
        merged_volume = float(task_dict.get('required_volume', 0)) if task_dict.get('required_volume') else 0
        target_task_dict = None
        
        if merge_dispatch_number:
            # 通过派车单号获取目标任务信息
            target_task_dict = DispatchService.get_dispatch_task_by_dispatch_number(merge_dispatch_number)
        elif merge_task_id:
            # 通过任务ID获取目标任务信息
            target_task_dict = DispatchService.get_dispatch_task_by_id(str(merge_task_id))
        
        if target_task_dict:
            target_required_volume = target_task_dict.get('required_volume', 0)
            # 计算合并后的总容积
            source_volume = float(task_dict.get('required_volume', 0)) if task_dict.get('required_volume') else 0
            target_volume = float(target_required_volume) if target_required_volume else 0
            merged_volume = source_volume + target_volume

        # 准备合并记录数据
        merge_data = {
            'source_task_id': str(task_id),
            'source_vehicle_id': source_vehicle_dict.get('id') if source_vehicle_dict else None,
            'operation_time': datetime.now(),
            'operator_id': current_user.id,
            'operator_name': getattr(current_user, 'full_name', None) or getattr(current_user, 'username', None) or f"ID:{current_user.id}",
            'operator_role': '车间地调',
            'original_volume': float(task_dict.get('required_volume', 0)) if task_dict.get('required_volume') else None,
            'merged_volume': merged_volume,  # 记录合并后的总容积
            'merge_reason': comment or '车间核查合并处理',
            'merge_status': 'completed',
            'source_dispatch_number': source_dispatch_number,  # 记录源派车单号
            'target_dispatch_number': target_dispatch_number,   # 记录目标派车单号
            # 新增车辆信息
            'new_vehicle_license_plate': new_vehicle_info.get('license_plate'),
            'new_vehicle_tonnage': float(new_vehicle_info.get('tonnage')) if new_vehicle_info.get('tonnage') else None,
            'new_vehicle_volume': float(new_vehicle_info.get('volume')) if new_vehicle_info.get('volume') else None,
            'new_vehicle_type': new_vehicle_info.get('vehicle_type'),
            'new_vehicle_carriage_number': new_vehicle_info.get('carriage_number')
        }
        
        # 使用服务层创建合并记录
        merge_result = VehicleMergeService.create_merge_record(merge_data)
        if not merge_result:
            raise ValueError('创建合并记录失败')
        
        merge_record_id = merge_result.get('id') if isinstance(merge_result, dict) else merge_result.id
        
        # 处理图片附件
        if attachments and merge_record_id:
            WorkshopDispatchBusiness._save_operation_attachments(
                attachments, 'merge', merge_record_id, current_user
            )

        # 更新当前任务状态为已合并，并记录合并后的总重量
        update_data = {
            'status': '待确认',
            'merge_target_task_id': None,  # 不记录目标任务ID
            'status_type': 2,  # 2表示合并
            'actual_weight': merged_actual_weight  # 记录合并后的总重量
        }
        DispatchService.update_dispatch_task(str(task_id), update_data)
        
        # 确定下一处理人角色
        next_handler_role = WorkshopDispatchBusiness._get_next_handler_role(task_id)
        
        # 更新处理人角色
        DispatchService.update_dispatch_task(str(task_id), {'current_handler_role': next_handler_role})
        
        # 记录状态历史
        WorkshopDispatchBusiness._record_status_history(
            task_id, f'车间核实合并到派车单号{merge_dispatch_number}', comment, next_handler_role, 'merge'
        )
        
        return {
            'success': True,
            'data': {
                'task_id': task_id,
                'status': '待确认',
                'current_handler_role': next_handler_role,
                'operation_type': 'merge',
                'merge_record_id': merge_record_id,
                'message': '车间地调核实操作（merge）成功'
            }
        }

    @staticmethod
    def _get_next_handler_role(task_id: int) -> str:
        """
        根据车辆供应商类型确定下一处理人角色
        
        Args:
            task_id: 任务ID
            
        Returns:
            str: 下一处理人角色
        """
        # 使用服务层获取车辆信息来判断供应商类型
        from app.services.vehicle.vehicle_downgrade_service import VehicleDowngradeService
        vehicle_dict = VehicleDowngradeService.get_vehicle_by_task_id(str(task_id))
        
        if vehicle_dict:
            supplier_type = vehicle_dict.get('supplier_type')
            if supplier_type == '班组':
                return '班组长'
            elif supplier_type == '大容积供应商':
                return '大容积供应商'
            else:
                return '供应商'
        else:
            return '供应商'

    @staticmethod
    def _record_status_history(task_id: int, status_change: str, comment: str, next_handler_role: str, operation_type: str):
        """
        记录状态历史
        
        Args:
            task_id: 任务ID
            status_change: 状态变更描述
            comment: 备注
            next_handler_role: 下一处理人角色
            operation_type: 操作类型
        """
        current_user = get_current_user()
        operator_name = (getattr(current_user, 'full_name', None) or 
                       getattr(current_user, 'username', None) or 
                       f"ID:{getattr(current_user, 'id', '系统')}")
        
        status_history_data = {
            'task_id': str(task_id),
            'status_change': status_change,
            'operator': operator_name,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'note': f'车间地调核实操作（{operation_type}）：{comment}',
            'next_handler_role': next_handler_role
        }
        
        # 调用服务层记录状态历史
        DispatchService.add_status_history(status_history_data)

    # @staticmethod
    # def assign_dispatch_task(task_id: int, assign_data: Dict[str, Any]) -> Dict[str, Any]:
    #     """
    #     分配派车任务
    #
    #     Args:
    #         task_id: 任务ID
    #         assign_data: 分配数据
    #
    #     Returns:
    #         Dict: 分配结果
    #     """
    #     try:
    #         current_user = get_current_user()
    #         task = ManualDispatchTask.query.get(task_id)
    #         if not task:
    #             raise ValueError(f'未找到ID为{task_id}的派车任务')
    #
    #         if task.status != '待分配':
    #             raise ValueError(f'当前任务状态为{task.status}，不能进行分配操作')
    #
    #         assignee_role = assign_data.get('assignee_role', '车间地调')
    #         assignee_id = assign_data.get('assignee_id')
    #         assignee_name = assign_data.get('assignee_name', '')
    #         remarks = assign_data.get('remarks', '')
    #
    #         # 更新任务状态和处理人
    #         task.status = '待车间核查'
    #         task.current_handler_role = assignee_role
    #         task.current_handler_id = assignee_id
    #         task.updated_at = datetime.now()
    #
    #         # 记录状态历史
    #         status_history = DispatchStatusHistory(
    #             task_id=task_id,
    #             status_change='任务分配',
    #             operator=(getattr(current_user, 'full_name', None) or
    #                      getattr(current_user, 'username', None) or
    #                      f"ID:{getattr(current_user, 'id', '系统')}"),
    #             timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
    #             note=f'分配给{assignee_role}（{assignee_name}）：{remarks}',
    #             next_handler_role=assignee_role
    #         )
    #         db.session.add(status_history)
    #
    #         # 提交事务
    #         db.session.commit()
    #
    #         return {
    #             'task_id': task_id,
    #             'status': task.status,
    #             'current_handler_role': task.current_handler_role,
    #             'current_handler_id': task.current_handler_id,
    #             'message': f'派车任务分配给{assignee_role}（{assignee_name}）成功'
    #         }
    #
    #     except Exception as e:
    #         db.session.rollback()
    #         raise e

    @staticmethod
    def cancel_dispatch_task(task_id: int, cancel_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        取消派车任务
        
        Args:
            task_id: 任务ID
            cancel_data: 取消数据
            
        Returns:
            Dict: 取消结果
        """
        try:
            current_user = get_current_user()
            # 使用服务层获取任务信息
            task_dict = DispatchService.get_dispatch_task_by_id(str(task_id))
            if not task_dict:
                raise ValueError(f'未找到ID为{task_id}的派车任务')
            
            # 检查任务状态是否允许取消操作
            allowed_statuses = ['待审核', '待响应', '待车间核查', '待核查', '待确认']
            if task_dict['status'] not in allowed_statuses:
                raise ValueError(f'当前任务状态为{task_dict["status"]}，不能进行取消操作')
            
            cancel_reason = cancel_data.get('cancel_reason', '')
            
            # 使用服务层更新任务状态
            update_data = {
                'status': '已取消',
                'current_handler_role': None
            }
            
            DispatchService.update_dispatch_task(str(task_id), update_data)
            
            # 记录状态历史（使用服务层方法）
            operator_name = (getattr(current_user, 'full_name', None) or 
                           getattr(current_user, 'username', None) or 
                           f"ID:{getattr(current_user, 'id', '系统')}")
            
            status_history_data = {
                'task_id': str(task_id),
                'status_change': '任务取消',
                'operator': operator_name,
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'note': f'取消原因：{cancel_reason}',
                'next_handler_role': None
            }
            
            # 调用服务层记录状态历史
            DispatchService.add_status_history(status_history_data)
            
            return {
                'task_id': task_id,
                'status': '已取消',
                'message': '派车任务取消成功'
            }
            
        except Exception as e:
            return WorkshopDispatchBusiness._error(f'取消派车任务失败：{str(e)}')
    
    @staticmethod
    def merge_vehicles(source_vehicle_id, target_vehicle_id):
        """
        合并车辆记录
        
        Args:
            source_vehicle_id: 源车辆ID
            target_vehicle_id: 目标车辆ID
        """
        # 调用服务层合并车辆
        try:
            result = DispatchService.merge_vehicles(source_vehicle_id, target_vehicle_id)
            return result
        except Exception as e:
            raise ValueError(f'合并车辆失败：{str(e)}')