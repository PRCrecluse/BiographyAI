import Foundation
import SwiftUI
import Combine
import UIKit

// MARK: - Local Profile Data
struct LocalProfileData {
    var name: String = ""
    var oneLineIntro: String = ""
    var profession: String = ""
    var education: String = ""
    var link: String = ""
    
    // 检查是否有自定义数据
    var hasCustomData: Bool {
        return !name.isEmpty || !oneLineIntro.isEmpty || !profession.isEmpty || !education.isEmpty || !link.isEmpty
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
            var components: [String] = []
            
            if !profession.isEmpty {
                components.append(profession)
            }
            if !education.isEmpty {
                components.append(education)
            }
            if !link.isEmpty {
                components.append(link)
            }
            
            return components.joined(separator: " | ")
        } else {
            // 如果没有自定义数据，显示默认预览信息
            return "1yr · Product Designer · Productivity / Dev Tools ·\nSaaS · AI Model · AI Apps · Creator & Builder"
        }
    }
}

// MARK: - User Profile Model
struct UserProfile: Codable, Identifiable {
    let id: String  // Supabase 使用 UUID 字符串
    let name: String
    let email: String
    let companyId: String?
    let createdAt: Date
    let updatedAt: Date
    
    enum CodingKeys: String, CodingKey {
        case id
        case name
        case email
        case companyId = "company_id"
        case createdAt = "created_at"
        case updatedAt = "updated_at"
    }
    
    // 添加自定义解码器处理日期格式
    init(from decoder: Decoder) throws {
        let container = try decoder.container(keyedBy: CodingKeys.self)
        
        id = try container.decode(String.self, forKey: .id)
        name = try container.decode(String.self, forKey: .name)
        email = try container.decode(String.self, forKey: .email)
        companyId = try container.decodeIfPresent(String.self, forKey: .companyId)
        
        // 灵活处理日期格式
        if let createdAtString = try? container.decode(String.self, forKey: .createdAt) {
            createdAt = ISO8601DateFormatter().date(from: createdAtString) ?? Date()
        } else if let createdAtTimestamp = try? container.decode(Double.self, forKey: .createdAt) {
            createdAt = Date(timeIntervalSince1970: createdAtTimestamp)
        } else {
            createdAt = Date()
        }
        
        if let updatedAtString = try? container.decode(String.self, forKey: .updatedAt) {
            updatedAt = ISO8601DateFormatter().date(from: updatedAtString) ?? Date()
        } else if let updatedAtTimestamp = try? container.decode(Double.self, forKey: .updatedAt) {
            updatedAt = Date(timeIntervalSince1970: updatedAtTimestamp)
        } else {
            updatedAt = Date()
        }
    }
    
    // 添加一个便利初始化器用于从 Supabase UUID 创建
    init(id: String, name: String, email: String, companyId: String? = nil, createdAt: Date = Date(), updatedAt: Date = Date()) {
        self.id = id
        self.name = name
        self.email = email
        self.companyId = companyId
        self.createdAt = createdAt
        self.updatedAt = updatedAt
    }
}

// MARK: - Business Card Model
struct BusinessCard: Codable, Identifiable {
    let id: String  // Supabase 使用 UUID 字符串
    let userId: String
    let whatIAmDoing: String
    let peopleIWantToMeet: String
    let professionEducation: String
    let personalLinks: [String: String]
    let createdAt: Date
    let updatedAt: Date
    
    enum CodingKeys: String, CodingKey {
        case id
        case userId = "user_id"
        case whatIAmDoing = "what_i_am_doing"
        case peopleIWantToMeet = "people_i_want_to_meet"
        case professionEducation = "profession_education"
        case personalLinks = "personal_links"
        case createdAt = "created_at"
        case updatedAt = "updated_at"
    }
    
    // 添加自定义解码器处理日期格式
    init(from decoder: Decoder) throws {
        let container = try decoder.container(keyedBy: CodingKeys.self)
        
        id = try container.decode(String.self, forKey: .id)
        userId = try container.decode(String.self, forKey: .userId)
        whatIAmDoing = try container.decode(String.self, forKey: .whatIAmDoing)
        peopleIWantToMeet = try container.decode(String.self, forKey: .peopleIWantToMeet)
        professionEducation = try container.decode(String.self, forKey: .professionEducation)
        personalLinks = try container.decodeIfPresent([String: String].self, forKey: .personalLinks) ?? [:]
        
        // 灵活处理日期格式
        if let createdAtString = try? container.decode(String.self, forKey: .createdAt) {
            createdAt = ISO8601DateFormatter().date(from: createdAtString) ?? Date()
        } else if let createdAtTimestamp = try? container.decode(Double.self, forKey: .createdAt) {
            createdAt = Date(timeIntervalSince1970: createdAtTimestamp)
        } else {
            createdAt = Date()
        }
        
        if let updatedAtString = try? container.decode(String.self, forKey: .updatedAt) {
            updatedAt = ISO8601DateFormatter().date(from: updatedAtString) ?? Date()
        } else if let updatedAtTimestamp = try? container.decode(Double.self, forKey: .updatedAt) {
            updatedAt = Date(timeIntervalSince1970: updatedAtTimestamp)
        } else {
            updatedAt = Date()
        }
    }
    
    // 添加便利初始化器
    init(id: String, userId: String, whatIAmDoing: String, peopleIWantToMeet: String, professionEducation: String, personalLinks: [String: String] = [:], createdAt: Date = Date(), updatedAt: Date = Date()) {
        self.id = id
        self.userId = userId
        self.whatIAmDoing = whatIAmDoing
        self.peopleIWantToMeet = peopleIWantToMeet
        self.professionEducation = professionEducation
        self.personalLinks = personalLinks
        self.createdAt = createdAt
        self.updatedAt = updatedAt
    }
}

// MARK: - Biography Models
struct BiographyTask: Identifiable {
    let id: String
    var status: Status
    var progress: Double
    var message: String
    let userRequirements: String
    let images: [UIImage]
    let createdAt: Date
    var pdfUrl: String?
    var errorMessage: String?
    var pdfData: Data?
    
    enum Status: String, CaseIterable {
        case submitted = "submitted"
        case processing = "processing"
        case completed = "completed"
        case failed = "failed"
        
        var displayName: String {
            switch self {
            case .submitted: return "Submitted".localized
            case .processing: return "Processing".localized
            case .completed: return "Completed".localized
            case .failed: return "Failed".localized
            }
        }
        
        var color: Color {
            switch self {
            case .submitted: return .blue
            case .processing: return .orange
            case .completed: return .green
            case .failed: return .red
            }
        }
    }
}

struct Biography: Identifiable, Codable {
    let id: String
    let title: String
    let content: String
    let pdfPath: String
    let thumbnailPath: String?
    let createdAt: Date
    let updatedAt: Date
    
    enum CodingKeys: String, CodingKey {
        case id, title, content
        case pdfPath = "pdf_path"
        case thumbnailPath = "thumbnail_path"
        case createdAt = "created_at"
        case updatedAt = "updated_at"
    }
    
    // 添加自定义解码器处理日期格式
    init(from decoder: Decoder) throws {
        let container = try decoder.container(keyedBy: CodingKeys.self)
        
        id = try container.decode(String.self, forKey: .id)
        title = try container.decode(String.self, forKey: .title)
        content = try container.decode(String.self, forKey: .content)
        pdfPath = try container.decode(String.self, forKey: .pdfPath)
        thumbnailPath = try container.decodeIfPresent(String.self, forKey: .thumbnailPath)
        
        // 灵活处理日期格式
        if let createdAtString = try? container.decode(String.self, forKey: .createdAt) {
            createdAt = ISO8601DateFormatter().date(from: createdAtString) ?? Date()
        } else if let createdAtTimestamp = try? container.decode(Double.self, forKey: .createdAt) {
            createdAt = Date(timeIntervalSince1970: createdAtTimestamp)
        } else {
            createdAt = Date()
        }
        
        if let updatedAtString = try? container.decode(String.self, forKey: .updatedAt) {
            updatedAt = ISO8601DateFormatter().date(from: updatedAtString) ?? Date()
        } else if let updatedAtTimestamp = try? container.decode(Double.self, forKey: .updatedAt) {
            updatedAt = Date(timeIntervalSince1970: updatedAtTimestamp)
        } else {
            updatedAt = Date()
        }
    }
    
    // 添加自定义编码器以保持日期格式一致
    func encode(to encoder: Encoder) throws {
        var container = encoder.container(keyedBy: CodingKeys.self)
        
        try container.encode(id, forKey: .id)
        try container.encode(title, forKey: .title)
        try container.encode(content, forKey: .content)
        try container.encode(pdfPath, forKey: .pdfPath)
        try container.encodeIfPresent(thumbnailPath, forKey: .thumbnailPath)
        
        // 使用ISO8601格式编码日期，与解码器保持一致
        let formatter = ISO8601DateFormatter()
        try container.encode(formatter.string(from: createdAt), forKey: .createdAt)
        try container.encode(formatter.string(from: updatedAt), forKey: .updatedAt)
    }
    
    // 添加便利初始化器
    init(id: String, title: String, content: String, pdfPath: String, thumbnailPath: String? = nil, createdAt: Date = Date(), updatedAt: Date = Date()) {
        self.id = id
        self.title = title
        self.content = content
        self.pdfPath = pdfPath
        self.thumbnailPath = thumbnailPath
        self.createdAt = createdAt
        self.updatedAt = updatedAt
    }
}

// MARK: - App State
class AppState: ObservableObject {
    @Published var isLoggedIn = false
    @Published var currentUser: UserProfile?
    @Published var currentBusinessCard: BusinessCard?
    @Published var showingSidebar = false
    @Published var showingAIGenerator = false
    
    // 本地侧边栏数据，用于首页显示
    @Published var localProfileData = LocalProfileData()
    
    // Assets 数据
    @Published var assetsImages: [UIImage] = []
    @Published var assetsComments: String = ""
    
    // Biography 数据
    @Published var biographies: [Biography] = []
    @Published var currentBiographyTask: BiographyTask?
    @Published var showingBiographyGenerator = false
    @Published var showingBiographyDetail = false
    @Published var selectedBiography: Biography?
    
    // 图片问答状态
    @Published var showingImageQA = false
    @Published var currentImageQAs: [ImageQA] = []
    @Published var biographyKnowledge: BiographyKnowledge?
    
    // UI 状态
    @Published var currentSection: HomeSection = .about
    @Published var showingCommunityDevelopmentAlert = false
    @Published var isAppStartupComplete = false // 添加启动完成状态
    
    enum HomeSection {
        case about, assets
    }
    
    private let supabaseService = SupabaseService.shared
    
    init() {
        // 只在主线程执行最基本的设置
        setupAuthStateListener()
        
        // 将耗时操作移到后台线程执行
        Task.detached(priority: .background) { [weak self] in
            // 检查登录状态 - 可以延迟
            await self?.checkLoginStatusInBackground()
            
            // 加载本地数据 - 在后台线程
            await self?.loadLocalProfileDataInBackground()
            
            // 加载传记数据 - 在后台线程  
            await self?.loadBiographiesInBackground()
            
            // 加载资产数据 - 在后台线程
            await self?.loadAssetsDataInBackground()
            
            // 标记启动完成
            await MainActor.run {
                // 添加小延迟确保UI渲染完成
                Task { @MainActor in
                    try? await Task.sleep(nanoseconds: 500_000_000) // 0.5秒
                    self?.isAppStartupComplete = true
                }
            }
        }
    }
    
    private func setupAuthStateListener() {
        // 监听 SupabaseService 的认证状态变化
        supabaseService.$isAuthenticated
            .receive(on: DispatchQueue.main)
            .assign(to: &$isLoggedIn)
    }
    
    private func checkLoginStatusInBackground() async {
        // 如果 SupabaseService 有会话，则尝试获取用户信息
        if supabaseService.isAuthenticated,
           let session = supabaseService.currentSession,
           let user = session.user {
            
            do {
                let profile = try await supabaseService.getProfile(by: user.id)
                await MainActor.run {
                    self.currentUser = profile
                    self.isLoggedIn = true
                }
            } catch {
                print("获取用户配置文件失败: \(error)")
                await MainActor.run {
                    self.isLoggedIn = false
                    self.currentUser = nil
                }
            }
        }
    }
    
    private func loadLocalProfileDataInBackground() async {
        // 在后台线程读取UserDefaults
        let name = UserDefaults.standard.string(forKey: "profile_name") ?? ""
        let oneLineIntro = UserDefaults.standard.string(forKey: "profile_one_line_intro") ?? ""
        let profession = UserDefaults.standard.string(forKey: "profile_profession") ?? ""
        let education = UserDefaults.standard.string(forKey: "profile_education") ?? ""
        let link = UserDefaults.standard.string(forKey: "profile_link") ?? ""
        
        // 在主线程更新UI
        await MainActor.run {
            self.localProfileData.name = name
            self.localProfileData.oneLineIntro = oneLineIntro
            self.localProfileData.profession = profession
            self.localProfileData.education = education
            self.localProfileData.link = link
        }
    }
    
    private func loadBiographiesInBackground() async {
        // 在后台线程加载数据
        let loadedBiographies = LocalStorageManager.shared.loadBiographies()
        
        // 在主线程更新UI
        await MainActor.run {
            self.biographies = loadedBiographies
            print("从本地存储加载了 \(loadedBiographies.count) 个传记")
        }
    }
    
    private func loadAssetsDataInBackground() async {
        // 在后台线程加载数据
        let loadedImages = LocalStorageManager.shared.loadAssetsImages()
        let loadedComments = LocalStorageManager.shared.loadAssetsComments()
        
        // 在主线程更新UI
        await MainActor.run {
            self.assetsImages = loadedImages
            self.assetsComments = loadedComments
            print("从本地存储加载了 \(loadedImages.count) 张资产图片")
            print("从本地存储加载用户评论: \(loadedComments.prefix(50))...")
        }
    }
    
    func signOut() {
        Task {
            do {
                try await supabaseService.signOut()
                await MainActor.run {
                    self.currentUser = nil
                    self.currentBusinessCard = nil
                    self.isLoggedIn = false
                }
            } catch {
                print("登出失败: \(error)")
            }
        }
    }
    
    // 删除账户
    func deleteAccount() async throws {
        guard currentUser != nil else {
            throw NSError(domain: "UserError", code: 1, userInfo: [NSLocalizedDescriptionKey: "未找到当前用户"])
        }
        
        do {
            // 1. 删除服务器端用户数据
            try await supabaseService.deleteUserAccount()
            
            // 2. 清除本地数据
            await MainActor.run {
                // 清除用户相关数据
                self.currentUser = nil
                self.currentBusinessCard = nil
                self.isLoggedIn = false
                
                // 清除本地存储的数据
                self.clearAllLocalData()
            }
            
            print("账户删除成功")
        } catch {
            print("删除账户失败: \(error)")
            throw error
        }
    }
    
    // 清除所有本地数据
    private func clearAllLocalData() {
        // 清除UserDefaults中的用户数据
        let keysToRemove = [
            "profile_name",
            "profile_one_line_intro", 
            "profile_profession",
            "profile_education",
            "profile_link"
        ]
        
        for key in keysToRemove {
            UserDefaults.standard.removeObject(forKey: key)
        }
        
        // 重置本地profile数据
        localProfileData = LocalProfileData()
        
        // 清除资产数据
        clearAllAssetsData()
        
        // 清除传记数据
        biographies.removeAll()
        do {
            try LocalStorageManager.shared.clearAllBiographies()
        } catch {
            print("清除本地传记数据失败: \(error)")
            // 继续执行，不要阻止删除流程
        }
        
        print("所有本地数据已清除")
    }
    
    // 加载本地配置文件数据
    func loadLocalProfileData() {
        if let name = UserDefaults.standard.string(forKey: "profile_name") {
            localProfileData.name = name
        }
        if let oneLineIntro = UserDefaults.standard.string(forKey: "profile_one_line_intro") {
            localProfileData.oneLineIntro = oneLineIntro
        }
        if let profession = UserDefaults.standard.string(forKey: "profile_profession") {
            localProfileData.profession = profession
        }
        if let education = UserDefaults.standard.string(forKey: "profile_education") {
            localProfileData.education = education
        }
        if let link = UserDefaults.standard.string(forKey: "profile_link") {
            localProfileData.link = link
        }
    }
    
    // 更新本地配置文件数据
    func updateLocalProfileData(name: String, oneLineIntro: String, profession: String, education: String, link: String) {
        localProfileData.name = name
        localProfileData.oneLineIntro = oneLineIntro
        localProfileData.profession = profession
        localProfileData.education = education
        localProfileData.link = link
        
        // 保存到本地存储
        UserDefaults.standard.set(name, forKey: "profile_name")
        UserDefaults.standard.set(oneLineIntro, forKey: "profile_one_line_intro")
        UserDefaults.standard.set(profession, forKey: "profile_profession")
        UserDefaults.standard.set(education, forKey: "profile_education")
        UserDefaults.standard.set(link, forKey: "profile_link")
    }
    
    // 加载传记数据
    func loadBiographies() {
        biographies = LocalStorageManager.shared.loadBiographies()
    }
    
    // MARK: - Assets Data Management
    
    // 加载用户资产数据
    func loadAssetsData() {
        // 加载图片
        assetsImages = LocalStorageManager.shared.loadAssetsImages()
        
        // 加载评论
        assetsComments = LocalStorageManager.shared.loadAssetsComments()
        
        print("已加载 \(assetsImages.count) 张图片和评论数据")
    }
    
    // 保存用户图片
    func saveAssetsImages() {
        do {
            try LocalStorageManager.shared.saveAssetsImages(assetsImages)
            print("用户图片已保存到持久化存储")
        } catch {
            print("保存用户图片失败: \(error)")
        }
    }
    
    // 保存用户评论
    func saveAssetsComments() {
        LocalStorageManager.shared.saveAssetsComments(assetsComments)
        print("用户评论已保存到持久化存储")
    }
    
    // 添加图片并保存
    func addAssetsImages(_ newImages: [UIImage]) {
        assetsImages.append(contentsOf: newImages)
        saveAssetsImages()
    }
    
    // 更新评论并保存
    func updateAssetsComments(_ newComments: String) {
        assetsComments = newComments
        saveAssetsComments()
    }
    
    // 清除所有资产数据
    func clearAllAssetsData() {
        do {
            try LocalStorageManager.shared.clearAllAssets()
            assetsImages.removeAll()
            assetsComments = ""
            print("所有用户资产数据已清除")
        } catch {
            print("清除用户资产数据失败: \(error)")
        }
    }
}

// MARK: - 图片问答相关模型
struct ImageQA: Codable, Identifiable {
    let id = UUID()
    let imageId: String
    let imagePath: String
    var time: String = ""
    var activity: String = ""
    var isCompleted: Bool = false
    
    enum CodingKeys: String, CodingKey {
        case imageId, imagePath, time, activity, isCompleted
    }
}

struct BiographyKnowledge: Codable {
    let id = UUID()
    let biographyId: String
    var imageQAs: [ImageQA] = []
    let createdAt: Date = Date()
    var updatedAt: Date = Date()
    
    enum CodingKeys: String, CodingKey {
        case biographyId, imageQAs, createdAt, updatedAt
    }
}

// MARK: - 扩展现有Biography模型
extension Biography {
    var hasKnowledge: Bool {
        return LocalStorageManager.shared.hasKnowledgeFor(biographyId: id)
    }
    
    var knowledge: BiographyKnowledge? {
        return LocalStorageManager.shared.loadKnowledge(for: id)
    }
} 