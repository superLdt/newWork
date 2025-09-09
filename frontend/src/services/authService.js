import { apiService } from './api'
import { ElMessage } from 'element-plus'

class AuthService {
  // 用户登录
  async login(username, password) {
    try {
      const response = await apiService.auth.login(username, password)
      
      if (response.code === 200) {
        // 保存token到localStorage
        localStorage.setItem('token', response.data.token)
        localStorage.setItem('user', JSON.stringify(response.data.user))
        
        // 登录成功后，尝试获取用户信息，确保用户数据最新
        await this.getUserInfo()
        ElMessage.success('登录成功')
        return { success: true, data: response.data }
      } else {
        // 根据不同的错误码返回具体的错误信息
        let errorMessage = response.message || '登录失败'
        
        if (response.code === 401) {
          errorMessage = '用户名或密码错误'
        } else if (response.code === 403) {
          errorMessage = '账户已被禁用，请联系管理员'
        } else if (response.code === 429) {
          errorMessage = '登录尝试次数过多，请稍后再试'
        }
        
        ElMessage.error(errorMessage)
        return { success: false, message: errorMessage }
      }
    } catch (error) {
      // 处理网络错误和超时
      let errorMessage = '网络错误'
      
      if (error.code === 'ECONNABORTED') {
        errorMessage = '请求超时，请检查网络连接'
      } else if (!error.response) {
        errorMessage = '网络连接失败，请检查网络设置'
      } else {
        // 使用API拦截器返回的统一错误信息
        errorMessage = error.message || '登录失败'
      }
      
      ElMessage.error(errorMessage)
      return { success: false, message: errorMessage }
    }
  }
  
  // 用户登出
  async logout() {
    try {
      const response = await apiService.auth.logout()
      
      if (response.code === 200) {
        // 清除本地存储的认证信息
        localStorage.removeItem('token')
        localStorage.removeItem('user')
        
        ElMessage.success('登出成功')
        return { success: true }
      } else {
        ElMessage.error(response.message || '登出失败')
        return { success: false, message: response.message }
      }
    } catch (error) {
      // 即使后端登出失败，也要清除本地认证信息
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      
      ElMessage.success('登出成功')
      return { success: true }
    }
  }
  
  // 获取当前用户信息
  async getUserInfo() {
    try {
      const response = await apiService.auth.getUserInfo()
      
      if (response.code === 200) {
        // 更新本地存储的用户信息
        localStorage.setItem('user', JSON.stringify(response.data))
        return { success: true, data: response.data }
      } else {
        ElMessage.error(response.message || '获取用户信息失败')
        return { success: false, message: response.message }
      }
    } catch (error) {
      // 统一处理获取用户信息失败的情况
      const errorMessage = error.response?.data?.message || error.message || '获取用户信息失败，请检查网络连接'
      ElMessage.error(errorMessage)
      return { success: false, message: errorMessage }
    }
  }
  
  // 检查用户是否已登录
  isAuthenticated() {
    const token = localStorage.getItem('token')
    return !!token
  }
  
  // 获取当前用户
  getCurrentUser() {
    const user = localStorage.getItem('user')
    return user ? JSON.parse(user) : null
  }
  
  // 获取认证token
  getToken() {
    return localStorage.getItem('token')
  }
}

// 创建并导出认证服务实例
export const authService = new AuthService()
export default authService