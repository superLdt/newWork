# -*- coding: utf-8 -*-
"""
批量导入服务
提供车辆数据的批量导入功能
"""

import json
from datetime import datetime
from typing import Dict, List, Any, Optional
from sqlalchemy.exc import SQLAlchemyError
from app.extensions import db
from app.models.vehicle.vehicle import Vehicle
from .vehicle_validation_service import VehicleValidationService
from .vehicle.vehicle_business_service import VehicleBusinessService


class BatchImportService:
    """批量导入服务类"""
    
    @staticmethod
    def import_vehicles(validation_results: List[Dict[str, Any]], 
                       user_id: Optional[int] = None,
                       batch_size: int = 100) -> Dict[str, Any]:
        """
        批量导入车辆数据
        
        Args:
            validation_results: 验证结果列表
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
                'success': True,
                'message': f'导入完成，成功{success_count}条，失败{error_count}条',
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
    def _process_batch(batch_results: List[Dict[str, Any]], 
                      user_id: Optional[int],
                      start_index: int) -> Dict[str, Any]:
        """
        处理一批数据
        
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
                
                # 移除不属于Vehicle模型的字段
                vehicle_data = BatchImportService._prepare_vehicle_data(data)
                
                # 创建车辆实例
                vehicle = Vehicle(**vehicle_data)
                
                # 设置车辆分类和验证数据（使用业务服务层）
                try:
                    VehicleBusinessService.set_vehicle_category(vehicle)
                    VehicleBusinessService.validate_vehicle_data(vehicle)
                except ValueError as e:
                    error_count += 1
                    errors.append(f"第{result['row']}行：{str(e)}")
                    continue
                
                # 添加到数据库会话
                db.session.add(vehicle)
                
                # 刷新以获取ID（但不提交）
                db.session.flush()
                
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
        准备车辆数据，移除不属于Vehicle模型的字段
        
        Args:
            data: 原始数据
            
        Returns:
            Dict[str, Any]: 清理后的车辆数据
        """
        # Vehicle模型的有效字段
        valid_fields = {
            'license_plate', 'carriage_number', 'actual_volume', 'vehicle_type',
            'vehicle_category', 'frequent_companies', 'notes', 'supplier_type',
            'status', 'manifest_number', 'dispatch_number', 'required_volume',
            'confirmed_volume', 'supplier_id', 'original_capacity'
        }
        
        # 过滤有效字段
        vehicle_data = {k: v for k, v in data.items() if k in valid_fields}
        
        # 设置默认值
        if 'status' not in vehicle_data or not vehicle_data['status']:
            vehicle_data['status'] = '待确认'
        
        # 确保frequent_companies是JSON字符串格式
        if 'frequent_companies' in vehicle_data:
            if isinstance(vehicle_data['frequent_companies'], str):
                # 如果已经是字符串，检查是否为有效JSON
                try:
                    json.loads(vehicle_data['frequent_companies'])
                except json.JSONDecodeError:
                    # 不是有效JSON，按逗号分割处理
                    companies = [c.strip() for c in vehicle_data['frequent_companies'].split(',') if c.strip()]
                    vehicle_data['frequent_companies'] = json.dumps(companies, ensure_ascii=False)
            elif isinstance(vehicle_data['frequent_companies'], list):
                vehicle_data['frequent_companies'] = json.dumps(vehicle_data['frequent_companies'], ensure_ascii=False)
            else:
                vehicle_data['frequent_companies'] = '[]'
        else:
            vehicle_data['frequent_companies'] = '[]'
        
        # 处理数值字段
        numeric_fields = ['actual_volume', 'required_volume', 'confirmed_volume', 'original_capacity']
        for field in numeric_fields:
            if field in vehicle_data and vehicle_data[field] is not None:
                try:
                    vehicle_data[field] = float(vehicle_data[field])
                except (ValueError, TypeError):
                    if field == 'actual_volume':  # 必填字段
                        raise ValueError(f'{field}字段必须为有效数值')
                    else:
                        vehicle_data[field] = None
        
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
        # 这里可以根据用户角色和权限系统进行验证
        
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
            'operation_type': 'batch_import_vehicles',
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
        # 这里可以集成到现有的操作日志系统中
        
        return log_data
    
    @staticmethod
    def rollback_import(vehicle_ids: List[int], user_id: Optional[int] = None) -> Dict[str, Any]:
        """
        回滚导入操作（删除指定的车辆记录）
        
        Args:
            vehicle_ids: 要删除的车辆ID列表
            user_id: 操作用户ID
            
        Returns:
            Dict[str, Any]: 回滚结果
        """
        try:
            deleted_count = 0
            
            for vehicle_id in vehicle_ids:
                vehicle = Vehicle.query.get(vehicle_id)
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