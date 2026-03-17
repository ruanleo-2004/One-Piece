# 海贼王主题网站项目
作者：20241316 马晟淇

## 项目简介
这是一个基于Flask框架精心打造的海贼王主题精品网站，融合了众多前沿Web开发技术与优秀设计理念，专为热爱海贼王的海米们匠心呈现！项目采用现代化架构设计，集成了**单页应用(SPA)** 路由系统，实现了流畅无刷新的用户体验；通过**响应式设计**，完美适配从移动设备到桌面端的各种屏幕尺寸。技术层面，项目展现了卓越的工程实践：采用**分层架构**（Models、Schemas、Views分离）确保代码的高度可维护性；**插件化设计**让功能扩展变得灵活便捷；集成**数据验证机制**保障数据完整性；运用**数据库迁移**实现平滑的版本迭代。此外，还融入了用户认证、邮件服务、定时任务等企业级功能，充分体现了项目的技术深度与实用性。

无论您是海贼王爱好者还是技术开发者，这个项目都将为您带来惊喜！

## 技术栈
- **后端框架**: Flask 2.3.2
- **数据库**: MySQL 5.7+
- **ORM**: SQLAlchemy 2.0.21
- **模板引擎**: Jinja2
- **前端**: Bootstrap 4.4.1, jQuery, SPA Router
- **其他库**: Flask-Login, Flask-Mail, Flask-Migrate, Flask-Reuploaded等

## 安装与启动步骤

### 1. 环境准备
在开始安装前，请确保您的系统已经安装了以下软件：

#### 1.1 Python
- 版本要求: Python 3.10+
- 下载地址: https://www.python.org/downloads/
- 安装步骤: 下载对应版本的安装包，按照提示安装（请勾选"Add Python to PATH"）

#### 1.2 MySQL
- 版本要求: MySQL 5.7+
- 下载地址: https://dev.mysql.com/downloads/mysql/
- 安装步骤: 
  - 下载并安装MySQL
  - 记住设置的root用户密码
  - 确保MySQL服务已启动

### 2. 项目解压
1. 将项目压缩包解压到您的本地目录
2. 解压后您将看到以下目录结构：
   ```
   马晟淇20241316/
   ├── One Piece/        # 项目主目录
   │   ├── applications/ # 应用核心目录
   │   │   ├── common/   # 通用功能模块
   │   │   ├── extensions/     # 扩展插件
   │   │   ├── models/         # 数据模型
   │   │   ├── schemas/        # 数据验证
   │   │   ├── view/           # 视图路由
   │   │   │   ├── plugin/     # 插件视图
   │   │   │   └── system/     # 系统视图
   │   │   ├── config.py       # 应用配置
   │   │   └── __init__.py     # 应用初始化
   │   ├── flask_session/      # Flask会话存储
   │   ├── plugins/            # 插件目录
   │   │   ├── blog/           # 博客插件
   │   │   └── realip/         # IP地址插件
   │   ├── static/             # 静态资源
   │   │   ├── css/            # CSS样式文件
   │   │   ├── images/         # 图片资源
   │   │   └── js/             # JavaScript文件
   │   ├── templates/          # 模板文件
   │   │   └── system/         # 系统页面模板
   │   ├── app.py              # 应用入口
   │   ├── migrate.sh          # 数据库迁移脚本
   │   ├── migrations/         # 数据库迁移文件
   │   └── venv/               # 虚拟环境
   ├── README.md           # 项目说明文件
   ├── requirements.txt    # 依赖列表
   └── 宾克斯的美酒.mp4    # 项目相关视频
   ```

### 3. 安装依赖
1. 打开命令提示符（CMD）或PowerShell
2. 进入项目根目录：
   ```bash
   cd "C:\Users\您的用户名\项目解压路径\马晟淇20241316\One Piece"
   ```
3. 创建虚拟环境（可选但推荐）：
   ```bash
   python -m venv venv
   ```
4. 激活虚拟环境：
   ```bash
   # Windows CMD
   venv\Scripts\activate.bat
   
   # Windows PowerShell
   venv\Scripts\Activate.ps1
   ```
5. 安装项目依赖：
   ```bash
   pip install -r requirements.txt
   ```

### 4. 配置数据库
1. 打开MySQL命令行客户端或MySQL Workbench
2. 登录MySQL（使用您设置的root密码）：
   ```sql
   mysql -u root -p
   ```
3. 创建数据库：
   ```sql
   CREATE DATABASE haizeiwang CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   ```
4. 配置项目数据库连接：
   - 打开`applications/config.py`文件
   - 找到以下配置：
     ```python
     # mysql 配置
     MYSQL_USERNAME = "root"
     MYSQL_PASSWORD = "root"
     MYSQL_HOST = "localhost"
     MYSQL_PORT = 3306
     MYSQL_DATABASE = "haizeiwang"
     ```
   - 修改`MYSQL_PASSWORD`为您的MySQL root密码
   - 如果您修改了数据库名称或端口，也需要相应调整

### 5. 数据库迁移
1. 回到项目根目录（确保虚拟环境已激活）
2. 初始化数据库迁移（如果没有migrations目录）：
   ```bash
   flask db init
   ```
3. 创建迁移文件：
   ```bash
   flask db migrate -m "初始化数据库"
   ```
4. 执行数据库迁移：
   ```bash
   flask db upgrade
   ```

### 6. 启动项目
1. 在项目根目录下执行以下命令：
   ```bash
   python app.py
   ```
   或使用Flask命令：
   ```bash
   flask --app app.py run -h 0.0.0.0 -p 5000 --debug
   ```
2.3. 启动成功后，您将看到类似以下输出：
   ```
   * Serving Flask app 'app.py'
   * Debug mode: on
   * Running on http://127.0.0.1:5000
   ```
3. 打开浏览器，访问`http://127.0.0.1:5000`或`http://localhost:5000`即可查看网站

## 项目功能说明

### 1. 主要模块
- **冒险启航**: 展示海贼王梦开始的地方
- **博客**: 发布和查看博客文章，支持评论和回复等功能
- **最新情报**: 展示海贼王相关新闻
- **篇章故事**: 海贼王草帽一伙冒险的篇章
- **恶魔果实**: 海贼王动漫里除霸气外特有的能力
- **漫画**: 带你走进海贼王的漫画画廊
- **用户中心**: 用户登录、注册、个人资料管理

### 2. 访问地址
- **普通用户首页**: `http://localhost:5000/`（自动重定向到博客页面）
- **博客页面**: `http://localhost:5000/blog/`
- **用户中心**: `http://localhost:5000/home`
- **后台管理**: `http://localhost:5000/admin`
  - 初始用户名: `admin`
  - 初始密码: `admin`（登录后请及时修改）

## 注意事项

1. **端口占用**: 如果5000端口被占用，可以使用`-p`参数指定其他端口，例如：
   ```bash
   flask --app app.py run -h 0.0.0.0 -p 8080 --debug
   ```

2. **数据库连接**: 确保MySQL服务已启动，且数据库配置信息正确

3. **依赖安装**: 如果安装依赖时出现问题，可以尝试更新pip：
   ```bash
   pip install --upgrade pip
   ```

4. **静态资源**: 项目包含大量静态资源（图片、音频等），请确保解压完整

5. **开发模式**: `--debug`参数用于开发环境，生产环境请移除

6. **首次登录**: 后台管理初始用户为`admin`，密码为`admin`，请务必在首次登录后修改密码

## 常见问题

### Q: 启动时提示数据库连接失败？
A: 请检查：
1. MySQL服务是否已启动
2. 数据库配置信息是否正确（用户名、密码、数据库名）
3. 防火墙是否阻止了数据库连接

### Q: 安装依赖时出现超时错误？
A: 可以使用国内镜像源安装：
```bash
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### Q: 页面显示不正常或缺少样式？
A: 请确保静态资源已正确解压，检查`static`目录是否完整

### Q: 无法登录后台管理？
A: 请确保数据库迁移已执行成功，初始用户信息已正确创建

## 联系方式
如果您在安装或使用过程中遇到问题，可以通过以下方式联系：
- 邮箱: 3838311763@qq.com
- 项目地址: [此处填写项目地址]

---

感谢您使用本项目！祝您使用愉快！
