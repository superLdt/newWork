"""
车辆业务服务层
处理所有与车辆相关的业务逻辑、验证规则和数据处理
"""
import json
import re
from datetime import datetime
from app.models.vehicle.vehicle import Vehicle
from app.extensions import db


class VehicleBusinessService:
    """车辆业务服务类"""
    
    @staticmethod
    def validate_vehicle_data(vehicle_data):
        """
        验证车辆数据完整性
        Args:
            vehicle_data: 车辆数据字典或Vehicle对象
        Returns:
            list: 错误信息列表
        """
        errors = []
        
        # 验证车牌号或车厢号
        license_plate = vehicle_data.get('license_plate') if isinstance(vehicle_data, dict) else vehicle_data.license_plate
        carriage_number = vehicle_data.get('carriage_number') if isinstance(vehicle_data, dict) else vehicle_data.carriage_number
        
        if not license_plate and not carriage_number:
            errors.append('车牌号或车厢号至少需要填写一个')
        
        # 验证容积
        actual_volume = vehicle_data.get('actual_volume') if isinstance(vehicle_data, dict) else vehicle_data.actual_volume
        if not actual_volume or actual_volume <= 0:
            errors.append('容积必须大于0')
        
        # 验证车厢号格式（如果是挂车）
        if carriage_number and '挂' in str(carriage_number):
            if not re.match(r'^[\u4e00-\u9fa5][A-Z][0-9A-Z]+挂$', str(carriage_number)):
                errors.append('车厢号格式不正确，应为：车牌号+挂，如：皖A36T3挂')
        
        return errors
    
    @staticmethod
    def set_vehicle_category(carriage_number):
        """
        根据车厢号自动设置车辆分类
        Args:
            carriage_number: 车厢号
        Returns:
            str: 车辆分类（单车/挂车）
        """
        if carriage_number and '挂' in str(carriage_number):
            return '挂车'
        else:
            return '单车'
    
    @staticmethod
    def process_frequent_companies(companies_list):
        """
        处理常用公司列表
        Args:
            companies_list: 公司列表（可以是字符串或列表）
        Returns:
            str: JSON格式的公司列表字符串
        """
        if isinstance(companies_list, str):
            try:
                # 如果是字符串，尝试解析为列表
                companies = json.loads(companies_list)
                if not isinstance(companies, list):
                    companies = [companies]
            except (json.JSONDecodeError, TypeError):
                # 如果解析失败，按逗号分割
                companies = [c.strip() for c in str(companies_list).split(',') if c.strip()]
        elif isinstance(companies_list, list):
            companies = companies_list
        else:
            companies = []
        
        return json.dumps(companies, ensure_ascii=False)
    
    @staticmethod
    def add_frequent_company_to_list(existing_companies, new_company):
        """
        向现有公司列表添加新公司
        Args:
            existing_companies: 现有公司列表（JSON字符串或列表）
            new_company: 新公司名
        Returns:
            str: 更新后的JSON格式公司列表
        """
        if isinstance(existing_companies, str):
            try:
                companies = json.loads(existing_companies or '[]')
            except (json.JSONDecodeError, TypeError):
                companies = []
        else:
            companies = existing_companies or []
        
        if not isinstance(companies, list):
            companies = []
        
        if new_company and new_company not in companies:
            companies.append(new_company)
        
        return json.dumps(companies, ensure_ascii=False)
    
    @staticmethod
    def get_frequent_companies_list(companies_json):
        """
        获取常用公司列表
        Args:
            companies_json: JSON格式的公司列表字符串
        Returns:
            list: 公司列表
        """
        try:
            return json.loads(companies_json or '[]')
        except (json.JSONDecodeError, TypeError):
            return []
    
    @staticmethod
    def prepare_vehicle_data(vehicle_data):
        """
        预处理车辆数据
        Args:
            vehicle_data: 原始车辆数据
        Returns:
            dict: 处理后的车辆数据
        """
        processed_data = dict(vehicle_data)
        
        # 自动设置车辆分类
        if 'carriage_number' in processed_data:
            processed_data['vehicle_category'] = VehicleBusinessService.set_vehicle_category(
                processed_data['carriage_number']
            )
        
        # 处理常用公司
        if 'frequent_companies' in processed_data:
            processed_data['frequent_companies'] = VehicleBusinessService.process_frequent_companies(
                processed_data['frequent_companies']
            )
        
        # 设置默认值
        if 'status' not in processed_data:
            processed_data['status'] = '待确认'
        
        if 'created_at' not in processed_data:
            processed_data['created_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        return processed_data
    
    @staticmethod
    def validate_and_prepare_vehicle(vehicle_data):
        """
        验证并准备车辆数据
        Args:
            vehicle_data: 车辆数据
        Returns:
            tuple: (is_valid, errors_or_data)
        """
        # 验证数据
        errors = VehicleBusinessService.validate_vehicle_data(vehicle_data)
        if errors:
            return False, errors
        
        # 准备数据
        processed_data = VehicleBusinessService.prepare_vehicle_data(vehicle_data)
        return True, processed_data
    
    @staticmethod
    def update_vehicle_frequent_companies(vehicle, new_company):
        """
        更新车辆的常用公司列表
        Args:
            vehicle: Vehicle对象
            new_company: 新公司名
        """
        vehicle.frequent_companies = VehicleBusinessService.add_frequent_company_to_list(
            vehicle.frequent_companies, new_company
        )
    
    @staticmethod
    def vehicle_to_dict(vehicle):
        """
        将Vehicle对象转换为字典格式
        Args:
            vehicle: Vehicle对象
        Returns:
            dict: 车辆数据的字典表示
        """
        if not vehicle:
            return None
            
        return {
            'id': vehicle.id,
            'plate_number': vehicle.plate_number,
            'vehicle_type': vehicle.vehicle_type,
            'owner_name': vehicle.owner_name,
            'owner_phone': vehicle.owner_phone,
            'owner_id_card': vehicle.owner_id_card,
            'vehicle_model': vehicle.vehicle_model,
            'vehicle_brand': vehicle.vehicle_brand,
            'vin_number': vehicle.vin_number,
            'engine_number': vehicle.engine_number,
            'registration_date': vehicle.registration_date,
            'carriage_number': vehicle.carriage_number,
            'vehicle_category': vehicle.vehicle_category,
            'annual_inspection_date': vehicle.annual_inspection_date,
            'insurance_expiry_date': vehicle.insurance_expiry_date,
            'frequent_companies': VehicleBusinessService.get_frequent_companies_list(vehicle.frequent_companies),
            'status': vehicle.status,
            'created_at': vehicle.created_at,
            'updated_at': vehicle.updated_at,
            'notes': vehicle.notes
        }