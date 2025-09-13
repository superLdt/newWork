# -*- coding: utf-8 -*-
"""
车辆数据验证服务
提供车辆数据的各种验证功能
"""

import re
import json
from typing import Dict, List, Any


class VehicleValidationService:
    """车辆数据验证服务类"""
    
    @staticmethod
    def validate_vehicle_data(data: Dict[str, Any]) -> List[str]:
        """
        验证车辆数据的完整性和正确性
        
        Args:
            data: 车辆数据字典
            
        Returns:
            List[str]: 错误信息列表，空列表表示验证通过
        """
        errors = []
        
        # 验证车牌号或车厢号至少有一个
        license_plate = data.get('license_plate', '').strip()
        carriage_number = data.get('carriage_number', '').strip()
        
        if not license_plate and not carriage_number:
            errors.append('车牌号或车厢号至少需要填写一个')
        
        # 验证容积
        actual_volume = data.get('actual_volume')
        if not actual_volume or actual_volume <= 0:
            errors.append('容积必须大于0')
        
        # 验证车厢号格式（如果填写了车厢号且包含"挂"字）
        if carriage_number and '挂' in carriage_number:
            if not VehicleValidationService.validate_carriage_number_format(carriage_number):
                errors.append('车厢号格式不正确，应为：车牌号+挂，如：皖A36T3挂')
        
        # 验证车牌号格式（如果填写了车牌号）
        if license_plate:
            if not VehicleValidationService.validate_license_plate_format(license_plate):
                errors.append('车牌号格式不正确，请输入正确的车牌号格式')
        
        # 验证车辆类型
        vehicle_type = data.get('vehicle_type')
        if vehicle_type and not VehicleValidationService.validate_vehicle_type(vehicle_type):
            errors.append('车辆类型不在允许的范围内')
        
        return errors
    
    @staticmethod
    def validate_license_plate_format(license_plate: str) -> bool:
        """
        验证车牌号格式
        
        Args:
            license_plate: 车牌号
            
        Returns:
            bool: 格式是否正确
        """
        if not license_plate:
            return False
        
        # 中国车牌号格式：省份简称 + 字母 + 数字字母组合
        # 例如：皖A12345、京B123AB、沪C12345D等
        pattern = r'^[\u4e00-\u9fa5][A-Z][0-9A-Z]{4,6}$'
        return bool(re.match(pattern, license_plate.strip()))
    
    @staticmethod
    def validate_carriage_number_format(carriage_number: str) -> bool:
        """
        验证车厢号格式（挂车）
        
        Args:
            carriage_number: 车厢号
            
        Returns:
            bool: 格式是否正确
        """
        if not carriage_number:
            return False
        
        # 挂车车厢号格式：车牌号 + "挂"
        # 例如：皖A36T3挂
        pattern = r'^[\u4e00-\u9fa5][A-Z][0-9A-Z]+挂$'
        return bool(re.match(pattern, carriage_number.strip()))
    
    @staticmethod
    def validate_vehicle_type(vehicle_type: str) -> bool:
        """
        验证车辆类型是否在允许范围内
        
        Args:
            vehicle_type: 车辆类型
            
        Returns:
            bool: 是否为有效的车辆类型
        """
        allowed_types = ['5吨', '8吨', '12吨', '20吨', '30吨', '40吨A', '40吨B']
        return vehicle_type in allowed_types
    
    @staticmethod
    def auto_set_category(data: Dict[str, Any]) -> Dict[str, Any]:
        """
        根据车厢号自动设置车辆分类
        
        Args:
            data: 车辆数据字典
            
        Returns:
            Dict[str, Any]: 更新后的车辆数据
        """
        carriage_number = data.get('carriage_number', '')
        if carriage_number and '挂' in carriage_number:
            data['vehicle_category'] = '挂车'
        else:
            data['vehicle_category'] = '单车'
        
        return data
    
    @staticmethod
    def validate_frequent_companies(companies_data: Any) -> List[str]:
        """
        验证常用公司数据格式
        
        Args:
            companies_data: 常用公司数据（可能是字符串、列表或其他格式）
            
        Returns:
            List[str]: 错误信息列表
        """
        errors = []
        
        if companies_data is None:
            return errors
        
        # 如果是字符串，尝试解析为JSON
        if isinstance(companies_data, str):
            try:
                companies_list = json.loads(companies_data)
                if not isinstance(companies_list, list):
                    errors.append('常用公司数据格式错误，应为数组格式')
            except json.JSONDecodeError:
                # 可能是逗号分隔的字符串
                if ',' in companies_data:
                    companies_list = [c.strip() for c in companies_data.split(',') if c.strip()]
                else:
                    errors.append('常用公司数据格式错误')
        elif isinstance(companies_data, list):
            companies_list = companies_data
        else:
            errors.append('常用公司数据类型错误')
        
        # 验证公司名称长度
        if 'companies_list' in locals():
            for company in companies_list:
                if not isinstance(company, str):
                    errors.append('公司名称必须为字符串')
                    break
                if len(company.strip()) == 0:
                    errors.append('公司名称不能为空')
                    break
                if len(company.strip()) > 100:
                    errors.append('公司名称长度不能超过100个字符')
                    break
        
        return errors
    
    @staticmethod
    def normalize_frequent_companies(companies_data: Any) -> str:
        """
        标准化常用公司数据为JSON字符串格式
        
        Args:
            companies_data: 常用公司数据
            
        Returns:
            str: JSON格式的公司列表字符串
        """
        if companies_data is None:
            return '[]'
        
        companies_list = []
        
        if isinstance(companies_data, str):
            try:
                # 尝试解析JSON
                companies_list = json.loads(companies_data)
                if not isinstance(companies_list, list):
                    companies_list = []
            except json.JSONDecodeError:
                # 按逗号分割
                if companies_data.strip():
                    companies_list = [c.strip() for c in companies_data.split(',') if c.strip()]
        elif isinstance(companies_data, list):
            companies_list = [str(c).strip() for c in companies_data if str(c).strip()]
        
        # 去重并保持顺序
        unique_companies = []
        for company in companies_list:
            if company not in unique_companies:
                unique_companies.append(company)
        
        return json.dumps(unique_companies, ensure_ascii=False)
    
    @staticmethod
    def validate_batch_data(records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        批量验证车辆数据
        
        Args:
            records: 车辆数据记录列表
            
        Returns:
            List[Dict[str, Any]]: 验证结果列表，每个元素包含原始数据、错误信息和验证状态
        """
        validation_results = []
        
        for index, record in enumerate(records, 1):
            # 数据验证
            data_errors = VehicleValidationService.validate_vehicle_data(record)
            
            # 常用公司验证
            companies_errors = VehicleValidationService.validate_frequent_companies(
                record.get('frequent_companies')
            )
            
            all_errors = data_errors + companies_errors
            
            # 自动设置车辆分类
            processed_record = VehicleValidationService.auto_set_category(record.copy())
            
            # 标准化常用公司数据
            processed_record['frequent_companies'] = VehicleValidationService.normalize_frequent_companies(
                processed_record.get('frequent_companies')
            )
            
            validation_results.append({
                'row': index,
                'original_data': record,
                'processed_data': processed_record,
                'errors': all_errors,
                'valid': len(all_errors) == 0
            })
        
        return validation_results
    
    @staticmethod
    def get_validation_summary(validation_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        获取验证结果摘要
        
        Args:
            validation_results: 验证结果列表
            
        Returns:
            Dict[str, Any]: 验证摘要信息
        """
        total_count = len(validation_results)
        valid_count = sum(1 for result in validation_results if result['valid'])
        invalid_count = total_count - valid_count
        
        # 统计错误类型
        error_types = {}
        for result in validation_results:
            if not result['valid']:
                for error in result['errors']:
                    error_types[error] = error_types.get(error, 0) + 1
        
        return {
            'total_count': total_count,
            'valid_count': valid_count,
            'invalid_count': invalid_count,
            'valid_rate': round(valid_count / total_count * 100, 2) if total_count > 0 else 0,
            'error_types': error_types
        }