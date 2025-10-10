"""
车辆业务逻辑迁移脚本
将业务逻辑从模型层迁移到服务层
"""

import os
import sys
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.extensions import db
from app.models.vehicle.vehicle import Vehicle
from app.services.vehicle.vehicle_business_service import VehicleBusinessService

def migrate_vehicle_data():
    """迁移现有车辆数据的业务逻辑"""
    app = create_app()
    
    with app.app_context():
        try:
            print("开始迁移车辆业务逻辑...")
            
            # 获取所有车辆记录
            vehicles = Vehicle.query.all()
            total_count = len(vehicles)
            updated_count = 0
            
            for vehicle in vehicles:
                try:
                    # 重新验证和更新车辆数据
                    vehicle_data = {
                        'license_plate': vehicle.license_plate,
                        'carriage_number': vehicle.carriage_number,
                        'actual_volume': vehicle.actual_volume,
                        'vehicle_type': vehicle.vehicle_type,
                        'vehicle_category': vehicle.vehicle_category,
                        'frequent_companies': vehicle.frequent_companies,
                        'supplier_type': vehicle.supplier_type,
                        'original_capacity': vehicle.original_capacity,
                        'status': vehicle.status
                    }
                    
                    # 使用业务服务验证数据
                    is_valid, result = VehicleBusinessService.validate_and_prepare_vehicle(vehicle_data)
                    
                    if is_valid:
                        # 更新标准化后的数据
                        vehicle.normalized_license_plate = result.get('normalized_license_plate')
                        vehicle.capacity_score = result.get('capacity_score')
                        vehicle.supplier_category = result.get('supplier_category')
                        
                        # 更新最后修改时间
                        vehicle.updated_at = datetime.utcnow()
                        
                        updated_count += 1
                        print(f"已更新车辆 {vehicle.id}: {vehicle.license_plate}")
                    else:
                        print(f"跳过车辆 {vehicle.id}: 验证失败 - {'; '.join(result)}")
                        
                except Exception as e:
                    print(f"处理车辆 {vehicle.id} 时出错: {str(e)}")
                    continue
            
            # 提交所有更改
            db.session.commit()
            
            print(f"\n迁移完成!")
            print(f"总记录数: {total_count}")
            print(f"成功更新: {updated_count}")
            print(f"跳过记录: {total_count - updated_count}")
            
        except Exception as e:
            db.session.rollback()
            print(f"迁移过程中发生错误: {str(e)}")
            raise

if __name__ == '__main__':
    migrate_vehicle_data()