#!/usr/bin/env python3
"""
架构守护脚本 - 确保代码遵循四层架构规范
检查数据层、服务层、应用层、表现层的职责分离
"""

import os
import re
import argparse
from pathlib import Path
from typing import List, Dict, Set

class ArchitectureGuard:
    def __init__(self):
        self.violations: List[Dict] = []
        self.checked_files: Set[str] = set()
        
        # 架构规则定义
        self.rules = {
            'data_layer': {
                'patterns': [
                    r'from flask import',
                    r'request\.',
                    r'jsonify\(',
                    r'@app\.route',
                    r'Blueprint\('
                ],
                'message': "数据层不应包含Web框架相关代码"
            },
            'service_layer': {
                'patterns': [
                    r'db\.session\.',
                    r'SELECT.*FROM',
                    r'INSERT INTO',
                    r'UPDATE.*SET',
                    r'DELETE FROM'
                ],
                'message': "服务层不应直接进行原始SQL操作"
            },
            'api_layer': {
                'patterns': [
                    r'business_logic',
                    r'复杂的if.*else链',
                    r'超过50行的函数'
                ],
                'message': "应用层应保持精简，不应包含复杂业务逻辑"
            }
        }
        
        # 文件类型和层级映射
        self.layer_mapping = {
            'models.py': 'data_layer',
            'services.py': 'service_layer',
            'api.py': 'api_layer',
            '.vue': 'presentation_layer',
            '.ts': 'presentation_layer',
            '.js': 'presentation_layer'
        }
    
    def determine_layer(self, file_path: str) -> str:
        """根据文件名确定所属架构层级"""
        filename = os.path.basename(file_path)
        for pattern, layer in self.layer_mapping.items():
            if pattern in filename or file_path.endswith(pattern):
                return layer
        return 'unknown'
    
    def check_file(self, file_path: str) -> None:
        """检查单个文件是否符合架构规范"""
        if file_path in self.checked_files:
            return
            
        self.checked_files.add(file_path)
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            layer = self.determine_layer(file_path)
            
            # 根据层级应用相应的规则
            if layer in self.rules:
                rules = self.rules[layer]
                for pattern in rules['patterns']:
                    if re.search(pattern, content):
                        self.violations.append({
                            'file': file_path,
                            'layer': layer,
                            'pattern': pattern,
                            'message': rules['message'],
                            'line': self.get_line_number(content, pattern)
                        })
                        
        except Exception as e:
            print(f"检查文件 {file_path} 时出错: {e}")
    
    def get_line_number(self, content: str, pattern: str) -> int:
        """获取匹配模式的行号"""
        lines = content.split('\n')
        for i, line in enumerate(lines, 1):
            if re.search(pattern, line):
                return i
        return -1
    
    def check_directory(self, directory: str, extensions: List[str] = None) -> None:
        """检查目录下的所有文件"""
        if extensions is None:
            extensions = ['.py', '.vue', '.ts', '.js']
            
        for root, _, files in os.walk(directory):
            for file in files:
                if any(file.endswith(ext) for ext in extensions):
                    file_path = os.path.join(root, file)
                    self.check_file(file_path)
    
    def report_violations(self) -> None:
        """生成架构违规报告"""
        if not self.violations:
            print("✅ 未发现架构违规")
            return
            
        print(f"\n❌ 发现 {len(self.violations)} 处架构违规:")
        print("=" * 80)
        
        for i, violation in enumerate(self.violations, 1):
            print(f"{i}. 文件: {violation['file']}")
            print(f"   层级: {violation['layer']}")
            print(f"   违规: {violation['message']}")
            print(f"   模式: {violation['pattern']}")
            if violation['line'] > 0:
                print(f"   行号: {violation['line']}")
            print("-" * 40)
    
    def get_stats(self) -> Dict:
        """获取检查统计信息"""
        return {
            'total_files': len(self.checked_files),
            'violations': len(self.violations),
            'violation_by_layer': self.get_violations_by_layer()
        }
    
    def get_violations_by_layer(self) -> Dict:
        """按层级统计违规数量"""
        result = {}
        for violation in self.violations:
            layer = violation['layer']
            result[layer] = result.get(layer, 0) + 1
        return result

def main():
    parser = argparse.ArgumentParser(description='架构守护脚本')
    parser.add_argument('--directory', '-d', default='.', 
                       help='要检查的目录路径')
    parser.add_argument('--strict', '-s', action='store_true',
                       help='严格模式，发现违规时返回非零退出码')
    parser.add_argument('--module', '-m', 
                       help='指定检查的模块名称')
    
    args = parser.parse_args()
    
    guard = ArchitectureGuard()
    
    # 确定检查目录
    check_dir = args.directory
    if args.module:
        check_dir = os.path.join(args.directory, 'src', args.module)
    
    if not os.path.exists(check_dir):
        print(f"错误: 目录 {check_dir} 不存在")
        return 1
    
    print(f"🔍 检查目录: {check_dir}")
    print(f"📋 检查文件类型: .py, .vue, .ts, .js")
    print("-" * 60)
    
    guard.check_directory(check_dir)
    guard.report_violations()
    
    stats = guard.get_stats()
    print(f"\n📊 检查统计:")
    print(f"   检查文件数: {stats['total_files']}")
    print(f"   架构违规数: {stats['violations']}")
    
    for layer, count in stats['violation_by_layer'].items():
        print(f"   {layer}违规: {count}")
    
    # 严格模式处理
    if args.strict and stats['violations'] > 0:
        print("\n❌ 严格模式: 发现架构违规，退出码为1")
        return 1
    
    return 0

if __name__ == '__main__':
    exit(main())
    print(xdl)