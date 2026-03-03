# ClawPiggy 测试指南

## Cookie 获取机制说明

### 当前实现

**获取方式：全量 cookies**

```python
cookies = context.cookies()  # 获取所有 claude.ai 域名下的 cookies
```

**包含的 cookies（典型）：**
- `sessionKey` - 主要认证 token（最重要）
- `__cf_bm` - Cloudflare bot management
- `lastActiveOrg` - 最后活跃的组织 ID
- 其他辅助 cookies

### 为什么获取全量？

1. **保险起见**：Claude.ai 可能需要多个 cookies 配合工作
2. **未来兼容**：如果 API 增加新的 cookie 要求，无需修改代码
3. **完整会话**：模拟真实浏览器环境

### 可能的优化

如果测试证明只需要 `sessionKey`，可以优化为：

```python
# 仅提取 sessionKey
session_cookie = next((c for c in context.cookies() if c['name'] == 'sessionKey'), None)
cookies = [session_cookie] if session_cookie else []
```

## 验证方法

### 方法 1：快速验证（推荐）

```bash
cd /path/to/clawpiggy
bash scripts/quick_test.sh
```

**测试内容：**
1. ✅ 依赖检查（playwright、requests）
2. 🔑 Cookie 提取（检查 sessionKey 是否存在）
3. ✅ Cookie 验证（调用 API 测试）
4. 📊 Usage API 测试（获取真实数据）
5. 🔬 最小 Cookie 测试（是否只需 sessionKey）

**预期输出：**
```
🧪 ClawPiggy Quick Test
========================

📦 Checking dependencies...
✅ Dependencies OK

🔑 Test 1: Cookie Extraction
----------------------------
📁 Found cached cookie: /Users/xxx/.config/openclaw/claude-session.json
   Cookie file size: 2.1K
   Last modified: Feb  9 22:30:00 2024
   Number of cookies: 5
   ✅ sessionKey present

✅ Test 2: Cookie Validation
-----------------------------
✅ Cookie is valid!
   API connection successful

📊 Test 3: Usage API
--------------------
✅ Usage data retrieved

   Messages: 45/50
   Remaining: 5
   Type: pro
   7-day usage: 180/300 minutes

🔬 Test 4: Minimal Cookie Test
-------------------------------
Testing with only sessionKey...
✅ Only sessionKey is sufficient!
   💡 Could optimize to extract only sessionKey

========================
✅ All tests completed!
```

### 方法 2：完整测试套件

```bash
cd /path/to/clawpiggy
python scripts/test_cookie.py
```

**测试内容：**
1. Cookie 结构分析（详细列出所有 cookies）
2. 最小 Cookie 验证（测试只用 sessionKey）
3. API 验证测试（调用 organizations API）
4. 完整工作流测试（cookie → usage API）

### 方法 3：手动逐步验证

#### Step 1: 提取 Cookie

```bash
python scripts/get_claude_cookie.py > /tmp/cookies.json
```

**首次运行：** 会打开浏览器窗口
**后续运行：** 使用缓存（如果有效）

**检查输出：**
```bash
cat ~/.config/openclaw/claude-session.json | python -m json.tool | head -20
```

应该看到类似：
```json
[
  {
    "name": "sessionKey",
    "value": "sk-ant-sid01-xxxxx",
    "domain": ".claude.ai",
    "path": "/",
    "expires": 1234567890,
    "httpOnly": true,
    "secure": true
  },
  ...
]
```

#### Step 2: 验证 Cookie

```bash
python scripts/get_usage.py ~/.config/openclaw/claude-session.json
```

**成功输出：**
```json
{
  "current_period": {
    "message_count": 45,
    "message_limit": 50,
    "remaining": 5
  },
  "reset_at": "2024-02-10T00:00:00.000Z",
  "usage_type": "pro"
}
```

**失败输出：**
```
Failed to get organizations: 401 Unauthorized
```

#### Step 3: 测试最小 Cookie

```bash
python -c "
import json
import sys
sys.path.insert(0, 'scripts')
from get_claude_cookie import validate_cookie

# 加载完整 cookies
with open('$HOME/.config/openclaw/claude-session.json') as f:
    full = json.load(f)

# 只提取 sessionKey
session = [c for c in full if c['name'] == 'sessionKey']

print(f'Full cookies valid: {validate_cookie(full)}')
print(f'Only sessionKey valid: {validate_cookie(session)}')
"
```

## 常见问题

### Q1: 为什么要测试"最小 Cookie"？

**原因：**
- 如果只需要 `sessionKey`，可以简化代码
- 减少存储空间
- 提高安全性（只存储必要的认证信息）

**测试目的：**
确定是否可以优化为只提取 `sessionKey`

### Q2: Cookie 会过期吗？

**是的**，Claude sessionKey 通常 30 天过期。

**脚本的处理：**
1. 每次使用前验证（调用 API 测试）
2. 如果过期，自动触发浏览器重新登录
3. 用户无需手动删除缓存

### Q3: 如何强制重新获取 Cookie？

```bash
# 删除缓存
rm ~/.config/openclaw/claude-session.json

# 重新提取
python scripts/get_claude_cookie.py
```

### Q4: 可以在无头模式运行吗？

**当前：** 不支持（`headless=False`）

**原因：**
- Claude.ai 有 bot 检测
- 需要真实浏览器环境登录
- 无头模式可能被识别为自动化

**可能的方案：**
- 使用环境变量 `CLAUDE_SESSION_KEY`
- 手动提取 cookie 后设置

### Q5: 如何在 CI/CD 中使用？

**方法 1：环境变量**
```bash
export CLAUDE_SESSION_KEY="sk-ant-sid01-xxxxx"
python scripts/get_claude_cookie.py
```

**方法 2：预先提取**
```bash
# 本地提取
python scripts/get_claude_cookie.py

# 上传到 CI secrets
cat ~/.config/openclaw/claude-session.json | base64

# CI 中解码
echo "$CLAUDE_COOKIE_BASE64" | base64 -d > ~/.config/openclaw/claude-session.json
```

## 性能基准

### Cookie 提取时间

| 场景 | 时间 |
|------|------|
| 环境变量（无验证） | ~0.1s |
| 缓存命中（有验证） | ~0.5s |
| 浏览器登录 | ~30-60s（取决于用户） |

### API 调用时间

| 操作 | 时间 |
|------|------|
| Cookie 验证 | ~0.3s |
| 获取 Usage | ~0.5s |
| 完整流程 | ~1s |

## 安全建议

1. **Cookie 文件权限**
   ```bash
   chmod 600 ~/.config/openclaw/claude-session.json
   ```

2. **不要提交到 Git**
   ```bash
   echo "claude-session.json" >> ~/.gitignore
   ```

3. **定期刷新**
   - 建议每 7 天重新验证
   - 或在使用前自动验证（已实现）

4. **环境变量安全**
   - 不要在日志中打印
   - 使用 secrets 管理工具
   - 避免在命令行历史中暴露

## 下一步

完成 Cookie 验证后，可以测试：

1. **隔离执行**
   ```bash
   bash scripts/execute_isolated.sh "Create a hello.txt file"
   ```

2. **集成到 openClaw**
   - 将 skill 加载到 Claude
   - 测试 usage 监控功能
   - 测试隔离任务执行

3. **性能优化**（如果最小 Cookie 测试通过）
   - 修改为只提取 sessionKey
   - 减小缓存文件大小
   - 提高提取速度
