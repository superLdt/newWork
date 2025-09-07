#!/usr/bin/env python3
"""
服务层 - 公司服务
处理与公司相关的业务逻辑
"""

from ..extensions import db
from ..models.company import Company
from ..utils.exceptions import ValidationError, ResourceNotFoundError


class CompanyService:
    """
    公司服务类
    处理公司相关的业务逻辑
    """

    @staticmethod
    def get_company_by_id(company_id):
        """
        根据ID获取公司信息
        
        Args:
            company_id (int): 公司ID
            
        Returns:
            Company: 公司对象，不存在时返回None
        """
        return Company.query.get(company_id)

    @staticmethod
    def get_company_by_name(name):
        """
        根据名称获取公司信息
        
        Args:
            name (str): 公司名称
            
        Returns:
            Company: 公司对象，不存在时返回None
        """
        return Company.query.filter_by(name=name).first()

    @staticmethod
    def create_company(name, description=None, address=None, phone=None):
        """
        创建新公司
        
        Args:
            name (str): 公司名称
            description (str, optional): 公司描述
            address (str, optional): 公司地址
            phone (str, optional): 联系电话
            
        Returns:
            Company: 创建的公司对象
            
        Raises:
            ValidationError: 当公司名称已存在时
        """
        if not name or not name.strip():
            raise ValidationError("公司名称不能为空")
            
        # 检查公司名称是否已存在
        existing_company = Company.query.filter_by(name=name.strip()).first()
        if existing_company:
            raise ValidationError("公司名称已存在")
            
        company = Company(
            name=name.strip(),
            description=description,
            address=address,
            phone=phone
        )
        
        try:
            db.session.add(company)
            db.session.commit()
            return company
        except Exception as e:
            db.session.rollback()
            raise ValidationError(f"创建公司失败: {str(e)}")

    @staticmethod
    def update_company(company_id, **kwargs):
        """
        更新公司信息
        
        Args:
            company_id (int): 公司ID
            **kwargs: 要更新的字段
            
        Returns:
            Company: 更新后的公司对象
            
        Raises:
            ResourceNotFoundError: 当公司不存在时
            ValidationError: 当更新数据无效时
        """
        company = Company.query.get(company_id)
        if not company:
            raise ResourceNotFoundError("公司不存在")
            
        # 处理可更新的字段
        allowed_fields = ['name', 'description', 'address', 'phone']
        for field, value in kwargs.items():
            if field in allowed_fields and value is not None:
                if field == 'name':
                    # 检查名称唯一性
                    existing = Company.query.filter(
                        Company.name == value.strip(),
                        Company.id != company_id
                    ).first()
                    if existing:
                        raise ValidationError("公司名称已存在")
                    setattr(company, field, value.strip())
                else:
                    setattr(company, field, value)
        
        try:
            db.session.commit()
            return company
        except Exception as e:
            db.session.rollback()
            raise ValidationError(f"更新公司失败: {str(e)}")

    @staticmethod
    def delete_company(company_id):
        """
        删除公司
        
        Args:
            company_id (int): 公司ID
            
        Returns:
            bool: 删除是否成功
            
        Raises:
            ResourceNotFoundError: 当公司不存在时
            ValidationError: 当公司有用户关联时
        """
        company = Company.query.get(company_id)
        if not company:
            raise ResourceNotFoundError("公司不存在")
            
        # 检查是否有用户关联
        from ..models.user import User
        if User.query.filter_by(company_id=company_id).count() > 0:
            raise ValidationError("该公司下有关联用户，无法删除")
            
        try:
            db.session.delete(company)
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            raise ValidationError(f"删除公司失败: {str(e)}")

    @staticmethod
    def list_companies(page=1, per_page=10):
        """
        获取公司列表
        
        Args:
            page (int): 页码，从1开始
            per_page (int): 每页记录数
            
        Returns:
            dict: 包含公司列表和分页信息的字典
        """
        if page < 1:
            page = 1
        if per_page < 1:
            per_page = 10
            
        pagination = Company.query.paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
        
        return {
            'items': [company.to_dict() for company in pagination.items],
            'total': pagination.total,
            'page': page,
            'per_page': per_page,
            'pages': pagination.pages,
            'has_next': pagination.has_next,
            'has_prev': pagination.has_prev
        }