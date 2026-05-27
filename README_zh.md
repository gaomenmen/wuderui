# WuDeRuiBo 吴德瑞博

中国文化交流平台 — 学习中文、练习太极、定制中国深度文化之旅。

> English version: [README.md](README.md)

## 技术栈

- **后端**: Flask（应用工厂模式）
- **数据库**: SQLite（开发环境）/ PostgreSQL（生产环境）
- **ORM**: Flask-SQLAlchemy
- **认证**: Flask-Login（单管理员账户）
- **国际化**: Flask-Babel（中英双语切换）
- **前端**: Bootstrap 5、Jinja2 模板、内联 SVG 水墨风设计
- **部署**: Render.com + Gunicorn + GitHub 自动部署

## 项目结构

```
wuderui/
├── app.py                  # 应用工厂 + CLI 命令
├── config.py               # 配置类（基于环境变量）
├── extensions.py           # db、login_manager、babel 实例
├── requirements.txt        # Python 依赖
├── admin/
│   └── routes.py           # 管理后台路由（14+ 个）
├── models/
│   ├── admin_user.py       # 管理员账户
│   ├── affiliate.py        # 推荐合伙人
│   ├── referral_click.py   # 推荐点击追踪
│   ├── inquiry.py          # 咨询表单提交
│   ├── commission.py       # 佣金记录
│   ├── monthly_report.py   # 月度报表
│   └── page_section.py     # CMS 内容版块
├── routes/
│   ├── main.py             # 公开页面路由 + 推荐链接追踪
│   ├── contact.py          # 联系表单 POST 处理
│   └── auth.py             # 管理员登录/登出
└── templates/
    ├── base.html            # 主布局（导航栏、页脚、双语 CSS）
    ├── index.html           # 首页
    ├── learn_chinese.html   # 中文课程页
    ├── tai_chi.html         # 太极拳课程页
    ├── custom_trips.html    # 10大定制旅行套餐
    ├── about.html           # 关于我们
    ├── contact.html         # 联系我们 + FAQ
    ├── affiliate.html       # 推荐分佣计划
    ├── auth/login.html      # 管理员登录页
    └── admin/               # 14 个管理后台模板
        ├── base.html        # 管理后台侧边栏布局
        ├── content/         # CMS 内容管理模板
        └── ...
```

## 本地开发

### 环境要求

- Python 3.10+
- Git

### 安装步骤

```bash
git clone https://github.com/gaomenmen/wuderui.git
cd wuderui
python -m venv venv

# Windows 激活虚拟环境
venv\Scripts\activate
# macOS/Linux 激活虚拟环境
source venv/bin/activate

pip install -r requirements.txt
flask run
```

启动后访问 http://127.0.0.1:5000

默认管理员账号: `admin` / `changeme123`

## 部署到 Render.com

### 1. 注册 Render 账号

前往 https://render.com 注册并绑定 GitHub 账号。

### 2. 创建 PostgreSQL 数据库

- Dashboard → New → PostgreSQL
- 记下 **Internal Database URL**（如 `postgresql://user:pass@host/db`）

### 3. 创建 Web 服务

- Dashboard → New → Web Service
- 连接你的 GitHub 仓库
- 配置：
  - **Build Command**: `pip install -r requirements.txt`
  - **Start Command**: `gunicorn app:app`
  - **Runtime**: Python 3

### 4. 配置环境变量

在 Web Service → Environment 中添加：

| 变量名 | 值 |
|--------|-----|
| `SECRET_KEY` | 随机32位以上字符串（如 `openssl rand -hex 32` 生成） |
| `DATABASE_URL` | 第2步获取的 PostgreSQL Internal URL |

### 5. 自动部署

每次 `git push` 到 `main` 分支，Render 会自动部署。

首次部署会自动：
- 创建所有数据库表
- 创建默认管理员账户（`admin` / `changeme123`）

**首次登录后请立即修改管理员密码。**

### 6. 创建额外管理员（可选）

```bash
# 在 Render Shell 中执行
flask create-admin <用户名> <密码>
```

## 管理后台使用指南

登录地址: `/admin/login`

### 控制面板（Dashboard）

总览统计：总咨询数、新咨询数、活跃推荐人数、本月佣金总额。

### 内容管理（CMS）

无需修改代码即可管理页面内容。

1. **内容管理** → 选择一个页面（首页、学中文、太极等）
2. **新建版块** → 填写双语字段：
   - `section_key`：版块标识（如 `hero`、`pricing`、`cta`）
   - `section_type`：版块类型（`hero`、`card`、`text_block`、`stats`、`cta`、`faq`）
   - 标题、副标题、正文 — 英文和中文各一份
   - 图片 URL、按钮文字、按钮链接
   - `extra_data`：JSON 格式的扩展数据（标签、统计数值等）
3. 版块保存后立即在前台页面生效；删除版块则自动回退到默认内容

所有 7 个公开页面均支持 CMS hero 编辑。无 CMS 数据时自动使用硬编码默认内容。

### 咨询管理（Inquiries）

查看所有联系表单提交。状态流程：新咨询 → 已联系 → 已转化 → 已关闭。

### 推荐合伙人（Affiliates）

管理推荐合作伙伴。每位合伙人获得唯一推荐码（如 `WDR-A3F7`）。

推荐追踪流程：
1. 访客点击 `你的网站.com/?ref=WDR-A3F7`
2. 系统记录点击并设置 30 天 Cookie
3. 访客提交咨询表单 → 咨询自动关联到推荐人
4. 管理员将咨询标记为"已转化" → 创建佣金记录

### 佣金管理（Commissions）

各服务类型佣金比例：
- 中文课程：5%
- 太极拳：8%
- 旅行套餐：10%

支持批量审批和批量标记已付。

### 报表与结算（Reports & Settlements）

按月生成推荐人汇总报表。查看已付佣金历史记录。

## 双语系统

网站支持中英文切换：

- URL 参数切换：`?lang=en` 或 `?lang=zh`
- 模板语法：`<span class="en">English</span><span class="zh">中文</span>`
- CSS 根据 `<html>` 的 class 控制显示哪一种语言

## 环境变量参考

| 变量 | 是否必填 | 默认值 | 说明 |
|------|----------|--------|------|
| `SECRET_KEY` | 生产环境必填 | `wuderui-dev-secret-key-2024` | Flask 会话加密密钥 |
| `DATABASE_URL` | 生产环境必填 | `sqlite:///wuderui.db` | 数据库连接字符串 |

## 测试联系方式（演示数据）

| 渠道 | 号码/地址 |
|------|-----------|
| WhatsApp | +86 138-0013-8000 |
| 微信 ID | WuDeRuiBo2026 |
| Facebook | facebook.com/wuderuibo |
| 邮箱 | hello@wuderuibo.com |
