# Cookie 提取方法对比

ClawPiggy 提供了三种 cookie 提取方法，适用于不同场景。

## 三种方法对比

| 特性 | Interactive<br/>交互式 | Persistent<br/>持久化 | Auto-detect<br/>自动检测 |
|------|----------------------|---------------------|----------------------|
| **脚本** | `get_claude_cookie_interactive.py` | `get_claude_cookie_persistent.py` | `get_claude_cookie.py` |
| **浏览器模式** | 🕶️ 无痕窗口 | 🌐 正常窗口 | 🕶️ 无痕窗口 |
| **保留登录** | ❌ 每次需要登录 | ✅ 保留登录状态 | ❌ 每次需要登录 |
| **需要确认** | ✅ 手动按 ENTER | ✅ 手动按 ENTER | ❌ 自动检测 |
| **可靠性** | ⭐️⭐️⭐️ 最高 | ⭐️⭐️⭐️ 最高 | ⭐️⭐️ 中等 |
| **速度（首次）** | 🐢 慢（需登录） | 🐢 慢（需登录） | 🐢 慢（需登录） |
| **速度（后续）** | 🐢 慢（需登录） | 🚀 快（已登录） | 🐢 慢（需登录） |
| **适用场景** | 首次设置 | 频繁使用 | 自动化脚本 |

## 方法 1：Interactive（交互式）

### 特点

- **无痕窗口**：每次都是全新的浏览器环境
- **手动确认**：用户完全控制登录流程
- **最可靠**：100% 避免 CSP 问题

### 使用场景

- ✅ 首次设置
- ✅ 故障排除
- ✅ 安全性要求高（不保留浏览器数据）
- ❌ 不适合频繁使用（每次都要登录）

### 使用方法

```bash
python scripts/get_claude_cookie_interactive.py
```

### 工作流程

```
启动脚本
    ↓
打开无痕浏览器窗口
    ↓
导航到 claude.ai
    ↓
[用户手动登录]
    ↓
[用户按 ENTER]
    ↓
提取 cookies
    ↓
验证 cookies
    ↓
保存到 ~/.config/openclaw/claude-session.json
    ↓
关闭浏览器
```

### 优点

- 🔒 安全：不保留任何浏览器数据
- ✅ 可靠：避免所有自动化检测问题
- 🧹 干净：每次都是全新环境

### 缺点

- 🐢 慢：每次都需要完整登录
- 👤 需要交互：不能完全自动化

## 方法 2：Persistent（持久化）⭐️ 推荐日常使用

### 特点

- **正常窗口**：使用真实的浏览器配置文件
- **保留登录**：登录状态在多次运行间保持
- **手动确认**：用户控制何时提取 cookies

### 使用场景

- ✅ **日常使用**（推荐）
- ✅ 频繁提取 cookies
- ✅ 希望避免重复登录
- ✅ 开发和测试

### 使用方法

```bash
python scripts/get_claude_cookie_persistent.py
```

### 工作流程

```
启动脚本
    ↓
打开持久化浏览器窗口
（使用 ~/.config/openclaw/browser-data/）
    ↓
导航到 claude.ai
    ↓
检查登录状态
    ├─ 已登录 → [用户按 ENTER]
    └─ 未登录 → [用户登录] → [用户按 ENTER]
    ↓
提取 cookies
    ↓
验证 cookies
    ↓
保存到 ~/.config/openclaw/claude-session.json
    ↓
关闭浏览器（保留配置文件）
```

### 优点

- 🚀 快速：第二次起可能已经登录
- 💾 保留状态：浏览器数据持久化
- 🌐 真实环境：像正常使用浏览器一样

### 缺点

- 💾 占用空间：保存浏览器配置文件（~50-100MB）
- 🔓 安全性稍低：保留了浏览器数据

### 浏览器数据位置

```
~/.config/openclaw/browser-data/
├── Default/
│   ├── Cookies
│   ├── Local Storage/
│   ├── Session Storage/
│   └── ...
└── ...
```

### 清理浏览器数据

如果需要重置（清除登录状态）：

```bash
rm -rf ~/.config/openclaw/browser-data/
```

## 方法 3：Auto-detect（自动检测）

### 特点

- **无痕窗口**：隔离的浏览器环境
- **自动检测**：尝试自动检测登录完成
- **双重机制**：URL 检测 + Cookie 轮询

### 使用场景

- ✅ 自动化脚本
- ✅ CI/CD（配合环境变量）
- ⚠️ 可能遇到 CSP 问题（已修复大部分）

### 使用方法

```bash
python scripts/get_claude_cookie.py
```

### 工作流程

```
启动脚本
    ↓
打开无痕浏览器窗口
    ↓
导航到 claude.ai
    ↓
[用户登录]
    ↓
自动检测登录完成
    ├─ 方法1: 检测 URL 变化 (/chat, /settings)
    └─ 方法2: 轮询检查 sessionKey cookie
    ↓
提取 cookies
    ↓
验证 cookies
    ↓
保存到 ~/.config/openclaw/claude-session.json
    ↓
关闭浏览器
```

### 优点

- 🤖 自动化：不需要手动按 ENTER
- 🔄 回退机制：多种检测方法

### 缺点

- ⚠️ 可能失败：CSP 或网络问题可能导致检测失败
- 🐢 慢：每次都需要登录
- 🕐 等待时间：自动检测需要轮询

## 推荐使用策略

### 首次设置

```bash
# 使用 Interactive 或 Persistent
python scripts/get_claude_cookie_persistent.py
```

### 日常使用

```bash
# 使用 Persistent（最快）
python scripts/get_claude_cookie_persistent.py

# 或者直接使用缓存的 cookie
python scripts/get_usage.py ~/.config/openclaw/claude-session.json
```

### 故障排除

```bash
# 使用 Interactive（最可靠）
python scripts/get_claude_cookie_interactive.py
```

### 自动化/CI/CD

```bash
# 使用环境变量（最快）
export CLAUDE_SESSION_KEY="sk-ant-sid01-xxxxx"
python scripts/get_usage.py
```

## 性能对比

### 首次运行（需要登录）

| 方法 | 时间 | 步骤 |
|------|------|------|
| Interactive | ~60s | 登录 + 手动确认 |
| Persistent | ~60s | 登录 + 手动确认 |
| Auto-detect | ~65s | 登录 + 自动检测（+5s 轮询） |

### 第二次运行

| 方法 | 时间 | 步骤 |
|------|------|------|
| Interactive | ~60s | 需要重新登录 |
| **Persistent** | **~5s** | ✅ 已登录，只需确认 |
| Auto-detect | ~60s | 需要重新登录 |

### 使用缓存（所有方法）

| 操作 | 时间 |
|------|------|
| 从缓存加载 | ~0.5s |
| 验证 cookie | ~0.3s |
| 获取 usage | ~0.5s |
| **总计** | **~1.3s** |

## 安全性对比

### Interactive（最安全）

- ✅ 不保留任何浏览器数据
- ✅ 每次都是全新环境
- ✅ 适合共享机器

### Persistent（中等）

- ⚠️ 保留浏览器配置文件
- ⚠️ 包含 cookies、缓存、历史记录
- ⚠️ 建议在个人机器使用
- ✅ 配置文件位置可控（`~/.config/openclaw/browser-data/`）

### Auto-detect（最安全）

- ✅ 不保留任何浏览器数据
- ✅ 每次都是全新环境

### 共同的安全措施

所有方法都：
- ✅ 提取的 cookie 保存在 `~/.config/openclaw/claude-session.json`
- ✅ 每次使用前验证 cookie 有效性
- ✅ 支持环境变量 `CLAUDE_SESSION_KEY`

## 实际使用示例

### 场景 1：开发者日常使用

```bash
# 首次设置（使用 persistent）
python scripts/get_claude_cookie_persistent.py

# 以后每次使用（可能已经登录）
python scripts/get_claude_cookie_persistent.py  # 快速提取
python scripts/get_usage.py ~/.config/openclaw/claude-session.json
```

### 场景 2：共享服务器

```bash
# 使用 interactive（不保留数据）
python scripts/get_claude_cookie_interactive.py

# 或使用环境变量
export CLAUDE_SESSION_KEY="sk-ant-sid01-xxxxx"
python scripts/get_usage.py
```

### 场景 3：CI/CD 自动化

```bash
# 在 GitHub Actions / GitLab CI
export CLAUDE_SESSION_KEY="${{ secrets.CLAUDE_SESSION_KEY }}"
python scripts/get_usage.py
```

### 场景 4：一次性任务

```bash
# 使用 interactive（最可靠）
python scripts/get_claude_cookie_interactive.py
python scripts/get_usage.py ~/.config/openclaw/claude-session.json
```

## 快速测试脚本更新

更新 `quick_test.sh` 来支持选择方法：

```bash
bash scripts/quick_test.sh
# 会提示选择方法：
# [1] Interactive (most reliable)
# [2] Persistent (fastest for repeated use)
# [3] Auto-detect (fully automated)
```

## 总结

### 🏆 最佳实践

1. **首次使用**：`get_claude_cookie_persistent.py`
2. **日常开发**：`get_claude_cookie_persistent.py`（保留登录）
3. **故障排除**：`get_claude_cookie_interactive.py`（最可靠）
4. **生产环境**：环境变量 `CLAUDE_SESSION_KEY`

### 🎯 选择指南

| 如果你想... | 使用 |
|-----------|------|
| 最快速度（重复使用） | Persistent |
| 最高可靠性 | Interactive |
| 完全自动化 | Auto-detect |
| 最高安全性 | Interactive + 环境变量 |
| 避免重复登录 | Persistent |

### 💡 Pro Tips

1. **Persistent 模式**第一次运行后，以后可能只需 5 秒
2. 所有方法都支持**三层回退**：环境变量 → 缓存 → 浏览器
3. Cookie 缓存**自动验证**，过期会自动重新提取
4. 可以随时切换方法，它们共享同一个缓存文件
