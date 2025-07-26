import Foundation
import UIKit

// MARK: - Agent API 数据模型
struct BiographyCreateRequest: Codable {
    let userRequirements: String
    let templateStyle: String
    let language: String
    
    enum CodingKeys: String, CodingKey {
        case userRequirements = "user_requirements"
        case templateStyle = "template_style"
        case language
    }
}

struct BiographyTaskResponse: Codable {
    let taskId: String
    let status: String
    let message: String
    
    enum CodingKeys: String, CodingKey {
        case taskId = "task_id"
        case status
        case message
    }
}

struct TaskStatusResponse: Codable {
    let taskId: String
    let status: String
    let progress: Double
    let message: String?
    let pdfUrl: String?
    let errorMessage: String?
    let error: String?
    let createdAt: String?
    private(set) var result: [String: Any]?
    
    enum CodingKeys: String, CodingKey {
        case taskId = "task_id"
        case status
        case progress
        case message
        case pdfUrl = "pdf_url"
        case errorMessage = "error_message"
        case result
        case error
        case createdAt = "created_at"
    }
    
    init(from decoder: Decoder) throws {
        let container = try decoder.container(keyedBy: CodingKeys.self)
        
        taskId = try container.decode(String.self, forKey: .taskId)
        status = try container.decode(String.self, forKey: .status)
        progress = try container.decodeIfPresent(Double.self, forKey: .progress) ?? 0.0
        message = try container.decodeIfPresent(String.self, forKey: .message)
        pdfUrl = try container.decodeIfPresent(String.self, forKey: .pdfUrl)
        errorMessage = try container.decodeIfPresent(String.self, forKey: .errorMessage)
        createdAt = try container.decodeIfPresent(String.self, forKey: .createdAt)
        error = try container.decodeIfPresent(String.self, forKey: .error)
        
        // 处理result字段
        result = nil
        if container.contains(.result) {
            // 尝试将result解析为字典
            if let resultValue = try? container.decodeNil(forKey: .result), resultValue {
                // result是null
                result = nil
            } else {
                // 尝试解析为JSON对象
                do {
                    let resultJSON = try container.decode(JSON.self, forKey: .result)
                    result = resultJSON.value as? [String: Any]
                } catch {
                    print("解析result字段失败: \(error)")
                }
            }
        }
    }
    
    func encode(to encoder: Encoder) throws {
        var container = encoder.container(keyedBy: CodingKeys.self)
        
        try container.encode(taskId, forKey: .taskId)
        try container.encode(status, forKey: .status)
        try container.encode(progress, forKey: .progress)
        if let message = message { try container.encode(message, forKey: .message) }
        if let pdfUrl = pdfUrl { try container.encode(pdfUrl, forKey: .pdfUrl) }
        if let errorMessage = errorMessage { try container.encode(errorMessage, forKey: .errorMessage) }
        if let createdAt = createdAt { try container.encode(createdAt, forKey: .createdAt) }
        if let error = error { try container.encode(error, forKey: .error) }
        
        // 不编码result字段
    }
}

// 辅助类，用于解码任意JSON
struct JSON: Codable {
    let value: Any
    
    init(_ value: Any) {
        self.value = value
    }
    
    init(from decoder: Decoder) throws {
        let container = try decoder.singleValueContainer()
        
        if container.decodeNil() {
            self.value = NSNull()
        } else if let bool = try? container.decode(Bool.self) {
            self.value = bool
        } else if let int = try? container.decode(Int.self) {
            self.value = int
        } else if let double = try? container.decode(Double.self) {
            self.value = double
        } else if let string = try? container.decode(String.self) {
            self.value = string
        } else if let array = try? container.decode([JSON].self) {
            self.value = array.map { $0.value }
        } else if let dict = try? container.decode([String: JSON].self) {
            self.value = dict.mapValues { $0.value }
        } else {
            throw DecodingError.dataCorruptedError(in: container, debugDescription: "无法解码JSON值")
        }
    }
    
    func encode(to encoder: Encoder) throws {
        var container = encoder.singleValueContainer()
        
        switch value {
        case is NSNull:
            try container.encodeNil()
        case let bool as Bool:
            try container.encode(bool)
        case let int as Int:
            try container.encode(int)
        case let double as Double:
            try container.encode(double)
        case let string as String:
            try container.encode(string)
        case let array as [Any]:
            try container.encode(array.map { JSON($0) })
        case let dict as [String: Any]:
            try container.encode(dict.mapValues { JSON($0) })
        default:
            throw EncodingError.invalidValue(value, EncodingError.Context(codingPath: container.codingPath, debugDescription: "无法编码JSON值"))
        }
    }
}

struct AIModelConfig: Codable {
    let provider: String
    let modelName: String
    let apiKey: String
    let apiBase: String?
    let temperature: Double
    let maxTokens: Int
    
    enum CodingKeys: String, CodingKey {
        case provider
        case modelName = "model_name"
        case apiKey = "api_key"
        case apiBase = "api_base"
        case temperature
        case maxTokens = "max_tokens"
    }
}

// MARK: - Agent Service
class AgentService: ObservableObject {
    static let shared = AgentService()
    
    // Agent API 配置 - 基于地理位置的智能路由
    private let domesticURL = "https://rocketing.online" // 国内用户API
    private let overseasURL = "https://biographyai.zeabur.app" // 海外用户API
    private var baseURL: String = "https://rocketing.online" // 默认使用国内API
    private var session: URLSession
    
    @Published var isConnected = false
    @Published var currentTask: BiographyTask?
    @Published var isReconnecting = false
    @Published var currentRegion: String = "检测中..." // 显示当前使用的区域
    
    private init() {
        // 配置URLSession，增加超时时间
        let config = URLSessionConfiguration.default
        config.timeoutIntervalForRequest = 30 // 30秒请求超时
        config.timeoutIntervalForResource = 60 // 60秒资源超时
        config.waitsForConnectivity = true // 等待网络连接
        self.session = URLSession(configuration: config)
        
        print("🔄 AgentService 初始化完成")
        print("📍 默认Agent服务地址: \(baseURL)")
        
        // 在后台进行地理位置检测和连接检查
        Task.detached(priority: .utility) { [weak self] in
            // 先进行IP地理位置检测
            await self?.detectUserRegionAndSetAPI()
            
            // 延迟2秒后检查连接状态
            try? await Task.sleep(nanoseconds: 2_000_000_000)
            print("⏰ 开始进行初始连接检查...")
            await self?.checkConnection()
        }
    }
    
    // MARK: - IP地理位置检测和智能路由
    private func detectUserRegionAndSetAPI() async {
        print("🌍 开始检测用户地理位置...")
        
        do {
            // 使用多个IP地理位置服务进行检测
            let region = try await detectRegionWithFallback()
            
            await MainActor.run {
                if region == "CN" {
                    // 中国境内用户
                    self.baseURL = self.domesticURL
                    self.currentRegion = "🇨🇳 中国大陆 (国内线路)"
                    print("🇨🇳 检测到中国境内用户，使用国内API: \(self.baseURL)")
                } else {
                    // 海外用户
                    self.baseURL = self.overseasURL
                    self.currentRegion = "🌍 海外地区 (国际线路)"
                    print("🌍 检测到海外用户，使用国际API: \(self.baseURL)")
                }
            }
            
        } catch {
            print("⚠️ IP地理位置检测失败: \(error.localizedDescription)")
            print("📍 使用默认国内API: \(baseURL)")
            
            await MainActor.run {
                self.currentRegion = "⚠️ 检测失败，使用默认线路"
            }
        }
    }
    
    private func detectRegionWithFallback() async throws -> String {
        // 尝试多个地理位置检测服务
        let geoServices = [
            "http://ip-api.com/json/?fields=countryCode",
            "https://ipapi.co/country_code/",
            "https://api.country.is"
        ]
        
        for serviceURL in geoServices {
            do {
                print("🔍 尝试使用服务: \(serviceURL)")
                let region = try await detectRegionFromService(serviceURL)
                print("✅ 成功检测到地区: \(region)")
                return region
            } catch {
                print("❌ 服务 \(serviceURL) 检测失败: \(error.localizedDescription)")
                continue
            }
        }
        
        throw NSError(domain: "GeoDetectionError", code: -1, userInfo: [NSLocalizedDescriptionKey: "所有地理位置服务都不可用"])
    }
    
    private func detectRegionFromService(_ serviceURL: String) async throws -> String {
        guard let url = URL(string: serviceURL) else {
            throw NSError(domain: "InvalidURL", code: -1, userInfo: [NSLocalizedDescriptionKey: "无效的URL"])
        }
        
        var request = URLRequest(url: url)
        request.timeoutInterval = 10 // 10秒超时
        request.setValue("application/json", forHTTPHeaderField: "Accept")
        
        let (data, response) = try await session.data(for: request)
        
        guard let httpResponse = response as? HTTPURLResponse,
              httpResponse.statusCode == 200 else {
            throw NSError(domain: "HTTPError", code: -1, userInfo: [NSLocalizedDescriptionKey: "HTTP请求失败"])
        }
        
        // 解析不同服务的响应格式
        if serviceURL.contains("ip-api.com") {
            // ip-api.com 返回 JSON: {"countryCode": "CN"}
            if let json = try? JSONSerialization.jsonObject(with: data) as? [String: Any],
               let countryCode = json["countryCode"] as? String {
                return countryCode
            }
        } else if serviceURL.contains("ipapi.co") {
            // ipapi.co 返回纯文本: "CN"
            if let countryCode = String(data: data, encoding: .utf8)?.trimmingCharacters(in: .whitespacesAndNewlines) {
                return countryCode
            }
        } else if serviceURL.contains("country.is") {
            // country.is 返回 JSON: {"country": "CN"}
            if let json = try? JSONSerialization.jsonObject(with: data) as? [String: Any],
               let countryCode = json["country"] as? String {
                return countryCode
            }
        }
        
        throw NSError(domain: "ParseError", code: -1, userInfo: [NSLocalizedDescriptionKey: "无法解析响应数据"])
    }
    
    // MARK: - 手动切换API线路
    func switchToDomesticAPI() {
        print("🔄 手动切换到国内API")
        baseURL = domesticURL
        currentRegion = "🇨🇳 中国大陆 (手动切换)"
        print("🇨🇳 已切换到国内API: \(baseURL)")
        
        // 重新检查连接
        checkConnection()
    }
    
    func switchToOverseasAPI() {
        print("🔄 手动切换到海外API")
        baseURL = overseasURL
        currentRegion = "🌍 海外地区 (手动切换)"
        print("🌍 已切换到海外API: \(baseURL)")
        
        // 重新检查连接
        checkConnection()
    }
    
    func retryRegionDetection() {
        print("🔄 重新进行地理位置检测...")
        Task {
            await detectUserRegionAndSetAPI()
            checkConnection()
        }
    }
    
    // MARK: - 连接检查
    func checkConnection() {
        print("🔍 开始检查Agent连接状态...")
        print("🌐 请求URL: \(baseURL)/api/health")
        
        Task {
            await MainActor.run {
                self.isReconnecting = true
            }
            
            do {
                let url = URL(string: "\(baseURL)/api/health")!
                print("📡 发送连接检查请求...")
                
                let startTime = CFAbsoluteTimeGetCurrent()
                let (data, response) = try await session.data(from: url)
                let requestTime = CFAbsoluteTimeGetCurrent() - startTime
                
                print("⏱️ 请求耗时: \(String(format: "%.2f", requestTime))秒")
                
                await MainActor.run {
                    if let httpResponse = response as? HTTPURLResponse {
                        print("📊 HTTP状态码: \(httpResponse.statusCode)")
                        print("📋 响应头: \(httpResponse.allHeaderFields)")
                        
                        let wasConnected = self.isConnected
                        self.isConnected = httpResponse.statusCode == 200
                        
                        if self.isConnected {
                            print("✅ Agent连接成功!")
                            if !wasConnected {
                                print("🔄 从断开状态恢复连接")
                            }
                        } else {
                            print("❌ Agent连接失败 - HTTP状态码: \(httpResponse.statusCode)")
                        }
                        
                        // 尝试解析响应数据
                        if let responseString = String(data: data, encoding: .utf8) {
                            print("📄 响应内容: \(responseString)")
                        }
                    } else {
                        print("❌ 无效的HTTP响应")
                        self.isConnected = false
                    }
                    self.isReconnecting = false
                }
            } catch {
                await MainActor.run {
                    let wasConnected = self.isConnected
                    self.isConnected = false
                    self.isReconnecting = false
                    
                    print("❌ Agent连接检查失败")
                    print("🔍 错误类型: \(type(of: error))")
                    print("📝 错误详情: \(error)")
                    
                    if let urlError = error as? URLError {
                        print("🌐 URL错误代码: \(urlError.code.rawValue)")
                        print("📍 错误域: \(urlError.localizedDescription)")
                        
                        switch urlError.code {
                        case .timedOut:
                            print("⏰ 连接超时 - 服务器可能无响应")
                        case .notConnectedToInternet:
                            print("📶 无网络连接")
                        case .cannotConnectToHost:
                            print("🚫 无法连接到服务器")
                        case .networkConnectionLost:
                            print("📡 网络连接丢失")
                        default:
                            print("🔍 其他网络错误: \(urlError.localizedDescription)")
                        }
                    }
                    
                    if wasConnected {
                        print("💔 从连接状态变为断开")
                    }
                }
            }
        }
    }
    
    // MARK: - 手动重连（带重试机制）
    func reconnectWithRetry(maxAttempts: Int = 3) {
        print("🔄 开始手动重连，最大尝试次数: \(maxAttempts)")
        
        Task {
            await MainActor.run {
                self.isReconnecting = true
            }
            
            for attempt in 1...maxAttempts {
                print("🎯 重连尝试 \(attempt)/\(maxAttempts)")
                
                await checkConnectionOnce()
                
                if await MainActor.run(body: { self.isConnected }) {
                    print("✅ 重连成功！")
                    await MainActor.run {
                        self.isReconnecting = false
                    }
                    return
                }
                
                if attempt < maxAttempts {
                    let delay = Double(attempt) * 2.0 // 递增延迟
                    print("⏳ 等待 \(delay) 秒后重试...")
                    try? await Task.sleep(nanoseconds: UInt64(delay * 1_000_000_000))
                }
            }
            
            print("❌ 重连失败，已尝试 \(maxAttempts) 次")
            await MainActor.run {
                self.isReconnecting = false
            }
        }
    }
    
    // MARK: - 单次连接检查
    private func checkConnectionOnce() async {
        do {
            let url = URL(string: "\(baseURL)/api/health")!
            let (data, response) = try await session.data(from: url)
            
            await MainActor.run {
                if let httpResponse = response as? HTTPURLResponse {
                    self.isConnected = httpResponse.statusCode == 200
                } else {
                    self.isConnected = false
                }
            }
        } catch {
            await MainActor.run {
                self.isConnected = false
            }
        }
    }
    
    // MARK: - 创建传记
    func createBiography(
        images: [UIImage],
        userRequirements: String,
        templateStyle: String = "classic",
        language: String = "zh-CN"
    ) async throws -> BiographyTask {
        
        guard !images.isEmpty else {
            throw AgentError.noImages
        }
        
        let url = URL(string: "\(baseURL)/api/biography/create")!
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        
        // 创建 multipart/form-data
        let boundary = UUID().uuidString
        request.setValue("multipart/form-data; boundary=\(boundary)", forHTTPHeaderField: "Content-Type")
        
        var body = Data()
        
        // 添加请求参数
        let requestData = BiographyCreateRequest(
            userRequirements: userRequirements,
            templateStyle: templateStyle,
            language: language
        )
        
        body.append("--\(boundary)\r\n".data(using: .utf8)!)
        body.append("Content-Disposition: form-data; name=\"user_requirements\"\r\n\r\n".data(using: .utf8)!)
        body.append("\(requestData.userRequirements)\r\n".data(using: .utf8)!)
        
        body.append("--\(boundary)\r\n".data(using: .utf8)!)
        body.append("Content-Disposition: form-data; name=\"template_style\"\r\n\r\n".data(using: .utf8)!)
        body.append("\(requestData.templateStyle)\r\n".data(using: .utf8)!)
        
        body.append("--\(boundary)\r\n".data(using: .utf8)!)
        body.append("Content-Disposition: form-data; name=\"language\"\r\n\r\n".data(using: .utf8)!)
        body.append("\(requestData.language)\r\n".data(using: .utf8)!)
        
        // 添加图片文件
        for (index, image) in images.enumerated() {
            guard let imageData = image.jpegData(compressionQuality: 0.8) else {
                continue
            }
            
            body.append("--\(boundary)\r\n".data(using: .utf8)!)
            body.append("Content-Disposition: form-data; name=\"files\"; filename=\"image_\(index).jpg\"\r\n".data(using: .utf8)!)
            body.append("Content-Type: image/jpeg\r\n\r\n".data(using: .utf8)!)
            body.append(imageData)
            body.append("\r\n".data(using: .utf8)!)
        }
        
        body.append("--\(boundary)--\r\n".data(using: .utf8)!)
        request.httpBody = body
        
        let (data, response) = try await session.data(for: request)
        
        guard let httpResponse = response as? HTTPURLResponse,
              httpResponse.statusCode == 200 else {
            throw AgentError.apiError("创建传记失败")
        }
        
        let taskResponse = try JSONDecoder().decode(BiographyTaskResponse.self, from: data)
        
        let task = BiographyTask(
            id: taskResponse.taskId,
            status: .submitted,
            progress: 0.0,
            message: taskResponse.message,
            userRequirements: userRequirements,
            images: images,
            createdAt: Date()
        )
        
        await MainActor.run {
            self.currentTask = task
        }
        
        return task
    }
    
    // MARK: - 查询任务状态
    func checkTaskStatus(taskId: String) async throws -> TaskStatusResponse {
        let url = URL(string: "\(baseURL)/api/biography/status/\(taskId)")!
        
        print("📡 请求任务状态: \(url.absoluteString)")
        
        let (data, response) = try await session.data(from: url)
        
        guard let httpResponse = response as? HTTPURLResponse else {
            print("❌ 非HTTP响应")
            throw AgentError.networkError
        }
        
        print("📊 状态查询HTTP状态码: \(httpResponse.statusCode)")
        
        if httpResponse.statusCode != 200 {
            if let errorString = String(data: data, encoding: .utf8) {
                print("❌ 服务器错误: \(errorString)")
            }
            throw AgentError.apiError("查询任务状态失败: HTTP \(httpResponse.statusCode)")
        }
        
        do {
            // 打印原始响应
            if let responseString = String(data: data, encoding: .utf8) {
                print("📄 状态查询响应: \(responseString)")
            }
            
            let decoder = JSONDecoder()
            return try decoder.decode(TaskStatusResponse.self, from: data)
        } catch {
            print("❌ JSON解析错误: \(error)")
            
            // 尝试解析错误响应
            if let errorDict = try? JSONSerialization.jsonObject(with: data) as? [String: Any],
               let detail = errorDict["detail"] as? String {
                throw AgentError.apiError("查询失败: \(detail)")
            }
            
            throw AgentError.decodingError
        }
    }
    
    // MARK: - 下载PDF
    func downloadBiography(taskId: String) async throws -> Data {
        let url = URL(string: "\(baseURL)/api/biography/download/\(taskId)")!
        let (data, response) = try await session.data(from: url)
        
        guard let httpResponse = response as? HTTPURLResponse,
              httpResponse.statusCode == 200 else {
            throw AgentError.apiError("下载PDF失败")
        }
        
        return data
    }
    
    // MARK: - 配置AI模型
    func configureAIModel(_ config: AIModelConfig) async throws {
        let url = URL(string: "\(baseURL)/api/models/configure")!
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        
        let jsonData = try JSONEncoder().encode(config)
        request.httpBody = jsonData
        
        let (_, response) = try await session.data(for: request)
        
        guard let httpResponse = response as? HTTPURLResponse,
              httpResponse.statusCode == 200 else {
            throw AgentError.apiError("配置AI模型失败")
        }
    }
    
    // MARK: - 轮询任务状态
    func startPollingTask(_ task: BiographyTask) {
        Task {
            while true {
                do {
                    let status = try await checkTaskStatus(taskId: task.id)
                    
                    await MainActor.run {
                        if let currentTask = self.currentTask, currentTask.id == task.id {
                            self.currentTask = BiographyTask(
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
                        }
                    }
                    
                    // 如果任务完成或失败，停止轮询
                    if status.status == "completed" || status.status == "failed" {
                        break
                    }
                    
                    // 等待5秒后再次查询
                    try await Task.sleep(nanoseconds: 5_000_000_000)
                    
                } catch {
                    print("轮询任务状态失败: \(error)")
                    break
                }
            }
        }
    }
}

// MARK: - 错误类型
enum AgentError: LocalizedError {
    case noImages
    case apiError(String)
    case networkError
    case decodingError
    
    var errorDescription: String? {
        switch self {
        case .noImages:
            return "请至少选择一张图片"
        case .apiError(let message):
            return message
        case .networkError:
            return "网络连接失败"
        case .decodingError:
            return "数据解析失败"
        }
    }
} 