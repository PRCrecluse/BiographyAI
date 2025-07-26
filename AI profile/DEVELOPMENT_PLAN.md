# AI 简历应用开发计划

> 目标：像素级复刻首页（暗黑背景 + 玫瑰色半透明底部导航栏），并串联登陆/注册、侧边栏、Supabase 数据持久化。

---

## 阶段 0：环境准备
1. 新建 `Fonts/` 文件夹并放入华文宋体字体文件（`STSongti-SC-Regular.ttf` & `STSongti-SC-Bold.ttf`）。
2. 在 **Info.plist** 中添加 `UIAppFonts`：
   ```xml
   <key>UIAppFonts</key>
   <array>
       <string>STSongti-SC-Regular.ttf</string>
       <string>STSongti-SC-Bold.ttf</string>
   </array>
   ```
3. 安装 CocoaPods/SwiftPM 依赖 **Supabase iOS SDK**（后续 CLI）：
   ```bash
   swift package add https://github.com/supabase-community/supabase-swift.git
   ```

## 阶段 1：项目结构 ✅ 已完成
```
AI profile/
 └─ AI profile/
     ├─ Fonts/ ──> 字体文件
     ├─ Models.swift ──> 数据模型
     ├─ Theme.swift ──> 颜色 & 字体封装
     ├─ Views/
     │   ├─ HomeView.swift
     │   ├─ LoginView.swift
     │   ├─ RegisterView.swift
     │   ├─ SidebarView.swift
     │   └─ Components/
     │       ├─ BottomTabBar.swift
     │       └─ ...
     ├─ Services/
     │   └─ SupabaseService.swift
     └─ AI_profileApp.swift ──> App 入口
```

## 阶段 2：主题 & 设计系统 ✅ 已完成
- `Theme.Color`：全局颜色（背景黑、文字白/浅灰、玫瑰-黑渐变）。
- `Theme.Font`：封装华文宋体粗体、常规体。

## 阶段 3：首页（HomeView） ✅ 已完成
1. **上半区**：
   - "Hello, I'm XXX" 采用 `STSongti-SC-Bold`，字号根据 Figma/Screenshot 估算如 36~40。
   - 逐渐变灰的子标题文字。
2. **下半区**：`About`、横向滑卡等（后期）。
3. **底部导航**：自定义 `BottomTabBar`；玫瑰色→黑色线性渐变 + 半透明 `background(.ultraThinMaterial)`。

## 阶段 4：认证 ✅ 已完成
- 仅提供"注册"按钮，点击弹出 `RegisterView`（输入邮箱+密码 or Apple/Google 注册）。
- 使用 Supabase Auth。

## 阶段 5：侧边栏 ✅ 已完成
- 滑出 `SidebarView` （`.offset` + `DragGesture`）。
- 提供输入栏：姓名 / 一句话介绍 / 职业。
- 保存后写入 Supabase `profiles` 或 `business_cards`。

## 阶段 6：数据同步 🔄 部分完成
- `SupabaseService` 提供 `loadProfile()`, `updateProfile()`。
- 使用 `AppState` 作为 `@StateObject` 注入环境。

## 阶段 7：发现页 & 收藏夹
- 占位图/后期实现。

---

### 工作流建议
1. 按阶段提交小 PR，保持编译通过。
2. 首页先用静态假数据 → 接入 Supabase 数据替换。
3. UI 先实现暗黑模式再适配浅色（若需）。
4. 频繁运行 `⌘ R` 预览 + TestFlight。 