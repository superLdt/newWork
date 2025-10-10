# 后端架构分层规则

为确保项目的可维护性和可扩展性，所有后端代码必须严格遵循以下四层架构结构：

## 1. 表现层 (Presentation Layer)
- **位置**: `backend/app/api/` 和 `backend/app/*/routes.py`
- **职责**: 
  - 处理HTTP请求和响应
  - 参数验证和数据转换
  - 调用服务层完成业务逻辑
  - 错误处理和返回统一格式
- **规则**:
  - 不能直接访问数据模型
  - 不能包含业务逻辑
  - 只能调用服务层方法
  - 路由函数应保持简洁

## 2. 服务层 (Service Layer)
- **位置**: `backend/app/services/`
- **职责**:
  - 实现业务逻辑
  - 处理数据转换和验证
  - 协调多个数据访问操作
  - 事务管理
- **规则**:
  - 不能直接处理HTTP请求/响应
  - 可以调用数据访问层
  - 应该是无状态的
  - 业务逻辑应封装在此层

## 3. 数据访问层 (Data Access Layer)
- **位置**: `backend/app/models/`
- **职责**:
  - 定义数据模型
  - 实现数据持久化操作
  - 封装数据库查询
- **规则**:
  - 只负责数据访问，不包含业务逻辑
  - 使用SQLAlchemy ORM进行数据库操作
  - 提供清晰的数据访问接口

## 4. 应用层 (Application Layer)
- **位置**: `backend/app/`
- **职责**:
  - 应用初始化和配置
  - 模块注册和依赖管理
  - 全局中间件配置
- **规则**:
  - 负责整合各层组件
  - 不包含具体业务逻辑
  - 处理应用级别的配置和初始化

## 分层依赖规则
```
表现层 → 服务层 → 数据访问层
   ↑                ↓
应用层 ←─────────────┘
```

- 表现层只能依赖服务层
- 服务层可以依赖数据访问层
- 数据访问层不应依赖其他层
- 应用层负责整合所有层

## 代码组织示例

### 表现层示例 (routes.py)
```python
from flask import jsonify, request
from ..services.user_service import UserService

@bp.route('/users', methods=['POST'])
def create_user():
    data = request.get_json()
    user = UserService.create_user(data)
    return jsonify({'code': 200, 'data': user})
```

### 服务层示例 (user_service.py)
```python
from ..models.user import User
from ..extensions import db

class UserService:
    @staticmethod
    def create_user(user_data):
        user = User(username=user_data['username'])
        user.set_password(user_data['password'])
        db.session.add(user)
        db.session.commit()
        return user.to_dict()
```

### 数据访问层示例 (user.py)
```python
from ..extensions import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    
    def to_dict(self):
        return {'id': self.id, 'username': self.username}
```

## 违规处理
违反以上分层规则的代码将不被接受，必须重构以符合架构要求。