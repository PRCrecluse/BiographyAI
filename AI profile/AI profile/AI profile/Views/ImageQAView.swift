import SwiftUI

struct ImageQAView: View {
    @EnvironmentObject var state: AppState
    @EnvironmentObject var themeManager: ThemeManager
    @Environment(\.dismiss) private var dismiss
    
    let images: [UIImage]
    let userRequirements: String
    let templateStyle: String
    let language: String
    let onComplete: ([ImageQA]) -> Void
    
    @State private var currentImageIndex = 0
    @State private var imageQAs: [ImageQA] = []
    @State private var currentTime = ""
    @State private var currentActivity = ""
    @State private var showingAlert = false
    @State private var alertMessage = ""
    
    var body: some View {
        NavigationView {
            VStack(spacing: 20) {
                // 标题和说明
                VStack(alignment: .leading, spacing: 8) {
                    Text("Image Questions".localized)
                        .font(Theme.Fonts.songtiBold(size: 24))
                        .foregroundColor(Theme.Colors.primaryText(for: themeManager.currentTheme))
                    
                    Text("Please answer questions about your photos to create a more accurate biography".localized)
                        .font(.system(size: 14))
                        .foregroundColor(Theme.Colors.secondaryText(for: themeManager.currentTheme).opacity(0.7))
                        .multilineTextAlignment(.leading)
                }
                .frame(maxWidth: .infinity, alignment: .leading)
                .padding(.horizontal, 24)
                .padding(.top, 20)
                
                // 进度指示器
                HStack {
                    Text("\("Photo".localized) \(currentImageIndex + 1) \("of".localized) \(images.count)")
                        .font(.system(size: 16, weight: .medium))
                        .foregroundColor(Theme.Colors.primaryText(for: themeManager.currentTheme))
                    
                    Spacer()
                }
                .padding(.horizontal, 24)
                
                // 当前图片
                if currentImageIndex < images.count {
                    VStack(spacing: 16) {
                        // 图片显示
                        Image(uiImage: images[currentImageIndex])
                            .resizable()
                            .aspectRatio(contentMode: .fit)
                            .frame(maxHeight: 200)
                            .cornerRadius(12)
                            .shadow(color: .black.opacity(0.1), radius: 4, x: 0, y: 2)
                            .padding(.horizontal, 24)
                        
                        VStack(spacing: 16) {
                            // 问题1：时间
                            VStack(alignment: .leading, spacing: 8) {
                                Text("What time was this photo taken?".localized)
                                    .font(.system(size: 16, weight: .medium))
                                    .foregroundColor(Theme.Colors.primaryText(for: themeManager.currentTheme))
                                
                                TextField("Enter time (e.g., 2020 summer, childhood, etc.)".localized, text: $currentTime)
                                    .textFieldStyle(RoundedBorderTextFieldStyle())
                                    .font(.system(size: 14))
                            }
                            
                            // 问题2：活动
                            VStack(alignment: .leading, spacing: 8) {
                                Text("What were you doing in this photo (during this time)?".localized)
                                    .font(.system(size: 16, weight: .medium))
                                    .foregroundColor(Theme.Colors.primaryText(for: themeManager.currentTheme))
                                
                                TextField("Enter what you were doing".localized, text: $currentActivity)
                                    .textFieldStyle(RoundedBorderTextFieldStyle())
                                    .font(.system(size: 14))
                            }
                        }
                        .padding(.horizontal, 24)
                    }
                }
                
                Spacer()
                
                // 底部按钮
                VStack(spacing: 12) {
                    HStack(spacing: 12) {
                        // 跳过按钮
                        Button("Skip This Photo".localized) {
                            skipCurrentPhoto()
                        }
                        .font(.system(size: 16))
                        .foregroundColor(Theme.Colors.secondaryText(for: themeManager.currentTheme))
                        .frame(maxWidth: .infinity)
                        .padding(.vertical, 12)
                        .background(
                            RoundedRectangle(cornerRadius: 8)
                                .stroke(Theme.Colors.secondaryText(for: themeManager.currentTheme), lineWidth: 1)
                        )
                        
                        // 下一张/完成按钮
                        Button(nextButtonTitle) {
                            if canProceed {
                                saveCurrentAnswerAndProceed()
                            }
                        }
                        .font(.system(size: 16, weight: .medium))
                        .foregroundColor(.white)
                        .frame(maxWidth: .infinity)
                        .padding(.vertical, 12)
                        .background(
                            RoundedRectangle(cornerRadius: 8)
                                .fill(canProceed ? AnyShapeStyle(Theme.Colors.buttonGradient) : AnyShapeStyle(Color.gray))
                        )
                        .disabled(!canProceed)
                    }
                }
                .padding(.horizontal, 24)
                .padding(.bottom, 40)
            }
            .background(Theme.Colors.background(for: themeManager.currentTheme))
            .navigationBarHidden(true)
        }
        .onAppear {
            setupInitialQAs()
        }
        .alert("Notice".localized, isPresented: $showingAlert) {
            Button("OK".localized) { }
        } message: {
            Text(alertMessage)
        }
    }
    
    // MARK: - 计算属性
    
    private var nextButtonTitle: String {
        if currentImageIndex == images.count - 1 {
            return "Complete Q&A".localized
        } else {
            return "Next Photo".localized
        }
    }
    
    private var canProceed: Bool {
        return !currentTime.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty &&
               !currentActivity.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty
    }
    
    // MARK: - 辅助方法
    
    private func setupInitialQAs() {
        imageQAs = images.enumerated().map { index, image in
            ImageQA(
                imageId: "image_\(index)_\(UUID().uuidString)",
                imagePath: "temp_path_\(index)",
                time: "",
                activity: "",
                isCompleted: false
            )
        }
    }
    
    private func saveCurrentAnswerAndProceed() {
        // 保存当前答案
        if currentImageIndex < imageQAs.count {
            imageQAs[currentImageIndex].time = currentTime.trimmingCharacters(in: .whitespacesAndNewlines)
            imageQAs[currentImageIndex].activity = currentActivity.trimmingCharacters(in: .whitespacesAndNewlines)
            imageQAs[currentImageIndex].isCompleted = true
        }
        
        if currentImageIndex == images.count - 1 {
            // 所有图片问答完成
            completeQA()
        } else {
            // 进入下一张图片
            moveToNextPhoto()
        }
    }
    
    private func skipCurrentPhoto() {
        if currentImageIndex == images.count - 1 {
            // 如果是最后一张，完成问答
            completeQA()
        } else {
            // 进入下一张图片
            moveToNextPhoto()
        }
    }
    
    private func moveToNextPhoto() {
        currentImageIndex += 1
        currentTime = ""
        currentActivity = ""
        
        // 如果该图片已有答案，加载它们
        if currentImageIndex < imageQAs.count {
            let qa = imageQAs[currentImageIndex]
            currentTime = qa.time
            currentActivity = qa.activity
        }
    }
    
    private func completeQA() {
        // 保存到LocalStorageManager
        LocalStorageManager.shared.saveImageQAs(imageQAs)
        
        // 传递所有问答结果给回调
        onComplete(imageQAs)
        dismiss()
    }
}

#Preview {
    ImageQAView(
        images: [UIImage(systemName: "photo") ?? UIImage()],
        userRequirements: "Test requirements",
        templateStyle: "classic",
        language: "en"
    ) { qas in
        print("Completed QAs: \(qas)")
    }
    .environmentObject(AppState())
    .environmentObject(ThemeManager.shared)
} 