# App Store 内购功能设置与测试指南

## ✅ 已完成的工作

1. **InAppPurchaseService服务** - 已创建并集成
2. **UI界面更新** - Generate按钮显示价格和付费流程
3. **付费协议文档** - 完整的法律条款
4. **异步代码修复** - 解决了async/await编译错误

## 🛠️ 接下来需要完成的步骤

### 步骤1: App Store Connect配置

#### 1.1 创建内购产品
1. 登录 [App Store Connect](https://appstoreconnect.apple.com)
2. 选择您的应用
3. 进入 **功能 → App内购买项目**
4. 点击 **+** 创建新的内购项目

#### 1.2 产品配置
```
产品类型: 消耗性产品 (Consumable)
产品ID: com.aiprofile.pdf_generation
参考名称: PDF Generation Service
价格: $5.99 USD (Tier 6)
```

#### 1.3 产品描述 (本地化)
**英文:**
- 显示名称: PDF Generation
- 描述: Generate a personalized biography PDF with AI

**中文:**
- 显示名称: PDF生成服务
- 描述: 使用AI生成个性化传记PDF文档

#### 1.4 审核信息
- 审核说明: "This consumable product allows users to generate one personalized biography PDF using AI technology."
- 审核附件: 添加应用截图展示购买流程

### 步骤2: Xcode项目配置

#### 2.1 添加StoreKit Configuration文件
1. 在Xcode中，右键项目 → New File → StoreKit Configuration File
2. 命名为 `Products.storekit`
3. 添加测试产品:
```
Product ID: com.aiprofile.pdf_generation
Type: Consumable
Price: $5.99
Locale: en_US
```

#### 2.2 配置项目设置
1. 选择项目 → Target → Signing & Capabilities
2. 添加 **In-App Purchase** capability
3. 确保Bundle Identifier与App Store Connect中的一致

#### 2.3 更新Info.plist (如需要)
```xml
<key>SKPaymentQueueStartsOnAppTransactionObserver</key>
<false/>
```

### 步骤3: 测试配置

#### 3.1 创建沙盒测试账户
1. 在App Store Connect中，进入 **用户和访问 → 沙盒**
2. 创建新的测试用户:
```
邮箱: test@yourdomain.com
密码: TestPassword123!
名字: Test User
姓氏: Store
国家/地区: 美国
```

#### 3.2 设备设置
1. 在测试设备上退出当前Apple ID
2. 进入 **设置 → App Store → 沙盒账户** 
3. 登录测试账户

### 步骤4: 代码测试

#### 4.1 在Xcode中启用StoreKit测试
1. Product → Scheme → Edit Scheme
2. Run → Options → StoreKit Configuration
3. 选择 `Products.storekit`

#### 4.2 本地测试代码
```swift
// 测试产品加载
func testProductLoading() {
    let purchaseService = InAppPurchaseService.shared
    
    // 检查产品是否加载
    DispatchQueue.main.asyncAfter(deadline: .now() + 2) {
        print("产品数量: \(purchaseService.products.count)")
        print("产品价格: \(purchaseService.pdfGenerationPrice)")
    }
}

// 测试购买流程
func testPurchase() async {
    let purchaseService = InAppPurchaseService.shared
    let success = await purchaseService.purchasePDFGeneration()
    print("购买结果: \(success)")
}
```

### 步骤5: 调试和验证

#### 5.1 控制台日志
运行应用时，查看控制台输出:
```
✅ 成功加载内购产品: 1 个
产品: com.aiprofile.pdf_generation - PDF Generation - $5.99
✅ 购买成功: com.aiprofile.pdf_generation
```

#### 5.2 常见问题排查

**问题1: 产品加载失败**
```
❌ 加载内购产品失败: Error
```
解决方案:
- 检查产品ID是否正确
- 确保网络连接正常
- 验证Bundle Identifier匹配

**问题2: 购买失败**
```
❌ 购买失败: Cannot connect to iTunes Store
```
解决方案:
- 确保使用沙盒测试账户
- 检查设备设置中的沙盒环境
- 重启应用重试

**问题3: 交易验证失败**
```
❌ 交易验证失败: failedVerification
```
解决方案:
- 检查网络连接
- 确保使用正确的Apple ID
- 联系Apple技术支持

### 步骤6: TestFlight测试

#### 6.1 上传Build
1. Archive项目并上传到App Store Connect
2. 在TestFlight中添加内部测试员
3. 分发测试版本

#### 6.2 沙盒测试
- TestFlight版本自动使用沙盒环境
- 使用真实的内购流程进行测试
- 验证整个购买和PDF生成流程

### 步骤7: 生产环境准备

#### 7.1 最终检查清单
- [ ] 内购产品已在App Store Connect中批准
- [ ] 应用税务和银行信息已配置
- [ ] 付费协议页面已集成到应用中
- [ ] 隐私政策已更新包含内购信息
- [ ] 用户协议已包含付费条款

#### 7.2 App审核准备
1. **审核说明**: 详细描述内购功能
2. **测试账户**: 提供有效的沙盒测试账户
3. **演示视频**: 录制完整的购买和使用流程
4. **合规文档**: 确保所有法律文档完整

## 🧪 快速测试步骤

### 最少配置测试
如果您想快速测试，最少需要:

1. **创建StoreKit配置文件** (步骤2.1)
2. **在Xcode中启用StoreKit测试** (步骤4.1)
3. **运行应用并测试购买按钮**

### 完整测试流程
1. 点击"Generate ($5.99)"按钮
2. 确认购买对话框出现
3. 选择"购买"或"取消"
4. 验证相应的成功/失败处理

## 📞 技术支持

如果遇到问题:
1. **查看控制台日志** - 大部分问题都有明确的错误信息
2. **检查网络连接** - 内购需要网络访问
3. **验证配置** - 确保所有ID和设置正确
4. **重启应用** - 有时候简单重启能解决问题

## 🚀 上线准备

当所有测试完成后:
1. 提交应用审核
2. 等待Apple批准内购产品
3. 发布应用到App Store
4. 监控内购收入和用户反馈

---

**恭喜！** 您的AI Profile应用现在已经完全支持内购功能了！ 🎉 