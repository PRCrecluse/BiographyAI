import Foundation
import SwiftUI

// MARK: - Supabase Response Models
struct SupabaseAuthResponse: Codable {
    let access_token: String?
    let token_type: String?
    let expires_in: Int?
    let refresh_token: String?
    let user: SupabaseUser?
}

// Separate model for signup response (user data is at root level)
struct SupabaseSignUpResponse: Codable {
    let id: String
    let aud: String
    let role: String
    let email: String
    let phone: String
    let confirmation_sent_at: String?
    let created_at: String
    let updated_at: String
    let is_anonymous: Bool
    
    enum CodingKeys: String, CodingKey {
        case id, aud, role, email, phone, created_at, updated_at, is_anonymous
        case confirmation_sent_at
    }
}

struct SupabaseUser: Codable {
    let id: String
    let email: String
    let email_confirmed_at: String?
    let created_at: String
}

struct SupabaseError: Codable {
    let message: String
    let error_description: String?
}

class SupabaseService: ObservableObject {
    static let shared = SupabaseService()
    
    // Supabase配置
    private let supabaseURL = "https://your-project-id.supabase.co"
    private let supabaseAnonKey = "your-supabase-anon-key-here"
    
    // 当前会话
    @Published var currentSession: SupabaseAuthResponse?
    @Published var isAuthenticated = false
    
    private init() {
        // 检查存储的会话
        loadStoredSession()
    }
    
    // MARK: - Session Management
    private func loadStoredSession() {
        if let sessionData = UserDefaults.standard.data(forKey: "supabase_session"),
           let session = try? JSONDecoder().decode(SupabaseAuthResponse.self, from: sessionData) {
            self.currentSession = session
            self.isAuthenticated = true
        }
    }
    
    private func saveSession(_ session: SupabaseAuthResponse) {
        if let sessionData = try? JSONEncoder().encode(session) {
            UserDefaults.standard.set(sessionData, forKey: "supabase_session")
        }
        self.currentSession = session
        self.isAuthenticated = true
    }
    
    private func clearSession() {
        UserDefaults.standard.removeObject(forKey: "supabase_session")
        self.currentSession = nil
        self.isAuthenticated = false
    }
    
    // MARK: - Auth Methods
    func signUp(email: String, password: String) async throws -> UserProfile {
        print("🔵 Starting signUp for email: \(email)")
        
        guard !email.isEmpty, !password.isEmpty else {
            print("❌ SignUp failed: Empty email or password")
            throw AuthError.invalidInput("邮箱和密码不能为空")
        }
        
        guard password.count >= 6 else {
            print("❌ SignUp failed: Password too short")
            throw AuthError.invalidInput("密码至少需要6个字符")
        }
        
        guard isValidEmail(email) else {
            print("❌ SignUp failed: Invalid email format")
            throw AuthError.invalidInput("请输入有效的邮箱地址")
        }
        
        let url = URL(string: "\(supabaseURL)/auth/v1/signup")!
        print("🔵 SignUp URL: \(url)")
        
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.addValue("application/json", forHTTPHeaderField: "Content-Type")
        request.addValue(supabaseAnonKey, forHTTPHeaderField: "apikey")
        request.addValue("Bearer \(supabaseAnonKey)", forHTTPHeaderField: "Authorization")
        
        let body = [
            "email": email,
            "password": password
        ]
        
        request.httpBody = try JSONSerialization.data(withJSONObject: body)
        print("🔵 Making signUp request...")
        
        do {
            let (data, response) = try await URLSession.shared.data(for: request)
            
            // 检查HTTP响应状态
            if let httpResponse = response as? HTTPURLResponse {
                print("🔵 SignUp response status: \(httpResponse.statusCode)")
                
                if httpResponse.statusCode >= 400 {
                    // 打印原始响应数据以便调试
                    if let responseString = String(data: data, encoding: .utf8) {
                        print("❌ SignUp error response: \(responseString)")
                    }
                    
                    // 尝试解析错误信息
                    if let errorData = try? JSONDecoder().decode(SupabaseError.self, from: data) {
                        print("❌ SignUp error: \(errorData.message)")
                        throw AuthError.serverError(errorData.message)
                    } else {
                        print("❌ SignUp failed with unknown error")
                        throw AuthError.serverError("注册失败，请稍后重试")
                    }
                }
            }
            
            // 打印成功响应以便调试
            if let responseString = String(data: data, encoding: .utf8) {
                print("✅ SignUp success response: \(responseString)")
            }
            
            let signUpResponse = try JSONDecoder().decode(SupabaseSignUpResponse.self, from: data)
            print("✅ SignUp decoded successfully")
            
            // For signup, we don't save session or create profile immediately
            // User needs to confirm email and then sign in
            print("✅ SignUp completed successfully - user needs to confirm email and sign in")
            
            // Return a temporary UserProfile for UI compatibility
            // The actual profile will be created during first sign-in
            return UserProfile(
                id: signUpResponse.id,
                name: "Pending Confirmation",
                email: signUpResponse.email
            )
        } catch {
            print("❌ SignUp network error: \(error.localizedDescription)")
            if let urlError = error as? URLError {
                print("❌ URLError code: \(urlError.code.rawValue)")
            }
            throw error
        }
    }
    
    func signIn(email: String, password: String) async throws -> UserProfile {
        guard !email.isEmpty, !password.isEmpty else {
            throw AuthError.invalidInput("邮箱和密码不能为空")
        }
        
        let url = URL(string: "\(supabaseURL)/auth/v1/token?grant_type=password")!
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.addValue("application/json", forHTTPHeaderField: "Content-Type")
        request.addValue(supabaseAnonKey, forHTTPHeaderField: "apikey")
        request.addValue("Bearer \(supabaseAnonKey)", forHTTPHeaderField: "Authorization")
        
        let body = [
            "email": email,
            "password": password
        ]
        
        request.httpBody = try JSONSerialization.data(withJSONObject: body)
        
        let (data, response) = try await URLSession.shared.data(for: request)
        
        // 检查HTTP响应状态
        if let httpResponse = response as? HTTPURLResponse {
            if httpResponse.statusCode >= 400 {
                // 尝试解析错误信息
                if let errorData = try? JSONDecoder().decode(SupabaseError.self, from: data) {
                    if errorData.message.contains("Invalid login credentials") {
                        throw AuthError.invalidCredentials("邮箱或密码错误")
                    } else {
                        throw AuthError.serverError(errorData.message)
                    }
                } else {
                    throw AuthError.serverError("登录失败，请稍后重试")
                }
            }
        }
        
        let authResponse = try JSONDecoder().decode(SupabaseAuthResponse.self, from: data)
        
        // 保存会话
        saveSession(authResponse)
        
        // 获取用户配置文件
        if let user = authResponse.user {
            if let profile = try await getProfile(by: user.id) {
                return profile
            } else {
                // 如果没有配置文件，创建一个新的
                return try await createProfile(
                    id: user.id,
                    name: "用户",
                    email: user.email
                )
            }
        } else {
            throw AuthError.serverError("登录成功但无法获取用户信息")
        }
    }
    
    func signOut() async throws {
        guard let session = currentSession, let accessToken = session.access_token else {
            clearSession()
            return
        }
        
        let url = URL(string: "\(supabaseURL)/auth/v1/logout")!
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.addValue("application/json", forHTTPHeaderField: "Content-Type")
        request.addValue(supabaseAnonKey, forHTTPHeaderField: "apikey")
        request.addValue("Bearer \(accessToken)", forHTTPHeaderField: "Authorization")
        
        let (_, _) = try await URLSession.shared.data(for: request)
        
        // 清除本地会话
        clearSession()
    }
    
    // MARK: - Profile Methods
    func createProfile(id: String, name: String, email: String) async throws -> UserProfile {
        guard let session = currentSession, let accessToken = session.access_token else {
            throw AuthError.notAuthenticated("用户未登录")
        }
        
        let url = URL(string: "\(supabaseURL)/rest/v1/profiles")!
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.addValue("application/json", forHTTPHeaderField: "Content-Type")
        request.addValue(supabaseAnonKey, forHTTPHeaderField: "apikey")
        request.addValue("Bearer \(accessToken)", forHTTPHeaderField: "Authorization")
        request.addValue("return=representation", forHTTPHeaderField: "Prefer")
        
        let body = [
            "id": id,
            "name": name,
            "email": email
        ]
        
        request.httpBody = try JSONSerialization.data(withJSONObject: body)
        
        let (data, response) = try await URLSession.shared.data(for: request)
        
        if let httpResponse = response as? HTTPURLResponse, httpResponse.statusCode >= 400 {
            throw AuthError.serverError("创建用户配置文件失败")
        }
        
        let profiles = try JSONDecoder().decode([UserProfile].self, from: data)
        guard let profile = profiles.first else {
            throw AuthError.serverError("创建用户配置文件失败")
        }
        
        return profile
    }
    
    func updateProfile(_ profile: UserProfile) async throws {
        guard let session = currentSession, let accessToken = session.access_token else {
            throw AuthError.notAuthenticated("用户未登录")
        }
        
        let url = URL(string: "\(supabaseURL)/rest/v1/profiles?id=eq.\(profile.id)")!
        var request = URLRequest(url: url)
        request.httpMethod = "PATCH"
        request.addValue("application/json", forHTTPHeaderField: "Content-Type")
        request.addValue(supabaseAnonKey, forHTTPHeaderField: "apikey")
        request.addValue("Bearer \(accessToken)", forHTTPHeaderField: "Authorization")
        
        let body = [
            "name": profile.name,
            "email": profile.email,
            "updated_at": ISO8601DateFormatter().string(from: Date())
        ]
        
        request.httpBody = try JSONSerialization.data(withJSONObject: body)
        
        let (_, response) = try await URLSession.shared.data(for: request)
        
        if let httpResponse = response as? HTTPURLResponse, httpResponse.statusCode >= 400 {
            throw AuthError.serverError("更新用户配置文件失败")
        }
    }
    
    func getProfile(by id: String) async throws -> UserProfile? {
        guard let session = currentSession, let accessToken = session.access_token else {
            throw AuthError.notAuthenticated("用户未登录")
        }
        
        let url = URL(string: "\(supabaseURL)/rest/v1/profiles?id=eq.\(id)&select=*")!
        var request = URLRequest(url: url)
        request.httpMethod = "GET"
        request.addValue("application/json", forHTTPHeaderField: "Content-Type")
        request.addValue(supabaseAnonKey, forHTTPHeaderField: "apikey")
        request.addValue("Bearer \(accessToken)", forHTTPHeaderField: "Authorization")
        
        let (data, response) = try await URLSession.shared.data(for: request)
        
        if let httpResponse = response as? HTTPURLResponse, httpResponse.statusCode >= 400 {
            return nil
        }
        
        let profiles = try JSONDecoder().decode([UserProfile].self, from: data)
        return profiles.first
    }
    
    // MARK: - Business Card Methods
    func createBusinessCard(
        userId: String,
        whatIAmDoing: String,
        peopleIWantToMeet: String,
        professionEducation: String,
        personalLinks: [String: String] = [:]
    ) async throws -> BusinessCard {
        guard let session = currentSession, let accessToken = session.access_token else {
            throw AuthError.notAuthenticated("用户未登录")
        }
        
        let url = URL(string: "\(supabaseURL)/rest/v1/business_cards")!
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.addValue("application/json", forHTTPHeaderField: "Content-Type")
        request.addValue(supabaseAnonKey, forHTTPHeaderField: "apikey")
        request.addValue("Bearer \(accessToken)", forHTTPHeaderField: "Authorization")
        request.addValue("return=representation", forHTTPHeaderField: "Prefer")
        
        let body: [String: Any] = [
            "user_id": userId,
            "what_i_am_doing": whatIAmDoing,
            "people_i_want_to_meet": peopleIWantToMeet,
            "profession_education": professionEducation,
            "personal_links": personalLinks
        ]
        
        request.httpBody = try JSONSerialization.data(withJSONObject: body)
        
        let (data, response) = try await URLSession.shared.data(for: request)
        
        if let httpResponse = response as? HTTPURLResponse, httpResponse.statusCode >= 400 {
            throw AuthError.serverError("创建名片失败")
        }
        
        let cards = try JSONDecoder().decode([BusinessCard].self, from: data)
        guard let card = cards.first else {
            throw AuthError.serverError("创建名片失败")
        }
        
        return card
    }
    
    func updateBusinessCard(_ card: BusinessCard) async throws {
        guard let session = currentSession, let accessToken = session.access_token else {
            throw AuthError.notAuthenticated("用户未登录")
        }
        
        let url = URL(string: "\(supabaseURL)/rest/v1/business_cards?id=eq.\(card.id)")!
        var request = URLRequest(url: url)
        request.httpMethod = "PATCH"
        request.addValue("application/json", forHTTPHeaderField: "Content-Type")
        request.addValue(supabaseAnonKey, forHTTPHeaderField: "apikey")
        request.addValue("Bearer \(accessToken)", forHTTPHeaderField: "Authorization")
        
        let body: [String: Any] = [
            "what_i_am_doing": card.whatIAmDoing,
            "people_i_want_to_meet": card.peopleIWantToMeet,
            "profession_education": card.professionEducation,
            "personal_links": card.personalLinks,
            "updated_at": ISO8601DateFormatter().string(from: Date())
        ]
        
        request.httpBody = try JSONSerialization.data(withJSONObject: body)
        
        let (_, response) = try await URLSession.shared.data(for: request)
        
        if let httpResponse = response as? HTTPURLResponse, httpResponse.statusCode >= 400 {
            throw AuthError.serverError("更新名片失败")
        }
    }
    
    func getBusinessCard(by userId: String) async throws -> BusinessCard? {
        guard let session = currentSession, let accessToken = session.access_token else {
            throw AuthError.notAuthenticated("用户未登录")
        }
        
        let url = URL(string: "\(supabaseURL)/rest/v1/business_cards?user_id=eq.\(userId)&select=*")!
        var request = URLRequest(url: url)
        request.httpMethod = "GET"
        request.addValue("application/json", forHTTPHeaderField: "Content-Type")
        request.addValue(supabaseAnonKey, forHTTPHeaderField: "apikey")
        request.addValue("Bearer \(accessToken)", forHTTPHeaderField: "Authorization")
        
        let (data, response) = try await URLSession.shared.data(for: request)
        
        if let httpResponse = response as? HTTPURLResponse, httpResponse.statusCode >= 400 {
            return nil
        }
        
        let cards = try JSONDecoder().decode([BusinessCard].self, from: data)
        return cards.first
    }
    
    // MARK: - Account Deletion
    func deleteUserAccount() async throws {
        guard let session = currentSession, 
              let accessToken = session.access_token,
              let user = session.user else {
            throw AuthError.notAuthenticated("用户未登录")
        }
        
        // 1. 删除用户的业务卡片
        do {
            let deleteCardURL = URL(string: "\(supabaseURL)/rest/v1/business_cards?user_id=eq.\(user.id)")!
            var deleteCardRequest = URLRequest(url: deleteCardURL)
            deleteCardRequest.httpMethod = "DELETE"
            deleteCardRequest.addValue("application/json", forHTTPHeaderField: "Content-Type")
            deleteCardRequest.addValue(supabaseAnonKey, forHTTPHeaderField: "apikey")
            deleteCardRequest.addValue("Bearer \(accessToken)", forHTTPHeaderField: "Authorization")
            
            let (_, _) = try await URLSession.shared.data(for: deleteCardRequest)
        } catch {
            print("删除业务卡片时出错: \(error)")
            // 继续执行，不因为这个错误中断整个流程
        }
        
        // 2. 删除用户配置文件
        do {
            let deleteProfileURL = URL(string: "\(supabaseURL)/rest/v1/profiles?id=eq.\(user.id)")!
            var deleteProfileRequest = URLRequest(url: deleteProfileURL)
            deleteProfileRequest.httpMethod = "DELETE"
            deleteProfileRequest.addValue("application/json", forHTTPHeaderField: "Content-Type")
            deleteProfileRequest.addValue(supabaseAnonKey, forHTTPHeaderField: "apikey")
            deleteProfileRequest.addValue("Bearer \(accessToken)", forHTTPHeaderField: "Authorization")
            
            let (_, _) = try await URLSession.shared.data(for: deleteProfileRequest)
        } catch {
            print("删除用户配置文件时出错: \(error)")
            // 继续执行，不因为这个错误中断整个流程
        }
        
        // 3. 删除认证账户 (这会删除实际的用户账户)
        let deleteUserURL = URL(string: "\(supabaseURL)/auth/v1/admin/users/\(user.id)")!
        var deleteUserRequest = URLRequest(url: deleteUserURL)
        deleteUserRequest.httpMethod = "DELETE"
        deleteUserRequest.addValue("application/json", forHTTPHeaderField: "Content-Type")
        deleteUserRequest.addValue(supabaseAnonKey, forHTTPHeaderField: "apikey")
        deleteUserRequest.addValue("Bearer \(accessToken)", forHTTPHeaderField: "Authorization")
        
        let (_, response) = try await URLSession.shared.data(for: deleteUserRequest)
        
        if let httpResponse = response as? HTTPURLResponse, httpResponse.statusCode >= 400 {
            throw AuthError.serverError("删除用户账户失败")
        }
        
        // 4. 清除本地会话
        clearSession()
    }
    
    // MARK: - Utility Methods
    private func isValidEmail(_ email: String) -> Bool {
        let emailRegEx = "[A-Z0-9a-z._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,64}"
        let emailPred = NSPredicate(format:"SELF MATCHES %@", emailRegEx)
        return emailPred.evaluate(with: email)
    }
}

// MARK: - Auth Errors
enum AuthError: LocalizedError {
    case invalidInput(String)
    case invalidCredentials(String)
    case serverError(String)
    case notAuthenticated(String)
    
    var errorDescription: String? {
        switch self {
        case .invalidInput(let message),
             .invalidCredentials(let message),
             .serverError(let message),
             .notAuthenticated(let message):
            return message
        }
    }
} 