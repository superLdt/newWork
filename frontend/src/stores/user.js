import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

/**
 * 用户状态管理
 */
export const useUserStore = defineStore('user', () => {
  // 状态
  const currentUser = ref(null)
  const token = ref(localStorage.getItem('token') || '')
  const isLoggedIn = ref(false)

  // 计算属性
  const userInfo = computed(() => currentUser.value)
  const userName = computed(() => currentUser.value?.username || '')
  const userRole = computed(() => currentUser.value?.role_name || '')
  const userId = computed(() => currentUser.value?.id || null)

  // 方法
  const setCurrentUser = (user) => {
    currentUser.value = user
    isLoggedIn.value = !!user
  }

  const setToken = (newToken) => {
    token.value = newToken
    if (newToken) {
      localStorage.setItem('token', newToken)
    } else {
      localStorage.removeItem('token')
    }
  }

  const login = async (credentials) => {
    try {
      // 这里应该调用登录API
      // const response = await authService.login(credentials)
      // setToken(response.token)
      // setCurrentUser(response.user)
      
      // 临时模拟登录
      const mockUser = {
        id: 1,
        username: credentials.username,
        role_name: '供应商',
        email: 'user@example.com'
      }
      setCurrentUser(mockUser)
      setToken('mock-token')
      
      return { success: true, user: mockUser }
    } catch (error) {
      console.error('Login failed:', error)
      throw error
    }
  }

  const logout = () => {
    setCurrentUser(null)
    setToken('')
    isLoggedIn.value = false
  }

  const updateUserInfo = (userInfo) => {
    if (currentUser.value) {
      currentUser.value = { ...currentUser.value, ...userInfo }
    }
  }

  // 初始化时检查token
  const initializeAuth = () => {
    const storedToken = localStorage.getItem('token')
    if (storedToken) {
      setToken(storedToken)
      // 这里应该验证token并获取用户信息
      // 临时设置模拟用户
      setCurrentUser({
        id: 1,
        username: 'demo_user',
        role_name: '供应商',
        email: 'demo@example.com'
      })
    }
  }

  return {
    // 状态
    currentUser,
    token,
    isLoggedIn,
    
    // 计算属性
    userInfo,
    userName,
    userRole,
    userId,
    
    // 方法
    setCurrentUser,
    setToken,
    login,
    logout,
    updateUserInfo,
    initializeAuth
  }
})