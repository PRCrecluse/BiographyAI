import SwiftUI

struct AIModelConfigView: View {
    @EnvironmentObject var state: AppState
    @StateObject private var agentService = AgentService.shared
    @State private var selectedProvider = "openai"
    @State private var apiKey = ""
    @State private var apiBase = ""
    @State private var temperature: Double = 0.7
    @State private var maxTokens: Int = 2000
    @State private var showingAlert = false
    @State private var alertMessage = ""
    @State private var isConfiguring = false
    
    let providers = [
        ("openai", "OpenAI", "GPT-4 / GPT-4V"),
        ("anthropic", "Anthropic", "Claude-3"),
        ("alibaba", "阿里云", "通义千问"),
        ("baidu", "百度", "文心一言"),
        ("zhipu", "智谱AI", "GLM-4")
    ]
    
    @State private var selectedModel = ""
    
    var body: some View {
        NavigationView {
            ZStack {
                Theme.Colors.background
                    .ignoresSafeArea()
                
                ScrollView {
                    VStack(alignment: .leading, spacing: 24) {
                        Text("AI模型配置")
                            .font(.system(size: 24, weight: .bold))
                            .foregroundColor(Theme.Colors.primaryText)
                        
                        // 提供商选择
                        VStack(alignment: .leading, spacing: 12) {
                            Text("选择AI提供商")
                                .font(.system(size: 16, weight: .semibold))
                                .foregroundColor(Theme.Colors.primaryText)
                            
                            ForEach(providers, id: \.0) { provider in
                                Button {
                                    selectedProvider = provider.0
                                } label: {
                                    HStack {
                                        VStack(alignment: .leading) {
                                            Text(provider.1)
                                                .font(.system(size: 14, weight: .medium))
                                                .foregroundColor(Theme.Colors.primaryText)
                                            Text(provider.2)
                                                .font(.system(size: 12))
                                                .foregroundColor(Theme.Colors.secondaryText)
                                        }
                                        Spacer()
                                        if selectedProvider == provider.0 {
                                            Image(systemName: "checkmark.circle.fill")
                                                .foregroundColor(.blue)
                                        }
                                    }
                                    .padding(12)
                                    .background(
                                        RoundedRectangle(cornerRadius: 8)
                                            .fill(selectedProvider == provider.0 ? Color.blue.opacity(0.1) : Theme.Colors.secondaryText.opacity(0.05))
                                    )
                                    .overlay(
                                        RoundedRectangle(cornerRadius: 8)
                                            .stroke(selectedProvider == provider.0 ? .blue : Theme.Colors.secondaryText.opacity(0.1), lineWidth: 1)
                                    )
                                }
                            }
                        }
                        
                        // API Key输入
                        VStack(alignment: .leading, spacing: 8) {
                            Text("API Key")
                                .font(.system(size: 16, weight: .semibold))
                                .foregroundColor(Theme.Colors.primaryText)
                            
                            SecureField("请输入API Key", text: $apiKey)
                                .textFieldStyle(RoundedBorderTextFieldStyle())
                        }
                        
                        // 保存按钮
                        Button {
                            saveConfiguration()
                        } label: {
                            Text("保存配置")
                                .font(.system(size: 16, weight: .semibold))
                                .foregroundColor(.white)
                                .frame(maxWidth: .infinity)
                                .frame(height: 50)
                                .background(
                                    RoundedRectangle(cornerRadius: 12)
                                        .fill(canSave ? Theme.Colors.primaryText : Theme.Colors.secondaryText.opacity(0.3))
                                )
                        }
                        .disabled(!canSave)
                        
                        Spacer(minLength: 100)
                    }
                    .padding(.horizontal, 24)
                    .padding(.top, 20)
                }
            }
            .toolbar {
                ToolbarItem(placement: .navigationBarLeading) {
                    Button("关闭") {
                        // 关闭配置页面的逻辑需要在父视图中处理
                    }
                }
            }
            .alert("提示", isPresented: $showingAlert) {
                Button("确定", role: .cancel) { }
            } message: {
                Text(alertMessage)
            }
        }
        .onAppear {
            loadConfiguration()
        }
    }
    
    private var canSave: Bool {
        return !apiKey.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty
    }
    
    private func loadConfiguration() {
        selectedProvider = UserDefaults.standard.string(forKey: "ai_provider") ?? "openai"
        apiKey = UserDefaults.standard.string(forKey: "ai_api_key") ?? ""
        apiBase = UserDefaults.standard.string(forKey: "ai_api_base") ?? ""
        temperature = UserDefaults.standard.double(forKey: "ai_temperature")
        if temperature == 0 { temperature = 0.7 }
        maxTokens = UserDefaults.standard.integer(forKey: "ai_max_tokens")
        if maxTokens == 0 { maxTokens = 2000 }
    }
    
    private func saveConfiguration() {
        guard canSave else { return }
        
        // 保存到本地
        UserDefaults.standard.set(selectedProvider, forKey: "ai_provider")
        UserDefaults.standard.set(apiKey, forKey: "ai_api_key")
        UserDefaults.standard.set(apiBase, forKey: "ai_api_base")
        UserDefaults.standard.set(temperature, forKey: "ai_temperature")
        UserDefaults.standard.set(maxTokens, forKey: "ai_max_tokens")
        
        alertMessage = "AI模型配置已保存！"
        showingAlert = true
    }
} 