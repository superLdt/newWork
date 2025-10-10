<template>
  <div class="system-config">
    <el-card class="config-card">
      <template #header>
        <div class="card-header">
          <span>系统配置</span>
        </div>
      </template>
      
      <!-- 管理员信息展示区域 -->
      <el-card class="admin-info-card" shadow="hover">
        <div class="admin-info-header">
          <el-icon class="admin-icon"><User /></el-icon>
          <span class="admin-title">当前管理员信息</span>
        </div>
        <el-divider />
        <div class="admin-info-content">
          <el-row :gutter="20">
            <el-col :span="12">
              <div class="info-item">
                <span class="info-label">用户名：</span>
                <span class="info-value">{{ currentUser.full_name || currentUser.username || '未知' }}</span>
              </div>
            </el-col>
            <el-col :span="12">
              <div class="info-item">
                <span class="info-label">登录角色：</span>
                <span class="info-value">{{ currentUserRole || '系统管理员' }}</span>
              </div>
            </el-col>
          </el-row>
          <el-row :gutter="20">
            <el-col :span="12">
              <div class="info-item">
                <span class="info-label">邮箱：</span>
                <span class="info-value">{{ currentUser.email || '未设置' }}</span>
              </div>
            </el-col>
            <el-col :span="12">
              <div class="info-item">
                <span class="info-label">联系电话：</span>
                <span class="info-value">{{ currentUser.phone || '未设置' }}</span>
              </div>
            </el-col>
          </el-row>
        </div>
      </el-card>
      
      <el-tabs v-model="activeTab">
        <el-tab-pane label="基本设置" name="basic">
          <el-form 
            :model="basicConfig" 
            label-width="120px" 
            class="config-form"
          >
            <el-form-item label="系统名称">
              <el-input v-model="basicConfig.systemName" />
            </el-form-item>
            <el-form-item label="系统Logo">
              <el-upload
                class="avatar-uploader"
                action="#"
                :show-file-list="false"
              >
                <img v-if="basicConfig.logo" :src="basicConfig.logo" class="avatar" />
                <el-icon v-else class="avatar-uploader-icon"><Plus /></el-icon>
              </el-upload>
            </el-form-item>
            <el-form-item label="默认语言">
              <el-select v-model="basicConfig.language">
                <el-option label="中文" value="zh-CN"></el-option>
                <el-option label="English" value="en-US"></el-option>
              </el-select>
            </el-form-item>
            <el-form-item label="时区设置">
              <el-select v-model="basicConfig.timezone">
                <el-option label="北京时间 (UTC+8)" value="UTC+8"></el-option>
                <el-option label="东京时间 (UTC+9)" value="UTC+9"></el-option>
                <el-option label="纽约时间 (UTC-5)" value="UTC-5"></el-option>
              </el-select>
            </el-form-item>
            <el-form-item label="启用维护模式">
              <el-switch v-model="basicConfig.maintenanceMode" />
            </el-form-item>
          </el-form>
        </el-tab-pane>
        
        <el-tab-pane label="邮件设置" name="email">
          <el-form 
            :model="emailConfig" 
            label-width="120px" 
            class="config-form"
          >
            <el-form-item label="SMTP服务器">
              <el-input v-model="emailConfig.smtpServer" />
            </el-form-item>
            <el-form-item label="端口">
              <el-input v-model="emailConfig.port" style="width: 200px;" />
            </el-form-item>
            <el-form-item label="用户名">
              <el-input v-model="emailConfig.username" />
            </el-form-item>
            <el-form-item label="密码">
              <el-input v-model="emailConfig.password" type="password" show-password />
            </el-form-item>
            <el-form-item label="发件人邮箱">
              <el-input v-model="emailConfig.senderEmail" />
            </el-form-item>
            <el-form-item label="启用SSL">
              <el-switch v-model="emailConfig.sslEnabled" />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="testEmailConfig">测试连接</el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>
        
        <el-tab-pane label="安全设置" name="security">
          <el-form 
            :model="securityConfig" 
            label-width="150px" 
            class="config-form"
          >
            <el-form-item label="密码最小长度">
              <el-input-number v-model="securityConfig.minPasswordLength" :min="6" :max="20" />
            </el-form-item>
            <el-form-item label="密码复杂度要求">
              <el-checkbox-group v-model="securityConfig.passwordRequirements">
                <el-checkbox label="uppercase">大写字母</el-checkbox>
                <el-checkbox label="lowercase">小写字母</el-checkbox>
                <el-checkbox label="number">数字</el-checkbox>
                <el-checkbox label="special">特殊字符</el-checkbox>
              </el-checkbox-group>
            </el-form-item>
            <el-form-item label="会话超时时间(分钟)">
              <el-slider 
                v-model="securityConfig.sessionTimeout" 
                :min="5" 
                :max="120" 
                show-input 
              />
            </el-form-item>
            <el-form-item label="启用双因素认证">
              <el-switch v-model="securityConfig.twoFactorAuth" />
            </el-form-item>
            <el-form-item label="登录失败尝试次数">
              <el-input-number v-model="securityConfig.maxLoginAttempts" :min="1" :max="10" />
            </el-form-item>
          </el-form>
        </el-tab-pane>
      </el-tabs>
      
      <div class="form-actions">
        <el-button type="primary" @click="saveConfig">保存配置</el-button>
        <el-button @click="resetConfig">重置</el-button>
      </div>
    </el-card>
  </div>
</template>

<script>
import { Plus } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { User } from '@element-plus/icons-vue'

export default {
  name: 'SystemConfig',
  components: {
    Plus,
    User
  },
  data() {
    return {
      activeTab: 'basic',
      basicConfig: {
        systemName: '智能运力系统',
        logo: '',
        language: 'zh-CN',
        timezone: 'UTC+8',
        maintenanceMode: false
      },
      emailConfig: {
        smtpServer: 'smtp.example.com',
        port: 587,
        username: 'admin@example.com',
        password: '',
        senderEmail: 'noreply@example.com',
        sslEnabled: true
      },
      securityConfig: {
        minPasswordLength: 8,
        passwordRequirements: ['uppercase', 'lowercase', 'number'],
        sessionTimeout: 30,
        twoFactorAuth: false,
        maxLoginAttempts: 5
      },
      currentUser: {},
      currentUserRole: ''
    }
  },
  mounted() {
    this.getCurrentUser()
  },
  methods: {
    getCurrentUser() {
      try {
        const user = JSON.parse(localStorage.getItem('user')) || {}
        this.currentUser = user
        
        // 获取用户角色，如果有多个角色，显示第一个
        if (user.roles && user.roles.length > 0) {
          this.currentUserRole = user.roles[0].name || '系统管理员'
        } else {
          this.currentUserRole = '系统管理员'
        }
      } catch (error) {
        console.error('获取用户信息失败:', error)
        this.currentUser = {}
        this.currentUserRole = '系统管理员'
      }
    },
    saveConfig() {
      ElMessage.success('配置保存成功')
    },
    resetConfig() {
      ElMessageBox.confirm(
        '确定要重置所有配置为默认值吗？',
        '确认重置',
        {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        }
      ).then(() => {
        // 重置为默认配置
        this.basicConfig = {
          systemName: '智能运力系统',
          logo: '',
          language: 'zh-CN',
          timezone: 'UTC+8',
          maintenanceMode: false
        }
        this.emailConfig = {
          smtpServer: 'smtp.example.com',
          port: 587,
          username: 'admin@example.com',
          password: '',
          senderEmail: 'noreply@example.com',
          sslEnabled: true
        }
        this.securityConfig = {
          minPasswordLength: 8,
          passwordRequirements: ['uppercase', 'lowercase', 'number'],
          sessionTimeout: 30,
          twoFactorAuth: false,
          maxLoginAttempts: 5
        }
        ElMessage.success('配置已重置为默认值')
      }).catch(() => {
        // 用户取消重置
      })
    },
    testEmailConfig() {
      ElMessage.info('正在测试邮件配置...')
      // 模拟测试过程
      setTimeout(() => {
        ElMessage.success('邮件配置测试成功')
      }, 1000)
    }
  }
}
</script>

<style scoped>
.system-config {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.config-form {
  max-width: 600px;
  margin: 20px 0;
}

.avatar-uploader .avatar {
  width: 100px;
  height: 100px;
  display: block;
}

.avatar-uploader-icon {
  font-size: 28px;
  color: #8c939d;
  width: 100px;
  height: 100px;
  text-align: center;
  border: 1px dashed #d9d9d9;
  border-radius: 6px;
  cursor: pointer;
  transition: border-color 0.3s;
}

.avatar-uploader-icon:hover {
  border-color: #409eff;
}

.form-actions {
  margin-top: 30px;
  padding-top: 20px;
  border-top: 1px solid #e4e7ed;
}

.form-actions .el-button {
  margin-right: 10px;
}

.admin-info-card {
  margin-bottom: 20px;
  border-radius: 8px;
  transition: all 0.3s ease;
  max-width: 100%;
  box-sizing: border-box;
}

.admin-info-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.admin-info-header {
  display: flex;
  align-items: center;
  margin-bottom: 10px;
}

.admin-icon {
  font-size: 20px;
  color: #409eff;
  margin-right: 8px;
  flex-shrink: 0;
}

.admin-title {
  font-size: 18px;
  font-weight: bold;
  color: #303133;
}

.info-item {
  display: flex;
  margin-bottom: 12px;
  align-items: center;
  flex-wrap: wrap;
}

.info-label {
  font-weight: 500;
  color: #606266;
  width: 80px;
  text-align: right;
  margin-right: 10px;
  flex-shrink: 0;
  line-height: 1.5;
}

.info-value {
  color: #303133;
  flex: 1;
  min-width: 0;
  word-break: break-all;
  line-height: 1.5;
}

.el-divider {
  margin: 15px 0;
}

/* 响应式优化 */
@media (max-width: 768px) {
  .admin-info-card {
    padding: 15px;
  }
  
  .info-item {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .info-label {
    width: 100%;
    text-align: left;
    margin-bottom: 4px;
  }
  
  .info-value {
    width: 100%;
  }
}
</style>