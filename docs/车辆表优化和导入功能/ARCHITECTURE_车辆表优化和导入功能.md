# 车辆表优化和XLSX导入功能 - 架构设计文档

## 1. 系统架构概览

### 1.1 架构模式
采用四层架构模式：
- **表现层（Presentation Layer）**：Vue 3 + Element Plus 前端界面
- **应用层（Application Layer）**：Flask 路由和控制器
- **服务层（Service Layer）**：业务逻辑处理和数据验证
- **数据层（Data Layer）**：SQLAlchemy ORM + SQLite 数据库

### 1.2 模块划分
```
车辆表优化和导入功能
├── 数据库层
│   ├── 车辆表结构优化
│   ├── 数据约束设计
│   └── 迁移脚本
├── 服务层
│   ├── 车辆数据验证服务
│   ├── Excel文件处理服务
│   └── 批量导入服务
├── 应用层
│   ├── 车辆管理API
│   ├── 文件上传API
│   └── 批量导入API
└── 表现层
    ├── 车辆管理界面优化
    ├── 导入功能界面
    └── 模板下载功能
```

## 2. 数据库设计

### 2.1 车辆表结构优化

#### 2.1.1 新增字段设计
```sql
-- 在现有vehicles表基础上新增字段
ALTER TABLE vehicles 
ADD COLUMN vehicle_category VARCHAR(10) COMMENT '车辆分类：单车/挂车';

ALTER TABLE vehicles 
ADD COLUMN frequent_companies TEXT COMMENT '常用公司列表，JSON格式存储';

-- 修改现有字段约束
ALTER TABLE vehicles 
MODIFY COLUMN actual_volume FLOAT NOT NULL COMMENT '实际容积（必填）';
```

#### 2.1.2 约束条件设计
```sql
-- 应用层约束：车牌号或车厢号至少有一个不为空
-- 通过业务逻辑验证实现，因为SQLite不支持复杂CHECK约束

-- 数据库层基础约束
ALTER TABLE vehicles 
ADD CONSTRAINT chk_vehicle_category 
CHECK (vehicle_category IN ('单车', '挂车'));
```

#### 2.1.3 索引优化
```sql
-- 为常用查询字段添加索引
CREATE INDEX idx_vehicles_license_plate ON vehicles(license_plate);
CREATE INDEX idx_vehicles_carriage_number ON vehicles(carriage_number);
CREATE INDEX idx_vehicles_vehicle_category ON vehicles(vehicle_category);
CREATE INDEX idx_vehicles_vehicle_type ON vehicles(vehicle_type);
```

### 2.2 数据迁移策略

#### 2.2.1 现有数据处理
```python
# 迁移脚本：为现有数据设置默认值
def upgrade():
    # 1. 添加新字段
    op.add_column('vehicles', sa.Column('vehicle_category', sa.String(10), comment='车辆分类'))
    op.add_column('vehicles', sa.Column('frequent_companies', sa.Text, comment='常用公司列表'))
    
    # 2. 更新现有数据的车辆分类
    connection = op.get_bind()
    connection.execute(
        "UPDATE vehicles SET vehicle_category = CASE "
        "WHEN carriage_number IS NOT NULL AND carriage_number != '' THEN '挂车' "
        "ELSE '单车' END"
    )
    
    # 3. 初始化常用公司字段
    connection.execute(
        "UPDATE vehicles SET frequent_companies = '[]' WHERE frequent_companies IS NULL"
    )
```

## 3. 后端服务设计

### 3.1 数据模型优化

#### 3.1.1 Vehicle模型扩展
```python
class Vehicle(db.Model):
    """车辆信息模型类 - 优化版本"""
    __tablename__ = 'vehicles'
    
    # 现有字段保持不变...
    
    # 新增字段
    vehicle_category = db.Column(db.String(10), comment='车辆分类：单车/挂车')
    frequent_companies = db.Column(db.Text, default='[]', comment='常用公司列表，JSON格式')
    
    # 约束验证
    @validates('license_plate', 'carriage_number')
    def validate_plate_or_carriage(self, key, value):
        """验证车牌号或车厢号至少有一个不为空"""
        if key == 'license_plate':
            if not value and not self.carriage_number:
                raise ValueError('车牌号或车厢号至少需要填写一个')
        elif key == 'carriage_number':
            if not value and not self.license_plate:
                raise ValueError('车牌号或车厢号至少需要填写一个')
        return value
    
    @validates('actual_volume')
    def validate_volume(self, key, value):
        """验证容积必填"""
        if value is None or value <= 0:
            raise ValueError('容积必须大于0')
        return value
    
    def set_vehicle_category(self):
        """根据车厢号自动设置车辆分类"""
        if self.carriage_number and '挂' in self.carriage_number:
            self.vehicle_category = '挂车'
        else:
            self.vehicle_category = '单车'
    
    def add_frequent_company(self, company_name):
        """添加常用公司"""
        import json
        companies = json.loads(self.frequent_companies or '[]')
        if company_name not in companies:
            companies.append(company_name)
            self.frequent_companies = json.dumps(companies, ensure_ascii=False)
    
    def get_frequent_companies(self):
        """获取常用公司列表"""
        import json
        return json.loads(self.frequent_companies or '[]')
    
    def to_dict(self):
        """扩展字典转换方法"""
        base_dict = super().to_dict()
        base_dict.update({
            'vehicle_category': self.vehicle_category,
            'frequent_companies': self.get_frequent_companies()
        })
        return base_dict
```

### 3.2 服务层设计

#### 3.2.1 车辆数据验证服务
```python
class VehicleValidationService:
    """车辆数据验证服务"""
    
    @staticmethod
    def validate_vehicle_data(data):
        """验证车辆数据"""
        errors = []
        
        # 验证车牌号或车厢号
        if not data.get('license_plate') and not data.get('carriage_number'):
            errors.append('车牌号或车厢号至少需要填写一个')
        
        # 验证容积
        volume = data.get('actual_volume')
        if not volume or volume <= 0:
            errors.append('容积必须大于0')
        
        # 验证车厢号格式（如果是挂车）
        carriage_number = data.get('carriage_number')
        if carriage_number and '挂' in carriage_number:
            if not re.match(r'^[\u4e00-\u9fa5][A-Z][0-9A-Z]+挂$', carriage_number):
                errors.append('车厢号格式不正确，应为：车牌号+挂，如：皖A36T3挂')
        
        return errors
    
    @staticmethod
    def auto_set_category(data):
        """自动设置车辆分类"""
        carriage_number = data.get('carriage_number', '')
        if carriage_number and '挂' in carriage_number:
            data['vehicle_category'] = '挂车'
        else:
            data['vehicle_category'] = '单车'
        return data
```

#### 3.2.2 Excel文件处理服务
```python
import pandas as pd
from io import BytesIO

class ExcelProcessingService:
    """Excel文件处理服务"""
    
    # 导入模板字段映射
    FIELD_MAPPING = {
        '车牌号': 'license_plate',
        '车厢号': 'carriage_number',
        '容积': 'actual_volume',
        '车辆类型': 'vehicle_type',
        '车辆分类': 'vehicle_category',
        '常用公司': 'frequent_companies',
        '备注': 'notes'
    }
    
    @classmethod
    def create_template(cls):
        """创建导入模板"""
        template_data = {
            '车牌号': ['皖A12345', '皖B67890'],
            '车厢号': ['皖A36T3挂', ''],
            '容积': [25.5, 30.0],
            '车辆类型': ['5吨', '8吨'],
            '车辆分类': ['挂车', '单车'],
            '常用公司': ['公司A,公司B', '公司C'],
            '备注': ['测试数据1', '测试数据2']
        }
        
        df = pd.DataFrame(template_data)
        
        # 创建Excel文件
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='车辆信息', index=False)
            
            # 添加数据验证和说明
            worksheet = writer.sheets['车辆信息']
            worksheet.insert_rows(1)
            worksheet['A1'] = '说明：车牌号或车厢号至少填写一个，容积必填，车厢号格式如：皖A36T3挂'
        
        output.seek(0)
        return output.getvalue()
    
    @classmethod
    def parse_excel_file(cls, file_content):
        """解析Excel文件"""
        try:
            df = pd.read_excel(BytesIO(file_content), sheet_name=0)
            
            # 转换字段名
            df.rename(columns=cls.FIELD_MAPPING, inplace=True)
            
            # 数据清洗
            df = df.fillna('')  # 填充空值
            
            # 转换为字典列表
            records = df.to_dict('records')
            
            return {'success': True, 'data': records}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    @classmethod
    def validate_import_data(cls, records):
        """验证导入数据"""
        validation_results = []
        
        for index, record in enumerate(records, 1):
            row_errors = VehicleValidationService.validate_vehicle_data(record)
            
            validation_results.append({
                'row': index,
                'data': record,
                'errors': row_errors,
                'valid': len(row_errors) == 0
            })
        
        return validation_results
```

#### 3.2.3 批量导入服务
```python
class BatchImportService:
    """批量导入服务"""
    
    @staticmethod
    def import_vehicles(validated_data, user_id):
        """批量导入车辆数据"""
        success_count = 0
        error_count = 0
        errors = []
        
        try:
            for item in validated_data:
                if item['valid']:
                    try:
                        # 自动设置车辆分类
                        data = VehicleValidationService.auto_set_category(item['data'])
                        
                        # 处理常用公司字段
                        if data.get('frequent_companies'):
                            companies = [c.strip() for c in data['frequent_companies'].split(',')]
                            data['frequent_companies'] = json.dumps(companies, ensure_ascii=False)
                        else:
                            data['frequent_companies'] = '[]'
                        
                        # 创建车辆记录
                        vehicle = Vehicle(**data)
                        db.session.add(vehicle)
                        
                        success_count += 1
                        
                    except Exception as e:
                        error_count += 1
                        errors.append(f"第{item['row']}行导入失败：{str(e)}")
                else:
                    error_count += 1
                    errors.extend([f"第{item['row']}行：{error}" for error in item['errors']])
            
            db.session.commit()
            
            return {
                'success': True,
                'success_count': success_count,
                'error_count': error_count,
                'errors': errors
            }
            
        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'error': f"批量导入失败：{str(e)}"
            }
```

## 4. API接口设计

### 4.1 车辆管理API扩展

#### 4.1.1 创建/更新车辆API
```python
@vehicle_bp.route('/vehicles', methods=['POST'])
@require_auth
def create_vehicle():
    """创建车辆（支持新字段）"""
    try:
        data = request.get_json()
        
        # 数据验证
        errors = VehicleValidationService.validate_vehicle_data(data)
        if errors:
            return jsonify({
                'success': False,
                'message': '数据验证失败',
                'errors': errors
            }), 400
        
        # 自动设置车辆分类
        data = VehicleValidationService.auto_set_category(data)
        
        # 处理常用公司
        if 'frequent_companies' in data and isinstance(data['frequent_companies'], list):
            data['frequent_companies'] = json.dumps(data['frequent_companies'], ensure_ascii=False)
        
        vehicle = Vehicle(**data)
        db.session.add(vehicle)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '车辆创建成功',
            'data': vehicle.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'创建失败：{str(e)}'
        }), 500
```

### 4.2 文件导入API

#### 4.2.1 模板下载API
```python
@vehicle_bp.route('/vehicles/import/template', methods=['GET'])
@require_auth
def download_import_template():
    """下载导入模板"""
    try:
        template_content = ExcelProcessingService.create_template()
        
        response = make_response(template_content)
        response.headers['Content-Type'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        response.headers['Content-Disposition'] = 'attachment; filename=vehicle_import_template.xlsx'
        
        return response
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'模板生成失败：{str(e)}'
        }), 500
```

#### 4.2.2 文件上传和预览API
```python
@vehicle_bp.route('/vehicles/import/preview', methods=['POST'])
@require_auth
def preview_import_data():
    """预览导入数据"""
    try:
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'message': '未找到上传文件'
            }), 400
        
        file = request.files['file']
        if not file.filename.endswith(('.xlsx', '.xls')):
            return jsonify({
                'success': False,
                'message': '文件格式不支持，请上传Excel文件'
            }), 400
        
        # 解析文件
        parse_result = ExcelProcessingService.parse_excel_file(file.read())
        if not parse_result['success']:
            return jsonify({
                'success': False,
                'message': f'文件解析失败：{parse_result["error"]}'
            }), 400
        
        # 验证数据
        validation_results = ExcelProcessingService.validate_import_data(parse_result['data'])
        
        # 统计结果
        total_count = len(validation_results)
        valid_count = sum(1 for item in validation_results if item['valid'])
        invalid_count = total_count - valid_count
        
        return jsonify({
            'success': True,
            'data': {
                'total_count': total_count,
                'valid_count': valid_count,
                'invalid_count': invalid_count,
                'preview_data': validation_results[:10],  # 只返回前10条预览
                'validation_results': validation_results
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'预览失败：{str(e)}'
        }), 500
```

#### 4.2.3 批量导入API
```python
@vehicle_bp.route('/vehicles/import/execute', methods=['POST'])
@require_auth
def execute_import():
    """执行批量导入"""
    try:
        data = request.get_json()
        validation_results = data.get('validation_results', [])
        
        if not validation_results:
            return jsonify({
                'success': False,
                'message': '没有可导入的数据'
            }), 400
        
        # 执行导入
        import_result = BatchImportService.import_vehicles(
            validation_results, 
            current_user.id
        )
        
        return jsonify(import_result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'导入失败：{str(e)}'
        }), 500
```

## 5. 前端组件设计

### 5.1 车辆表单组件优化

#### 5.1.1 表单验证规则
```javascript
// VehicleForm.vue
const vehicleRules = {
  // 自定义验证：车牌号或车厢号至少填一个
  plateOrCarriage: [
    {
      validator: (rule, value, callback) => {
        if (!vehicleForm.license_plate && !vehicleForm.carriage_number) {
          callback(new Error('车牌号或车厢号至少需要填写一个'))
        } else {
          callback()
        }
      },
      trigger: 'blur'
    }
  ],
  actual_volume: [
    { required: true, message: '请输入容积', trigger: 'blur' },
    { type: 'number', min: 0.1, message: '容积必须大于0', trigger: 'blur' }
  ],
  carriage_number: [
    {
      validator: (rule, value, callback) => {
        if (value && value.includes('挂')) {
          const pattern = /^[\u4e00-\u9fa5][A-Z][0-9A-Z]+挂$/
          if (!pattern.test(value)) {
            callback(new Error('车厢号格式不正确，应为：车牌号+挂，如：皖A36T3挂'))
          }
        }
        callback()
      },
      trigger: 'blur'
    }
  ]
}
```

### 5.2 导入功能组件

#### 5.2.1 导入对话框组件
```vue
<!-- VehicleImportDialog.vue -->
<template>
  <el-dialog v-model="visible" title="批量导入车辆" width="80%" :close-on-click-modal="false">
    <el-steps :active="currentStep" align-center>
      <el-step title="上传文件" />
      <el-step title="数据预览" />
      <el-step title="导入结果" />
    </el-steps>
    
    <!-- 步骤1：文件上传 -->
    <div v-if="currentStep === 0" class="upload-step">
      <div class="template-download">
        <el-button type="primary" @click="downloadTemplate">
          <el-icon><Download /></el-icon>
          下载导入模板
        </el-button>
        <span class="tip">请先下载模板，按格式填写数据后上传</span>
      </div>
      
      <el-upload
        ref="uploadRef"
        :auto-upload="false"
        :on-change="handleFileChange"
        :before-upload="beforeUpload"
        accept=".xlsx,.xls"
        drag
      >
        <el-icon class="el-icon--upload"><upload-filled /></el-icon>
        <div class="el-upload__text">
          将Excel文件拖到此处，或<em>点击上传</em>
        </div>
        <template #tip>
          <div class="el-upload__tip">
            支持.xlsx、.xls格式，文件大小不超过10MB
          </div>
        </template>
      </el-upload>
    </div>
    
    <!-- 步骤2：数据预览 -->
    <div v-if="currentStep === 1" class="preview-step">
      <div class="preview-summary">
        <el-row :gutter="20">
          <el-col :span="8">
            <el-statistic title="总记录数" :value="previewData.total_count" />
          </el-col>
          <el-col :span="8">
            <el-statistic title="有效记录" :value="previewData.valid_count" />
          </el-col>
          <el-col :span="8">
            <el-statistic title="错误记录" :value="previewData.invalid_count" />
          </el-col>
        </el-row>
      </div>
      
      <el-table :data="previewData.preview_data" border>
        <el-table-column prop="row" label="行号" width="80" />
        <el-table-column prop="data.license_plate" label="车牌号" />
        <el-table-column prop="data.carriage_number" label="车厢号" />
        <el-table-column prop="data.actual_volume" label="容积" />
        <el-table-column prop="data.vehicle_type" label="车辆类型" />
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.valid ? 'success' : 'danger'">
              {{ row.valid ? '有效' : '错误' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="错误信息">
          <template #default="{ row }">
            <div v-if="!row.valid">
              <div v-for="error in row.errors" :key="error" class="error-text">
                {{ error }}
              </div>
            </div>
          </template>
        </el-table-column>
      </el-table>
    </div>
    
    <!-- 步骤3：导入结果 -->
    <div v-if="currentStep === 2" class="result-step">
      <el-result
        :icon="importResult.success ? 'success' : 'error'"
        :title="importResult.success ? '导入完成' : '导入失败'"
      >
        <template #sub-title>
          <div v-if="importResult.success">
            <p>成功导入 {{ importResult.success_count }} 条记录</p>
            <p v-if="importResult.error_count > 0">
              失败 {{ importResult.error_count }} 条记录
            </p>
          </div>
          <div v-else>
            {{ importResult.message }}
          </div>
        </template>
        
        <template #extra v-if="importResult.errors && importResult.errors.length > 0">
          <el-collapse>
            <el-collapse-item title="查看错误详情">
              <div v-for="error in importResult.errors" :key="error" class="error-item">
                {{ error }}
              </div>
            </el-collapse-item>
          </el-collapse>
        </template>
      </el-result>
    </div>
    
    <template #footer>
      <div class="dialog-footer">
        <el-button @click="visible = false">取消</el-button>
        <el-button v-if="currentStep > 0" @click="prevStep">上一步</el-button>
        <el-button 
          v-if="currentStep < 2" 
          type="primary" 
          @click="nextStep"
          :disabled="!canProceed"
          :loading="loading"
        >
          {{ currentStep === 1 ? '开始导入' : '下一步' }}
        </el-button>
        <el-button v-if="currentStep === 2" type="primary" @click="finish">
          完成
        </el-button>
      </div>
    </template>
  </el-dialog>
</template>
```

## 6. 性能优化设计

### 6.1 数据库优化
- **索引策略**：为常用查询字段添加索引
- **分页查询**：大数据量时使用分页加载
- **连接池**：优化数据库连接管理

### 6.2 文件处理优化
- **流式处理**：大文件使用流式读取
- **分批导入**：超过1000条记录时分批处理
- **异步处理**：导入操作使用后台任务

### 6.3 前端优化
- **虚拟滚动**：大数据量表格使用虚拟滚动
- **懒加载**：组件按需加载
- **缓存策略**：合理使用浏览器缓存

## 7. 安全设计

### 7.1 文件上传安全
- **文件类型验证**：严格限制文件格式
- **文件大小限制**：防止大文件攻击
- **病毒扫描**：集成文件安全检查

### 7.2 数据安全
- **输入验证**：所有输入数据严格验证
- **SQL注入防护**：使用ORM参数化查询
- **权限控制**：基于角色的访问控制

### 7.3 操作审计
- **操作日志**：记录所有导入操作
- **数据追踪**：记录数据变更历史
- **异常监控**：实时监控异常操作

## 8. 监控和日志

### 8.1 性能监控
- **响应时间监控**：API响应时间统计
- **资源使用监控**：CPU、内存使用情况
- **并发处理监控**：同时处理的导入任务数

### 8.2 业务监控
- **导入成功率**：统计导入操作成功率
- **数据质量监控**：监控数据完整性
- **用户行为分析**：分析用户使用模式

### 8.3 日志管理
- **结构化日志**：使用JSON格式记录日志
- **日志分级**：ERROR、WARN、INFO、DEBUG
- **日志轮转**：定期清理历史日志

---

**文档版本**：v1.0  
**创建时间**：2024-12-19  
**负责人**：系统架构师  
**审核状态**：待审核