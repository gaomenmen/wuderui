# WuDeRuiBo 吴德瑞博

中国文化交流平台 — 学习中文、练习太极、定制中国深度文化之旅。

> English version: [README.md](README.md)

## 技术栈

- **后端**: Flask（应用工厂模式）
- **数据库**: SQLite（开发环境）/ PostgreSQL（生产环境）
- **ORM**: Flask-SQLAlchemy
- **数据库迁移**: Flask-Migrate (Alembic)
- **认证**: Flask-Login（单管理员账户）
- **国际化**: Flask-Babel（中英双语切换）
- **前端**: Bootstrap 5、Jinja2 模板、内联 SVG 水墨风设计
- **测试**: pytest
- **部署**: Gunicorn + 任意 PaaS 平台（Render、Railway、Fly.io 等）

## 项目结构

```
wuderui/
├── app.py                  # 应用工厂 + CLI 命令
├── config.py               # 配置类（基于环境变量）
├── extensions.py           # db、login_manager、babel、migrate 实例
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

## 快速开始

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
pip install pytest  # 用于运行测试
flask run
```

启动后访问 http://127.0.0.1:5000

默认管理员账号: `admin` / `changeme123`（首次登录会强制要求修改密码）

## 本地验证

### 启动应用

```bash
flask run
```

首次运行会自动创建 SQLite 数据库（`instance/wuderui.db`）和所有表，并创建默认管理员账户。

### 验证前台页面

| 页面 | 地址 | 检查内容 |
|------|------|----------|
| 首页 | `/` | Hero区、3个服务卡片、目的地网格、客户评价 |
| 学中文 | `/learn-chinese` | 课程分类、3档定价、师资卡片 |
| 太极拳 | `/tai-chi` | 24式课程网格、定价、好处介绍 |
| 定制旅行 | `/custom-trips` | 10条旅行线路含价格、服务详情面板（点击展开） |
| 关于我们 | `/about` | 品牌故事、理念 |
| 联系我们 | `/contact` | 联系方式可点击链接、咨询表单 |
| 推荐分佣 | `/affiliate` | 分佣计划介绍 |
| 管理员登录 | `/admin/login` | 使用 `admin` / `changeme123` 登录 |

### 验证管理后台

1. 登录 `/admin/login`，账号 `admin` / `changeme123`
2. **控制面板** — 查看统计数据
3. **内容管理** → 点击"同步所有默认内容" → 确认7个页面共27个版块已创建
4. 编辑某个版块的标题 → 访问前台页面 → 确认文字已更新
5. 删除一个版块 → 前台页面自动回退到默认内容
6. **推荐合伙人** → 新建一个 → 确认推荐码已生成
7. 访问 `/?ref=WDR-XXXX` → 确认管理后台有点击记录
8. 提交咨询表单 → 确认咨询出现在管理后台
9. 将咨询标记为"已转化" → 创建佣金 → 标记已付

### 验证新功能

#### CMS 内容管理系统

1. 登录管理后台 → **内容管理** → 点击"同步所有默认内容"
2. 选择一个页面（如首页）→ 编辑版块的中英文标题
3. 访问前台页面 → 确认文字已更新
4. 切换版块为隐藏 → 前台页面自动回退到硬编码默认内容
5. 删除一个版块 → 前台页面完全恢复为默认内容
6. 拖拽调整版块顺序 → 前台页面按新顺序显示

#### 定制旅行 — 可点击的服务详情面板

1. 访问 `/custom-trips`
2. 滚动到4个服务卡片：专业摄影、当地美食、英文导游、全天支持
3. 点击每个卡片 → 展开详细内容，之前的面板自动收起（手风琴效果）
4. 当前激活的卡片会显示高亮边框和抬起动画
5. 当地面板中的美食推荐与10个旅行目的地一一对应

#### 服务定价

三个服务页面均已添加定价：

- **学中文** (`/learn-chinese`)：3档 — 免费 / ¥1,680 标准课 / ¥4,200 强化课
- **太极拳** (`/tai-chi`)：3档 — 免费 / $49 完整课程 / $129 私教辅导
- **定制旅行** (`/custom-trips`)：10个目的地，¥4,800–¥12,800/人

### 创建额外管理员

```bash
flask create-admin <用户名> <密码>
```

## 运行测试

```bash
pip install pytest
python -m pytest tests/ -v
```

15 个测试覆盖：模型逻辑（密码哈希、佣金计算、CMS 版块）、路由处理（联系表单、推荐追踪、管理认证）、管理后台 CRUD 操作。

## 数据库迁移

使用 Flask-Migrate 管理数据库结构变更：

```bash
flask db migrate -m "变更描述"   # 生成迁移文件
flask db upgrade                # 应用迁移
```

开发环境启动时自动运行 `db.create_all()`。生产环境请使用 `flask db upgrade` 安全应用迁移。

## 生产环境安全检查清单

部署到生产环境前务必完成：

- [ ] 设置 `SECRET_KEY` 为强随机字符串（32位以上）
- [ ] 设置 `DATABASE_URL` 为 PostgreSQL 连接字符串
- [ ] 修改默认管理员密码（首次登录会强制修改）
- [ ] 通过 `ADMIN_PASSWORD` 环境变量设置初始密码
- [ ] 确保 `FLASK_DEBUG` 未启用
- [ ] 使用 HTTPS（大部分 PaaS 平台默认提供）
- [ ] 检查模板中的联系信息 — 将演示数据替换为真实信息

## 管理后台使用指南

登录地址: `/admin/login`

### 内容管理（CMS）

无需修改代码即可管理页面内容。

1. **内容管理** → 点击"同步所有默认内容"导入现有页面内容
2. 选择页面 → 编辑版块的标题、正文、图片、按钮等
3. 切换版块显示/隐藏，拖拽调整顺序
4. 删除版块则前台自动回退到硬编码默认内容

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

## 部署

应用已配置好 Gunicorn 生产服务器：

```bash
gunicorn app:app
```

在部署平台上设置以下环境变量：

| 变量 | 是否必填 | 说明 |
|------|----------|------|
| `SECRET_KEY` | 是 | 随机32位以上字符串，用于会话加密 |
| `DATABASE_URL` | 是 | PostgreSQL 连接字符串 |
| `ADMIN_PASSWORD` | 否 | 初始管理员密码（默认: `changeme123`） |

完整配置示例请参考 [.env.example](.env.example)。

兼容任何支持 Python 的 PaaS 平台（Render、Railway、Fly.io、Heroku 等）。

### 媒体文件存储

CMS 图片 URL 指向外部主机，当前应用不处理文件上传。如后续添加图片上传功能，请使用云存储（S3、Cloudflare R2 等）——PaaS 文件系统是临时的，重启后上传文件会丢失。

## 测试联系方式（演示数据）

| 渠道 | 号码/地址 |
|------|-----------|
| WhatsApp | +86 138-0013-8000 |
| 微信 ID | WuDeRuiBo2026 |
| Facebook | facebook.com/wuderuibo |
| 邮箱 | hello@wuderuibo.com |

以上为演示/测试数据，正式上线前请替换为真实联系方式。
