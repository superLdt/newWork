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
      <el-table-column prop="plateNumber" label="车牌号" width="120"></el-table-column>
      <el-table-column prop="compartmentNumber" label="车厢号" width="120"></el-table-column>
      <el-table-column prop="vehicleType" label="车型" width="100">
        <template slot-scope="scope">
          {{ scope.row.vehicleType }}吨
        </template>
      </el-table-column>
      <el-table-column prop="originalCapacity" label="原始载重量(吨)" width="150"></el-table-column>
      <el-table-column prop="actualVolume" label="实际容积(m³)" width="150"></el-table-column>
      <el-table-column prop="conversionFactor" label="折算系数" width="120"></el-table-column>
      <el-table-column prop="status" label="状态" width="100">
        <template slot-scope="scope">
          <el-tag :type="scope.row.status === 'active' ? 'success' : 'info'">
            {{ scope.row.status === 'active' ? '启用' : '禁用' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="lastUpdated" label="最后更新时间" width="180"></el-table-column>
      <el-table-column label="操作" fixed="right" width="250">
        <template slot-scope="scope">
          <el-button 
            size="mini" 
            type="primary" 
            @click="handleEdit(scope.row)"
            v-permission="'vehicle:update'"
          >编辑</el-button>
          <el-button 
            size="mini" 
            type="success" 
            @click="handleUpdateVolume(scope.row)"
            v-permission="'workshop:update_volume'"
          >更新容积</el-button>
          <el-button 
            size="mini" 
            type="danger" 
            @click="handleDelete(scope.row)"
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
              <el-input v-model="vehicleForm.plateNumber" placeholder="请输入车牌号"></el-input>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="车厢号" prop="compartmentNumber">
              <el-input v-model="vehicleForm.compartmentNumber" placeholder="如：皖A36T3挂"></el-input>
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="车型" prop="vehicleType">
              <el-select v-model="vehicleForm.vehicleType" placeholder="请选择车型" @change="handleVehicleTypeChange">
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
              <el-input v-model="vehicleForm.vehicleCategory" readonly placeholder="自动识别"></el-input>
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="实际容积(m³)" prop="actualVolume">
              <el-input-number v-model="vehicleForm.actualVolume" :min="0.1" :precision="2" placeholder="必填"></el-input-number>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="原始载重量(吨)">
              <el-input-number v-model="vehicleForm.originalCapacity" :min="0" :precision="2"></el-input-number>
            </el-form-item>
          </el-col>
        </el-row>
        
        <el-form-item label="常用公司">
          <el-select 
            v-model="vehicleForm.frequentCompanies" 
            multiple 
            filterable 
            allow-create 
            placeholder="请选择或输入常用公司"
            style="width: 100%"
          >
            <el-option 
              v-for="company in companyOptions" 
              :key="company" 
              :label="company" 
              :value="company"
            ></el-option>
          </el-select>
        </el-form-item>
        
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="供应商类型">
              <el-select v-model="vehicleForm.supplierType" placeholder="请选择供应商类型">
                <el-option 
                  v-for="option in supplierTypeOptions" 
                  :key="option.value" 
                  :label="option.label" 
                  :value="option.value"
                ></el-option>
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
        
        <el-form-item label="备注">
          <el-input 
            v-model="vehicleForm.notes" 
            type="textarea" 
            :rows="3" 
            placeholder="请输入备注信息"
          ></el-input>
        </el-form-item>
      </el-form>
+      <template #footer>
+        <div class="dialog-footer">
+          <el-button @click="vehicleDialogVisible = false">取消</el-button>
+          <el-button type="primary" @click="submitVehicleForm">确定</el-button>
+        </div>
+      </template>
     </el-dialog>
    
    <!-- 更新容积对话框 -->
    <volume-form 
      :visible.sync="volumeDialogVisible" 
      :vehicle="selectedVehicle" 
      @update-success="handleVolumeUpdateSuccess"
    ></volume-form>
    
    <!-- 批量导入对话框 -->
    <vehicle-import-dialog 
      v-model="importDialogVisible" 
      @import-success="handleImportSuccess"
    ></vehicle-import-dialog>
  </div>
</template>

<script>
import VolumeForm from './components/VolumeForm.vue';
import VehicleImportDialog from '@/components/VehicleImportDialog.vue';
import { vehicleService, addVehicle, updateVehicle, deleteVehicle } from '@/services/vehicleService';
import permission from '@/directives/permission';
import { Upload } from '@element-plus/icons-vue';

export default {
  name: 'VehicleManagement',
  components: {
    VolumeForm,
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
      volumeDialogVisible: false,
      importDialogVisible: false,
      dialogTitle: '',
      selectedVehicle: null,
      vehicleForm: {
        id: null,
        plateNumber: '',
        compartmentNumber: '',
        vehicleType: '',
        vehicleCategory: '',
        originalCapacity: 0,
        actualVolume: 0,
        conversionFactor: 0,
        frequentCompanies: [],
        notes: '',
        supplierType: '',
        status: 'active'
      },
      vehicleRules: {
        // 自定义验证：车牌号或车厢号至少填一个
        plateOrCarriage: [
          {
            validator: (rule, value, callback) => {
              if (!this.vehicleForm.plateNumber && !this.vehicleForm.compartmentNumber) {
                callback(new Error('车牌号或车厢号至少需要填写一个'))
              } else {
                callback()
              }
            },
            trigger: 'blur'
          }
        ],
        actualVolume: [
          { required: true, message: '请输入容积', trigger: 'blur' },
          { type: 'number', min: 0.1, message: '容积必须大于0', trigger: 'blur' }
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
      // 车型折算系数表
      conversionFactors: {
        '5吨': 0.45,
        '8吨': 0.51,
        '12吨': 0.63,
        '20吨': 0.83,
        '30吨': 1.00,
        '40吨A': 1.12,
        '40吨B': 1.23
      },
      // 供应商类型选项
      supplierTypeOptions: [
        { value: '委办公司', label: '委办公司' },
        { value: '班组', label: '班组' },
        { value: '承运商', label: '承运商' }
      ],
      // 公司选项（示例数据，实际应从后端获取）
      companyOptions: [
        '公司A', '公司B', '公司C', '公司D', '公司E'
      ]
    };
  },
  created() {
    this.fetchVehicles();
  },
  methods: {
    // 获取车辆列表
    async fetchVehicles() {
      this.loading = true;
      try {
        const response = await vehicleService.getVehicleList({
          page: this.currentPage,
          pageSize: this.pageSize,
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
        return vehicle.plateNumber.toLowerCase().includes(query) || 
               vehicle.compartmentNumber.toLowerCase().includes(query);
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
    
    // 显示添加车辆对话框
    showAddVehicleDialog(vehicle = null) {
      console.log('showAddVehicleDialog triggered');
      this.dialogTitle = '添加车辆';
      this.vehicleForm = {
        id: null,
        plateNumber: '',
        compartmentNumber: '',
        vehicleType: '',
        vehicleCategory: '',
        originalCapacity: 0,
        actualVolume: 0,
        conversionFactor: 0,
        frequentCompanies: [],
        notes: '',
        supplierType: '',
        status: 'active'
      };
      this.vehicleDialogVisible = true;
    },
    
    // 编辑车辆
    handleEdit(vehicle) {
      this.dialogTitle = '编辑车辆';
      this.vehicleForm = {
        ...vehicle,
        frequentCompanies: vehicle.frequent_companies || [],
        plateNumber: vehicle.license_plate || '',
        compartmentNumber: vehicle.carriage_number || '',
        actualVolume: vehicle.actual_volume || 0,
        originalCapacity: vehicle.original_capacity || 0,
        vehicleCategory: vehicle.vehicle_category || '',
        supplierType: vehicle.supplier_type || ''
      };
      this.vehicleDialogVisible = true;
    },
    
    // 更新容积
    handleUpdateVolume(vehicle) {
      this.selectedVehicle = vehicle;
      this.volumeDialogVisible = true;
    },
    
    // 删除车辆
    handleDelete(vehicle) {
      this.$confirm('确认删除该车辆?', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(async () => {
        try {
          await deleteVehicle(vehicle.id);
          this.$message.success('删除成功');
          this.fetchVehicles();
        } catch (error) {
          this.$message.error('删除失败：' + error.message);
        }
      }).catch(() => {
        this.$message.info('已取消删除');
      });
    },
    
    // 提交车辆表单
    submitVehicleForm() {
      console.log('submitVehicleForm triggered'); // Add this line
      this.$refs.vehicleForm.validate(async valid => {
        console.log('Form validation result:', valid); // Add this line
        if (!valid) return;
        
        try {
          // 根据车型设置折算系数
          this.vehicleForm.conversionFactor = this.conversionFactors[this.vehicleForm.vehicleType] || 0;
          
          // 创建后端期望的字段映射
          const vehicleData = {
            license_plate: this.vehicleForm.plateNumber,
            carriage_number: this.vehicleForm.compartmentNumber,
            vehicle_type: this.vehicleForm.vehicleType,
            vehicle_category: this.vehicleForm.vehicleCategory,
            original_capacity: this.vehicleForm.originalCapacity,
            actual_volume: this.vehicleForm.actualVolume,
            frequent_companies: this.vehicleForm.frequentCompanies,
            notes: this.vehicleForm.notes,
            supplier_type: this.vehicleForm.supplierType,
            status: this.vehicleForm.status
          };
          console.log('Submitting vehicle data:', vehicleData); // Add this line
          
          if (this.vehicleForm.id) {
            // 更新车辆
            await updateVehicle({ id: this.vehicleForm.id, ...vehicleData });
            this.$message.success('更新成功');
          } else {
            // 添加车辆
            await addVehicle(vehicleData);
            this.$message.success('添加成功');
          }
          
          this.vehicleDialogVisible = false;
          this.fetchVehicles();
        } catch (error) {
          this.$message.error((this.vehicleForm.id ? '更新' : '添加') + '失败：' + error.message);
        }
      });
    },
    
    // 处理车型变化
    handleVehicleTypeChange(value) {
      // 根据车型自动设置折算系数
      this.vehicleForm.conversionFactor = this.conversionFactors[value] || 0;
    },
    
    // 监听车厢号变化，自动设置车辆分类
    handleCarriageNumberChange() {
      if (this.vehicleForm.compartmentNumber && this.vehicleForm.compartmentNumber.includes('挂')) {
        this.vehicleForm.vehicleCategory = '挂车';
      } else {
        this.vehicleForm.vehicleCategory = '单车';
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
    
    // 容积更新成功回调
    handleVolumeUpdateSuccess() {
      this.fetchVehicles();
    }
  },
  
  watch: {
    // 监听车厢号变化
    'vehicleForm.compartmentNumber'() {
      this.handleCarriageNumberChange();
    },
    // 监听车牌号变化
     'vehicleForm.plateNumber'() {
       if (!this.vehicleForm.compartmentNumber) {
         this.vehicleForm.vehicleCategory = '单车';
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