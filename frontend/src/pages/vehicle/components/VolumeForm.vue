<template>
  <el-dialog
    title="更新车辆容积"
    :visible.sync="dialogVisible"
    width="60%"
    @close="handleClose"
  >
    <div v-if="vehicle" class="volume-form">
      <!-- 车辆基本信息 -->
      <el-card class="info-card">
        <div slot="header">
          <span>车辆基本信息</span>
        </div>
        <el-row :gutter="20">
          <el-col :span="12">
            <div class="info-item">
              <span class="label">车牌号:</span>
              <span class="value">{{ vehicle.plateNumber }}</span>
            </div>
          </el-col>
          <el-col :span="12">
            <div class="info-item">
              <span class="label">车厢号:</span>
              <span class="value">{{ vehicle.compartmentNumber }}</span>
            </div>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <div class="info-item">
              <span class="label">原始载重量:</span>
              <span class="value">{{ vehicle.originalCapacity }}吨</span>
            </div>
          </el-col>
          <el-col :span="12">
            <div class="info-item">
              <span class="label">当前实际容积:</span>
              <span class="value">{{ vehicle.actualVolume }}m³</span>
            </div>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="12">
            <div class="info-item">
              <span class="label">车型:</span>
              <span class="value">{{ formatVehicleType(vehicle.vehicleType) }}</span>
            </div>
          </el-col>
          <el-col :span="12">
            <div class="info-item">
              <span class="label">折算系数:</span>
              <span class="value">{{ vehicle.conversionFactor }}</span>
            </div>
          </el-col>
        </el-row>
      </el-card>

      <!-- 车型折算系数表 -->
      <el-card class="conversion-table-card">
        <div slot="header">
          <span>车型折算系数表（参考）</span>
        </div>
        <el-table :data="conversionTableData" border style="width: 100%">
          <el-table-column prop="type" label="车型"></el-table-column>
          <el-table-column prop="volume" label="容积(m³)"></el-table-column>
          <el-table-column prop="factor" label="车型折算系数"></el-table-column>
        </el-table>
      </el-card>

      <!-- 容积更新表单 -->
      <el-form :model="form" :rules="rules" ref="volumeForm" label-width="120px" class="update-form">
        <el-form-item label="新实际容积(m³)" prop="newVolume">
          <el-input-number 
            v-model="form.newVolume" 
            :min="minVolume" 
            :max="maxVolume" 
            :precision="2"
          ></el-input-number>
          <span class="volume-range">允许范围: {{ minVolume }} ~ {{ maxVolume }}m³</span>
        </el-form-item>
        
        <el-form-item label="修改原因" prop="reason">
          <el-input 
            type="textarea" 
            v-model="form.reason" 
            :rows="3"
            placeholder="请详细说明修改容积的原因"
          ></el-input>
        </el-form-item>
        
        <el-form-item label="容积照片" prop="volumePhoto">
          <el-upload
            class="upload-container"
            action="/api/upload/image"
            :on-preview="handlePreview"
            :on-remove="handleRemove"
            :on-success="handleVolumePhotoSuccess"
            :before-upload="beforeUpload"
            :limit="1"
            :file-list="volumePhotoList"
            list-type="picture"
          >
            <el-button size="small" type="primary">选择文件</el-button>
            <div slot="tip" class="el-upload__tip">支持jpg/png格式，不超过5MB</div>
          </el-upload>
        </el-form-item>
        
        <el-form-item label="审批凭证" prop="approvalDocument">
          <el-upload
            class="upload-container"
            action="/api/upload/document"
            :on-preview="handlePreview"
            :on-remove="handleRemove"
            :on-success="handleApprovalDocSuccess"
            :before-upload="beforeUpload"
            :limit="1"
            :file-list="approvalDocList"
            list-type="picture"
          >
            <el-button size="small" type="primary">选择文件</el-button>
            <div slot="tip" class="el-upload__tip">支持jpg/png/pdf格式，不超过10MB</div>
          </el-upload>
        </el-form-item>
      </el-form>
    </div>
    
    <div slot="footer" class="dialog-footer">
      <el-button @click="dialogVisible = false">取消</el-button>
      <el-button type="primary" @click="submitForm" :loading="submitting">提交</el-button>
    </div>
    
    <!-- 图片预览 -->
    <el-dialog
      title="预览"
      :visible.sync="previewVisible"
      append-to-body
      width="50%"
    >
      <img width="100%" :src="previewUrl" alt="预览图">
    </el-dialog>
  </el-dialog>
</template>

<script>
import { updateVehicleVolume } from '@/services/vehicleService';

export default {
  name: 'VolumeForm',
  props: {
    visible: {
      type: Boolean,
      default: false
    },
    vehicle: {
      type: Object,
      default: null
    }
  },
  data() {
    // 验证容积范围
    const validateVolume = (rule, value, callback) => {
      if (value < this.minVolume || value > this.maxVolume) {
        callback(new Error(`容积必须在 ${this.minVolume} 到 ${this.maxVolume} 之间`));
      } else {
        callback();
      }
    };
    
    return {
      dialogVisible: this.visible,
      form: {
        newVolume: 0,
        reason: '',
        volumePhotoUrl: '',
        approvalDocUrl: ''
      },
      rules: {
        newVolume: [
          { required: true, message: '请输入新实际容积', trigger: 'blur' },
          { validator: validateVolume, trigger: 'blur' }
        ],
        reason: [
          { required: true, message: '请输入修改原因', trigger: 'blur' },
          { min: 10, max: 500, message: '长度在 10 到 500 个字符', trigger: 'blur' }
        ],
        volumePhotoUrl: [
          { required: true, message: '请上传容积照片', trigger: 'change' }
        ],
        approvalDocUrl: [
          { required: true, message: '请上传审批凭证', trigger: 'change' }
        ]
      },
      volumePhotoList: [],
      approvalDocList: [],
      previewVisible: false,
      previewUrl: '',
      submitting: false,
      // 车型折算系数表数据
      conversionTableData: [
        { type: '5吨', volume: '≥35', factor: '0.45' },
        { type: '8吨', volume: '≥45', factor: '0.51' },
        { type: '12吨', volume: '≥55', factor: '0.63' },
        { type: '20吨', volume: '≥100', factor: '0.83' },
        { type: '30吨', volume: '≥130', factor: '1.00' },
        { type: '40吨A', volume: '≥150', factor: '1.12' },
        { type: '40吨B', volume: '≥180', factor: '1.23' }
      ]
    };
  },
  computed: {
    // 计算容积允许的最小值（当前容积的80%）
    minVolume() {
      return this.vehicle ? Math.round(this.vehicle.actualVolume * 0.8 * 100) / 100 : 0;
    },
    // 计算容积允许的最大值（当前容积的120%）
    maxVolume() {
      return this.vehicle ? Math.round(this.vehicle.actualVolume * 1.2 * 100) / 100 : 0;
    }
  },
  watch: {
    visible(val) {
      this.dialogVisible = val;
    },
    vehicle(val) {
      if (val) {
        this.form.newVolume = val.actualVolume;
      }
    },
    dialogVisible(val) {
      this.$emit('update:visible', val);
    }
  },
  methods: {
    // 格式化车型显示
    formatVehicleType(type) {
      if (type === '40A') return '40吨A';
      if (type === '40B') return '40吨B';
      return `${type}吨`;
    },
    
    // 处理对话框关闭
    handleClose() {
      this.$refs.volumeForm.resetFields();
      this.volumePhotoList = [];
      this.approvalDocList = [];
      this.form = {
        newVolume: this.vehicle ? this.vehicle.actualVolume : 0,
        reason: '',
        volumePhotoUrl: '',
        approvalDocUrl: ''
      };
    },
    
    // 文件上传前验证
    beforeUpload(file) {
      // 容积照片验证
      if (file.name.endsWith('.jpg') || file.name.endsWith('.jpeg') || file.name.endsWith('.png')) {
        const isLt5M = file.size / 1024 / 1024 < 5;
        if (!isLt5M) {
          this.$message.error('上传图片大小不能超过 5MB!');
          return false;
        }
        return true;
      }
      
      // 审批凭证验证（允许PDF）
      if (file.name.endsWith('.pdf')) {
        const isLt10M = file.size / 1024 / 1024 < 10;
        if (!isLt10M) {
          this.$message.error('上传PDF大小不能超过 10MB!');
          return false;
        }
        return true;
      }
      
      this.$message.error('上传文件格式不正确!');
      return false;
    },
    
    // 处理容积照片上传成功
    handleVolumePhotoSuccess(response, file, fileList) {
      if (response.code === 0) {
        this.form.volumePhotoUrl = response.data.url;
      } else {
        this.$message.error('上传失败：' + response.message);
      }
    },
    
    // 处理审批凭证上传成功
    handleApprovalDocSuccess(response, file, fileList) {
      if (response.code === 0) {
        this.form.approvalDocUrl = response.data.url;
      } else {
        this.$message.error('上传失败：' + response.message);
      }
    },
    
    // 处理文件预览
    handlePreview(file) {
      this.previewUrl = file.url;
      this.previewVisible = true;
    },
    
    // 处理文件移除
    handleRemove(file, fileList) {
      if (file.response && file.response.data) {
        const url = file.response.data.url;
        if (this.form.volumePhotoUrl === url) {
          this.form.volumePhotoUrl = '';
        }
        if (this.form.approvalDocUrl === url) {
          this.form.approvalDocUrl = '';
        }
      }
    },
    
    // 提交表单
    submitForm() {
      this.$refs.volumeForm.validate(async valid => {
        if (!valid) return;
        
        this.submitting = true;
        try {
          const data = {
            vehicleId: this.vehicle.id,
            originalVolume: this.vehicle.actualVolume,
            newVolume: this.form.newVolume,
            reason: this.form.reason,
            volumePhotoUrl: this.form.volumePhotoUrl,
            approvalDocUrl: this.form.approvalDocUrl
          };
          
          await updateVehicleVolume(data);
          this.$message.success('车辆容积更新成功');
          this.dialogVisible = false;
          this.$emit('update-success');
        } catch (error) {
          this.$message.error('更新失败：' + error.message);
        } finally {
          this.submitting = false;
        }
      });
    }
  }
};
</script>

<style scoped>
.volume-form {
  margin-bottom: 20px;
}

.info-card {
  margin-bottom: 20px;
}

.info-item {
  margin-bottom: 10px;
  line-height: 24px;
}

.label {
  font-weight: bold;
  margin-right: 10px;
  color: #606266;
}

.value {
  color: #303133;
}

.conversion-table-card {
  margin-bottom: 20px;
}

.update-form {
  margin-top: 20px;
}

.volume-range {
  margin-left: 10px;
  color: #909399;
  font-size: 12px;
}

.upload-container {
  width: 100%;
}

.el-upload__tip {
  line-height: 1.2;
}
</style>