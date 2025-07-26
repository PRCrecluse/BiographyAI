# 首页和侧边栏数据同步功能

## 功能概述

已成功实现首页和侧边栏之间的实时数据同步功能。当用户在侧边栏中编辑个人信息时，首页会立即显示更新的内容。

## 技术实现

### 1. 数据模型（Models.swift）

#### LocalProfileData 结构体
```swift
struct LocalProfileData {
    var name: String = ""
    var oneLineIntro: String = ""
    var profession: String = ""
    var education: String = ""
    
    // 检查是否有自定义数据
    var hasCustomData: Bool {
        return !name.isEmpty || !oneLineIntro.isEmpty || !profession.isEmpty || !education.isEmpty
    }
    
    // 获取显示用的姓名
    var displayName: String {
        return name.isEmpty ? "Recluse" : name
    }
    
    // 获取显示用的一句话介绍
    var displayOneLineIntro: String {
        return oneLineIntro.isEmpty ? "Building tools to amplify\nour imagination." : oneLineIntro
    }
    
    // 获取显示用的详细信息
    var displayDetailInfo: String {
        if hasCustomData {
            // 如果有自定义数据，只显示用户输入的信息
            let professionInfo = profession.isEmpty ? "" : profession
            let separator = (!profession.isEmpty && !education.isEmpty) ? " | " : ""
            let educationInfo = education.isEmpty ? "" : education
            
            return "\(professionInfo)\(separator)\(educationInfo)"
        } else {
            // 如果没有自定义数据，显示默认预览信息
            return "1yr · Product Designer · Productivity / Dev Tools ·\nSaaS · AI Model · AI Apps · Creator & Builder"
        }
    }
}
```

#### AppState 扩展
- 添加了 `@Published var localProfileData = LocalProfileData()` 用于响应式数据绑定
- 实现了 `loadLocalProfileData()` 方法从 UserDefaults 加载数据
- 实现了 `updateLocalProfileData()` 方法同时更新内存和本地存储

### 2. 首页显示逻辑（HomeView.swift）

首页现在使用动态数据而不是硬编码内容：

```swift
// 主标题 - 显示用户名或默认名称
Text("Hello, I'm \(state.localProfileData.displayName)")

// 一句话介绍 - 显示用户输入或默认介绍
Text(state.localProfileData.displayOneLineIntro)

// 详细信息 - 智能显示用户数据或预览信息
Text(state.localProfileData.displayDetailInfo)
```

### 3. 侧边栏同步逻辑（SidebarView.swift）

#### 数据加载
- `onAppear` 时调用 `loadCurrentProfile()` 
- 优先从 AppState 的 localProfileData 加载
- 如果为空，则从 LocalStorageManager 和 Supabase 数据加载

#### 数据保存
保存时同时更新三个地方：
1. **AppState.localProfileData** - 立即触发 UI 更新
2. **LocalStorageManager** - 本地持久化存储
3. **Supabase** - 云端数据备份

```swift
private func saveProfile() {
    // 1. 更新AppState - 触发首页立即更新
    state.updateLocalProfileData(
        name: name,
        oneLineIntro: oneLineIntro,
        profession: profession,
        education: education
    )
    
    // 2. 本地存储
    LocalStorageManager.shared.saveUserProfile(...)
    
    // 3. 云端同步（异步）
    Task {
        // Supabase 更新...
    }
}
```

## 用户体验

### 预览模式
- 用户首次使用时，显示精美的预览内容
- 姓名："Recluse"
- 介绍："Building tools to amplify our imagination."
- 详细信息：完整的开发者资料展示

### 自定义模式
用户在侧边栏输入信息后：
- **姓名**：显示用户输入的真实姓名
- **介绍**：显示用户的一句话介绍
- **详细信息**：只显示用户填写的职业和教育信息，去除默认的"1yr · Product Designer"等预览内容

### 实时同步
- 用户在侧边栏点击 "Save" 按钮
- 侧边栏自动关闭
- 首页立即显示更新后的内容
- 无需刷新或重启应用

## 数据持久化

### 三级存储策略
1. **内存级别**：AppState.localProfileData（响应式更新）
2. **本地级别**：UserDefaults（应用重启后保持）
3. **云端级别**：Supabase（跨设备同步）

### 数据恢复优先级
1. AppState 内存数据（最快）
2. UserDefaults 本地数据（离线可用）
3. Supabase 云端数据（联网时同步）

## 示例场景

### 场景1：Steve Jobs 的资料
用户在侧边栏输入：
- Name: "Steve Jobs"
- One-line intro: "Think Different"
- Profession: "CEO"
- Education: "Reed College"

首页将显示：
- "Hello, I'm Steve Jobs"
- "Think Different"
- "CEO | Reed College"

### 场景2：部分信息
用户只输入：
- Name: "John"
- Profession: "Designer"

首页将显示：
- "Hello, I'm John"
- "Building tools to amplify our imagination." （默认）
- "Designer" （只显示职业，无分隔符）

## 技术优势

1. **响应式设计**：使用 SwiftUI 的 @Published 实现即时更新
2. **数据一致性**：三级存储确保数据不丢失
3. **性能优化**：内存优先，避免频繁 I/O 操作
4. **用户友好**：智能切换预览/自定义模式
5. **离线支持**：本地存储保证离线可用性 