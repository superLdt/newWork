from datetime import datetime
import json
import logging
from typing import Dict, List, Optional, Tuple, Any
from sqlalchemy.exc import SQLAlchemyError
from app.models.vehicle.vehicle_capacity_reference import VehicleCapacityReference
from app.extensions import db

logger = logging.getLogger(__name__)


class VehicleCapacityReferenceService:
    """
    车辆容积参考服务类
    处理车辆日常管理相关的业务逻辑
    """
    
    @staticmethod
    def get_vehicle_list(page: int = 1, per_page: int = 10, query: str = '') -> Tuple[List[Dict], int]:
        """
        获取车辆容积参考列表
        
        Args:
            page: 页码
            per_page: 每页数量
            query: 搜索关键词
            
        Returns:
            Tuple[List[Dict], int]: 车辆列表和总数
        """
        try:
            # 构建查询
            query_obj = VehicleCapacityReference.query
            
            # 添加搜索条件
            if query:
                query_obj = query_obj.filter(
                    db.or_(
                        VehicleCapacityReference.license_plate.like(f'%{query}%'),
                        VehicleCapacityReference.carriage_number.like(f'%{query}%'),
                        VehicleCapacityReference.vehicle_type.like(f'%{query}%')
                    )
                )
            
            # 分页查询
            pagination = query_obj.paginate(
                page=page,
                per_page=per_page,
                error_out=False
            )
            
            # 转换为字典格式
            vehicles = [vehicle.to_dict() for vehicle in pagination.items]
            
            return vehicles, pagination.total
        except SQLAlchemyError as e:
            logger.error(f"获取车辆列表失败: {str(e)}")
            raise
    
    @staticmethod
    def get_vehicle_by_id(vehicle_id: int) -> Optional[Dict]:
        """
        根据ID获取车辆详情
        
        Args:
            vehicle_id: 车辆ID
            
        Returns:
            Optional[Dict]: 车辆详情或None
        """
        try:
            vehicle = VehicleCapacityReference.query.get(vehicle_id)
            return vehicle.to_dict() if vehicle else None
        except SQLAlchemyError as e:
            logger.error(f"获取车辆详情失败: {str(e)}")
            raise
    
    @staticmethod
    def infer_type_and_capacity(standard_volume: Optional[float]) -> Optional[Tuple[str, float]]:
        """
        根据标准容积自动推断车型与原始载重量（吨）
        规则：
        - >=180 → 40吨B（40）
        - >=150 → 40吨A（40）
        - >=130 → 30吨（30）
        - >=100 → 20吨（20）
        - >=55  → 12吨（12）
        - >=45  → 8吨（8）
        - >=35  → 5吨（5）
        其余返回None
        """
        if standard_volume is None:
            return None
        try:
            v = float(standard_volume)
        except (TypeError, ValueError):
            return None
        # 从高到低匹配
        if v >= 180:
            return '40吨B', 40.0
        if v >= 150:
            return '40吨A', 40.0
        if v >= 130:
            return '30吨', 30.0
        if v >= 100:
            return '20吨', 20.0
        if v >= 55:
            return '12吨', 12.0
        if v >= 45:
            return '8吨', 8.0
        if v >= 35:
            return '5吨', 5.0
        return None

    @staticmethod
    def normalize_supplier_category(raw: Any) -> str:
        """
        规范化供应商分类为以下三种之一：
        - 供应商
        - 内部单位
        - 外包驾驶管理公司
        若无法识别，则返回原始去空白后的字符串；为空返回空串。
        特殊约定：当值为结构化命名（例如以“内部-”开头，如“内部-华东事业群”）时，保留原值不降级为通用分类。
        """
        def _norm_str(s: str) -> str:
            s = (s or '').strip()
            if not s:
                return ''
            # 对结构化命名保留原值（如：内部-华东事业群、内部-XX中心）
            if s.startswith('内部-') or s.startswith('内部－') or s.startswith('内部—'):
                return s
            # 关键字匹配（中文环境）
            if any(k in s for k in ['外包', '驾驶', '管理公司']):
                return '外包驾驶管理公司'
            if '内部' in s:
                return '内部单位'
            if '供应' in s or s == '供应商':
                return '供应商'
            return s
        if raw is None:
            return ''
        if isinstance(raw, list):
            # 若为列表，取第一个有效项
            for item in raw:
                if isinstance(item, str) and item.strip():
                    return _norm_str(item)
            return ''
        if isinstance(raw, str):
            # 可能是JSON串
            text = raw.strip()
            if text.startswith('[') and text.endswith(']'):
                try:
                    arr = json.loads(text)
                    return VehicleCapacityReferenceService.normalize_supplier_category(arr)
                except Exception:
                    return ''
            return _norm_str(text)
        # 其他类型转字符串处理
        return _norm_str(str(raw))

    @staticmethod
    def create_vehicle(vehicle_data: Dict[str, Any]) -> Dict:
        """
        创建车辆容积参考
        
        Args:
            vehicle_data: 车辆数据
            
        Returns:
            Dict: 创建的车辆信息
        """
        try:
            # 基于标准容积自动推断车型与原始载重（若未提供）
            std_vol = vehicle_data.get('standard_volume')
            infer = VehicleCapacityReferenceService.infer_type_and_capacity(std_vol)
            if infer:
                inferred_type, inferred_cap = infer
                if not vehicle_data.get('vehicle_type'):
                    vehicle_data['vehicle_type'] = inferred_type
                if not vehicle_data.get('original_capacity'):
                    vehicle_data['original_capacity'] = inferred_cap

            # 规范化供应商分类
            if 'suppliers' in vehicle_data:
                vehicle_data['suppliers'] = VehicleCapacityReferenceService.normalize_supplier_category(
                    vehicle_data.get('suppliers')
                )

            # 验证数据
            errors = VehicleCapacityReferenceService._validate_vehicle_data(vehicle_data)
            if errors:
                raise ValueError(f"数据验证失败: {', '.join(errors)}")
            
            # 处理常用公司列表
            frequent_companies = vehicle_data.get('frequent_companies', [])
            if isinstance(frequent_companies, list):
                frequent_companies_json = json.dumps(frequent_companies, ensure_ascii=False)
            else:
                frequent_companies_json = '[]'
            
            # 自动设置车辆分类
            vehicle_category = VehicleCapacityReferenceService._auto_set_category(
                vehicle_data.get('carriage_number', '')
            )
            
            # 创建车辆对象
            vehicle = VehicleCapacityReference(
                vehicle_type=vehicle_data.get('vehicle_type'),
                standard_volume=vehicle_data.get('standard_volume'),
                license_plate=vehicle_data.get('license_plate'),
                carriage_number=vehicle_data.get('carriage_number'),
                vehicle_category=vehicle_category,
                frequent_companies=frequent_companies_json,
                status=vehicle_data.get('status', 'active'),
                original_capacity=vehicle_data.get('original_capacity'),
                suppliers=vehicle_data.get('suppliers', '')
            )
            
            db.session.add(vehicle)
            db.session.commit()
            
            logger.info(f"成功创建车辆容积参考: {vehicle.id}")
            return vehicle.to_dict()
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"创建车辆失败: {str(e)}")
            raise
    
    @staticmethod
    def update_vehicle(vehicle_id: int, update_data: Dict[str, Any]) -> Optional[Dict]:
        """
        更新车辆容积参考
        
        Args:
            vehicle_id: 车辆ID
            update_data: 更新数据
            
        Returns:
            Optional[Dict]: 更新后的车辆信息或None
        """
        try:
            vehicle = VehicleCapacityReference.query.get(vehicle_id)
            if not vehicle:
                return None

            # 基于标准容积自动推断（若未提供车型/原始载重且有标准容积）
            if 'standard_volume' in update_data:
                infer = VehicleCapacityReferenceService.infer_type_and_capacity(update_data.get('standard_volume'))
                if infer:
                    inferred_type, inferred_cap = infer
                    if not update_data.get('vehicle_type'):
                        update_data['vehicle_type'] = inferred_type
                    if not update_data.get('original_capacity'):
                        update_data['original_capacity'] = inferred_cap

            # 规范化供应商分类
            if 'suppliers' in update_data:
                update_data['suppliers'] = VehicleCapacityReferenceService.normalize_supplier_category(
                    update_data.get('suppliers')
                )
            
            # 验证数据
            errors = VehicleCapacityReferenceService._validate_vehicle_data(update_data, is_update=True)
            if errors:
                raise ValueError(f"数据验证失败: {', '.join(errors)}")
            
            # 更新字段
            for key, value in update_data.items():
                if key == 'frequent_companies':
                    # 处理常用公司列表
                    if isinstance(value, list):
                        setattr(vehicle, key, json.dumps(value, ensure_ascii=False))
                    else:
                        setattr(vehicle, key, '[]')
                elif key == 'carriage_number':
                    # 更新车厢号时自动设置车辆分类
                    setattr(vehicle, key, value)
                    vehicle.vehicle_category = VehicleCapacityReferenceService._auto_set_category(value or '')
                elif hasattr(vehicle, key):
                    setattr(vehicle, key, value)
            
            # 更新时间戳
            vehicle.updated_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            db.session.commit()
            
            logger.info(f"成功更新车辆容积参考: {vehicle_id}")
            return vehicle.to_dict()
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"更新车辆失败: {str(e)}")
            raise
    
    @staticmethod
    def delete_vehicle(vehicle_id: int) -> bool:
        """
        删除车辆容积参考
        
        Args:
            vehicle_id: 车辆ID
            
        Returns:
            bool: 是否删除成功
        """
        try:
            vehicle = VehicleCapacityReference.query.get(vehicle_id)
            if not vehicle:
                return False
            
            db.session.delete(vehicle)
            db.session.commit()
            
            logger.info(f"成功删除车辆容积参考: {vehicle_id}")
            return True
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"删除车辆失败: {str(e)}")
            raise
    
    @staticmethod
    def _validate_vehicle_data(vehicle_data: Dict[str, Any], is_update: bool = False) -> List[str]:
        """
        验证车辆数据
        
        Args:
            vehicle_data: 车辆数据
            is_update: 是否为更新操作
            
        Returns:
            List[str]: 错误信息列表
        """
        errors = []
        
        # 验证车牌号或车厢号
        license_plate = vehicle_data.get('license_plate')
        carriage_number = vehicle_data.get('carriage_number')
        
        if not is_update or 'license_plate' in vehicle_data or 'carriage_number' in vehicle_data:
            if not license_plate and not carriage_number:
                errors.append('车牌号或车厢号至少需要填写一个')
        
        # 验证车型（导入时跳过车型验证，因为会自动推断）
        vehicle_type = vehicle_data.get('vehicle_type')
        if not is_update:
            if not vehicle_type:
                errors.append('车型不能为空')
            elif vehicle_type not in VehicleCapacityReference.get_vehicle_type_choices():
                errors.append('车型选择无效')
        
        # 验证标准容积
        standard_volume = vehicle_data.get('standard_volume')
        if not is_update or 'standard_volume' in vehicle_data:
            if standard_volume is not None and standard_volume <= 0:
                errors.append('标准容积必须大于0')
        
        # 验证原始载重量
        original_capacity = vehicle_data.get('original_capacity')
        if original_capacity is not None and original_capacity <= 0:
            errors.append('原始载重量必须大于0')
        
        return errors
    
    @staticmethod
    def _auto_set_category(carriage_number: str) -> str:
        """
        根据车厢号自动设置车辆分类
        
        Args:
            carriage_number: 车厢号
            
        Returns:
            str: 车辆分类
        """
        if carriage_number and '挂' in carriage_number:
            return '挂车'
        return '单车'
    
    @staticmethod
    def get_available_vehicles() -> List[Dict]:
        """
        获取可用车辆列表
        
        Returns:
            List[Dict]: 可用车辆列表
        """
        try:
            vehicles = VehicleCapacityReference.query.filter_by(status='active').all()
            return [vehicle.to_dict() for vehicle in vehicles]
        except SQLAlchemyError as e:
            logger.error(f"获取可用车辆列表失败: {str(e)}")
            raise
    
    @staticmethod
    def search_vehicles(license_plate: str = None, carriage_number: str = None) -> List[Dict]:
        """
        搜索车辆
        
        Args:
            license_plate: 车牌号
            carriage_number: 车厢号
            
        Returns:
            List[Dict]: 搜索结果
        """
        try:
            query_obj = VehicleCapacityReference.query
            
            if license_plate:
                query_obj = query_obj.filter(
                    VehicleCapacityReference.license_plate.like(f'%{license_plate}%')
                )
            
            if carriage_number:
                query_obj = query_obj.filter(
                    VehicleCapacityReference.carriage_number.like(f'%{carriage_number}%')
                )
            
            vehicles = query_obj.all()
            return [vehicle.to_dict() for vehicle in vehicles]
        except SQLAlchemyError as e:
            logger.error(f"搜索车辆失败: {str(e)}")
            raise