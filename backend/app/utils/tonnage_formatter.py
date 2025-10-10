"""
吨位格式处理工具类
用于处理标准吨位字段格式，去掉类似'40吨A吨'格式中的最后一个'吨'字
"""
import re
from typing import Optional


class TonnageFormatter:
    """吨位格式处理器"""
    
    @staticmethod
    def format_tonnage(tonnage: str) -> str:
        """
        格式化吨位字符串，去掉重复的'吨'字
        
        Args:
            tonnage: 原始吨位字符串，如'40吨A吨'、'5吨吨'等
            
        Returns:
            str: 格式化后的吨位字符串，如'40吨A'、'5吨'等
            
        Examples:
            >>> TonnageFormatter.format_tonnage('40吨A吨')
            '40吨A'
            >>> TonnageFormatter.format_tonnage('5吨吨')
            '5吨'
            >>> TonnageFormatter.format_tonnage('40吨A')
            '40吨A'
        """
        if not tonnage or not isinstance(tonnage, str):
            return tonnage
        
        # 去除首尾空格
        tonnage = tonnage.strip()
        
        # 处理'数字吨字母吨'格式，如'40吨A吨' -> '40吨A'
        pattern1 = r'^(\d+吨[A-Z])吨$'
        match1 = re.match(pattern1, tonnage)
        if match1:
            return match1.group(1)
        
        # 处理'数字吨吨'格式，如'5吨吨' -> '5吨'
        pattern2 = r'^(\d+)吨吨$'
        match2 = re.match(pattern2, tonnage)
        if match2:
            return f"{match2.group(1)}吨"
        
        # 处理多个连续'吨'字的情况
        tonnage = re.sub(r'吨+', '吨', tonnage)
        
        return tonnage
    
    @staticmethod
    def validate_tonnage_format(tonnage: str) -> bool:
        """
        验证吨位格式是否正确
        
        Args:
            tonnage: 吨位字符串
            
        Returns:
            bool: 格式是否正确
        """
        if not tonnage or not isinstance(tonnage, str):
            return False
        
        # 标准格式：数字+吨+可选字母
        pattern = r'^\d+吨[A-Z]?$'
        return bool(re.match(pattern, tonnage.strip()))
    
    @staticmethod
    def extract_tonnage_number(tonnage: str) -> Optional[int]:
        """
        从吨位字符串中提取数字部分
        
        Args:
            tonnage: 吨位字符串，如'40吨A'
            
        Returns:
            Optional[int]: 吨位数字，如40，如果提取失败返回None
        """
        if not tonnage or not isinstance(tonnage, str):
            return None
        
        match = re.match(r'^(\d+)吨', tonnage.strip())
        if match:
            try:
                return int(match.group(1))
            except ValueError:
                return None
        return None
    
    @staticmethod
    def extract_tonnage_grade(tonnage: str) -> Optional[str]:
        """
        从吨位字符串中提取档位字母
        
        Args:
            tonnage: 吨位字符串，如'40吨A'
            
        Returns:
            Optional[str]: 档位字母，如'A'，如果没有档位返回None
        """
        if not tonnage or not isinstance(tonnage, str):
            return None
        
        match = re.match(r'^\d+吨([A-Z])$', tonnage.strip())
        if match:
            return match.group(1)
        return None
    
    @staticmethod
    def normalize_tonnage_list(tonnage_list: list) -> list:
        """
        批量格式化吨位列表
        
        Args:
            tonnage_list: 吨位字符串列表
            
        Returns:
            list: 格式化后的吨位列表
        """
        if not tonnage_list:
            return []
        
        return [TonnageFormatter.format_tonnage(tonnage) for tonnage in tonnage_list if tonnage]
    
    @staticmethod
    def get_standard_tonnage_options():
        """
        获取标准吨位选项列表
        
        Returns:
            list: 标准吨位选项
        """
        return ['5吨', '8吨', '12吨', '20吨', '30吨', '40吨A', '40吨B']
    
    @staticmethod
    def is_valid_standard_tonnage(tonnage: str) -> bool:
        """
        检查是否为有效的标准吨位
        
        Args:
            tonnage: 吨位字符串
            
        Returns:
            bool: 是否为标准吨位
        """
        formatted_tonnage = TonnageFormatter.format_tonnage(tonnage)
        return formatted_tonnage in TonnageFormatter.get_standard_tonnage_options()