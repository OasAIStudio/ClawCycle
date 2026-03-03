# ClawPiggy 故障排除指南

## CSP (内容安全策略) 错误

### 问题描述

运行 `get_claude_cookie.py` 时遇到错误：

```
Login timeout: Page.wait_for_function: EvalError: Evaluating a string as JavaScript
violates the following Content Security Policy directive because 'unsafe-eval' is not
an allowed source of script...
```

### 原因

Claude.ai 使用严格的内容安全策略（CSP），阻止 Playwright 的 `wait_for_function()` 执行字符串形式的 JavaScript 代码。

### 解决方案

我们提供了两个版本的 cookie 提取脚本：

#### 方案 1：自动检测版本（推荐）

**脚本：** `get_claude_cookie.py`

**特点：**
- 尝试自动检测登录完成（通过 URL 变化）
- 如果 URL 检测失败，回退到检查 sessionKey cookie
- 无需手动确认

**使用：**
```bash
python scripts/get_claude_cookie.py
```

**适用场景：**
- 自动化脚本
- CI/CD 环境（配合环境变量）
- 希望无交互运行

#### 方案 2：交互式版本（最可靠）

**脚本：** `get_claude_cookie_interactive.py`

**特点：**
- 打开浏览器后等待用户手动确认
- 避免所有 CSP 相关问题
- 100% 可靠

**使用：**
```bash
python scripts/get_claude_cookie_interactive.py
```

**流程：**
1. 脚本打开浏览器窗口
2. 你在浏览器中登录 Claude.ai
3. 登录成功后，回到终端按 ENTER
4. 脚本提取并验证 cookies

**适用场景：**
- 首次设置
- 遇到自动检测问题时
- 需要确保成功提取

### 快速测试脚本更新

`quick_test.sh` 现在默认使用交互式版本：

```bash
bash scripts/quick_test.sh
```

当提示 "Run cookie extraction now?" 时，选择 `y`，然后：
1. 浏览器会自动打开
2. 登录 Claude.ai
3. 回到终端按 ENTER
4. 完成！

## 其他常见问题

### 问题：Playwright 未安装

**错误：**
```
❌ playwright not installed
```

**解决：**
```bash
pip install playwright
playwright install chromium
```

### 问题：Cookie 验证失败

**错误：**
```
Cookie validation failed: 401 Unauthorized
```

**原因：**
- Cookie 已过期
- 账号被登出
- 网络问题

**解决：**
```bash
# 删除缓存
rm ~/.config/openclaw/claude-session.json

# 重新提取
python scripts/get_claude_cookie_interactive.py
```

### 问题：找不到 sessionKey

**错误：**
```
❌ Error: sessionKey not found in cookies
```

**原因：**
- 登录未完成
- 登录失败
- 太快按了 ENTER

**解决：**
1. 确保完全登录（看到聊天界面）
2. 等待页面完全加载
3. 再按 ENTER

### 问题：浏览器无法打开

**错误：**
```
Browser not found
```

**原因：**
- Chromium 未安装

**解决：**
```bash
playwright install chromium
```

### 问题：在服务器/无界面环境中运行

**场景：** 没有图形界面的服务器

**解决方案：使用环境变量**

```bash
# 1. 在本地提取 cookie
python scripts/get_claude_cookie_interactive.py

# 2. 查看 sessionKey
cat ~/.config/openclaw/claude-session.json | grep sessionKey

# 3. 在服务器上设置环境变量
export CLAUDE_SESSION_KEY="sk-ant-sid01-xxxxx"

# 4. 运行脚本（会使用环境变量）
python scripts/get_usage.py
```

## 技术细节

### CSP 是什么？

内容安全策略（Content Security Policy）是一种安全机制，防止：
- XSS 攻击
- 代码注入
- 未授权的脚本执行

Claude.ai 的 CSP 设置了 `script-src 'strict-dynamic'`，这意味着：
- 不允许 `eval()`
- 不允许内联脚本
- 不允许字符串形式的 JavaScript

### Playwright 的 wait_for_function 问题

```python
# ❌ 这种方式违反 CSP
page.wait_for_function("window.location.pathname.includes('/chat')")

# ✅ 这种方式绕过 CSP
page.wait_for_url(lambda url: '/chat' in url.path)

# ✅ 最可靠：手动确认
input("Press ENTER when logged in...")
```

### 为什么交互式版本最可靠？

1. **不依赖 JavaScript 执行** - 完全避免 CSP
2. **用户控制** - 确保登录完全完成
3. **兼容性好** - 适用于所有环境
4. **调试友好** - 可以看到浏览器状态

### 自动检测的两种方法

**方法 1：URL 检测**
```python
page.wait_for_url(lambda url: '/chat' in url.path)
```
- 优点：快速、不需要轮询
- 缺点：可能被 CSP 阻止

**方法 2：Cookie 轮询**
```python
while time.time() - start_time < 120:
    cookies = context.cookies()
    if any(c['name'] == 'sessionKey' for c in cookies):
        break
    time.sleep(2)
```
- 优点：绕过 CSP、可靠
- 缺点：需要轮询、稍慢

## 推荐工作流

### 首次使用

```bash
# 1. 使用交互式版本（最可靠）
python scripts/get_claude_cookie_interactive.py

# 2. 验证 cookie
python scripts/get_usage.py ~/.config/openclaw/claude-session.json

# 3. 运行完整测试
bash scripts/quick_test.sh
```

### 日常使用

```bash
# Cookie 会自动从缓存加载
python scripts/get_usage.py ~/.config/openclaw/claude-session.json
```

### Cookie 过期时

```bash
# 自动检测并重新提取
python scripts/get_claude_cookie.py

# 或使用交互式版本
python scripts/get_claude_cookie_interactive.py
```

## 性能对比

| 方法 | 速度 | 可靠性 | 适用场景 |
|------|------|--------|---------|
| 环境变量 | ⚡️⚡️⚡️ 最快 | ⭐️⭐️⭐️ 高 | CI/CD、自动化 |
| 缓存 + 验证 | ⚡️⚡️ 快 | ⭐️⭐️⭐️ 高 | 日常使用 |
| 自动检测 | ⚡️ 中等 | ⭐️⭐️ 中 | 首次设置 |
| 交互式 | ⚡️ 中等 | ⭐️⭐️⭐️ 最高 | 首次设置、故障排除 |

## 调试技巧

### 查看详细日志

```bash
# 所有诊断信息输出到 stderr
python scripts/get_claude_cookie_interactive.py 2>&1 | tee cookie_debug.log
```

### 检查 cookie 内容

```bash
# 美化输出
cat ~/.config/openclaw/claude-session.json | python -m json.tool

# 只看 cookie 名称
cat ~/.config/openclaw/claude-session.json | python -c "
import json, sys
cookies = json.load(sys.stdin)
for c in cookies:
    print(c['name'])
"
```

### 手动测试 API

```bash
# 提取 sessionKey 值
SESSION_KEY=$(cat ~/.config/openclaw/claude-session.json | python -c "
import json, sys
cookies = json.load(sys.stdin)
sk = next((c['value'] for c in cookies if c['name'] == 'sessionKey'), None)
print(sk)
")

# 手动调用 API
curl -H "Cookie: sessionKey=$SESSION_KEY" \
     https://claude.ai/api/organizations
```

## 需要帮助？

如果以上方法都不能解决问题：

1. 查看完整错误日志
2. 检查网络连接
3. 确认 Claude.ai 服务状态：https://status.anthropic.com
4. 尝试清除浏览器缓存后重新登录
5. 使用交互式版本并在浏览器中手动确认登录成功

## 未来改进

可能的优化方向：

1. **支持更多浏览器**
   - Firefox
   - Safari
   - 用户自定义浏览器路径

2. **更智能的检测**
   - 检测页面元素
   - 监听网络请求
   - 多重验证机制

3. **更好的错误提示**
   - 具体的失败原因
   - 自动修复建议
   - 可视化调试界面
