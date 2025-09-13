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
      
      <el-button 
        type="primary" 
        icon="el-icon-plus" 
        @click="showAddVehicleDialog"
        v-permission="'vehicle:create'"
      >添加车辆</el-button>
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
    <el-dialog :title="dialogTitle" :visible.sync="vehicleDialogVisible" width="50%">
      <el-form :model="vehicleForm" :rules="vehicleRules" ref="vehicleForm" label-width="120px">
        <el-form-item label="车牌号" prop="plateNumber">
          <el-input v-model="vehicleForm.plateNumber"></el-input>
        </el-form-item>
        <el-form-item label="车厢号" prop="compartmentNumber">
          <el-input v-model="vehicleForm.compartmentNumber"></el-input>
        </el-form-item>
        <el-form-item label="车型" prop="vehicleType">
          <el-select v-model="vehicleForm.vehicleType" placeholder="请选择车型">
            <el-option label="5吨" value="5"></el-option>
            <el-option label="8吨" value="8"></el-option>
            <el-option label="12吨" value="12"></el-option>
            <el-option label="20吨" value="20"></el-option>
            <el-option label="30吨" value="30"></el-option>
            <el-option label="40吨A" value="40A"></el-option>
            <el-option label="40吨B" value="40B"></el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="原始载重量(吨)" prop="originalCapacity">
          <el-input-number v-model="vehicleForm.originalCapacity" :min="0" :precision="2"></el-input-number>
        </el-form-item>
        <el-form-item label="实际容积(m³)" prop="actualVolume">
          <el-input-number v-model="vehicleForm.actualVolume" :min="0" :precision="2"></el-input-number>
        </el-form-item>
        <el-form-item label="状态" prop="status">
          <el-switch
            v-model="vehicleForm.status"
            active-value="active"
            inactive-value="inactive"
            active-text="启用"
            inactive-text="禁用"
          ></el-switch>
        </el-form-item>
      </el-form>
      <div slot="footer" class="dialog-footer">
        <el-button @click="vehicleDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitVehicleForm">确定</el-button>
      </div>
    </el-dialog>
    
    <!-- 更新容积对话框 -->
    <volume-form 
      :visible.sync="volumeDialogVisible" 
      :vehicle="selectedVehicle" 
      @update-success="handleVolumeUpdateSuccess"
    ></volume-form>
  </div>
</template>

<script>
import VolumeForm from './components/VolumeForm.vue';
import { getVehicleList, addVehicle, updateVehicle, deleteVehicle } from '@/services/vehicleService';
import permission from '@/directives/permission';

export default {
  name: 'VehicleManagement',
  components: {
    VolumeForm
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
      dialogTitle: '',
      selectedVehicle: null,
      vehicleForm: {
        id: null,
        plateNumber: '',
        compartmentNumber: '',
        vehicleType: '',
        originalCapacity: 0,
        actualVolume: 0,
        conversionFactor: 0,
        status: 'active'
      },
      vehicleRules: {
        plateNumber: [
          { required: true, message: '请输入车牌号', trigger: 'blur' },
          { min: 5, max: 10, message: '长度在 5 到 10 个字符', trigger: 'blur' }
        ],
        compartmentNumber: [
          { required: true, message: '请输入车厢号', trigger: 'blur' }
        ],
        vehicleType: [
          { required: true, message: '请选择车型', trigger: 'change' }
        ],
        originalCapacity: [
          { required: true, message: '请输入原始载重量', trigger: 'blur' }
        ],
        actualVolume: [
          { required: true, message: '请输入实际容积', trigger: 'blur' }
        ]
      },
      // 车型折算系数表
      conversionFactors: {
        '5': 0.45,
        '8': 0.51,
        '12': 0.63,
        '20': 0.83,
        '30': 1.00,
        '40A': 1.12,
        '40B': 1.23
      }
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
        const response = await getVehicleList({
          page: this.currentPage,
          pageSize: this.pageSize,
          query: this.searchQuery
        });
        this.vehicles = response.data.items;
        this.filteredVehicles = [...this.vehicles];
        this.totalVehicles = response.data.total;
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
    showAddVehicleDialog() {
      this.dialogTitle = '添加车辆';
      this.vehicleForm = {
        id: null,
        plateNumber: '',
        compartmentNumber: '',
        vehicleType: '',
        originalCapacity: 0,
        actualVolume: 0,
        conversionFactor: 0,
        status: 'active'
      };
      this.vehicleDialogVisible = true;
    },
    
    // 编辑车辆
    handleEdit(vehicle) {
      this.dialogTitle = '编辑车辆';
      this.vehicleForm = { ...vehicle };
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
      this.$refs.vehicleForm.validate(async valid => {
        if (!valid) return;
        
        try {
          // 根据车型设置折算系数
          this.vehicleForm.conversionFactor = this.conversionFactors[this.vehicleForm.vehicleType] || 0;
          
          if (this.vehicleForm.id) {
            // 更新车辆
            await updateVehicle(this.vehicleForm);
            this.$message.success('更新成功');
          } else {
            // 添加车辆
            await addVehicle(this.vehicleForm);
            this.$message.success('添加成功');
          }
          
          this.vehicleDialogVisible = false;
          this.fetchVehicles();
        } catch (error) {
          this.$message.error((this.vehicleForm.id ? '更新' : '添加') + '失败：' + error.message);
        }
      });
    },
    
    // 容积更新成功回调
    handleVolumeUpdateSuccess() {
      this.fetchVehicles();
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