import SwiftUI
import PDFKit

struct BiographyDetailView: View {
    @EnvironmentObject var state: AppState
    let biography: Biography
    @State private var showingShareSheet = false
    @State private var showingDeleteAlert = false
    @State private var shareData: Data?
    
    var body: some View {
        NavigationView {
            VStack(spacing: 0) {
                // PDF 预览
                PDFViewRepresentable(biography: biography)
                    .ignoresSafeArea(edges: .bottom)
            }
            .navigationTitle(biography.title)
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarLeading) {
                    Button("关闭") {
                        state.showingBiographyDetail = false
                    }
                }
                
                ToolbarItem(placement: .navigationBarTrailing) {
                    Menu {
                        Button {
                            shareDocument()
                        } label: {
                            Label("分享", systemImage: "square.and.arrow.up")
                        }
                        
                        Button {
                            downloadToFiles()
                        } label: {
                            Label("保存到文件", systemImage: "folder")
                        }
                        
                        Divider()
                        
                        Button(role: .destructive) {
                            showingDeleteAlert = true
                        } label: {
                            Label("删除", systemImage: "trash")
                        }
                    } label: {
                        Image(systemName: "ellipsis.circle")
                    }
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
            .sheet(isPresented: $showingShareSheet) {
                if let shareData = shareData {
                    ShareSheet(items: [shareData])
                }
            }
        }
    }
    
    private func shareDocument() {
        do {
            let data = try LocalStorageManager.shared.getBiographyPDFData(biography: biography)
            shareData = data
            showingShareSheet = true
        } catch {
            print("Failed to get PDF data: \(error)")
        }
    }
    
    private func downloadToFiles() {
        do {
            let data = try LocalStorageManager.shared.getBiographyPDFData(biography: biography)
            let tempURL = FileManager.default.temporaryDirectory.appendingPathComponent("\(biography.title).pdf")
            try data.write(to: tempURL)
            
            let documentPicker = UIDocumentPickerViewController(forExporting: [tempURL])
            
            if let windowScene = UIApplication.shared.connectedScenes.first as? UIWindowScene,
               let window = windowScene.windows.first {
                window.rootViewController?.present(documentPicker, animated: true)
            }
        } catch {
            print("Failed to export file: \(error)")
        }
    }
    
    private func deleteBiography() {
        do {
            try LocalStorageManager.shared.deleteBiography(biography)
            state.biographies = LocalStorageManager.shared.loadBiographies()
            state.showingBiographyDetail = false
        } catch {
            print("Failed to delete biography: \(error)")
        }
    }
}

// MARK: - PDF View Representable
struct PDFViewRepresentable: UIViewRepresentable {
    let biography: Biography
    
    func makeUIView(context: Context) -> PDFView {
        let pdfView = PDFView()
        pdfView.autoScales = true
        pdfView.displayMode = .singlePageContinuous
        pdfView.displayDirection = .vertical
        
        // 加载PDF文档
        loadPDFDocument(into: pdfView)
        
        return pdfView
    }
    
    func updateUIView(_ uiView: PDFView, context: Context) {
        // 可以在这里处理更新
    }
    
    private func loadPDFDocument(into pdfView: PDFView) {
        do {
            let data = try LocalStorageManager.shared.getBiographyPDFData(biography: biography)
            print("PDF data loaded successfully, size: \(data.count) bytes")
            
            if let document = PDFDocument(data: data) {
                pdfView.document = document
                print("PDF document created successfully")
            } else {
                print("Failed to create PDFDocument from data")
                showErrorDocument(in: pdfView)
            }
        } catch {
            print("加载PDF失败: \(error)")
            print("PDF路径: \(biography.pdfPath)")
            
            // 检查文件是否存在
            let fileURL = URL(fileURLWithPath: biography.pdfPath)
            if FileManager.default.fileExists(atPath: fileURL.path) {
                print("PDF文件存在，但读取失败")
            } else {
                print("PDF文件不存在: \(fileURL.path)")
            }
            
            showErrorDocument(in: pdfView)
        }
    }
    
    private func showErrorDocument(in pdfView: PDFView) {
        // 创建一个简单的错误页面
        let errorText = "Cannot load PDF document".localized
        let renderer = UIGraphicsImageRenderer(size: CGSize(width: 400, height: 600))
        
        let image = renderer.image { context in
            UIColor.white.setFill()
            context.fill(CGRect(origin: .zero, size: CGSize(width: 400, height: 600)))
            
            let attrs: [NSAttributedString.Key: Any] = [
                .font: UIFont.systemFont(ofSize: 24),
                .foregroundColor: UIColor.black
            ]
            
            let rect = CGRect(x: 50, y: 250, width: 300, height: 100)
            errorText.draw(in: rect, withAttributes: attrs)
        }
        
        // 将图片转换为PDF数据
        let pdfData = NSMutableData()
        UIGraphicsBeginPDFContextToData(pdfData, CGRect(origin: .zero, size: image.size), nil)
        UIGraphicsBeginPDFPage()
        image.draw(at: .zero)
        UIGraphicsEndPDFContext()
        
        if let document = PDFDocument(data: pdfData as Data) {
            pdfView.document = document
        }
    }
}

// MARK: - Share Sheet
struct ShareSheet: UIViewControllerRepresentable {
    let items: [Any]
    
    func makeUIViewController(context: Context) -> UIActivityViewController {
        let controller = UIActivityViewController(activityItems: items, applicationActivities: nil)
        return controller
    }
    
    func updateUIViewController(_ uiViewController: UIActivityViewController, context: Context) {
        // 不需要更新
    }
}

// MARK: - Biography List View
struct BiographyListView: View {
    @EnvironmentObject var state: AppState
    
    var body: some View {
        VStack(alignment: .leading, spacing: 16) {
            Text("My Biographies")
                .font(.system(size: 18, weight: .semibold))
                .foregroundColor(Theme.Colors.primaryText)
            
            if state.biographies.isEmpty {
                // 空状态
                VStack(spacing: 12) {
                    Image(systemName: "book.closed")
                        .font(.system(size: 40))
                        .foregroundColor(Theme.Colors.secondaryText.opacity(0.4))
                    
                    Text("No biographies generated yet")
                        .font(.system(size: 14))
                        .foregroundColor(Theme.Colors.secondaryText.opacity(0.7))
                }
                .frame(maxWidth: .infinity)
                .frame(height: 120)
                .background(
                    RoundedRectangle(cornerRadius: 12)
                        .stroke(Theme.Colors.secondaryText.opacity(0.2), style: StrokeStyle(lineWidth: 1, dash: [5]))
                )
            } else {
                // 传记列表
                LazyVGrid(columns: Array(repeating: GridItem(.flexible()), count: 2), spacing: 12) {
                    ForEach(state.biographies) { biography in
                        BiographyCardView(biography: biography)
                            .onTapGesture {
                                state.selectedBiography = biography
                                state.showingBiographyDetail = true
                            }
                    }
                }
            }
        }
    }
}

// MARK: - Biography Card View
struct BiographyCardView: View {
    let biography: Biography
    @State private var thumbnailImage: UIImage?
    
    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            // 缩略图或默认图标
            Group {
                if let thumbnail = thumbnailImage {
                    Image(uiImage: thumbnail)
                        .resizable()
                        .aspectRatio(contentMode: .fill)
                } else {
                    Rectangle()
                        .fill(Theme.Colors.secondaryText.opacity(0.1))
                        .overlay(
                            Image(systemName: "doc.richtext")
                                .font(.system(size: 24))
                                .foregroundColor(Theme.Colors.secondaryText.opacity(0.4))
                        )
                }
            }
            .frame(height: 80)
            .clipped()
            .cornerRadius(8)
            
            // 标题
            Text(biography.title)
                .font(.system(size: 12, weight: .medium))
                .foregroundColor(Theme.Colors.primaryText)
                .lineLimit(2)
                .multilineTextAlignment(.leading)
            
            // 日期
            Text(DateFormatter.localizedString(from: biography.createdAt, dateStyle: .short, timeStyle: .none))
                .font(.system(size: 10))
                .foregroundColor(Theme.Colors.secondaryText.opacity(0.6))
        }
        .padding(8)
        .background(
            RoundedRectangle(cornerRadius: 12)
                .fill(Theme.Colors.secondaryText.opacity(0.05))
        )
        .onAppear {
            loadThumbnail()
        }
    }
    
    private func loadThumbnail() {
        thumbnailImage = LocalStorageManager.shared.getBiographyThumbnail(biography: biography)
    }
} 