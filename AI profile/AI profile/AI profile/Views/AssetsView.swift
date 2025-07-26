import SwiftUI

// MARK: - Image Picker for Cover Change
struct ImagePicker: UIViewControllerRepresentable {
    let onImageSelected: (UIImage) -> Void
    @Environment(\.presentationMode) var presentationMode
    
    func makeUIViewController(context: Context) -> UIImagePickerController {
        let picker = UIImagePickerController()
        picker.delegate = context.coordinator
        picker.sourceType = .photoLibrary
        return picker
    }
    
    func updateUIViewController(_ uiViewController: UIImagePickerController, context: Context) {}
    
    func makeCoordinator() -> Coordinator {
        Coordinator(self)
    }
    
    class Coordinator: NSObject, UIImagePickerControllerDelegate, UINavigationControllerDelegate {
        let parent: ImagePicker
        
        init(_ parent: ImagePicker) {
            self.parent = parent
        }
        
        func imagePickerController(_ picker: UIImagePickerController, didFinishPickingMediaWithInfo info: [UIImagePickerController.InfoKey : Any]) {
            if let image = info[.originalImage] as? UIImage {
                parent.onImageSelected(image)
            }
            parent.presentationMode.wrappedValue.dismiss()
        }
        
        func imagePickerControllerDidCancel(_ picker: UIImagePickerController) {
            parent.presentationMode.wrappedValue.dismiss()
        }
    }
}

struct AssetsView: View {
    @EnvironmentObject var state: AppState
    @EnvironmentObject var themeManager: ThemeManager
    
    var body: some View {
        ZStack {
            // 背景
            Theme.Colors.background(for: themeManager.currentTheme)
                .ignoresSafeArea()
            
            if state.biographies.isEmpty {
                // 空状态
                emptyStateView
            } else {
                // 有内容时的视图
                contentView
            }
        }
        .sheet(isPresented: $state.showingBiographyDetail) {
            if let biography = state.selectedBiography {
                BiographyDetailView(biography: biography)
                    .environmentObject(state)
                    .environmentObject(themeManager)
            }
        }
        .onAppear {
            // 只在传记列表为空时才加载，避免重复加载
            if state.biographies.isEmpty {
                loadBiographies()
            }
        }
    }
    
    // MARK: - 空状态视图
    private var emptyStateView: some View {
        VStack(spacing: 24) {
            Spacer()
            
            VStack(spacing: 16) {
                Image(systemName: "book.closed")
                    .font(.system(size: 60))
                    .foregroundColor(Theme.Colors.secondaryText(for: themeManager.currentTheme).opacity(0.4))
                
                VStack(spacing: 8) {
                    Text("No biographies yet")
                        .font(.system(size: 20, weight: .semibold))
                        .foregroundColor(Theme.Colors.primaryText(for: themeManager.currentTheme))
                    
                    Text("Create your first biography to get started")
                        .font(.system(size: 14))
                        .foregroundColor(Theme.Colors.secondaryText(for: themeManager.currentTheme).opacity(0.7))
                        .multilineTextAlignment(.center)
                }
            }
            
            Spacer()
        }
        .padding(.horizontal, 24)
        .padding(.top, 80)
    }
    
    // MARK: - 内容视图
    private var contentView: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 24) {
                // 我的传记列表
                biographyListView
                
                Spacer(minLength: 100) // 为底部导航留空间
            }
            .padding(.horizontal, 24)
            .padding(.top, 80) // 为顶部按钮留空间
        }
    }
    
    // MARK: - 传记列表视图
    private var biographyListView: some View {
        VStack(alignment: .leading, spacing: 16) {
            Text("My Biographies".localized)
                .font(.system(size: 20, weight: .semibold))
                .foregroundColor(Theme.Colors.primaryText(for: themeManager.currentTheme))
                .padding(.leading, 8) // 增加左侧间距
            
            LazyVGrid(columns: [
                GridItem(.flexible(), spacing: 16),
                GridItem(.flexible(), spacing: 16)
            ], spacing: 16) {
                ForEach(state.biographies) { biography in
                    AssetsBiographyCardView(biography: biography)
                        .environmentObject(state)
                        .environmentObject(themeManager)
                }
            }
        }
    }
    
    private func loadBiographies() {
        state.biographies = LocalStorageManager.shared.loadBiographies()
    }
}

// MARK: - Assets Biography Card View
struct AssetsBiographyCardView: View {
    let biography: Biography
    @EnvironmentObject var state: AppState
    @EnvironmentObject var themeManager: ThemeManager
    @State private var showingDeleteAlert = false
    @State private var showingRenameAlert = false
    @State private var showingChangeCoverAlert = false
    @State private var showingImagePicker = false
    @State private var newTitle = ""
    @State private var showingSuccessAlert = false
    @State private var successMessage = ""
    @State private var coverRefreshID = UUID() // 用于强制刷新封面
    
    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            // 缩略图
            AsyncImage(url: createCacheBreakingURL(from: biography.thumbnailPath)) { image in
                image
                    .resizable()
                    .aspectRatio(contentMode: .fill)
            } placeholder: {
                RoundedRectangle(cornerRadius: 12)
                    .fill(Theme.Colors.secondaryText(for: themeManager.currentTheme).opacity(0.1))
                    .overlay(
                        Image(systemName: "doc.text")
                            .font(.system(size: 24))
                            .foregroundColor(Theme.Colors.secondaryText(for: themeManager.currentTheme).opacity(0.5))
                    )
            }
            .frame(height: 120)
            .clipShape(RoundedRectangle(cornerRadius: 12))
            .id(coverRefreshID) // 强制刷新当coverRefreshID改变时
            
            // 标题和日期
            VStack(alignment: .leading, spacing: 4) {
                Text(biography.title)
                    .font(.system(size: 14, weight: .medium))
                    .foregroundColor(Theme.Colors.primaryText(for: themeManager.currentTheme))
                    .lineLimit(2)
                
                Text(DateFormatter.localizedString(from: biography.createdAt, dateStyle: .short, timeStyle: .none))
                    .font(.system(size: 12))
                    .foregroundColor(Theme.Colors.secondaryText(for: themeManager.currentTheme))
            }
            
            Spacer()
        }
        .frame(maxWidth: .infinity)
        .background(
            RoundedRectangle(cornerRadius: 16)
                .fill(Theme.Colors.secondaryText(for: themeManager.currentTheme).opacity(0.1))
        )
        .onTapGesture {
            state.selectedBiography = biography
            state.showingBiographyDetail = true
        }
        .contextMenu {
            Button {
                state.selectedBiography = biography
                state.showingBiographyDetail = true
            } label: {
                Label("View", systemImage: "eye")
            }
            
            Button {
                newTitle = biography.title
                showingRenameAlert = true
            } label: {
                Label("Rename".localized, systemImage: "pencil")
            }
            
            Button {
                showingChangeCoverAlert = true
            } label: {
                Label("Change Cover".localized, systemImage: "photo")
            }
            
            Button(role: .destructive) {
                showingDeleteAlert = true
            } label: {
                Label("Delete", systemImage: "trash")
            }
        }
        .alert("Delete Biography", isPresented: $showingDeleteAlert) {
            Button("Cancel", role: .cancel) { }
            Button("Delete", role: .destructive) {
                deleteBiography()
            }
        } message: {
            Text("Are you sure you want to delete this biography? This action cannot be undone.")
        }
        .alert("Rename Biography".localized, isPresented: $showingRenameAlert) {
            TextField("Enter new title".localized, text: $newTitle)
            Button("Cancel", role: .cancel) { }
            Button("Save") {
                renameBiography()
            }
        } message: {
            Text("Enter a new title for this biography")
        }
        .confirmationDialog("Cover Photo".localized, isPresented: $showingChangeCoverAlert) {
            Button("Choose from Photos".localized) {
                showingImagePicker = true
            }
            Button("Cancel", role: .cancel) { }
        }
        .sheet(isPresented: $showingImagePicker) {
            ImagePicker { selectedImage in
                changeCover(selectedImage)
            }
        }
        .alert("Success", isPresented: $showingSuccessAlert) {
            Button("OK") { }
        } message: {
            Text(successMessage)
        }
    }
    
    private func deleteBiography() {
        do {
            try LocalStorageManager.shared.deleteBiography(biography)
            state.biographies = LocalStorageManager.shared.loadBiographies()
        } catch {
            print("Failed to delete biography: \(error)")
        }
    }
    
    private func renameBiography() {
        guard !newTitle.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty else { return }
        
        do {
            try LocalStorageManager.shared.renameBiography(biography, newTitle: newTitle)
            state.biographies = LocalStorageManager.shared.loadBiographies()
            successMessage = "Title updated successfully".localized
            showingSuccessAlert = true
        } catch {
            print("Failed to rename biography: \(error)")
        }
    }
    
    private func changeCover(_ newImage: UIImage) {
        do {
            try LocalStorageManager.shared.updateBiographyCover(biography, newCoverImage: newImage)
            
            // 强制刷新封面显示
            coverRefreshID = UUID()
            
            // 重新加载传记列表
            DispatchQueue.main.asyncAfter(deadline: .now() + 0.1) {
                state.biographies = LocalStorageManager.shared.loadBiographies()
            }
            
            successMessage = "Cover updated successfully".localized
            showingSuccessAlert = true
        } catch {
            print("Failed to change cover: \(error)")
        }
    }
    
    // 创建带有缓存破坏参数的URL
    private func createCacheBreakingURL(from path: String?) -> URL? {
        guard let path = path, !path.isEmpty else { return nil }
        
        let fileURL = URL(fileURLWithPath: path)
        guard var components = URLComponents(url: fileURL, resolvingAgainstBaseURL: false) else {
            return fileURL
        }
        
        // 使用coverRefreshID来破坏缓存，确保每次更换封面时URL都不同
        components.queryItems = [URLQueryItem(name: "refresh", value: coverRefreshID.uuidString)]
        
        return components.url ?? fileURL
    }
}

#Preview {
    AssetsView()
        .environmentObject(AppState())
        .environmentObject(ThemeManager.shared)
} 