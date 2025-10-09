# 前端上线配置指南

## 概述
本文档详细说明了前端项目从开发环境到生产环境的部署配置要点，确保项目能够在生产环境中正常运行。

## 环境配置

### 1. 环境变量配置

#### 开发环境 (`.env`)
```bash
# 开发环境配置
VITE_API_BASE_URL=http://localhost:5000
```

#### 生产环境 (`.env.production`)
```bash
# 生产环境配置
VITE_API_BASE_URL=https://your-production-domain.com
```

**注意事项：**
- 生产环境必须使用 HTTPS 协议
- 确保生产域名已正确配置 SSL 证书
- API 基础 URL 不要包含尾部斜杠

### 2. 构建配置检查

#### Vite 配置 (`vite.config.js`)
```javascript
export default defineConfig({
  plugins: [vue()],
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:5000',
        changeOrigin: true,
      }
    }
  },
  // 生产环境构建配置
  build: {
    outDir: 'dist',
    assetsDir: 'assets',
    sourcemap: false, // 生产环境建议关闭源码映射
    minify: 'terser',
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ['vue', 'vue-router'],
          ui: ['element-plus']
        }
      }
    }
  }
})
```

## 部署前检查清单

### 1. 环境变量检查
- [ ] 确认 `.env.production` 文件存在
- [ ] 验证 `VITE_API_BASE_URL` 指向正确的生产服务器
- [ ] 检查所有环境变量是否正确设置

### 2. API 配置检查
- [ ] 确认 `src/services/api.js` 中的 baseURL 配置正确
- [ ] 验证 API 请求能够正确使用环境变量
- [ ] 测试文件上传和下载功能的 URL 构建

### 3. 路由配置检查
- [ ] 确认路由模式适合生产环境（通常使用 history 模式）
- [ ] 检查路由懒加载是否正常工作
- [ ] 验证路由守卫功能

### 4. 静态资源检查
- [ ] 确认图片、字体等静态资源路径正确
- [ ] 检查 favicon 和其他元数据
- [ ] 验证 PWA 配置（如果使用）

## 构建和部署步骤

### 1. 构建生产版本
```bash
# 安装依赖
npm install

# 构建生产版本
npm run build
```

### 2. 构建产物检查
构建完成后，检查 `dist` 目录：
```
dist/
├── index.html          # 主页面
├── assets/            # 静态资源
│   ├── *.js          # JavaScript 文件
│   ├── *.css         # CSS 文件
│   └── *.woff2       # 字体文件
└── favicon.ico        # 网站图标
```

### 3. 服务器配置

#### Nginx 配置示例
```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    # 重定向到 HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;
    
    # SSL 证书配置
    ssl_certificate /path/to/certificate.crt;
    ssl_certificate_key /path/to/private.key;
    
    # 前端静态文件
    location / {
        root /path/to/dist;
        try_files $uri $uri/ /index.html;
        
        # 缓存配置
        location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
            expires 1y;
            add_header Cache-Control "public, immutable";
        }
    }
    
    # API 代理
    location /api/ {
        proxy_pass http://backend-server:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

#### Apache 配置示例
```apache
<VirtualHost *:443>
    ServerName your-domain.com
    DocumentRoot /path/to/dist
    
    # SSL 配置
    SSLEngine on
    SSLCertificateFile /path/to/certificate.crt
    SSLCertificateKeyFile /path/to/private.key
    
    # 前端路由支持
    <Directory "/path/to/dist">
        RewriteEngine On
        RewriteBase /
        RewriteRule ^index\.html$ - [L]
        RewriteCond %{REQUEST_FILENAME} !-f
        RewriteCond %{REQUEST_FILENAME} !-d
        RewriteRule . /index.html [L]
    </Directory>
    
    # API 代理
    ProxyPass /api/ http://backend-server:5000/api/
    ProxyPassReverse /api/ http://backend-server:5000/api/
</VirtualHost>
```

## 性能优化配置

### 1. 代码分割
```javascript
// 路由懒加载
const routes = [
  {
    path: '/dashboard',
    component: () => import('@/pages/Dashboard.vue')
  }
]
```

### 2. 资源压缩
```javascript
// vite.config.js
export default defineConfig({
  build: {
    rollupOptions: {
      output: {
        manualChunks: {
          'element-plus': ['element-plus'],
          'vue-vendor': ['vue', 'vue-router']
        }
      }
    }
  }
})
```

### 3. CDN 配置
```javascript
// 使用 CDN 加载第三方库
export default defineConfig({
  build: {
    rollupOptions: {
      external: ['vue', 'element-plus'],
      output: {
        globals: {
          vue: 'Vue',
          'element-plus': 'ElementPlus'
        }
      }
    }
  }
})
```

## 安全配置

### 1. CSP (内容安全策略)
```html
<meta http-equiv="Content-Security-Policy" 
      content="default-src 'self'; 
               script-src 'self' 'unsafe-inline'; 
               style-src 'self' 'unsafe-inline'; 
               img-src 'self' data: https:;">
```

### 2. 环境变量安全
- 不要在前端代码中暴露敏感信息
- 使用 `VITE_` 前缀的环境变量会被打包到前端代码中
- 敏感配置应该在服务器端处理

## 监控和日志

### 1. 错误监控
```javascript
// 全局错误处理
window.addEventListener('error', (event) => {
  console.error('Global error:', event.error)
  // 发送错误信息到监控服务
})

window.addEventListener('unhandledrejection', (event) => {
  console.error('Unhandled promise rejection:', event.reason)
  // 发送错误信息到监控服务
})
```

### 2. 性能监控
```javascript
// 页面加载性能监控
window.addEventListener('load', () => {
  const perfData = performance.getEntriesByType('navigation')[0]
  console.log('Page load time:', perfData.loadEventEnd - perfData.fetchStart)
})
```

## 测试验证

### 1. 功能测试
- [ ] 登录/登出功能
- [ ] 主要业务流程
- [ ] 文件上传下载
- [ ] 响应式布局

### 2. 性能测试
- [ ] 页面加载速度
- [ ] 资源加载优化
- [ ] 移动端性能

### 3. 兼容性测试
- [ ] 主流浏览器兼容性
- [ ] 移动端兼容性
- [ ] 不同屏幕分辨率

## 常见问题和解决方案

### 1. 路由刷新 404 问题
**问题：** 在生产环境中刷新页面出现 404 错误
**解决：** 配置服务器支持 SPA 路由，将所有请求重定向到 `index.html`

### 2. API 跨域问题
**问题：** 生产环境中 API 请求跨域失败
**解决：** 配置服务器代理或后端 CORS 设置

### 3. 静态资源加载失败
**问题：** CSS、JS 文件加载 404
**解决：** 检查 `publicPath` 配置和服务器静态文件配置

### 4. 环境变量不生效
**问题：** 生产环境中环境变量没有正确加载
**解决：** 确认 `.env.production` 文件存在且变量名以 `VITE_` 开头

## 部署后验证

### 1. 基础功能验证
```bash
# 检查网站是否可访问
curl -I https://your-domain.com

# 检查 API 是否正常
curl https://your-domain.com/api/health
```

### 2. 性能验证
- 使用 Chrome DevTools 检查网络请求
- 使用 Lighthouse 进行性能评估
- 检查资源加载时间和大小

### 3. 日志检查
- 检查服务器访问日志
- 检查浏览器控制台是否有错误
- 验证错误监控是否正常工作

## 维护和更新

### 1. 版本管理
- 使用语义化版本号
- 记录每次部署的版本信息
- 保留回滚方案

### 2. 缓存策略
- 合理设置静态资源缓存时间
- 使用文件哈希避免缓存问题
- 配置 CDN 缓存策略

### 3. 监控告警
- 设置性能监控告警
- 配置错误率监控
- 监控服务器资源使用情况

---

**注意：** 本指南基于当前项目配置编写，实际部署时请根据具体环境和需求进行调整。