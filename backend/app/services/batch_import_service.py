# -*- coding: utf-8 -*-
"""
批量导入服务
提供车辆数据的批量导入功能（导入到车辆容积参考表 vehicle_capacity_reference）
"""

import json
from datetime import datetime
from typing import Dict, List, Any, Optional
from sqlalchemy.exc import SQLAlchemyError
from app.extensions import db
# from app.models.vehicle.vehicle import Vehicle  # 旧：导入到派车 vehicles 表
from app.models.vehicle.vehicle_capacity_reference import VehicleCapacityReference
from .vehicle.vehicle_business_service import VehicleBusinessService  # 仍可能用于其他校验保留导入，但本模块不再依赖其分类
from app.services.vehicle.vehicle_capacity_reference_service import VehicleCapacityReferenceService


class BatchImportService:
    """批量导入服务类（导入到 vehicle_capacity_reference）"""
    
    @staticmethod
    def import_vehicles(validation_results: List[Dict[str, Any]], 
                       user_id: Optional[int] = None,
                       batch_size: int = 100) -> Dict[str, Any]:
        """
        批量导入车辆基础资料（车辆容积参考）
        
        Args:
            validation_results: 验证结果列表（来自 ExcelProcessingService.validate_and_process_data 返回值中的 validation_results）
            user_id: 操作用户ID
            batch_size: 批处理大小
            
        Returns:
            Dict[str, Any]: 导入结果
        """
        success_count = 0
        error_count = 0
        errors = []
        created_vehicles = []
        
        # 筛选出有效的数据
        valid_results = [result for result in validation_results if result['valid']]
        
        if not valid_results:
            return {
                'success': False,
                'message': '没有有效的数据可以导入',
                'success_count': 0,
                'error_count': len(validation_results),
                'errors': ['所有数据都包含验证错误'],
                'created_vehicles': []
            }
        
        try:
            # 分批处理数据
            for i in range(0, len(valid_results), batch_size):
                batch = valid_results[i:i + batch_size]
                batch_result = BatchImportService._process_batch(
                    batch, user_id, success_count + 1
                )
                
                success_count += batch_result['success_count']
                error_count += batch_result['error_count']
                errors.extend(batch_result['errors'])
                created_vehicles.extend(batch_result['created_vehicles'])
            
            # 提交事务
            db.session.commit()
            
            return {
                'success': success_count > 0,
                'message': (f'导入完成，成功{success_count}条，失败{error_count}条' if success_count > 0 else f'导入失败，成功{success_count}条，失败{error_count}条'),
                'success_count': success_count,
                'error_count': error_count,
                'errors': errors,
                'created_vehicles': created_vehicles
            }
            
        except Exception as e:
            # 回滚事务
            db.session.rollback()
            return {
                'success': False,
                'message': f'批量导入失败：{str(e)}',
                'success_count': 0,
                'error_count': len(valid_results),
                'errors': [f'系统错误：{str(e)}'],
                'created_vehicles': []
            }
    
    @staticmethod
    def _build_dedup_filter(data: Dict[str, Any]):
        """
        构建去重查询条件：
        优先使用(license_plate, carriage_number)组合；
        若仅有其一，则用单列去重；
        若两者皆无，则返回None，由上层判定无效。
        """
        license_plate = (data.get('license_plate') or '').strip()
        carriage_number = (data.get('carriage_number') or '').strip()
        if license_plate and carriage_number:
            return (VehicleCapacityReference.license_plate == license_plate, 
                    VehicleCapacityReference.carriage_number == carriage_number)
        if license_plate:
            return (VehicleCapacityReference.license_plate == license_plate,)
        if carriage_number:
            return (VehicleCapacityReference.carriage_number == carriage_number,)
        return None

    @staticmethod
    def _process_batch(batch_results: List[Dict[str, Any]], 
                      user_id: Optional[int],
                      start_index: int) -> Dict[str, Any]:
        """
        处理一批数据（导入到 vehicle_capacity_reference）
        
        Args:
            batch_results: 批次验证结果
            user_id: 操作用户ID
            start_index: 起始索引
            
        Returns:
            Dict[str, Any]: 批次处理结果
        """
        success_count = 0
        error_count = 0
        errors = []
        created_vehicles = []
        
        for result in batch_results:
            try:
                # 获取处理后的数据
                data = result['processed_data'].copy()
                
                # 映射为 VehicleCapacityReference 模型需要的数据
                vcr_data = BatchImportService._prepare_vehicle_data(data)

                # 基础字段校验（车牌或车厢至少一个、体积/载重为正数等，但不验证车型必填因为会自动推断）
                validation_errors = VehicleCapacityReferenceService._validate_vehicle_data(vcr_data, is_update=True)
                if validation_errors:
                    error_count += 1
                    errors.append(f"第{result['row']}行：{'; '.join(validation_errors)}")
                    continue
                
                # 去重校验
                conds = BatchImportService._build_dedup_filter(vcr_data)
                if not conds:
                    error_count += 1
                    errors.append(f"第{result['row']}行：车牌号与车厢号不能同时为空")
                    continue
                existing_q = VehicleCapacityReference.query
                for c in conds:
                    existing_q = existing_q.filter(c)
                existing = existing_q.first()
                if existing:
                    # 已存在则跳过（不计为失败，便于幂等）
                    created_vehicles.append({
                        'row': result['row'],
                        'id': existing.id,
                        'license_plate': existing.license_plate,
                        'carriage_number': existing.carriage_number,
                        'vehicle_category': existing.vehicle_category,
                        'duplicate': True
                    })
                    continue
                
                # 自动设置车辆分类
                vcr_data['vehicle_category'] = VehicleCapacityReferenceService._auto_set_category(
                    vcr_data.get('carriage_number', '') or ''
                )
                
                # 创建记录
                vehicle = VehicleCapacityReference(**vcr_data)
                db.session.add(vehicle)
                db.session.flush()  # 刷新获取ID
                
                success_count += 1
                created_vehicles.append({
                    'row': result['row'],
                    'id': vehicle.id,
                    'license_plate': vehicle.license_plate,
                    'carriage_number': vehicle.carriage_number,
                    'vehicle_category': vehicle.vehicle_category
                })
                
            except SQLAlchemyError as e:
                error_count += 1
                errors.append(f"第{result['row']}行数据库错误：{str(e)}")
                
            except Exception as e:
                error_count += 1
                errors.append(f"第{result['row']}行处理失败：{str(e)}")
        
        return {
            'success_count': success_count,
            'error_count': error_count,
            'errors': errors,
            'created_vehicles': created_vehicles
        }
    
    @staticmethod
    def _prepare_vehicle_data(data: Dict[str, Any]) -> Dict[str, Any]:
        """
        准备车辆基础数据（VehicleCapacityReference），移除不属于该模型的字段
        
        Args:
            data: 原始数据
            
        Returns:
            Dict[str, Any]: 清理后的车辆数据
        """
        # VehicleCapacityReference 模型的有效字段
        valid_fields = {
            'vehicle_type', 'standard_volume', 'license_plate', 'carriage_number',
            'vehicle_category', 'frequent_companies', 'status', 'original_capacity', 'suppliers'
        }
        
        # 过滤有效字段
        vehicle_data = {k: v for k, v in data.items() if k in valid_fields}
        
        # 设置默认值（状态默认为 active）
        if 'status' not in vehicle_data or not vehicle_data['status']:
            vehicle_data['status'] = 'active'
        
        # 确保 frequent_companies 是JSON字符串格式
        if 'frequent_companies' in vehicle_data:
            if isinstance(vehicle_data['frequent_companies'], str):
                try:
                    json.loads(vehicle_data['frequent_companies'])
                except json.JSONDecodeError:
                    vehicle_data['frequent_companies'] = '[]'
            elif isinstance(vehicle_data['frequent_companies'], list):
                vehicle_data['frequent_companies'] = json.dumps(vehicle_data['frequent_companies'], ensure_ascii=False)
            else:
                vehicle_data['frequent_companies'] = '[]'
        else:
            vehicle_data['frequent_companies'] = '[]'
        
        # 数值字段规范化
        for field in ['standard_volume', 'original_capacity']:
            if field in vehicle_data and vehicle_data[field] not in (None, ''):
                try:
                    vehicle_data[field] = float(vehicle_data[field])
                except (TypeError, ValueError):
                    vehicle_data[field] = None
            else:
                vehicle_data[field] = None if vehicle_data.get(field) in (None, '') else vehicle_data.get(field)
        
        # 基于标准容积自动补充车型与原始载重量（仅当未提供时）
        std_vol = vehicle_data.get('standard_volume')
        if std_vol is not None:
            infer = VehicleCapacityReferenceService.infer_type_and_capacity(std_vol)
            if infer:
                inferred_type, inferred_capacity = infer
                if not vehicle_data.get('vehicle_type'):
                    vehicle_data['vehicle_type'] = inferred_type
                if not vehicle_data.get('original_capacity'):
                    vehicle_data['original_capacity'] = inferred_capacity
        
        # 规范化供应商分类（供应商、内部单位、外包驾驶管理公司）
        if 'suppliers' in vehicle_data and vehicle_data['suppliers'] is not None:
            vehicle_data['suppliers'] = VehicleCapacityReferenceService.normalize_supplier_category(vehicle_data['suppliers'])
        
        # 去除前后空白
        for k in ['license_plate', 'carriage_number', 'vehicle_type', 'suppliers', 'status']:
            if k in vehicle_data and isinstance(vehicle_data[k], str):
                vehicle_data[k] = vehicle_data[k].strip()
        
        return vehicle_data
    
    @staticmethod
    def validate_import_permission(user_id: Optional[int]) -> Dict[str, Any]:
        """
        验证用户是否有导入权限
        
        Args:
            user_id: 用户ID
            
        Returns:
            Dict[str, Any]: 权限验证结果
        """
        # TODO: 实现具体的权限验证逻辑
        if user_id is None:
            return {
                'valid': False,
                'message': '用户未登录，无法执行导入操作'
            }
        
        # 暂时允许所有登录用户导入
        return {
            'valid': True,
            'message': '权限验证通过'
        }
    
    @staticmethod
    def get_import_statistics(created_vehicles: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        获取导入统计信息
        
        Args:
            created_vehicles: 创建的车辆列表
            
        Returns:
            Dict[str, Any]: 统计信息
        """
        if not created_vehicles:
            return {
                'total_count': 0,
                'category_stats': {},
                'type_stats': {}
            }
        
        # 按车辆分类统计
        category_stats = {}
        for vehicle in created_vehicles:
            category = vehicle.get('vehicle_category', '未知')
            category_stats[category] = category_stats.get(category, 0) + 1
        
        return {
            'total_count': len(created_vehicles),
            'category_stats': category_stats,
            'import_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
    
    @staticmethod
    def create_import_log(import_result: Dict[str, Any], 
                         user_id: Optional[int] = None,
                         filename: str = '') -> Dict[str, Any]:
        """
        创建导入日志记录
        
        Args:
            import_result: 导入结果
            user_id: 操作用户ID
            filename: 导入文件名
            
        Returns:
            Dict[str, Any]: 日志记录信息
        """
        log_data = {
            'operation_type': 'batch_import_vehicle_capacity_reference',
            'user_id': user_id,
            'filename': filename,
            'success': import_result['success'],
            'success_count': import_result['success_count'],
            'error_count': import_result['error_count'],
            'total_count': import_result['success_count'] + import_result['error_count'],
            'errors': import_result['errors'][:10],  # 只记录前10个错误
            'import_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        # TODO: 将日志保存到数据库或日志文件
        return log_data
    
    @staticmethod
    def rollback_import(vehicle_ids: List[int], user_id: Optional[int] = None) -> Dict[str, Any]:
        """
        回滚导入操作（删除指定的车辆容积参考记录）
        
        Args:
            vehicle_ids: 要删除的车辆ID列表
            user_id: 操作用户ID
            
        Returns:
            Dict[str, Any]: 回滚结果
        """
        try:
            deleted_count = 0
            
            for vehicle_id in vehicle_ids:
                vehicle = VehicleCapacityReference.query.get(vehicle_id)
                if vehicle:
                    db.session.delete(vehicle)
                    deleted_count += 1
            
            db.session.commit()
            
            return {
                'success': True,
                'message': f'成功回滚{deleted_count}条记录',
                'deleted_count': deleted_count
            }
            
        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'message': f'回滚失败：{str(e)}',
                'deleted_count': 0
            }