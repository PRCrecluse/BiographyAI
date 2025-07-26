import Foundation
import UIKit

class LocalStorageManager {
    static let shared = LocalStorageManager()
    
    private let userDefaults = UserDefaults.standard
    private let fileManager = FileManager.default
    private let documentsDirectory: URL
    
    // 添加缓存以避免重复文件I/O
    private var cachedBiographies: [Biography]?
    private var cachedImagePaths: [String]?
    private var lastBiographyLoadTime: Date?
    private var lastImagePathLoadTime: Date?
    private let cacheTimeout: TimeInterval = 30 // 30秒缓存超时
    
    // 用户资料存储键
    private enum Keys {
        static let userName = "user_name"
        static let userOneLineIntro = "user_one_line_intro"
        static let userProfession = "user_profession"
        static let userEducation = "user_education"
        static let userLink = "user_link"
        static let biographies = "biographies"
        // 新增：用户资产存储键
        static let assetsImages = "assets_images"
        static let assetsComments = "assets_comments"
        static let imageQAs = "image_qas" // 图片问答数据
    }
    
    private init() {
        documentsDirectory = fileManager.urls(for: .documentDirectory, in: .userDomainMask)[0]
    }
    
    // 文件路径
    private var biographiesDirectory: URL {
        let dir = documentsDirectory.appendingPathComponent("Biographies")
        if !fileManager.fileExists(atPath: dir.path) {
            try? fileManager.createDirectory(at: dir, withIntermediateDirectories: true)
        }
        return dir
    }
    
    // 新增：资产目录
    private var assetsDirectory: URL {
        let dir = documentsDirectory.appendingPathComponent("Assets")
        if !fileManager.fileExists(atPath: dir.path) {
            try? fileManager.createDirectory(at: dir, withIntermediateDirectories: true)
        }
        return dir
    }
    
    // 保存用户资料
    func saveUserProfile(name: String, oneLineIntro: String, profession: String, education: String, link: String) {
        userDefaults.set(name, forKey: Keys.userName)
        userDefaults.set(oneLineIntro, forKey: Keys.userOneLineIntro)
        userDefaults.set(profession, forKey: Keys.userProfession)
        userDefaults.set(education, forKey: Keys.userEducation)
        userDefaults.set(link, forKey: Keys.userLink)
        
        // 强制同步
        userDefaults.synchronize()
        
        print("用户资料已保存到本地存储:")
        print("姓名: \(name)")
        print("一句话介绍: \(oneLineIntro)")
        print("职业: \(profession)")
        print("教育/经验: \(education)")
        print("链接: \(link)")
    }
    
    // 获取用户资料
    func fetchUserProfile() -> (name: String, oneLineIntro: String, profession: String, education: String, link: String) {
        let name = userDefaults.string(forKey: Keys.userName) ?? ""
        let oneLineIntro = userDefaults.string(forKey: Keys.userOneLineIntro) ?? ""
        let profession = userDefaults.string(forKey: Keys.userProfession) ?? ""
        let education = userDefaults.string(forKey: Keys.userEducation) ?? ""
        let link = userDefaults.string(forKey: Keys.userLink) ?? ""
        
        print("从本地存储加载用户资料:")
        print("姓名: \(name)")
        print("一句话介绍: \(oneLineIntro)")
        print("职业: \(profession)")
        print("教育/经验: \(education)")
        print("链接: \(link)")
        
        return (name: name, oneLineIntro: oneLineIntro, profession: profession, education: education, link: link)
    }
    
    // 清除用户资料
    func clearUserProfile() {
        userDefaults.removeObject(forKey: Keys.userName)
        userDefaults.removeObject(forKey: Keys.userOneLineIntro)
        userDefaults.removeObject(forKey: Keys.userProfession)
        userDefaults.removeObject(forKey: Keys.userEducation)
        userDefaults.removeObject(forKey: Keys.userLink)
        
        userDefaults.synchronize()
        
        print("用户资料已从本地存储清除")
    }
    
    // MARK: - Biography Management
    
    // 保存传记PDF
    func saveBiographyPDF(data: Data, biography: Biography) throws -> URL {
        let fileName = "\(biography.id).pdf"
        let fileURL = biographiesDirectory.appendingPathComponent(fileName)
        
        try data.write(to: fileURL)
        print("传记PDF已保存到: \(fileURL.path)")
        
        return fileURL
    }
    
    // 保存传记缩略图
    func saveBiographyThumbnail(image: UIImage, biography: Biography) throws -> URL {
        let fileName = "\(biography.id)_thumbnail.png"
        let fileURL = biographiesDirectory.appendingPathComponent(fileName)
        
        guard let imageData = image.pngData() else {
            throw LocalStorageError.imageProcessingFailed
        }
        
        try imageData.write(to: fileURL)
        print("传记缩略图已保存到: \(fileURL.path)")
        
        return fileURL
    }
    
    // 保存传记到本地存储 (修复：保存为JSON文件)
    func saveBiography(_ biography: Biography) throws {
        // 保存Biography对象为JSON文件
        let fileName = "\(biography.id).json"
        let fileURL = biographiesDirectory.appendingPathComponent(fileName)
        
        let encoder = JSONEncoder()
        encoder.dateEncodingStrategy = .iso8601
        let data = try encoder.encode(biography)
        try data.write(to: fileURL)
        
        // 清除缓存，强制重新加载
        cachedBiographies = nil
        lastBiographyLoadTime = nil
        
        print("传记已保存到本地存储: \(biography.title)")
        print("JSON文件位置: \(fileURL.path)")
    }
    
    // 加载所有传记
    func loadBiographies() -> [Biography] {
        // 检查缓存是否有效
        if let cached = cachedBiographies,
           let lastLoad = lastBiographyLoadTime,
           Date().timeIntervalSince(lastLoad) < cacheTimeout {
            return cached
        }
        
        let biographyDir = documentsDirectory.appendingPathComponent("Biographies")
        
        guard fileManager.fileExists(atPath: biographyDir.path) else {
            let emptyResult: [Biography] = []
            cachedBiographies = emptyResult
            lastBiographyLoadTime = Date()
            return emptyResult
        }
        
        var biographies: [Biography] = []
        
        do {
            let fileURLs = try fileManager.contentsOfDirectory(at: biographyDir, includingPropertiesForKeys: nil)
            let jsonFiles = fileURLs.filter { $0.pathExtension == "json" }
            
            for fileURL in jsonFiles {
                do {
                    let data = try Data(contentsOf: fileURL)
                    let decoder = JSONDecoder()
                    decoder.dateDecodingStrategy = .iso8601
                    let biography = try decoder.decode(Biography.self, from: data)
                    biographies.append(biography)
                } catch {
                    print("Failed to load biography from \(fileURL): \(error)")
                }
            }
        } catch {
            print("Failed to read biographies directory: \(error)")
        }
        
        // 按创建时间排序
        biographies.sort { $0.createdAt > $1.createdAt }
        
        // 更新缓存
        cachedBiographies = biographies
        lastBiographyLoadTime = Date()
        
        return biographies
    }
    
    // 删除传记 (修复：删除JSON文件)
    func deleteBiography(_ biography: Biography) throws {
        // 删除PDF文件
        let pdfURL = URL(fileURLWithPath: biography.pdfPath)
        if fileManager.fileExists(atPath: pdfURL.path) {
            try fileManager.removeItem(at: pdfURL)
        }
        
        // 删除缩略图文件
        if let thumbnailPath = biography.thumbnailPath {
            let thumbnailURL = URL(fileURLWithPath: thumbnailPath)
            if fileManager.fileExists(atPath: thumbnailURL.path) {
                try fileManager.removeItem(at: thumbnailURL)
            }
        }
        
        // 删除JSON文件
        let jsonFileName = "\(biography.id).json"
        let jsonURL = biographiesDirectory.appendingPathComponent(jsonFileName)
        if fileManager.fileExists(atPath: jsonURL.path) {
            try fileManager.removeItem(at: jsonURL)
        }
        
        // 清除缓存，强制重新加载
        cachedBiographies = nil
        lastBiographyLoadTime = nil
        
        print("传记已删除: \(biography.title)")
    }
    
    // 获取传记PDF数据
    func getBiographyPDFData(biography: Biography) throws -> Data {
        let pdfURL = URL(fileURLWithPath: biography.pdfPath)
        return try Data(contentsOf: pdfURL)
    }
    
    // 获取传记缩略图
    func getBiographyThumbnail(biography: Biography) -> UIImage? {
        guard let thumbnailPath = biography.thumbnailPath else { return nil }
        let thumbnailURL = URL(fileURLWithPath: thumbnailPath)
        
        guard let imageData = try? Data(contentsOf: thumbnailURL) else { return nil }
        return UIImage(data: imageData)
    }
    
    // 清除所有传记
    func clearAllBiographies() throws {
        let biographies = loadBiographies()
        
        // 删除所有文件
        for biography in biographies {
            try deleteBiography(biography)
        }
        
        // 清除存储
        userDefaults.removeObject(forKey: Keys.biographies)
        userDefaults.synchronize()
        
        print("所有传记已清除")
    }
    
    // 重命名传记
    func renameBiography(_ biography: Biography, newTitle: String) throws {
        var biographies = loadBiographies()
        
        guard let index = biographies.firstIndex(where: { $0.id == biography.id }) else {
            throw LocalStorageError.biographyNotFound
        }
        
        // 创建更新后的传记
        let updatedBiography = Biography(
            id: biography.id,
            title: newTitle,
            content: biography.content,
            pdfPath: biography.pdfPath,
            thumbnailPath: biography.thumbnailPath,
            createdAt: biography.createdAt,
            updatedAt: Date()
        )
        
        biographies[index] = updatedBiography
        
        let data = try JSONEncoder().encode(biographies)
        userDefaults.set(data, forKey: Keys.biographies)
        userDefaults.synchronize()
        
        print("传记已重命名: \(biography.title) -> \(newTitle)")
    }
    
    // 更换传记封面
    func updateBiographyCover(_ biography: Biography, newCoverImage: UIImage) throws {
        guard let thumbnailPath = biography.thumbnailPath else {
            throw LocalStorageError.thumbnailNotFound
        }
        
        let thumbnailURL = URL(fileURLWithPath: thumbnailPath)
        
        guard let imageData = newCoverImage.pngData() else {
            throw LocalStorageError.imageProcessingFailed
        }
        
        // 更新封面图片文件
        try imageData.write(to: thumbnailURL)
        
        // 更新传记的更新时间
        var biographies = loadBiographies()
        
        guard let index = biographies.firstIndex(where: { $0.id == biography.id }) else {
            throw LocalStorageError.biographyNotFound
        }
        
        let updatedBiography = Biography(
            id: biography.id,
            title: biography.title,
            content: biography.content,
            pdfPath: biography.pdfPath,
            thumbnailPath: biography.thumbnailPath,
            createdAt: biography.createdAt,
            updatedAt: Date()
        )
        
        biographies[index] = updatedBiography
        
        let data = try JSONEncoder().encode(biographies)
        userDefaults.set(data, forKey: Keys.biographies)
        userDefaults.synchronize()
        
        print("传记封面已更新: \(biography.title)")
    }
    
    // MARK: - Assets Management (Images & Comments)
    
    // 保存用户图片到本地
    func saveAssetsImages(_ images: [UIImage]) throws {
        // 清除旧的图片文件
        let existingImagePaths = loadAssetsImagePaths()
        for imagePath in existingImagePaths {
            let imageURL = URL(fileURLWithPath: imagePath)
            if fileManager.fileExists(atPath: imageURL.path) {
                try? fileManager.removeItem(at: imageURL)
            }
        }
        
        var imagePaths: [String] = []
        
        for (index, image) in images.enumerated() {
            let fileName = "asset_image_\(index)_\(UUID().uuidString).png"
            let fileURL = assetsDirectory.appendingPathComponent(fileName)
            
            guard let imageData = image.pngData() else {
                throw LocalStorageError.imageProcessingFailed
            }
            
            try imageData.write(to: fileURL)
            imagePaths.append(fileURL.path)
            print("资产图片已保存: \(fileURL.path)")
        }
        
        // 保存图片路径到UserDefaults
        let data = try JSONEncoder().encode(imagePaths)
        userDefaults.set(data, forKey: Keys.assetsImages)
        userDefaults.synchronize()
        
        print("已保存 \(images.count) 张资产图片")
    }
    
    // 加载用户图片路径
    private func loadAssetsImagePaths() -> [String] {
        // 检查缓存是否有效
        if let cachedPaths = cachedImagePaths,
           let lastLoad = lastImagePathLoadTime,
           Date().timeIntervalSince(lastLoad) < cacheTimeout {
            return cachedPaths
        }
        
        guard let data = userDefaults.data(forKey: Keys.assetsImages) else {
            let emptyResult: [String] = []
            cachedImagePaths = emptyResult
            lastImagePathLoadTime = Date()
            return emptyResult
        }
        
        do {
            let imagePaths = try JSONDecoder().decode([String].self, from: data)
            // 更新缓存
            cachedImagePaths = imagePaths
            lastImagePathLoadTime = Date()
            return imagePaths
        } catch {
            print("加载图片路径失败: \(error)")
            let emptyResult: [String] = []
            cachedImagePaths = emptyResult
            lastImagePathLoadTime = Date()
            return emptyResult
        }
    }
    
    // 加载用户图片
    func loadAssetsImages() -> [UIImage] {
        let imagePaths = loadAssetsImagePaths()
        var images: [UIImage] = []
        
        for imagePath in imagePaths {
            let imageURL = URL(fileURLWithPath: imagePath)
            if let imageData = try? Data(contentsOf: imageURL),
               let image = UIImage(data: imageData) {
                images.append(image)
            }
        }
        
        print("从本地存储加载了 \(images.count) 张资产图片")
        return images
    }
    
    // 保存用户评论
    func saveAssetsComments(_ comments: String) {
        userDefaults.set(comments, forKey: Keys.assetsComments)
        userDefaults.synchronize()
        print("用户评论已保存到本地存储")
    }
    
    // 加载用户评论
    func loadAssetsComments() -> String {
        let comments = userDefaults.string(forKey: Keys.assetsComments) ?? ""
        print("从本地存储加载用户评论: \(comments.prefix(50))...")
        return comments
    }
    
    // 清除所有用户资产
    func clearAllAssets() throws {
        // 清除图片文件
        let imagePaths = loadAssetsImagePaths()
        for imagePath in imagePaths {
            let imageURL = URL(fileURLWithPath: imagePath)
            if fileManager.fileExists(atPath: imageURL.path) {
                try fileManager.removeItem(at: imageURL)
            }
        }
        
        // 清除存储数据
        userDefaults.removeObject(forKey: Keys.assetsImages)
        userDefaults.removeObject(forKey: Keys.assetsComments)
        userDefaults.synchronize()
        
        print("所有用户资产已清除")
    }
    
    // MARK: - Image Q&A Management (Current Session)
    
    // 保存当前会话的图片问答数据
    func saveImageQAs(_ imageQAs: [ImageQA]) {
        do {
            let data = try JSONEncoder().encode(imageQAs)
            userDefaults.set(data, forKey: Keys.imageQAs)
            userDefaults.synchronize()
            print("图片问答数据已保存: \(imageQAs.count) 条")
        } catch {
            print("保存图片问答数据失败: \(error)")
        }
    }
    
    // 加载当前会话的图片问答数据
    func loadImageQAs() -> [ImageQA] {
        guard let data = userDefaults.data(forKey: Keys.imageQAs) else {
            print("没有找到图片问答数据")
            return []
        }
        
        do {
            let imageQAs = try JSONDecoder().decode([ImageQA].self, from: data)
            print("从本地存储加载了 \(imageQAs.count) 条图片问答数据")
            return imageQAs
        } catch {
            print("加载图片问答数据失败: \(error)")
            return []
        }
    }
    
    // 清除当前会话的图片问答数据
    func clearImageQAs() {
        userDefaults.removeObject(forKey: Keys.imageQAs)
        userDefaults.synchronize()
        print("图片问答数据已清除")
    }
    
    // 更新单个图片问答
    func updateImageQA(_ updatedQA: ImageQA) {
        var imageQAs = loadImageQAs()
        
        if let index = imageQAs.firstIndex(where: { $0.imageId == updatedQA.imageId }) {
            imageQAs[index] = updatedQA
        } else {
            imageQAs.append(updatedQA)
        }
        
        saveImageQAs(imageQAs)
    }
    
    // MARK: - 缓存管理
    
    /// 清理过期缓存
    func clearExpiredCache() {
        let now = Date()
        
        if let lastBiographyLoad = lastBiographyLoadTime,
           now.timeIntervalSince(lastBiographyLoad) > cacheTimeout {
            cachedBiographies = nil
            lastBiographyLoadTime = nil
        }
        
        if let lastImagePathLoad = lastImagePathLoadTime,
           now.timeIntervalSince(lastImagePathLoad) > cacheTimeout {
            cachedImagePaths = nil
            lastImagePathLoadTime = nil
        }
    }
    
    /// 清理所有缓存
    func clearAllCache() {
        cachedBiographies = nil
        cachedImagePaths = nil
        lastBiographyLoadTime = nil
        lastImagePathLoadTime = nil
    }
}

// MARK: - Local Storage Errors
enum LocalStorageError: LocalizedError {
    case imageProcessingFailed
    case fileNotFound
    case saveError
    case biographyNotFound
    case thumbnailNotFound
    
    var errorDescription: String? {
        switch self {
        case .imageProcessingFailed:
            return "图片处理失败"
        case .fileNotFound:
            return "文件未找到"
        case .saveError:
            return "保存失败"
        case .biographyNotFound:
            return "传记未找到"
        case .thumbnailNotFound:
            return "封面未找到"
        }
    }
}

// MARK: - 知识库管理扩展
extension LocalStorageManager {
    
    // MARK: - 知识库存储路径
    private var knowledgeDirectory: URL {
        let dir = documentsDirectory.appendingPathComponent("Knowledge")
        if !FileManager.default.fileExists(atPath: dir.path) {
            try? FileManager.default.createDirectory(at: dir, withIntermediateDirectories: true)
        }
        return dir
    }
    
    private func knowledgeFilePath(for biographyId: String) -> URL {
        return knowledgeDirectory.appendingPathComponent("\(biographyId)_knowledge.json")
    }
    
    // MARK: - 知识库操作方法
    
    /// 保存传记知识库
    func saveKnowledge(_ knowledge: BiographyKnowledge) throws {
        let encoder = JSONEncoder()
        encoder.dateEncodingStrategy = .iso8601
        
        let data = try encoder.encode(knowledge)
        let filePath = knowledgeFilePath(for: knowledge.biographyId)
        
        try data.write(to: filePath)
        print("✅ 知识库已保存: \(knowledge.biographyId)")
    }
    
    /// 加载传记知识库
    func loadKnowledge(for biographyId: String) -> BiographyKnowledge? {
        let filePath = knowledgeFilePath(for: biographyId)
        
        guard FileManager.default.fileExists(atPath: filePath.path) else {
            return nil
        }
        
        do {
            let data = try Data(contentsOf: filePath)
            let decoder = JSONDecoder()
            decoder.dateDecodingStrategy = .iso8601
            
            let knowledge = try decoder.decode(BiographyKnowledge.self, from: data)
            return knowledge
        } catch {
            print("⚠️ 加载知识库失败: \(error)")
            return nil
        }
    }
    
    /// 检查是否存在知识库
    func hasKnowledgeFor(biographyId: String) -> Bool {
        let filePath = knowledgeFilePath(for: biographyId)
        return FileManager.default.fileExists(atPath: filePath.path)
    }
    
    /// 删除知识库
    func deleteKnowledge(for biographyId: String) throws {
        let filePath = knowledgeFilePath(for: biographyId)
        
        if FileManager.default.fileExists(atPath: filePath.path) {
            try FileManager.default.removeItem(at: filePath)
            print("✅ 知识库已删除: \(biographyId)")
        }
    }
    
    /// 更新知识库中的图片问答
    func updateImageQA(_ imageQA: ImageQA, for biographyId: String) throws {
        var knowledge = loadKnowledge(for: biographyId) ?? BiographyKnowledge(biographyId: biographyId)
        
        // 更新或添加图片问答
        if let index = knowledge.imageQAs.firstIndex(where: { $0.imageId == imageQA.imageId }) {
            knowledge.imageQAs[index] = imageQA
        } else {
            knowledge.imageQAs.append(imageQA)
        }
        
        knowledge.updatedAt = Date()
        try saveKnowledge(knowledge)
    }
    
    /// 获取所有已完成问答的知识库
    func getAllKnowledgeWithCompletedQA() -> [BiographyKnowledge] {
        let knowledgeFiles = try? FileManager.default.contentsOfDirectory(at: knowledgeDirectory, includingPropertiesForKeys: nil)
        
        var knowledgeList: [BiographyKnowledge] = []
        
        knowledgeFiles?.forEach { file in
            if file.pathExtension == "json",
               let biographyId = file.lastPathComponent.components(separatedBy: "_knowledge.json").first,
               let knowledge = loadKnowledge(for: biographyId),
               knowledge.imageQAs.contains(where: { $0.isCompleted }) {
                knowledgeList.append(knowledge)
            }
        }
        
        return knowledgeList
    }
} 