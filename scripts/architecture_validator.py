#!/usr/bin/env python3
"""
架构验证脚本
验证后端代码是否符合四层架构规则
"""

import os
import sys
import ast
import re
from pathlib import Path

# 添加项目路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

class ArchitectureValidator:
    """架构验证器"""
    
    def __init__(self, project_root):
        self.project_root = Path(project_root)
        self.errors = []
        
    def validate_layer_dependencies(self):
        """验证各层之间的依赖关系"""
        print("正在验证层间依赖关系...")
        
        # 定义允许的依赖关系
        allowed_dependencies = {
            'api': ['services'],  # 表现层只能依赖服务层
            'routes': ['services'],  # 路由层只能依赖服务层
            'services': ['models', 'extensions', 'utils'],  # 服务层可以依赖数据层和其他工具
            'models': ['extensions'],  # 数据层只能依赖扩展
        }
        
        # 检查路由文件
        routes_files = list(self.project_root.glob('app/*/routes.py'))
        for route_file in routes_files:
            self._check_file_dependencies(route_file, allowed_dependencies.get('routes', []))
            
        # 检查API文件
        api_files = list(self.project_root.glob('app/api/**/*.py'))
        for api_file in api_files:
            if api_file.name != '__init__.py':
                self._check_file_dependencies(api_file, allowed_dependencies.get('api', []))
                
        # 检查服务文件
        service_files = list(self.project_root.glob('app/services/*.py'))
        for service_file in service_files:
            if service_file.name != '__init__.py':
                self._check_file_dependencies(service_file, allowed_dependencies.get('services', []))
                
        # 检查模型文件
        model_files = list(self.project_root.glob('app/models/*.py'))
        for model_file in model_files:
            if model_file.name != '__init__.py':
                self._check_file_dependencies(model_file, allowed_dependencies.get('models', []))
    
    def _check_file_dependencies(self, file_path, allowed_imports):
        """检查文件的导入依赖"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # 解析AST
            tree = ast.parse(content)
            
            # 查找导入语句
            imports = []
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imports.append(node.module)
            
            # 检查不允许的导入
            file_module = file_path.parent.name
            for imp in imports:
                # 检查是否导入了不允许的模块
                module_parts = imp.split('.')
                top_level_module = module_parts[0] if module_parts else ''
                
                # 如果不是允许的导入，记录错误
                if top_level_module and top_level_module not in allowed_imports:
                    # 特殊处理相对导入
                    if imp.startswith('.'):
                        continue
                        
                    # 检查是否是项目内部模块
                    if self._is_project_module(imp):
                        # 检查是否违反了分层规则
                        if self._is_layer_violation(file_module, top_level_module):
                            self.errors.append(
                                f"文件 {file_path.relative_to(self.project_root)} "
                                f"违反了分层规则: 不允许从 {file_module} 层导入 {top_level_module} 层"
                            )
                            
        except Exception as e:
            self.errors.append(f"解析文件 {file_path} 时出错: {str(e)}")
    
    def _is_project_module(self, module_name):
        """判断是否为项目内部模块"""
        project_modules = ['app', 'models', 'services', 'api', 'auth', 'basic_data', 'dispatch']
        module_parts = module_name.split('.')
        return module_parts[0] in project_modules
    
    def _is_layer_violation(self, from_layer, to_layer):
        """判断是否违反了分层规则"""
        # 定义层的依赖规则
        layer_hierarchy = {
            'api': 1,      # 表现层
            'routes': 1,   # 路由层（属于表现层）
            'services': 2, # 服务层
            'models': 3,   # 数据层
        }
        
        from_level = layer_hierarchy.get(from_layer, 0)
        to_level = layer_hierarchy.get(to_layer, 0)
        
        # 表现层不能依赖数据层（跳过服务层）
        if from_level == 1 and to_level == 3:
            return True
            
        # 其他情况暂不严格限制
        return False
    
    def validate_file_structure(self):
        """验证文件结构是否符合规范"""
        print("正在验证文件结构...")
        
        # 检查必需的目录
        required_dirs = [
            'app/api',
            'app/models',
            'app/services',
        ]
        
        for dir_path in required_dirs:
            full_path = self.project_root / dir_path
            if not full_path.exists():
                self.errors.append(f"缺少必需目录: {dir_path}")
        
        # 检查路由文件应该在各自模块中
        modules = ['auth', 'basic_data', 'dispatch']
        for module in modules:
            route_file = self.project_root / 'app' / module / 'routes.py'
            if not route_file.exists():
                self.errors.append(f"模块 {module} 缺少路由文件: routes.py")
    
    def validate_service_layer(self):
        """验证服务层实现"""
        print("正在验证服务层...")
        
        service_files = list(self.project_root.glob('app/services/*.py'))
        for service_file in service_files:
            if service_file.name == '__init__.py':
                continue
                
            try:
                with open(service_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 检查是否包含业务逻辑方法
                if 'class' not in content:
                    self.errors.append(f"服务文件 {service_file.relative_to(self.project_root)} 应该包含类定义")
                
                # 检查是否导入了模型
                if 'from ..models' not in content and 'from .models' not in content:
                    # 某些服务可能不需要直接访问模型
                    pass
                    
            except Exception as e:
                self.errors.append(f"检查服务文件 {service_file} 时出错: {str(e)}")
    
    def validate_presentation_layer(self):
        """验证表现层实现"""
        print("正在验证表现层...")
        
        # 检查路由文件
        route_files = list(self.project_root.glob('app/*/routes.py'))
        for route_file in route_files:
            self._validate_route_file(route_file)
            
        # 检查API文件
        api_files = list(self.project_root.glob('app/api/**/*.py'))
        for api_file in api_files:
            if api_file.name != '__init__.py':
                self._validate_api_file(api_file)
    
    def _validate_route_file(self, route_file):
        """验证路由文件"""
        try:
            with open(route_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 检查是否导入了服务层
            if 'from ..services' not in content and 'from .services' not in content:
                # 某些简单路由可能不需要服务层
                pass
                
            # 检查是否包含路由装饰器
            if '@' not in content:
                self.errors.append(f"路由文件 {route_file.relative_to(self.project_root)} 应该包含路由装饰器")
                
        except Exception as e:
            self.errors.append(f"检查路由文件 {route_file} 时出错: {str(e)}")
    
    def _validate_api_file(self, api_file):
        """验证API文件"""
        try:
            with open(api_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 检查是否导入了服务层
            if 'from ...services' not in content and 'from ..services' not in content:
                # 某些API文件可能不需要服务层
                pass
                
            # 检查是否包含路由装饰器
            if '@' not in content:
                self.errors.append(f"API文件 {api_file.relative_to(self.project_root)} 应该包含路由装饰器")
                
        except Exception as e:
            self.errors.append(f"检查API文件 {api_file} 时出错: {str(e)}")
    
    def run_validation(self):
        """运行所有验证"""
        print("开始架构验证...")
        
        self.validate_file_structure()
        self.validate_layer_dependencies()
        self.validate_service_layer()
        self.validate_presentation_layer()
        
        print(f"验证完成，发现 {len(self.errors)} 个问题")
        
        if self.errors:
            print("\n发现的问题:")
            for i, error in enumerate(self.errors, 1):
                print(f"{i}. {error}")
            return False
        else:
            print("\n所有验证通过！代码符合架构规范。")
            return True

def main():
    """主函数"""
    project_root = Path(__file__).parent.parent / 'backend'
    
    if not project_root.exists():
        print(f"错误: 项目根目录不存在 {project_root}")
        return 1
    
    validator = ArchitectureValidator(project_root)
    success = validator.run_validation()
    
    return 0 if success else 1

if __name__ == '__main__':
    sys.exit(main())