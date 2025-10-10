<template>
  <div class="login-page">
    <div class="login-container">
      <div class="login-left">
        <div class="brand">
          <div class="logo">
            <el-icon :size="40"><Avatar /></el-icon>
          </div>
          <h1>智能运力系统</h1>
          <p class="slogan">高效、智能的运输管理平台</p>
        </div>
        
        <div class="features">
          <div class="feature-item">
            <el-icon :size="20" color="#409eff"><Check /></el-icon>
            <span>智能调度优化</span>
          </div>
          <div class="feature-item">
            <el-icon :size="20" color="#409eff"><Check /></el-icon>
            <span>实时数据监控</span>
          </div>
          <div class="feature-item">
            <el-icon :size="20" color="#409eff"><Check /></el-icon>
            <span>多维度报表分析</span>
          </div>
        </div>
      </div>
      
      <div class="login-right">
        <div class="login-card">
          <div class="login-header">
            <h2>欢迎回来</h2>
            <p>请登录您的账户</p>
          </div>
          
          <!-- 登录方式切换 -->
          <div class="login-methods">
            <el-tabs v-model="activeTab" class="login-tabs">
              <el-tab-pane label="账号密码登录" name="password">
                <el-form 
                  :model="loginForm" 
                  :rules="loginRules" 
                  ref="loginForm" 
                  class="login-form"
                  @submit.prevent="handleLogin"
                >
                  <el-form-item prop="username">
                    <el-input 
                      v-model="loginForm.username" 
                      placeholder="用户名/邮箱"
                      size="large"
                      clearable
                      class="login-input"
                    >
                      <template #prefix>
                        <el-icon><User /></el-icon>
                      </template>
                    </el-input>
                  </el-form-item>
                  
                  <el-form-item prop="password">
                    <el-input 
                      v-model="loginForm.password" 
                      type="password" 
                      placeholder="密码"
                      show-password
                      size="large"
                      class="login-input"
                    >
                      <template #prefix>
                        <el-icon><Lock /></el-icon>
                      </template>
                    </el-input>
                  </el-form-item>
                  
                  <div class="form-options">
                    <el-checkbox v-model="rememberMe" size="small">记住我</el-checkbox>
                    <el-link type="primary" :underline="false" size="small">忘记密码？</el-link>
                  </div>
                  
                  <el-form-item>
                    <el-button 
                      type="primary" 
                      native-type="submit" 
                      :loading="loading"
                      class="login-button"
                      size="large"
                      round
                    >
                      {{ loading ? '登录中...' : '登录' }}
                    </el-button>
                  </el-form-item>
                  
                  <!-- 错误提示 -->
                  <div v-if="errorMessage" class="error-message">
                    <el-alert 
                      :title="errorMessage" 
                      type="error" 
                      show-icon 
                      :closable="false"
                      class="error-alert"
                    />
                  </div>
                </el-form>
              </el-tab-pane>
              
              <el-tab-pane label="飞书扫码登录" name="feishu">
                <div class="feishu-login">
                  <div class="qrcode-container">
                    <div class="qrcode-placeholder">
                      <el-icon :size="48" color="#409eff"><Monitor /></el-icon>
                      <p>飞书扫码登录</p>
                    </div>
                  </div>
                  <p class="qrcode-tip">请使用飞书扫描二维码登录</p>
                  <el-button 
                    type="primary" 
                    class="refresh-qrcode"
                    @click="refreshQrCode"
                    size="small"
                    link
                  >
                    刷新二维码
                  </el-button>
                </div>
              </el-tab-pane>
            </el-tabs>
          </div>
          
          <div class="third-party-login">
            <p class="divider">
              <span>其他登录方式</span>
            </p>
            <div class="third-party-icons">
              <el-button circle @click="handleFeishuAuth" class="social-btn">
                <el-icon :size="20"><Monitor /></el-icon>
              </el-button>
            </div>
          </div>
        </div>
        
        <div class="login-footer">
          <p>© 2025 安徽**运输中心 - 智能运力系统</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { Avatar, User, Lock, Monitor, Check } from '@element-plus/icons-vue'
import { authService } from '@/services/authService'

export default {
  name: 'Login',
  components: {
    Avatar,
    User,
    Lock,
    Monitor,
    Check
  },
  data() {
    return {
      activeTab: 'password',
      loginForm: {
        username: '',
        password: ''
      },
      loginRules: {
        username: [
          { required: true, message: '请输入用户名或邮箱', trigger: 'blur' }
        ],
        password: [
          { required: true, message: '请输入密码', trigger: 'blur' }
        ]
      },
      rememberMe: false,
      loading: false,
      qrcodeUrl: '', // 实际项目中应从后端获取
      errorMessage: '',
    }
  },
  mounted() {
    // 组件挂载时生成二维码
    this.generateQrCode();
  },
  methods: {
    async handleLogin() {
      this.$refs.loginForm.validate(async (valid) => {
        if (valid) {
          this.loading = true
          
          try {
            // 使用认证服务进行登录
            const result = await authService.login(
              this.loginForm.username, 
              this.loginForm.password
            )
            
            if (result.success) {
              // 登录成功后初始化权限存储中的用户信息
              const { usePermissionStore } = await import('@/stores/permission');
              const permissionStore = usePermissionStore();
              await permissionStore.initializeFromToken();
              // 登录成功后跳转到仪表盘
              this.$router.push('/')
            } else {
              // 显示具体的错误信息
              this.errorMessage = result.message || '登录失败，请检查用户名和密码'
              if (this.errorMessage) {
                setTimeout(() => {
                  this.errorMessage = ''
                }, 5000)
              }
            }
          } catch (error) {
            console.error('登录失败:', error)
            this.errorMessage = error.message || '登录失败，请稍后再试。'
            if (this.errorMessage) {
              setTimeout(() => {
                this.errorMessage = ''
              }, 5000)
            }
          } finally {
            this.loading = false
          }
        }
      })
    },
    handleFeishuAuth() {
      // 模拟飞书授权登录
      this.loading = true
      setTimeout(() => {
        this.loading = false
        this.$router.push('/')
      }, 1000)
    },
    generateQrCode() {
      // 模拟生成二维码
      // 实际项目中应该调用后端API获取二维码
      this.qrcodeUrl = '' // 这里留空，使用占位符
    },
    refreshQrCode() {
      // 刷新二维码
      this.generateQrCode()
      this.$message.success('二维码已刷新')
    }
  }
}
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #f5f7fa 0%, #e4e7eb 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
}

.login-container {
  display: flex;
  width: 100%;
  max-width: 900px;
  height: 600px;
  background: white;
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 15px 35px rgba(50, 50, 93, 0.1), 0 5px 15px rgba(0, 0, 0, 0.07);
}

.login-left {
  flex: 1;
  background: linear-gradient(135deg, #409eff 0%, #2c3e50 100%);
  color: white;
  padding: 50px 40px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}

.brand {
  text-align: center;
}

.logo {
  margin-bottom: 20px;
}

.logo i {
  background: rgba(255, 255, 255, 0.2);
  border-radius: 50%;
  padding: 20px;
}

.brand h1 {
  font-size: 28px;
  font-weight: 600;
  margin-bottom: 10px;
  letter-spacing: 1px;
}

.slogan {
  font-size: 16px;
  opacity: 0.9;
  margin-bottom: 0;
}

.features {
  margin-top: 30px;
}

.feature-item {
  display: flex;
  align-items: center;
  margin-bottom: 20px;
  font-size: 16px;
}

.feature-item i {
  margin-right: 12px;
}

.login-right {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  padding: 40px;
}

.login-card {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.login-header {
  text-align: center;
  margin-bottom: 30px;
}

.login-header h2 {
  font-size: 24px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 8px;
}

.login-header p {
  color: #909399;
  margin: 0;
  font-size: 14px;
}

:deep(.el-tabs__item) {
  font-size: 15px;
  font-weight: 500;
  color: #606266;
}

:deep(.el-tabs__item.is-active) {
  color: #409eff;
  font-weight: 600;
}

:deep(.el-tabs__active-bar) {
  background-color: #409eff;
}

.login-form {
  margin-top: 20px;
}

.login-input {
  height: 46px;
}

:deep(.el-input__wrapper) {
  border-radius: 8px;
  box-shadow: 0 0 0 1px #e4e7ed inset;
  transition: box-shadow 0.3s;
}

:deep(.el-input__wrapper.is-focus) {
  box-shadow: 0 0 0 1px #409eff inset;
}

:deep(.el-input__prefix) {
  padding-left: 12px;
}

:deep(.el-input__suffix) {
  padding-right: 12px;
}

.form-options {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 25px;
}

:deep(.el-checkbox__label) {
  color: #606266;
  font-size: 14px;
}

:deep(.el-link) {
  font-size: 14px;
}

.login-button {
  width: 100%;
  margin-top: 10px;
  background: linear-gradient(135deg, #409eff, #2c3e50);
  border: none;
  font-size: 16px;
  font-weight: 500;
  letter-spacing: 1px;
  transition: all 0.3s;
  height: 46px;
}

.login-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(64, 158, 255, 0.4);
}

/* 错误提示样式 */
.error-message {
  margin-top: 15px;
  animation: shake 0.5s ease-in-out;
}

.error-alert {
  border-radius: 8px;
  border: 1px solid #f56c6c;
  background-color: #fef0f0;
}

:deep(.el-alert__title) {
  font-size: 14px;
  font-weight: 500;
}

@keyframes shake {
  0%, 100% { transform: translateX(0); }
  25% { transform: translateX(-5px); }
  75% { transform: translateX(5px); }
}

.feishu-login {
  padding: 20px 0;
  text-align: center;
}

.qrcode-container {
  width: 180px;
  height: 180px;
  margin: 0 auto 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 1px dashed #e4e7ed;
  border-radius: 12px;
  background-color: #f5f7fa;
}

.qrcode-placeholder {
  text-align: center;
  color: #909399;
}

.qrcode-placeholder p {
  margin: 15px 0 0;
  font-size: 15px;
  color: #606266;
}

.qrcode-tip {
  color: #909399;
  font-size: 14px;
  margin-bottom: 15px;
}

.refresh-qrcode {
  font-size: 14px;
}

.third-party-login {
  margin: 25px 0;
}

.divider {
  position: relative;
  text-align: center;
  margin: 0;
  font-size: 14px;
  color: #c0c4cc;
}

.divider span {
  background: white;
  padding: 0 15px;
  position: relative;
  z-index: 1;
}

.divider::before {
  content: "";
  position: absolute;
  top: 50%;
  left: 0;
  right: 0;
  height: 1px;
  background-color: #e4e7ed;
  z-index: 0;
}

.third-party-icons {
  display: flex;
  justify-content: center;
  margin-top: 20px;
}

.social-btn {
  width: 42px;
  height: 42px;
  margin: 0 8px;
  border: 1px solid #e4e7ed;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.05);
  transition: all 0.3s;
}

.social-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
  border-color: #409eff;
}

.login-footer {
  text-align: center;
  padding-top: 20px;
  border-top: 1px solid #e4e7ed;
}

.login-footer p {
  color: #c0c4cc;
  font-size: 13px;
  margin: 0;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .login-container {
    flex-direction: column;
    height: auto;
  }
  
  .login-left {
    padding: 30px 20px;
  }
  
  .login-right {
    padding: 30px 20px;
  }
  
  .brand h1 {
    font-size: 24px;
  }
  
  .feature-item {
    font-size: 14px;
  }
}
</style>