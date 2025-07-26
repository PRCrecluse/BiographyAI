import SwiftUI
import PhotosUI
import Darwin
import StoreKit

struct BiographyGeneratorView: View {
    @EnvironmentObject var state: AppState
    @EnvironmentObject var themeManager: ThemeManager
    @StateObject private var agentService = AgentService.shared
    @StateObject private var purchaseService = InAppPurchaseService.shared
    @StateObject private var localBiographyService = LocalBiographyService.shared
    @State private var userRequirements = ""
    @State private var selectedTemplate = "classic"
    @State private var selectedLanguage = "en"
    @State private var isGenerating = false
    @State private var showingAlert = false
    @State private var alertMessage = ""
    @State private var showingPurchaseAlert = false
    @State private var useLocalGeneration = false

    
    // 图片上传相关状态
    @State private var showingImageViewer = false
    @State private var selectedImageIndex = 0
    @State private var showingImagePicker = false // 用于旧版本的图片选择器
    
    let templates = [
        ("classic", "Classic Style".localized),
        ("modern", "Modern Style".localized),
        ("elegant", "Elegant Style".localized),
        ("creative", "Creative Style".localized)
    ]
    
    let languages = [
        ("en", "English".localized),
        ("it", "Italian".localized),
        ("fr", "French".localized),
        ("pt", "Portuguese".localized),
        ("es", "Spanish".localized)
    ]
    
    var body: some View {
        ZStack {
            Theme.Colors.background
                .ignoresSafeArea()
            
            VStack(spacing: 0) {
                // 自定义顶部栏
                HStack {
                    Button("Cancel".localized) {
                        state.showingBiographyGenerator = false
                    }
                    .font(.system(size: 16))
                    .foregroundColor(.blue)
                    
                    Spacer()
                    
                    Text("Generate Biography".localized)
                        .font(.system(size: 18, weight: .semibold))
                        .foregroundColor(Theme.Colors.primaryText(for: themeManager.currentTheme))
                    
                    Spacer()
                    
                    // 占位，保持标题居中
                    Text("Cancel".localized)
                        .font(.system(size: 16))
                        .foregroundColor(.clear)
                }
                .padding(.horizontal, 24)
                .padding(.top, 20)
                .padding(.bottom, 16)
                
                ScrollView {
                    VStack(alignment: .leading, spacing: 24) {
                        // 连接状态指示器
                        connectionStatusView
                        
                        // 图片上传和预览区域
                            uploadedImagesSection
                        
                        // 用户要求输入
                        userRequirementsSection
                        
                        // 模板选择
                        templateSelectionSection
                        
                        // 语言选择
                        languageSelectionSection
                        
                        // 生成按钮
                        generateButtonSection
                        
                        // 当前任务状态
                        if let task = state.currentBiographyTask {
                            taskStatusSection(task)
                        }
                        
                        Spacer(minLength: 100)
                    }
                    .padding(.horizontal, 24)
                }
            }
        }
        .alert("Notice".localized, isPresented: $showingAlert) {
            Button("OK", role: .cancel) { 
                // 不清理任务状态，让View Results按钮持续显示
                // 任务状态将在用户重新进入页面时清理
            }
        } message: {
            Text(alertMessage)
        }
        // 已移除：不再显示本地生成弹窗，网络未连接时显示暗淡按钮
        .fullScreenCover(isPresented: $showingImageViewer) {
            ImageViewerView(images: state.assetsImages, currentIndex: $selectedImageIndex)
        }
        .sheet(isPresented: $showingImagePicker) {
            if #available(iOS 16.0, *) {
                EmptyView() // 不会用到
            } else {
                LegacyImagePicker { images in
                    Task {
                        await addNewImages(images)
                    }
                }
            }
        }
        .sheet(isPresented: $state.showingImageQA) {
            ImageQAView(
                images: state.assetsImages,
                userRequirements: userRequirements,
                templateStyle: selectedTemplate,
                language: selectedLanguage
            ) { completedQAs in
                handleQACompletion(completedQAs)
            }
            .environmentObject(state)
            .environmentObject(themeManager)
        }
        .onAppear {
            // 只在用户实际进入传记生成页面时才检查连接
            // agentService.checkConnection() - 移到实际需要时
            loadDefaultRequirements()
            
            // 当用户重新进入页面时，清理之前的任务状态
            // 这样View Results按钮会消失，用户可以开始新的生成
            if let task = state.currentBiographyTask, task.status == .completed {
                state.currentBiographyTask = nil
            }
        }
    }
    
    // MARK: - 连接状态视图
    private var connectionStatusView: some View {
        HStack {
            if agentService.isReconnecting {
                ProgressView()
                    .scaleEffect(0.6)
                    .frame(width: 8, height: 8)
            } else {
                Circle()
                    .fill(agentService.isConnected ? .green : .red)
                    .frame(width: 8, height: 8)
            }
            
            Text(agentService.isReconnecting ? "Reconnecting...".localized : 
                 (agentService.isConnected ? "Agent Connected".localized : "Agent Disconnected".localized))
                .font(.system(size: 12))
                .foregroundColor(Theme.Colors.primaryText(for: themeManager.currentTheme))
            
            Spacer()
            
            Button(agentService.isReconnecting ? "Connecting...".localized : "Reconnect".localized) {
                print("🔘 用户点击了重连按钮")
                print("📱 当前连接状态: \(agentService.isConnected ? "已连接" : "未连接")")
                print("🔄 当前重连状态: \(agentService.isReconnecting ? "重连中" : "空闲")")
                
                if !agentService.isReconnecting {
                    agentService.reconnectWithRetry()
                }
            }
            .font(.system(size: 12))
            .foregroundColor(agentService.isReconnecting ? .gray : .blue)
            .disabled(agentService.isReconnecting)
        }
        .padding(.horizontal, 12)
        .padding(.vertical, 8)
        .background(
            RoundedRectangle(cornerRadius: 8)
                .fill(Color.gray.opacity(0.2))
        )
    }
    
    // MARK: - 已上传图片区域
    private var uploadedImagesSection: some View {
        VStack(alignment: .leading, spacing: 12) {
            HStack {
                Text(String(format: "My Highlights (%d)".localized, state.assetsImages.count))
                .font(.system(size: 18, weight: .semibold))
                    .foregroundColor(Theme.Colors.primaryText(for: themeManager.currentTheme))
                
                Spacer()
                
                // 上传图片按钮 - 版本兼容
                addImageButton
            }
            
            // 添加图片必需提示
            Text("Note: At least 9 photos are required for biography generation.".localized)
                .font(.system(size: 11))
                .foregroundColor(.gray)
                .multilineTextAlignment(.leading)
            
            if state.assetsImages.isEmpty {
                // 空状态 - 大的上传区域
                Button {
                    openImagePicker()
                } label: {
                    VStack(spacing: 12) {
                        Image(systemName: "photo.on.rectangle.angled")
                            .font(.system(size: 40))
                            .foregroundColor(.gray)
                        
                        VStack(spacing: 4) {
                            Text("Add your highlights (Optional)".localized)
                                .font(.system(size: 16, weight: .medium))
                                .foregroundColor(Theme.Colors.primaryText(for: themeManager.currentTheme))
                            
                            Text("Upload images to enrich your biography, or skip to create text-only".localized)
                                .font(.system(size: 12))
                                .foregroundColor(.gray)
                                .multilineTextAlignment(.center)
                        }
                    }
                    .frame(maxWidth: .infinity)
                    .frame(height: 120)
                    .background(
                        RoundedRectangle(cornerRadius: 12)
                            .fill(Color.gray.opacity(0.1))
                            .overlay(
                                RoundedRectangle(cornerRadius: 12)
                                    .stroke(Color.gray.opacity(0.3), style: StrokeStyle(lineWidth: 1, dash: [5]))
                            )
                    )
                }
            } else {
                // 已有图片时的网格显示
                LazyVGrid(columns: Array(repeating: GridItem(.flexible(), spacing: 8), count: 3), spacing: 8) {
                    ForEach(0..<state.assetsImages.count, id: \.self) { index in
                        Button {
                            selectedImageIndex = index
                            showingImageViewer = true
                        } label: {
                        Image(uiImage: state.assetsImages[index])
                            .resizable()
                            .aspectRatio(contentMode: .fill)
                                .frame(width: 80, height: 80)
                            .clipped()
                            .cornerRadius(8)
                    }
                }
                    
                    // 添加图片按钮
                    Button {
                        openImagePicker()
                    } label: {
                        RoundedRectangle(cornerRadius: 8)
                            .stroke(Color.gray.opacity(0.4), style: StrokeStyle(lineWidth: 1, dash: [5]))
                            .frame(width: 80, height: 80)
                            .overlay(
                                Image(systemName: "plus")
                                    .font(.system(size: 20))
                                    .foregroundColor(.gray)
                            )
                    }
                }
            }
        }
    }
    
    // MARK: - Version-aware Add Image Button
    @ViewBuilder
    private var addImageButton: some View {
        if #available(iOS 16.0, *) {
            PhotosPickerButton()
        } else {
            Button {
                openImagePicker()
            } label: {
                HStack(spacing: 4) {
                    Image(systemName: "plus")
                        .font(.system(size: 12, weight: .bold))
                    Text("Add".localized)
                        .font(.system(size: 12, weight: .medium))
                }
                .foregroundColor(.blue)
                .padding(.horizontal, 8)
                .padding(.vertical, 4)
                .background(
                    RoundedRectangle(cornerRadius: 6)
                        .stroke(.blue, lineWidth: 1)
                )
            }
        }
    }
    
    @available(iOS 16.0, *)
    private struct PhotosPickerButton: View {
        @EnvironmentObject var state: AppState
        @State private var selectedItems: [PhotosPickerItem] = []
        
        var body: some View {
            PhotosPicker(selection: $selectedItems, maxSelectionCount: 30, matching: .any(of: [.images, .videos])) {
                HStack(spacing: 4) {
                    Image(systemName: "plus")
                        .font(.system(size: 12, weight: .bold))
                    Text("Add".localized)
                        .font(.system(size: 12, weight: .medium))
                }
                .foregroundColor(.blue)
                .padding(.horizontal, 8)
                .padding(.vertical, 4)
                .background(
                    RoundedRectangle(cornerRadius: 6)
                        .stroke(.blue, lineWidth: 1)
                )
            }
            .onChange(of: selectedItems) { newItems in
                if !newItems.isEmpty {
                    Task {
                        await loadImagesFromPhotosPicker(newItems)
                        await MainActor.run {
                            selectedItems = []
                        }
                    }
                }
            }
        }
        
        @MainActor
        private func loadImagesFromPhotosPicker(_ items: [PhotosPickerItem]) async {
            var newImages: [UIImage] = []
            
            for item in items {
                if state.assetsImages.count + newImages.count >= 30 {
                    break
                }
                
                if let data = try? await item.loadTransferable(type: Data.self),
                   let image = UIImage(data: data) {
                    newImages.append(image)
                }
            }
            
            state.addAssetsImages(newImages)
        }
    }
    
    private func openImagePicker() {
        if #available(iOS 16.0, *) {
            // iOS 16+ 会通过 PhotosPicker 自动处理，这里只是占位
            // 实际的图片选择通过 PhotosPicker 的 selection binding 处理
            return
        } else {
            // iOS 15 及以下使用传统的图片选择器
            showingImagePicker = true
        }
    }
    
    // MARK: - 用户要求区域
    private var userRequirementsSection: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text("Biography Requirements".localized)
                .font(.system(size: 18, weight: .semibold))
                .foregroundColor(Theme.Colors.primaryText(for: themeManager.currentTheme))
            
            Text("Describe how you want to write the biography, including style, key content, etc.".localized)
                .font(.system(size: 12))
                .foregroundColor(Color.gray)
            
            TextEditor(text: $userRequirements)
                .font(.system(size: 14))
                .foregroundColor(Theme.Colors.primaryText(for: themeManager.currentTheme))
                .padding(12)
                .frame(minHeight: 120)
                .background(
                    RoundedRectangle(cornerRadius: 12)
                        .fill(Color.gray.opacity(0.1))
                )
                .overlay(
                    RoundedRectangle(cornerRadius: 12)
                        .stroke(Color.gray.opacity(0.3), lineWidth: 1)
                )
                .onChange(of: userRequirements) { newValue in
                    // 当用户修改要求时自动保存到持久化存储
                    state.updateAssetsComments(newValue)
                }
        }
    }
    
    // MARK: - 模板选择区域
    private var templateSelectionSection: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text("Template Style".localized)
                .font(.system(size: 18, weight: .semibold))
                .foregroundColor(Theme.Colors.primaryText(for: themeManager.currentTheme))
            
            LazyVGrid(columns: Array(repeating: GridItem(.flexible()), count: 2), spacing: 8) {
                ForEach(templates, id: \.0) { template in
                    Button {
                        selectedTemplate = template.0
                    } label: {
                        VStack(spacing: 8) {
                            Image(systemName: getTemplateIcon(template.0))
                                .font(.system(size: 20))
                                .foregroundColor(selectedTemplate == template.0 ? .white : Theme.Colors.primaryText(for: themeManager.currentTheme))
                            
                            Text(template.1)
                                .font(.system(size: 12, weight: .medium))
                                .foregroundColor(selectedTemplate == template.0 ? .white : Theme.Colors.primaryText(for: themeManager.currentTheme))
                        }
                        .frame(height: 60)
                        .frame(maxWidth: .infinity)
                        .background(
                            RoundedRectangle(cornerRadius: 12)
                                .fill(selectedTemplate == template.0 ? Theme.Colors.rose : Theme.Colors.secondaryText(for: themeManager.currentTheme).opacity(0.2))
                        )
                        .overlay(
                            RoundedRectangle(cornerRadius: 12)
                                .stroke(selectedTemplate == template.0 ? Theme.Colors.rose : Theme.Colors.secondaryText(for: themeManager.currentTheme).opacity(0.4), lineWidth: 1)
                        )
                    }
                }
            }
        }
    }
    
    // MARK: - 语言选择区域
    private var languageSelectionSection: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text("Language".localized)
                .font(.system(size: 18, weight: .semibold))
                .foregroundColor(Theme.Colors.primaryText(for: themeManager.currentTheme))
            
            HStack(spacing: 8) {
                ForEach(languages, id: \.0) { language in
                    Button {
                        selectedLanguage = language.0
                    } label: {
                        Text(language.1)
                            .font(.system(size: 12, weight: .medium))
                            .foregroundColor(selectedLanguage == language.0 ? .white : Theme.Colors.primaryText(for: themeManager.currentTheme))
                            .padding(.horizontal, 16)
                            .padding(.vertical, 8)
                            .background(
                                RoundedRectangle(cornerRadius: 20)
                                    .fill(selectedLanguage == language.0 ? Theme.Colors.rose : Theme.Colors.secondaryText(for: themeManager.currentTheme).opacity(0.2))
                            )
                            .overlay(
                                RoundedRectangle(cornerRadius: 20)
                                    .stroke(selectedLanguage == language.0 ? Theme.Colors.rose : Theme.Colors.secondaryText(for: themeManager.currentTheme).opacity(0.4), lineWidth: 1)
                            )
                    }
                }
                Spacer()
            }
        }
    }
    
    // MARK: - 生成按钮区域
    private var generateButtonSection: some View {
        VStack(spacing: 12) {
            Button {
                handleGenerateBiography()
            } label: {
                HStack {
                    if isGenerating || purchaseService.isPurchasing {
                        ProgressView()
                            .scaleEffect(0.8)
                            .progressViewStyle(CircularProgressViewStyle(tint: .white))
                    }
                    
                    Text(getButtonText())
                        .font(.system(size: 18, weight: .semibold))
                        .foregroundColor(getButtonTextColor())
                }
                .frame(maxWidth: .infinity)
                .frame(height: 50)
                .background(
                    getButtonColor(),
                    in: RoundedRectangle(cornerRadius: 12)
                )
            }
            .disabled(!canGenerate || isGenerating || purchaseService.isPurchasing)
            
            // 付费协议提示
            Text("Purchase indicates you agree to our payment terms".localized)
                .font(.system(size: 11))
                .foregroundColor(.gray)
                .multilineTextAlignment(.center)
            
            // View Results按钮 - 只在生成完成时显示
            if let task = state.currentBiographyTask, task.status == .completed {
                Button {
                    viewResults(task)
                } label: {
                    Text("View Results".localized)
                        .font(.system(size: 16, weight: .semibold))
                        .foregroundColor(.white)
                        .frame(maxWidth: .infinity)
                        .frame(height: 50)
                        .background(
                            RoundedRectangle(cornerRadius: 12)
                                .fill(Theme.Colors.buttonGradient)
                        )
                }
            }
        }
    }
    
    private func getButtonText() -> String {
        if purchaseService.isPurchasing {
            return "Processing Purchase...".localized
        } else if isGenerating || localBiographyService.isGenerating {
            if useLocalGeneration {
                return "本地生成中... 请稍等"
            } else {
                return "Generating... Please wait, about 1 minute".localized
            }
        } else {
            return "Generate".localized
        }
    }
    
    private func getButtonColor() -> LinearGradient {
        if canGenerate {
            // 在浅色模式下使用白色，深色模式下使用和View Results一样的渐变
            if themeManager.currentTheme == .light {
                return LinearGradient(
                    colors: [.white, .white],
                    startPoint: .leading,
                    endPoint: .trailing
                )
            } else {
                return Theme.Colors.buttonGradient
            }
        } else {
            return LinearGradient(
                colors: [Color.gray.opacity(0.4), Color.gray.opacity(0.4)],
                startPoint: .leading,
                endPoint: .trailing
            )
        }
    }
    
    private func getButtonTextColor() -> Color {
        if canGenerate {
            // 在浅色模式下使用黑色文字，深色模式下使用白色文字
            return themeManager.currentTheme == .light ? .black : .white
        } else {
            return .white
        }
    }
    
    // MARK: - 任务状态区域
    private func taskStatusSection(_ task: BiographyTask) -> some View {
        VStack(alignment: .leading, spacing: 12) {
            HStack {
                Text("Generation Progress".localized)
                    .font(.system(size: 16, weight: .semibold))
                    .foregroundColor(Theme.Colors.primaryText(for: themeManager.currentTheme))
                
                Spacer()
                
                Text(task.status.displayName)
                    .font(.system(size: 12, weight: .medium))
                    .foregroundColor(task.status.color)
                    .padding(.horizontal, 8)
                    .padding(.vertical, 4)
                    .background(
                        RoundedRectangle(cornerRadius: 12)
                            .fill(task.status.color.opacity(0.1))
                    )
            }
            
            if task.status == .processing {
                ProgressView(value: task.progress)
                    .progressViewStyle(LinearProgressViewStyle())
                
                Text("\(Int(task.progress * 100))% - \(task.message)")
                    .font(.system(size: 12))
                    .foregroundColor(Theme.Colors.primaryText(for: themeManager.currentTheme))
            }
            
            if task.status == .completed {
                Text("✅ \(task.message)")
                    .font(.system(size: 12))
                    .foregroundColor(Theme.Colors.primaryText(for: themeManager.currentTheme))
            }
            
            if task.status == .failed {
                Text(task.errorMessage ?? "Generation Failed".localized)
                    .font(.system(size: 12))
                    .foregroundColor(.red)
            }
        }
        .padding(16)
        .background(
            RoundedRectangle(cornerRadius: 12)
                .fill(Color.gray.opacity(0.1))
        )
    }
    
    // MARK: - Helper Methods
    private func getTemplateIcon(_ template: String) -> String {
        switch template {
        case "classic": return "doc.text"
        case "modern": return "rectangle.stack"
        case "elegant": return "leaf"
        case "creative": return "paintbrush"
        default: return "doc"
        }
    }
    
    private var canGenerate: Bool {
        return !userRequirements.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty &&
               !isGenerating &&
               !localBiographyService.isGenerating &&
               agentService.isConnected &&  // 只有网络连接时才能生成
               state.assetsImages.count >= 9  // 至少需要9张照片
    }
    
    private func loadDefaultRequirements() {
        if userRequirements.isEmpty {
            userRequirements = state.assetsComments.isEmpty ? 
                "Please write a personal biography for me based on the provided images, showcasing my life experiences, growth journey, and important moments." : 
                state.assetsComments
        }
    }
    
    private func viewResults(_ task: BiographyTask) {
        // 先保存PDF到本地
            downloadAndSaveBiography(task)
        
        // 然后跳转到Assets页面
        DispatchQueue.main.asyncAfter(deadline: .now() + 1.0) {
            state.showingBiographyGenerator = false
            state.currentSection = .assets
            // 不清理任务状态，保持View Results按钮可用
        }
    }
    
    private func startPollingTaskStatus(_ task: BiographyTask) {
        Task {
            // 立即检查一次状态（可能任务已经完成）
            do {
                let initialStatus = try await agentService.checkTaskStatus(taskId: task.id)
                print("初始任务状态检查: \(initialStatus.status)")
                
                await MainActor.run {
                    if let currentTask = state.currentBiographyTask, currentTask.id == task.id {
                        let newStatus = BiographyTask.Status(rawValue: initialStatus.status) ?? .failed
                        state.currentBiographyTask = BiographyTask(
                            id: currentTask.id,
                            status: newStatus,
                            progress: initialStatus.progress,
                            message: initialStatus.message ?? "处理中...",
                            userRequirements: currentTask.userRequirements,
                            images: currentTask.images,
                            createdAt: currentTask.createdAt,
                            pdfUrl: initialStatus.pdfUrl,
                            errorMessage: initialStatus.errorMessage ?? initialStatus.error
                        )
                    }
                }
                
                // 如果任务已经完成，直接返回
                if initialStatus.status == "completed" || initialStatus.status == "failed" {
                    print("任务已完成，无需轮询")
                    return
                }
            } catch {
                print("初始状态检查失败: \(error)")
            }
            
            // 开始轮询
            while true {
                do {
                    // 等待3秒后查询
                    try await Task.sleep(nanoseconds: 3_000_000_000)
                    
                    let status = try await agentService.checkTaskStatus(taskId: task.id)
                    
                    await MainActor.run {
                        if let currentTask = state.currentBiographyTask, currentTask.id == task.id {
                            let newStatus = BiographyTask.Status(rawValue: status.status) ?? .failed
                            print("轮询更新任务状态: \(status.status) -> \(newStatus)")
                            
                            state.currentBiographyTask = BiographyTask(
                                id: currentTask.id,
                                status: newStatus,
                                progress: status.progress,
                                message: status.message ?? "处理中...",
                                userRequirements: currentTask.userRequirements,
                                images: currentTask.images,
                                createdAt: currentTask.createdAt,
                                pdfUrl: status.pdfUrl,
                                errorMessage: status.errorMessage ?? status.error
                            )
                        }
                    }
                    
                    // 如果任务完成或失败，停止轮询
                    if status.status == "completed" || status.status == "failed" {
                        print("任务轮询完成，状态: \(status.status)")
                        break
                    }
                } catch {
                    print("轮询任务状态失败: \(error)")
                    
                    // 尝试重新连接
                    if let agentError = error as? AgentError {
                        print("代理错误: \(agentError.localizedDescription)")
                    }
                    
                    // 等待5秒后重试
                    try? await Task.sleep(nanoseconds: 5_000_000_000)
                }
            }
        }
    }
    
    private func handleGenerateBiography() {
        print("🎯 handleGenerateBiography 被调用")
        print("📊 当前状态: isGenerating=\(isGenerating), canGenerate=\(canGenerate)")
        print("🔗 Agent连接状态: \(agentService.isConnected)")
        print("💰 购买状态: canGeneratePDF=\(purchaseService.canGeneratePDF())")
        print("📸 当前照片数量: \(state.assetsImages.count)")
        
        // 首先检查照片数量
        if state.assetsImages.count < 9 {
            print("❌ 照片数量不足: \(state.assetsImages.count)/9")
            alertMessage = "Please upload at least 9 photos to generate a personal biography.".localized
            showingAlert = true
            return
        }
        
        // 检查是否需要购买
        if !purchaseService.canGeneratePDF() {
            print("❌ 用户未购买，需要先购买")
            Task {
                print("🛒 开始购买流程...")
                let success = await purchaseService.purchasePDFGeneration()
                
                if success {
                    print("✅ 购买成功，开始传记生成")
                    await MainActor.run {
                        checkConnectionAndStartGeneration()
                    }
                } else {
                    print("❌ 内购失败: \(purchaseService.purchaseError ?? "Unknown error")")
                    await MainActor.run {
                        alertMessage = "Purchase failed: \(purchaseService.purchaseError ?? "Unknown error")"
                        showingAlert = true
                    }
                }
            }
        } else {
            print("✅ 用户已购买，直接开始传记生成")
            checkConnectionAndStartGeneration()
        }
    }
    
    private func checkConnectionAndStartGeneration() {
        // 确保在生成传记前检查连接
        agentService.checkConnection()
        
        if agentService.isConnected {
            startBiographyGeneration()
        } else {
            // 连接失败，尝试重新连接
            Task {
                await agentService.checkConnection()
                if agentService.isConnected {
                    await MainActor.run {
                        startBiographyGeneration()
                    }
                } else {
                    // 网络未连接，不做任何操作，按钮已经是暗淡不可点击状态
                    print("❌ Agent服务连接失败，按钮将保持暗淡不可点击状态")
                }
            }
        }
    }
    
    private func startBiographyGeneration() {
        print("🚀 开始传记生成...")
        print("📸 当前图片数量: \(state.assetsImages.count)")
        print("🔍 图片数组是否为空: \(state.assetsImages.isEmpty)")
        
        // 1. 检查是否有图片需要问答
        if !state.assetsImages.isEmpty {
            print("✅ 发现图片，每次Generate都重新开始问答流程")
            
            // 每次Generate都清除旧的问答数据，重新开始
            print("🧹 清除旧的问答数据，重新开始问答流程")
            LocalStorageManager.shared.clearImageQAs()
            
            // 启动问答界面
            print("📝 启动图片问答界面...")
            print("🎯 设置 state.showingImageQA = true")
            
            // 确保UI更新在主线程上执行
            DispatchQueue.main.async {
                state.showingImageQA = true
            }
            return
        } else {
            print("⚠️ 没有图片，跳过问答环节")
        }
        
        // 2. 读取问答数据
        let imageQAs = LocalStorageManager.shared.loadImageQAs()
        print("📊 读取到问答数据: \(imageQAs.count)个")
        
        for (index, qa) in imageQAs.enumerated() {
            print("  问答\(index+1): 时期='\(qa.time)', 活动='\(qa.activity)', 完成=\(qa.isCompleted)")
        }
        
        // 3. 构建增强需求
        let enhancedRequirements = buildEnhancedRequirements(
            originalRequirements: userRequirements, 
            imageQAs: imageQAs
        )
        
        print("📏 增强需求构建完成，长度: \(enhancedRequirements.count)字符")
        print("📝 增强需求预览:\n\(String(enhancedRequirements.prefix(300)))...")
        
        // 4. 开始生成传记
        Task {
            await originalGenerateBiography(with: imageQAs)
        }
    }
    
    private func handleQACompletion(_ completedQAs: [ImageQA]) {
        // 保存问答数据到状态和本地存储
        state.currentImageQAs = completedQAs
        LocalStorageManager.shared.saveImageQAs(completedQAs)
        
        // 调试信息
        print("✅ 图片问答完成，共 \(completedQAs.count) 个问答")
        for (index, qa) in completedQAs.enumerated() {
            if qa.isCompleted {
                print("  问答\(index+1): 时期=\(qa.time), 活动=\(qa.activity)")
            }
        }
        
        // 开始实际的传记生成
        Task {
            await originalGenerateBiography(with: completedQAs)
        }
    }
    
    private func originalGenerateBiography(with imageQAs: [ImageQA]) async {
        print("📝 开始调用AI服务生成传记...")
        
        await MainActor.run {
            isGenerating = true
            alertMessage = ""
        }
        
        do {
            // 构建增强需求
            let enhancedRequirements = buildEnhancedRequirements(
                originalRequirements: userRequirements,
                imageQAs: imageQAs
            )
            
            print("🔧 最终需求构建完成:")
            print("📊 需求长度: \(enhancedRequirements.count)字符")
            print("📝 需求内容: \(enhancedRequirements)")
            
            // 发送生成请求
            print("🌐 向Agent服务发送生成请求...")
            let task = try await agentService.createBiography(
                images: state.assetsImages,
                userRequirements: enhancedRequirements,  // 使用增强需求
                templateStyle: selectedTemplate,
                language: selectedLanguage
            )
            
            print("✅ Agent服务返回任务ID: \(task.id)")
            
            await MainActor.run {
                state.currentBiographyTask = task
                isGenerating = false
            }
            
            // 开始轮询任务状态
            print("🔄 开始轮询任务状态...")
            startCustomPollingTask(task)
            
        } catch {
            print("❌ API传记生成失败: \(error)")
            print("🔄 自动切换到本地生成作为备用方案...")
            
            await MainActor.run {
                isGenerating = false
            }
            
            // 自动切换到本地生成
            await startLocalBiographyGenerationAsFallback()
        }
    }
    
    // MARK: - 本地生成方法
    private func startLocalBiographyGenerationAsFallback() async {
        print("🏠 API失败，启动本地传记生成作为备用方案...")
        
        await MainActor.run {
            isGenerating = true
            useLocalGeneration = true
        }
        
        do {
            let result = await localBiographyService.generateBiography(
                from: state.assetsImages,
                userRequirements: userRequirements,
                language: selectedLanguage
            )
            
            switch result {
            case .success(let pdfURL):
                print("✅ 本地传记生成成功（备用方案）: \(pdfURL)")
                
                // 创建一个本地任务状态
                let localTask = BiographyTask(
                    id: "local_\(Int(Date().timeIntervalSince1970))",
                    status: .completed,
                    progress: 1.0,
                    message: "本地传记生成完成（备用方案）",
                    userRequirements: userRequirements,
                    images: state.assetsImages,
                    createdAt: Date(),
                    pdfUrl: pdfURL.absoluteString
                )
                
                await MainActor.run {
                    state.currentBiographyTask = localTask
                    isGenerating = false
                    useLocalGeneration = false
                    
                    // 重新加载传记列表以显示新生成的传记
                    state.biographies = LocalStorageManager.shared.loadBiographies()
                    print("✅ 传记列表已刷新，新增传记数量: \(state.biographies.count)")
                    
                    // 备用方案完成，无需显示弹窗 - 让用户体验更加无缝
                    print("✅ 备用方案完成，传记已生成并保存到Assets")
                }
                
            case .failure(let error):
                print("❌ 本地传记生成失败（备用方案）: \(error)")
                await MainActor.run {
                    isGenerating = false
                    useLocalGeneration = false
                    alertMessage = "API服务不可用，本地生成也失败了: \(error.localizedDescription)"
                    showingAlert = true
                }
            }
            
        } catch {
            print("❌ 本地传记生成出错（备用方案）: \(error)")
            await MainActor.run {
                isGenerating = false
                useLocalGeneration = false
                alertMessage = "API服务不可用，本地生成也出错了: \(error.localizedDescription)"
                showingAlert = true
            }
        }
    }
    
    private func startLocalBiographyGeneration() {
        print("🏠 开始本地传记生成...")
        
        Task {
            await MainActor.run {
                isGenerating = true
                useLocalGeneration = true
            }
            
            do {
                let result = await localBiographyService.generateBiography(
                    from: state.assetsImages,
                    userRequirements: userRequirements,
                    language: selectedLanguage
                )
                
                switch result {
                case .success(let pdfURL):
                    print("✅ 本地传记生成成功: \(pdfURL)")
                    
                    // 创建一个本地任务状态
                    let localTask = BiographyTask(
                        id: "local_\(Int(Date().timeIntervalSince1970))",
                        status: .completed,
                        progress: 1.0,
                        message: "本地传记生成完成",
                        userRequirements: userRequirements,
                        images: state.assetsImages,
                        createdAt: Date(),
                        pdfUrl: pdfURL.absoluteString
                    )
                    
                    await MainActor.run {
                        state.currentBiographyTask = localTask
                        isGenerating = false
                        useLocalGeneration = false
                        
                        // 重新加载传记列表以显示新生成的传记
                        state.biographies = LocalStorageManager.shared.loadBiographies()
                        print("✅ 传记列表已刷新，新增传记数量: \(state.biographies.count)")
                        
                        alertMessage = "传记已成功生成！(本地模式)\n您可以在Assets页面查看。"
                        showingAlert = true
                    }
                    
                case .failure(let error):
                    print("❌ 本地传记生成失败: \(error)")
                    await MainActor.run {
                        isGenerating = false
                        useLocalGeneration = false
                        alertMessage = "本地生成失败: \(error.localizedDescription)"
                        showingAlert = true
                    }
                }
                
            } catch {
                print("❌ 本地传记生成出错: \(error)")
                await MainActor.run {
                    isGenerating = false
                    useLocalGeneration = false
                    alertMessage = "本地生成出错: \(error.localizedDescription)"
                    showingAlert = true
                }
            }
        }
    }
    
    private func buildEnhancedRequirements(originalRequirements: String, imageQAs: [ImageQA]) -> String {
        var enhanced = originalRequirements
        
        print("🔧 构建增强需求，总问答数: \(imageQAs.count)")
        
        if !imageQAs.isEmpty {
            enhanced += "\n\n=== 用户提供的真实生活片段（请将这些融入传记的不同章节中）===\n"
            
            // 按时间顺序整理用户的回答
            let completedQAs = imageQAs.filter { $0.isCompleted && !$0.time.isEmpty && !$0.activity.isEmpty }
            
            print("📊 有效问答数: \(completedQAs.count)")
            
            for (index, qa) in completedQAs.enumerated() {
                enhanced += "\n【生活片段\(index + 1)】\n"
                enhanced += "时期：\(qa.time)\n"
                enhanced += "经历：\(qa.activity)\n"
                print("  ✅ 片段\(index+1): \(qa.time) - \(qa.activity)")
            }
            
            enhanced += "\n=== 重要撰写指导 ===\n"
            enhanced += "1. 请将上述每个生活片段自然地融入传记的相应时期章节中\n"
            enhanced += "2. 根据时间顺序组织这些真实经历，形成连贯的人生故事\n"
            enhanced += "3. 在每个相关章节中详细描述对应时期的活动和经历\n"
            enhanced += "4. 绝对不要编造或添加用户没有提到的内容\n"
            enhanced += "5. 如果某个时期缺乏信息，可以简短处理，但不要虚构\n"
            enhanced += "6. 确保每个章节都基于用户提供的真实信息\n"
            enhanced += "7. 用温馨的语言将这些生活片段编织成完整的人生故事\n\n"
            enhanced += "请按照时间顺序，将用户的真实经历写成一篇完整的个人传记，每个章节都要包含对应时期用户提供的真实活动和经历。"
        }
        
        return enhanced
    }
    
    private func startCustomPollingTask(_ task: BiographyTask) {
        Task {
            print("🔄 开始自定义轮询任务状态，任务ID: \(task.id)")
            var failureCount = 0
            let maxFailures = 3  // 最多允许3次连续失败
            
            while true {
                do {
                    print("📡 正在查询任务状态...")
                    let status = try await agentService.checkTaskStatus(taskId: task.id)
                    
                    // 重置失败计数器
                    failureCount = 0
                    
                    print("📊 收到状态更新: \(status.status), 进度: \(status.progress), 消息: \(status.message ?? "无消息")")
                    
                    await MainActor.run {
                        // 直接更新UI绑定的状态
                        if let currentTask = state.currentBiographyTask, currentTask.id == task.id {
                            let updatedTask = BiographyTask(
                                id: currentTask.id,
                                status: BiographyTask.Status(rawValue: status.status) ?? .failed,
                                progress: status.progress,
                                message: status.message ?? "处理中...",
                                userRequirements: currentTask.userRequirements,
                                images: currentTask.images,
                                createdAt: currentTask.createdAt,
                                pdfUrl: status.pdfUrl,
                                errorMessage: status.errorMessage ?? status.error
                            )
                            
                            print("🔄 更新UI状态: \(updatedTask.status.rawValue), 进度: \(updatedTask.progress)")
                            state.currentBiographyTask = updatedTask
                            
                            // 如果任务完成，处理结果
                            if status.status == "completed" {
                                print("✅ 任务完成，开始下载并保存传记")
                                downloadAndSaveBiography(updatedTask)
                            }
                        }
                    }
                    
                    // 如果任务完成或失败，停止轮询
                    if status.status == "completed" || status.status == "failed" {
                        print("✅ 轮询完成，最终状态: \(status.status)")
                        break
                    }
                    
                    // 等待3秒后再次查询
                    try await Task.sleep(nanoseconds: 3_000_000_000)
                    
                } catch {
                    failureCount += 1
                    print("❌ 轮询任务状态失败 (\(failureCount)/\(maxFailures)): \(error)")
                    
                    if failureCount >= maxFailures {
                        print("🔄 轮询连续失败\(maxFailures)次，切换到本地生成作为备用方案")
                        await startLocalBiographyGenerationAsFallback()
                        break
                    }
                    
                    // 等待5秒后重试
                    try? await Task.sleep(nanoseconds: 5_000_000_000)
                }
            }
        }
    }
    
    private func downloadAndSaveBiography(_ task: BiographyTask) {
        Task {
            do {
                // 尝试从服务器下载PDF，如果失败则本地生成
                var pdfData: Data
                
                do {
                    pdfData = try await agentService.downloadBiography(taskId: task.id)
                    print("从服务器下载PDF成功")
                } catch {
                    print("从服务器下载PDF失败，使用本地生成: \(error)")
                    // 本地生成格式化的PDF
                    pdfData = generateFormattedPDF(content: task.message, images: state.assetsImages)
                }
                
                // 保存PDF到本地
                let biography = Biography(
                    id: task.id,
                    title: "Personal Biography - \(DateFormatter.localizedString(from: task.createdAt, dateStyle: .medium, timeStyle: .none))",
                    content: task.message,
                    pdfPath: "",
                    thumbnailPath: nil,
                    createdAt: task.createdAt,
                    updatedAt: Date()
                )
                
                let pdfURL = try LocalStorageManager.shared.saveBiographyPDF(data: pdfData, biography: biography)
                
                // 生成缩略图
                let thumbnailImage = generateBiographyThumbnail(for: biography.title)
                let thumbnailURL = try LocalStorageManager.shared.saveBiographyThumbnail(image: thumbnailImage, biography: biography)
                
                // 更新PDF路径
                let updatedBiography = Biography(
                    id: biography.id,
                    title: biography.title,
                    content: biography.content,
                    pdfPath: pdfURL.path,
                    thumbnailPath: thumbnailURL.path,
                    createdAt: biography.createdAt,
                    updatedAt: biography.updatedAt
                )
                
                try LocalStorageManager.shared.saveBiography(updatedBiography)
                
                await MainActor.run {
                    // 更新应用状态
                    state.biographies = LocalStorageManager.shared.loadBiographies()
                    
                    // 立即显示完成提示，View Results按钮会持续显示
                    alertMessage = "Biography generation completed! It has been saved to the assets page."
                    showingAlert = true
                }
                
            } catch {
                await MainActor.run {
                    alertMessage = "Failed to download biography: \(error.localizedDescription)"
                    showingAlert = true
                }
            }
        }
    }
    
    private func generateFormattedPDF(content: String, images: [UIImage]) -> Data {
        let pdfData = NSMutableData()
        let pageRect = CGRect(x: 0, y: 0, width: 612, height: 792) // 标准A4尺寸
        
        UIGraphicsBeginPDFContextToData(pdfData, pageRect, nil)
        
        // 封面页
        UIGraphicsBeginPDFPage()
        drawBiographyCoverPage(content: content, rect: pageRect, images: images)
        
        // 内容页 - 将长文本分页
        let pages = splitContentIntoPages(content: content, pageRect: pageRect)
        for (index, pageContent) in pages.enumerated() {
            UIGraphicsBeginPDFPage()
            drawBiographyContentPage(content: pageContent, rect: pageRect, pageNumber: index + 1, totalPages: pages.count)
        }
        
        UIGraphicsEndPDFContext()
        
        return pdfData as Data
    }
    
    private func drawBiographyCoverPage(content: String, rect: CGRect, images: [UIImage]) {
        let context = UIGraphicsGetCurrentContext()!
        
        // 背景渐变
        let colors = [UIColor(red: 0.9, green: 0.95, blue: 1.0, alpha: 1.0).cgColor,
                      UIColor(red: 0.7, green: 0.8, blue: 0.95, alpha: 1.0).cgColor]
        let gradient = CGGradient(colorsSpace: CGColorSpaceCreateDeviceRGB(), colors: colors as CFArray, locations: nil)!
        context.drawLinearGradient(gradient, start: CGPoint(x: 0, y: 0), end: CGPoint(x: 0, y: rect.height), options: [])
        
        // 标题 - 使用系统字体支持多语言
        let titleFont = UIFont.systemFont(ofSize: 28, weight: .bold) // 使用系统字体
        let titleAttrs: [NSAttributedString.Key: Any] = [
            .font: titleFont,
            .foregroundColor: UIColor(red: 0.2, green: 0.3, blue: 0.6, alpha: 1.0),
            .paragraphStyle: {
                let style = NSMutableParagraphStyle()
                style.alignment = .center
                return style
            }()
        ]
        
        let title = "个人传记 Personal Biography" // 支持中英文
        let titleRect = CGRect(x: 50, y: 120, width: rect.width - 100, height: 80)
        title.draw(in: titleRect, withAttributes: titleAttrs)
        
        // 图片网格 - 如果有图片的话
        if !images.isEmpty {
            let imageSize: CGFloat = 90
            let spacing: CGFloat = 15
            let startY: CGFloat = 250
            let cols = min(3, images.count)
            let rows = min(2, (images.count + cols - 1) / cols)
            
            for (index, image) in images.prefix(6).enumerated() {
                let row = index / cols
                let col = index % cols
                let x = (rect.width - CGFloat(cols) * imageSize - CGFloat(cols - 1) * spacing) / 2 + CGFloat(col) * (imageSize + spacing)
                let y = startY + CGFloat(row) * (imageSize + spacing)
                
                let imageRect = CGRect(x: x, y: y, width: imageSize, height: imageSize)
                
                // 绘制阴影
                context.setShadow(offset: CGSize(width: 2, height: 2), blur: 4, color: UIColor.black.withAlphaComponent(0.3).cgColor)
                image.draw(in: imageRect)
                context.setShadow(offset: .zero, blur: 0, color: nil)
                
                // 图片边框
                context.setStrokeColor(UIColor.white.cgColor)
                context.setLineWidth(3)
                context.stroke(imageRect)
            }
        }
        
        // 副标题 - 使用系统字体支持多语言
        let subtitleFont = UIFont.systemFont(ofSize: 16, weight: .medium) // 使用系统字体而非斜体
        let subtitleAttrs: [NSAttributedString.Key: Any] = [
            .font: subtitleFont,
            .foregroundColor: UIColor(red: 0.4, green: 0.5, blue: 0.7, alpha: 1.0),
            .paragraphStyle: {
                let style = NSMutableParagraphStyle()
                style.alignment = .center
                return style
            }()
        ]
        
        let subtitle = "我的人生旅程 A Journey Through Life"
        let subtitleRect = CGRect(x: 50, y: 500, width: rect.width - 100, height: 40)
        subtitle.draw(in: subtitleRect, withAttributes: subtitleAttrs)
        
        // 日期和装饰线
        let dateFormatter = DateFormatter()
        dateFormatter.dateStyle = .long
        let dateString = dateFormatter.string(from: Date())
        
        let dateAttrs: [NSAttributedString.Key: Any] = [
            .font: UIFont.systemFont(ofSize: 14),
            .foregroundColor: UIColor(red: 0.5, green: 0.6, blue: 0.8, alpha: 1.0),
            .paragraphStyle: {
                let style = NSMutableParagraphStyle()
                style.alignment = .center
                return style
            }()
        ]
        
        let dateRect = CGRect(x: 50, y: 650, width: rect.width - 100, height: 30)
        dateString.draw(in: dateRect, withAttributes: dateAttrs)
        
        // 装饰线
        context.setStrokeColor(UIColor(red: 0.7, green: 0.8, blue: 0.95, alpha: 1.0).cgColor)
        context.setLineWidth(1)
        context.move(to: CGPoint(x: rect.width * 0.3, y: 630))
        context.addLine(to: CGPoint(x: rect.width * 0.7, y: 630))
        context.strokePath()
    }
    
    private func splitContentIntoPages(content: String, pageRect: CGRect) -> [String] {
        // 确保内容不为空
        guard !content.isEmpty else {
            return [""]
        }
        
        // 使用系统字体以支持中文字符显示
        let contentAttrs: [NSAttributedString.Key: Any] = [
            .font: UIFont.systemFont(ofSize: 12),
            .foregroundColor: UIColor.black, // 明确设置文字颜色为黑色
            .paragraphStyle: {
                let style = NSMutableParagraphStyle()
                style.lineSpacing = 6 // 增加行间距
                style.alignment = .left // 改为左对齐，避免中文排版问题
                return style
            }()
        ]
        
        let availableRect = CGRect(x: 60, y: 80, width: pageRect.width - 120, height: pageRect.height - 160)
        
        var pages: [String] = []
        var currentPosition = 0
        
        // 使用安全的字符串索引处理
        while currentPosition < content.count {
            // 安全地获取剩余文本
            let startIndex = content.index(content.startIndex, offsetBy: currentPosition)
            let remainingText = String(content[startIndex...])
            
            // 如果剩余文本为空，退出循环
            if remainingText.isEmpty {
                break
            }
            
            let remainingAttributedString = NSAttributedString(string: remainingText, attributes: contentAttrs)
            
            let textContainer = NSTextContainer(size: availableRect.size)
            let layoutManager = NSLayoutManager()
            let textStorage = NSTextStorage(attributedString: remainingAttributedString)
            
            textStorage.addLayoutManager(layoutManager)
            layoutManager.addTextContainer(textContainer)
            
            let glyphRange = layoutManager.glyphRange(for: textContainer)
            let characterRange = layoutManager.characterRange(forGlyphRange: glyphRange, actualGlyphRange: nil)
            
            if characterRange.length == 0 {
                // 如果没有字符能够适应当前页面，添加少量文本避免无限循环
                let fallbackLength = min(100, remainingText.count)
                let fallbackText = String(remainingText.prefix(fallbackLength))
                pages.append(fallbackText)
                currentPosition += fallbackLength
                continue
            }
            
            // 安全地获取页面文本
            let pageTextLength = min(characterRange.length, remainingText.count)
            let pageText = String(remainingText.prefix(pageTextLength))
            pages.append(pageText)
            
            currentPosition += pageTextLength
            
            // 防止无限循环
            if pageTextLength == 0 {
                break
            }
        }
        
        // 确保至少有一页
        if pages.isEmpty {
            pages.append(content)
        }
        
        return pages
    }
    
    private func drawBiographyContentPage(content: String, rect: CGRect, pageNumber: Int, totalPages: Int) {
        // 页面背景
        UIColor.white.setFill()
        UIRectFill(rect)
        
        // 页眉装饰线
        let context = UIGraphicsGetCurrentContext()!
        context.setStrokeColor(UIColor(red: 0.7, green: 0.8, blue: 0.95, alpha: 1.0).cgColor)
        context.setLineWidth(1)
        context.move(to: CGPoint(x: 60, y: 50))
        context.addLine(to: CGPoint(x: rect.width - 60, y: 50))
        context.strokePath()
        
        // 页眉文字 - 使用系统字体支持多语言
        let headerAttrs: [NSAttributedString.Key: Any] = [
            .font: UIFont.systemFont(ofSize: 10),
            .foregroundColor: UIColor.gray
        ]
        
        let headerText = "个人传记 Personal Biography"
        let headerRect = CGRect(x: 60, y: 30, width: rect.width - 120, height: 15)
        headerText.draw(in: headerRect, withAttributes: headerAttrs)
        
        // 页码
        let pageText = "Page \(pageNumber) of \(totalPages)"
        let pageAttrs: [NSAttributedString.Key: Any] = [
            .font: UIFont.systemFont(ofSize: 10),
            .foregroundColor: UIColor.gray,
            .paragraphStyle: {
                let style = NSMutableParagraphStyle()
                style.alignment = .right
                return style
            }()
        ]
        pageText.draw(in: headerRect, withAttributes: pageAttrs)
        
        // 内容 - 使用系统字体以支持中文字符显示
        let contentAttrs: [NSAttributedString.Key: Any] = [
            .font: UIFont.systemFont(ofSize: 12),
            .foregroundColor: UIColor.black, // 确保文字颜色为黑色
            .backgroundColor: UIColor.clear, // 确保背景透明
            .paragraphStyle: {
                let style = NSMutableParagraphStyle()
                style.lineSpacing = 6 // 增加行间距
                style.alignment = .left // 改为左对齐，避免中文排版问题
                return style
            }()
        ]
        
        let contentRect = CGRect(x: 60, y: 80, width: rect.width - 120, height: rect.height - 160)
        
        // 安全地绘制内容，避免空内容导致的显示问题
        if !content.isEmpty {
            content.draw(in: contentRect, withAttributes: contentAttrs)
        }
        
        // 页脚装饰线
        context.setStrokeColor(UIColor(red: 0.7, green: 0.8, blue: 0.95, alpha: 1.0).cgColor)
        context.setLineWidth(1)
        context.move(to: CGPoint(x: 60, y: rect.height - 50))
        context.addLine(to: CGPoint(x: rect.width - 60, y: rect.height - 50))
        context.strokePath()
    }
    
    private func generateBiographyThumbnail(for title: String) -> UIImage {
        let size = CGSize(width: 200, height: 150)
        let renderer = UIGraphicsImageRenderer(size: size)
        
        return renderer.image { context in
            // 背景渐变
            let colors = [UIColor(red: 0.9, green: 0.95, blue: 1.0, alpha: 1.0).cgColor,
                          UIColor(red: 0.7, green: 0.8, blue: 0.95, alpha: 1.0).cgColor]
            let gradient = CGGradient(colorsSpace: CGColorSpaceCreateDeviceRGB(), colors: colors as CFArray, locations: nil)!
            context.cgContext.drawLinearGradient(gradient, start: CGPoint(x: 0, y: 0), end: CGPoint(x: 0, y: size.height), options: [])
            
            // 书本图标
            let bookIcon = UIImage(systemName: "book.closed.fill")?.withTintColor(UIColor(red: 0.2, green: 0.3, blue: 0.6, alpha: 1.0), renderingMode: .alwaysOriginal)
            bookIcon?.draw(in: CGRect(x: size.width/2 - 20, y: 30, width: 40, height: 30))
            
            // 标题
            let titleAttrs: [NSAttributedString.Key: Any] = [
                .font: UIFont.boldSystemFont(ofSize: 11),
                .foregroundColor: UIColor(red: 0.2, green: 0.3, blue: 0.6, alpha: 1.0),
                .paragraphStyle: {
                    let style = NSMutableParagraphStyle()
                    style.alignment = .center
                    return style
                }()
            ]
            
            let titleText = title.components(separatedBy: " - ").first ?? title
            let titleRect = CGRect(x: 10, y: 80, width: size.width - 20, height: 60)
            titleText.draw(in: titleRect, withAttributes: titleAttrs)
        }
    }
    
    // MARK: - Image Upload Functions
    
    @MainActor
    private func addNewImages(_ images: [UIImage]) async {
        // 检查内存使用量
        guard checkMemoryUsage() else {
            alertMessage = "Memory usage has reached the limit, unable to add more media"
            showingAlert = true
            return
        }
        
        var validImages: [UIImage] = []
        
        for image in images {
            // 检查是否超过30张限制
            if state.assetsImages.count + validImages.count >= 30 {
                alertMessage = "Maximum image limit reached (30 images)"
                showingAlert = true
                break
            }
            
            validImages.append(image)
            
            // 实时检查内存使用
            if !checkMemoryUsage(additionalImages: validImages) {
                alertMessage = "Memory limit reached, stop loading more images"
                showingAlert = true
                break
            }
        }
        
        // 使用AppState的方法添加图片并自动保存
        state.addAssetsImages(validImages)
        
        print("Successfully added \(validImages.count) images via legacy picker, total \(state.assetsImages.count) images")
    }
    
    private func checkMemoryUsage(additionalImages: [UIImage] = []) -> Bool {
        // 获取可用内存
        let freeMemory = getAvailableMemory()
        let currentUsedMemory = getUsedMemoryByImages(state.assetsImages)
        let additionalMemory = getUsedMemoryByImages(additionalImages)
        let totalUsedMemory = currentUsedMemory + additionalMemory
        
        // 如果已使用内存超过可用内存的50%，则不允许添加更多
        return totalUsedMemory < UInt64(Double(freeMemory) * 0.5)
    }
    
    private func getAvailableMemory() -> UInt64 {
        var info = mach_task_basic_info()
        var count = mach_msg_type_number_t(MemoryLayout<mach_task_basic_info>.size)/4
        
        let result: kern_return_t = withUnsafeMutablePointer(to: &info) {
            $0.withMemoryRebound(to: integer_t.self, capacity: 1) {
                task_info(mach_task_self_, task_flavor_t(MACH_TASK_BASIC_INFO), $0, &count)
            }
        }
        
        if result == KERN_SUCCESS {
            return info.resident_size
        }
        return 0
    }
    
    private func getUsedMemoryByImages(_ images: [UIImage]) -> UInt64 {
        var totalMemory: UInt64 = 0
        for image in images {
            let bytesPerPixel = 4 // RGBA
            let totalPixels = Int(image.size.width * image.size.height * image.scale * image.scale)
            totalMemory += UInt64(totalPixels * bytesPerPixel)
        }
        return totalMemory
    }
}

// MARK: - Image Viewer Component

struct ImageViewerView: View {
    let images: [UIImage]
    @Binding var currentIndex: Int
    @Environment(\.dismiss) private var dismiss
    
    var body: some View {
        ZStack {
            // 黑色背景
            Color.black
                .ignoresSafeArea()
            
            if !images.isEmpty {
                // 图片显示
                TabView(selection: $currentIndex) {
                    ForEach(0..<images.count, id: \.self) { index in
                        ZoomableImageView(image: images[index])
                            .tag(index)
                    }
                }
                .tabViewStyle(PageTabViewStyle(indexDisplayMode: .never))
                .ignoresSafeArea()
                
                // 顶部关闭按钮
                VStack {
                    HStack {
                        Button {
                            dismiss()
                        } label: {
                            Image(systemName: "xmark")
                                .font(.system(size: 20))
                                .foregroundColor(.white)
                                .padding(12)
                                .background(Color.black.opacity(0.5))
                                .clipShape(Circle())
                        }
                        Spacer()
                    }
                    .padding(.top, 50)
                    .padding(.horizontal, 20)
                    
                    Spacer()
                    
                    // 底部页码指示器
                    HStack {
                        Spacer()
                        Text("\(currentIndex + 1)/\(images.count)")
                            .font(.system(size: 16, weight: .medium))
                            .foregroundColor(.white)
                            .padding(.horizontal, 12)
                            .padding(.vertical, 6)
                            .background(Color.black.opacity(0.7))
                            .cornerRadius(15)
                    }
                    .padding(.bottom, 50)
                    .padding(.horizontal, 20)
                }
            }
        }
        .onAppear {
            // 确保索引在有效范围内
            if currentIndex >= images.count {
                currentIndex = max(0, images.count - 1)
            }
        }
    }
}

// MARK: - Zoomable Image View

struct ZoomableImageView: View {
    let image: UIImage
    @State private var scale: CGFloat = 1.0
    @State private var lastScale: CGFloat = 1.0
    @State private var offset: CGSize = .zero
    @State private var lastOffset: CGSize = .zero
    
    var body: some View {
        GeometryReader { geometry in
            Image(uiImage: image)
                .resizable()
                .aspectRatio(contentMode: .fit)
                .frame(width: geometry.size.width, height: geometry.size.height)
                .scaleEffect(scale)
                .offset(offset)
                .gesture(
                    SimultaneousGesture(
                        // 缩放手势
                        MagnificationGesture()
                            .onChanged { value in
                                scale = lastScale * value
                            }
                            .onEnded { value in
                                lastScale = scale
                                // 限制缩放范围
                                if scale < 1.0 {
                                    withAnimation(.easeInOut(duration: 0.3)) {
                                        scale = 1.0
                                        lastScale = 1.0
                                        offset = .zero
                                        lastOffset = .zero
                                    }
                                } else if scale > 3.0 {
                                    withAnimation(.easeInOut(duration: 0.3)) {
                                        scale = 3.0
                                        lastScale = 3.0
                                    }
                                }
                            },
                        
                        // 拖拽手势
                        DragGesture()
                            .onChanged { value in
                                if scale > 1.0 {
                                    offset = CGSize(
                                        width: lastOffset.width + value.translation.width,
                                        height: lastOffset.height + value.translation.height
                                    )
                                }
                            }
                            .onEnded { value in
                                lastOffset = offset
                            }
                    )
                )
                .onTapGesture(count: 2) {
                    // 双击缩放
                    withAnimation(.easeInOut(duration: 0.3)) {
                        if scale == 1.0 {
                            scale = 2.0
                            lastScale = 2.0
                        } else {
                            scale = 1.0
                            lastScale = 1.0
                            offset = .zero
                            lastOffset = .zero
                        }
                    }
                }
        }
    }
}

// MARK: - Legacy Image Picker for iOS 15 and below

struct LegacyImagePicker: UIViewControllerRepresentable {
    let onImagesSelected: ([UIImage]) -> Void
    @Environment(\.dismiss) private var dismiss
    
    func makeUIViewController(context: Context) -> UIImagePickerController {
        let picker = UIImagePickerController()
        picker.delegate = context.coordinator
        picker.sourceType = .photoLibrary
        picker.allowsEditing = false
        return picker
    }
    
    func updateUIViewController(_ uiViewController: UIImagePickerController, context: Context) {
        // 不需要更新
    }
    
    func makeCoordinator() -> Coordinator {
        Coordinator(self)
    }
    
    class Coordinator: NSObject, UIImagePickerControllerDelegate, UINavigationControllerDelegate {
        let parent: LegacyImagePicker
        
        init(_ parent: LegacyImagePicker) {
            self.parent = parent
        }
        
        func imagePickerController(_ picker: UIImagePickerController, didFinishPickingMediaWithInfo info: [UIImagePickerController.InfoKey: Any]) {
            if let image = info[.originalImage] as? UIImage {
                parent.onImagesSelected([image])
            }
            parent.dismiss()
        }
        
        func imagePickerControllerDidCancel(_ picker: UIImagePickerController) {
            parent.dismiss()
        }
    }
} 