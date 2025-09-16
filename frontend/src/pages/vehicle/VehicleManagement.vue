<template>
  <div class="vehicle-management">
    <h1>车辆管理</h1>
    
    <div class="search-bar">
      <el-input
        v-model="searchQuery"
        placeholder="输入车牌号或车厢号搜索"
        prefix-icon="el-icon-search"
        @input="handleSearch"
        clearable
      ></el-input>
      
      <div class="toolbar-buttons">
        <el-button 
          type="primary" 
          icon="el-icon-plus" 
          @click="showAddVehicleDialog"
          v-permission="'vehicle:create'"
        >添加车辆</el-button>
        <el-button 
          type="success" 
          icon="el-icon-upload" 
          @click="showImportDialog"
          v-permission="'vehicle:create'"
        >批量导入</el-button>
      </div>
    </div>
    
    <el-table
      :data="filteredVehicles"
      border
      style="width: 100%"
      v-loading="loading"
    >
      <el-table-column prop="license_plate" label="车牌号" width="120"></el-table-column>
      <el-table-column prop="carriage_number" label="车厢号" width="120"></el-table-column>
      <el-table-column prop="vehicle_type" label="车型" width="100">
        <template #default="{ row }">
          {{ row.vehicle_type }}
        </template>
      </el-table-column>
      <el-table-column prop="original_capacity" label="原始载重量(吨)" width="150"></el-table-column>
      <el-table-column prop="standard_volume" label="标准容积(m³)" width="150"></el-table-column>
      <el-table-column prop="status" label="状态" width="100">
        <template #default="{ row }">
          <el-tag :type="row.status === 'active' ? 'success' : 'info'">
            {{ row.status === 'active' ? '启用' : '禁用' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="updated_at" label="最后更新时间" width="180"></el-table-column>
      <el-table-column label="操作" fixed="right" width="250">
        <template #default="{ row }">
          <el-button 
            size="mini" 
            type="primary" 
            @click="handleEdit(row)"
            v-permission="'vehicle:update'"
          >编辑</el-button>

          <el-button 
            size="mini" 
            type="danger" 
            @click="handleDelete(row)"
            v-permission="'vehicle:delete'"
          >删除</el-button>
        </template>
      </el-table-column>
    </el-table>
    
    <div class="pagination">
      <el-pagination
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
        :current-page="currentPage"
        :page-sizes="[10, 20, 50, 100]"
        :page-size="pageSize"
        layout="total, sizes, prev, pager, next, jumper"
        :total="totalVehicles"
      ></el-pagination>
    </div>
    
    <!-- 添加/编辑车辆对话框 -->
    <el-dialog v-model="vehicleDialogVisible" :title="dialogTitle" width="50%">
      <el-form :model="vehicleForm" :rules="vehicleRules" ref="vehicleForm" label-width="120px">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="车牌号" prop="plateOrCarriage">
              <el-input v-model="vehicleForm.license_plate" placeholder="请输入车牌号"></el-input>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="车厢号" prop="compartmentNumber">
              <el-input v-model="vehicleForm.carriage_number" placeholder="如：皖A36T3挂"></el-input>
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="车型" prop="vehicleType">
              <el-select v-model="vehicleForm.vehicle_type" placeholder="请选择车型" @change="handleVehicleTypeChange">
                <el-option label="5吨" value="5吨"></el-option>
                <el-option label="8吨" value="8吨"></el-option>
                <el-option label="12吨" value="12吨"></el-option>
                <el-option label="20吨" value="20吨"></el-option>
                <el-option label="30吨" value="30吨"></el-option>
                <el-option label="40吨A" value="40吨A"></el-option>
                <el-option label="40吨B" value="40吨B"></el-option>
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="车辆分类">
              <el-input v-model="vehicleForm.vehicle_category" readonly placeholder="自动识别"></el-input>
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="标准容积(m³)" prop="standardVolume">
              <el-input-number v-model="vehicleForm.standard_volume" :min="0.1" :precision="2" placeholder="必填"></el-input-number>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="原始载重量(吨)">
              <el-input-number v-model="vehicleForm.original_capacity" :min="0" :precision="2"></el-input-number>
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-form-item label="常用公司">
          <el-select 
            v-model="vehicleForm.frequent_companies" 
            multiple 
            filterable 
            placeholder="请选择派车单位"
            style="width: 100%"
            :loading="loadingCompanies"
          >
            <el-option 
              v-for="unit in dispatchUnitOptions" 
              :key="unit.id" 
              :label="unit.name" 
              :value="unit.name"
            ></el-option>
          </el-select>
        </el-form-item>
        
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="供应商类型">
              <el-select v-model="vehicleForm.suppliers" placeholder="请选择供应商类型" style="width: 100%">
                <el-option label="内部单位" value="内部单位"></el-option>
                <el-option label="供应商" value="供应商"></el-option>
                <el-option label="外包驾驶管理公司" value="外包驾驶管理公司"></el-option>
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="状态">
              <el-switch
                v-model="vehicleForm.status"
                active-value="active"
                inactive-value="inactive"
                active-text="启用"
                inactive-text="禁用"
              ></el-switch>
            </el-form-item>
          </el-col>
        </el-row>
        

      </el-form>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="vehicleDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="submitVehicleForm">确定</el-button>
        </div>
      </template>
     </el-dialog>
    

    
    <!-- 批量导入对话框 -->
    <vehicle-import-dialog 
      v-model="importDialogVisible" 
      @import-success="handleImportSuccess"
    ></vehicle-import-dialog>
  </div>
</template>

<script>
import VehicleImportDialog from '@/components/VehicleImportDialog.vue';
import { vehicleCapacityReferenceService } from '@/services/vehicleCapacityReferenceService';
import { dispatchUnitService } from '@/services/dispatchUnitService';
import permission from '@/directives/permission';
import { Upload } from '@element-plus/icons-vue';

export default {
  name: 'VehicleManagement',
  components: {
    VehicleImportDialog,
    Upload
  },
  directives: {
    permission
  },
  data() {
    return {
      vehicles: [],
      filteredVehicles: [],
      loading: false,
      searchQuery: '',
      currentPage: 1,
      pageSize: 10,
      totalVehicles: 0,
      vehicleDialogVisible: false,
      importDialogVisible: false,
      dialogTitle: '',
      vehicleForm: {
        id: null,
        license_plate: '',
        carriage_number: '',
        vehicle_type: '',
        vehicle_category: '',
        original_capacity: 0,
        standard_volume: 0,
        frequent_companies: [],
        suppliers: '',
        status: 'active'
      },
      vehicleRules: {
        // 自定义验证：车牌号或车厢号至少填一个
        plateOrCarriage: [
          {
            validator: (rule, value, callback) => {
              if (!this.vehicleForm.license_plate && !this.vehicleForm.carriage_number) {
                callback(new Error('车牌号或车厢号至少需要填写一个'))
              } else {
                callback()
              }
            },
            trigger: 'blur'
          }
        ],
        standardVolume: [
          { required: true, message: '请输入标准容积', trigger: 'blur' },
          { type: 'number', min: 0.1, message: '标准容积必须大于0', trigger: 'blur' }
        ],
        compartmentNumber: [
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
      },

      dispatchUnitOptions: [],
      loadingCompanies: false
    };
  },
  created() {
    this.fetchVehicles();
    this.fetchDispatchUnits();
  },
  methods: {
    // 获取车辆列表
    async fetchVehicles() {
      this.loading = true;
      try {
        const response = await vehicleCapacityReferenceService.getVehicleList({
          page: this.currentPage,
          per_page: this.pageSize,
          query: this.searchQuery
        });
        if (response.code === 0) {
          this.vehicles = response.data.items || [];
          this.filteredVehicles = [...this.vehicles];
          this.totalVehicles = response.data.total || 0;
        } else {
          this.$message.error(response.message || '获取车辆列表失败');
        }
      } catch (error) {
        this.$message.error('获取车辆列表失败：' + error.message);
      } finally {
        this.loading = false;
      }
    },
    
    // 搜索处理
    handleSearch() {
      if (!this.searchQuery) {
        this.filteredVehicles = [...this.vehicles];
        return;
      }
      
      const query = this.searchQuery.toLowerCase();
      this.filteredVehicles = this.vehicles.filter(vehicle => {
        return vehicle.license_plate.toLowerCase().includes(query) || 
               vehicle.carriage_number.toLowerCase().includes(query);
      });
    },
    
    // 分页处理
    handleSizeChange(size) {
      this.pageSize = size;
      this.fetchVehicles();
    },
    handleCurrentChange(page) {
      this.currentPage = page;
      this.fetchVehicles();
    },

    // 获取派车单位列表
    async fetchDispatchUnits() {
      this.loadingCompanies = true;
      try {
        const response = await dispatchUnitService.getDispatchUnitList({
          page: 1,
          per_page: 1000 // 获取所有单位
        });
        if (response.code === 0) {
          this.dispatchUnitOptions = response.data.items || [];
        } else {
          this.$message.error(response.message || '获取派车单位列表失败');
        }
      } catch (error) {
        console.error('获取派车单位列表失败:', error);
        this.$message.error('获取派车单位列表失败：' + error.message);
      } finally {
        this.loadingCompanies = false;
      }
    },
    
    // 显示添加车辆对话框
    showAddVehicleDialog(vehicle = null) {
      console.log('showAddVehicleDialog triggered');
      this.dialogTitle = '添加车辆';
      this.vehicleForm = {
        id: null,
        license_plate: '',
        carriage_number: '',
        vehicle_type: '',
        vehicle_category: '',
        original_capacity: 0,
        standard_volume: 0,
        frequent_companies: [],
        suppliers: '',
        status: 'active'
      };
      this.vehicleDialogVisible = true;
    },
    
    // 编辑车辆
    handleEdit(vehicle) {
      this.dialogTitle = '编辑车辆';
      this.vehicleForm = {
        ...vehicle,
        frequent_companies: vehicle.frequent_companies || [],
        license_plate: vehicle.license_plate || '',
        carriage_number: vehicle.carriage_number || '',
        standard_volume: vehicle.standard_volume || 0,
        original_capacity: vehicle.original_capacity || 0,
        vehicle_category: vehicle.vehicle_category || '',
        suppliers: vehicle.suppliers || ''
      };
      this.vehicleDialogVisible = true;
    },
    

    
    // 删除车辆
    handleDelete(vehicle) {
      this.$confirm('确认删除该车辆?', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(async () => {
        try {
          const response = await vehicleCapacityReferenceService.deleteVehicle(vehicle.id);
          if (response.code === 0) {
            this.$message.success('删除成功');
            this.fetchVehicles();
          } else {
            this.$message.error(response.message || '删除失败');
          }
        } catch (error) {
          this.$message.error('删除失败：' + error.message);
        }
      }).catch(() => {
        this.$message.info('已取消删除');
      });
    },
    
    // 提交车辆表单
    submitVehicleForm() {
      console.log('submitVehicleForm triggered');
      this.$refs.vehicleForm.validate(async valid => {
        console.log('Form validation result:', valid);
        if (!valid) return;
        
        try {
          // 创建后端期望的字段映射
          const vehicleData = {
            license_plate: this.vehicleForm.license_plate,
            carriage_number: this.vehicleForm.carriage_number,
            vehicle_type: this.vehicleForm.vehicle_type,
            vehicle_category: this.vehicleForm.vehicle_category,
            original_capacity: this.vehicleForm.original_capacity,
            standard_volume: this.vehicleForm.standard_volume,
            frequent_companies: this.vehicleForm.frequent_companies,
            suppliers: this.vehicleForm.suppliers,
            status: this.vehicleForm.status
          };
          console.log('Submitting vehicle data:', vehicleData);
          
          let response;
          if (this.vehicleForm.id) {
            // 更新车辆
            response = await vehicleCapacityReferenceService.updateVehicle({ id: this.vehicleForm.id, ...vehicleData });
          } else {
            // 添加车辆
            response = await vehicleCapacityReferenceService.createVehicle(vehicleData);
          }
          
          if (response.code === 0) {
            this.$message.success(this.vehicleForm.id ? '更新成功' : '添加成功');
            this.vehicleDialogVisible = false;
            this.fetchVehicles();
          } else {
            this.$message.error(response.message || (this.vehicleForm.id ? '更新失败' : '添加失败'));
          }
        } catch (error) {
          this.$message.error((this.vehicleForm.id ? '更新' : '添加') + '失败：' + error.message);
        }
      });
    },
    
    // 处理车型变化
    handleVehicleTypeChange(value) {
      // 车型变化时的处理逻辑（如果需要的话）
      console.log('车型已变更为:', value);
    },
    
    // 监听车厢号变化，自动设置车辆分类
    handleCarriageNumberChange() {
      if (this.vehicleForm.carriage_number && this.vehicleForm.carriage_number.includes('挂')) {
        this.vehicleForm.vehicle_category = '挂车';
      } else {
        this.vehicleForm.vehicle_category = '单车';
      }
    },

    // 显示导入对话框
    showImportDialog() {
      this.importDialogVisible = true;
    },
    
    // 导入成功回调
    handleImportSuccess() {
      this.$message.success('车辆导入成功');
      this.fetchVehicles(); // 刷新车辆列表
    },
    
    // 获取派车单位列表
    async fetchDispatchUnits() {
      this.loadingCompanies = true;
      try {
        const response = await dispatchUnitService.getDispatchUnitList();
        if (response.code === 0) {
          this.dispatchUnitOptions = response.data.items || response.data || [];
        } else {
          this.$message.error(response.message || '获取派车单位列表失败');
          this.dispatchUnitOptions = [];
        }
      } catch (error) {
        console.error('获取派车单位列表失败:', error);
        this.$message.error('获取派车单位列表失败');
        this.dispatchUnitOptions = [];
      } finally {
        this.loadingCompanies = false;
      }
    },
    

  },
  
  watch: {
    // 监听车厢号变化
    'vehicleForm.carriage_number'() {
      this.handleCarriageNumberChange();
    },
    // 监听车牌号变化
     'vehicleForm.license_plate'() {
       if (!this.vehicleForm.carriage_number) {
         this.vehicleForm.vehicle_category = '单车';
       }
     }
  }
};
</script>

<style scoped>
.vehicle-management {
  padding: 20px;
}

.search-bar {
  display: flex;
  justify-content: space-between;
  margin-bottom: 20px;
}

.search-bar .el-input {
  width: 300px;
  margin-right: 10px;
}

.pagination {
  margin-top: 20px;
  text-align: right;
}
</style>