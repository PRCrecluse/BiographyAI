import SwiftUI
import MessageUI

struct SidebarView: View {
    @EnvironmentObject var state: AppState
    @EnvironmentObject var themeManager: ThemeManager
    @StateObject private var agentService = AgentService.shared
    @State private var showingPersonalInfo = false
    @State private var showingLanguageSettings = false
    @State private var showingAppearanceSettings = false
    @State private var showingNetworkSettings = false
    @State private var showingDeleteConfirmation = false
    @State private var showingDeleteAlert = false
    @State private var deleteError: String?
    @State private var showingMailComposer = false
    
    var body: some View {
        VStack(alignment: .leading, spacing: 20) {
            // 菜单标题
            HStack {
                                    Text("Settings".localized)
                        .font(Theme.Fonts.songtiBold(size: 24))
                        .foregroundColor(Theme.Colors.primaryText(for: themeManager.currentTheme))
                Spacer()
            }
            .padding(.top, 100)
            
            Divider()
                .background(Theme.Colors.secondaryText(for: themeManager.currentTheme))
                .padding(.top, 20)
            
            // 菜单按钮
            VStack(spacing: 16) {
                // Personal info 按钮
                Button {
                    showingPersonalInfo = true
                } label: {
                    HStack {
                        Image(systemName: "person.circle")
                            .font(.system(size: 20))
                            .foregroundColor(Theme.Colors.primaryText(for: themeManager.currentTheme))
                        
                        Text("Personal info".localized)
                            .font(Theme.Fonts.songtiRegular(size: 16))
                            .foregroundColor(Theme.Colors.primaryText(for: themeManager.currentTheme))
                        
                        Spacer()
                        
                        Image(systemName: "chevron.right")
                            .font(.system(size: 12))
                            .foregroundColor(Theme.Colors.secondaryText(for: themeManager.currentTheme).opacity(0.6))
                    }
                    .padding(.vertical, 16)
                    .padding(.horizontal, 16)
                    .background(
                        RoundedRectangle(cornerRadius: 12)
                            .fill(Theme.Colors.secondaryText(for: themeManager.currentTheme).opacity(0.1))
                    )
                }
                
                // Language setting 按钮
                Button {
                    showingLanguageSettings = true
                } label: {
                    HStack {
                        Image(systemName: "globe")
                            .font(.system(size: 20))
                            .foregroundColor(Theme.Colors.primaryText(for: themeManager.currentTheme))
                        
                        Text("Language setting".localized)
                            .font(Theme.Fonts.songtiRegular(size: 16))
                            .foregroundColor(Theme.Colors.primaryText(for: themeManager.currentTheme))
                        
                        Spacer()
                        
                        Image(systemName: "chevron.right")
                            .font(.system(size: 12))
                            .foregroundColor(Theme.Colors.secondaryText(for: themeManager.currentTheme).opacity(0.6))
                    }
                    .padding(.vertical, 16)
                    .padding(.horizontal, 16)
                    .background(
                        RoundedRectangle(cornerRadius: 12)
                            .fill(Theme.Colors.secondaryText(for: themeManager.currentTheme).opacity(0.1))
                    )
                }
                
                // Appearance 按钮
                Button {
                    showingAppearanceSettings = true
                } label: {
                    HStack {
                        Image(systemName: "paintbrush")
                            .font(.system(size: 20))
                            .foregroundColor(Theme.Colors.primaryText(for: themeManager.currentTheme))
                        
                        Text("Appearance".localized)
                            .font(Theme.Fonts.songtiRegular(size: 16))
                            .foregroundColor(Theme.Colors.primaryText(for: themeManager.currentTheme))
                        
                        Spacer()
                        
                        Image(systemName: "chevron.right")
                            .font(.system(size: 12))
                            .foregroundColor(Theme.Colors.secondaryText(for: themeManager.currentTheme).opacity(0.6))
                    }
                    .padding(.vertical, 16)
                    .padding(.horizontal, 16)
                    .background(
                        RoundedRectangle(cornerRadius: 12)
                            .fill(Theme.Colors.secondaryText(for: themeManager.currentTheme).opacity(0.1))
                    )
                }
                
                // Network Settings 按钮
                Button {
                    showingNetworkSettings = true
                } label: {
                    HStack {
                        Image(systemName: "network")
                            .font(.system(size: 20))
                            .foregroundColor(Theme.Colors.primaryText(for: themeManager.currentTheme))
                        
                        VStack(alignment: .leading, spacing: 2) {
                            Text("Network Settings".localized)
                                .font(Theme.Fonts.songtiRegular(size: 16))
                                .foregroundColor(Theme.Colors.primaryText(for: themeManager.currentTheme))
                            
                            Text(agentService.currentRegion)
                                .font(.system(size: 12))
                                .foregroundColor(Theme.Colors.secondaryText(for: themeManager.currentTheme))
                        }
                        
                        Spacer()
                        
                        HStack(spacing: 4) {
                            Circle()
                                .fill(agentService.isConnected ? .green : .red)
                                .frame(width: 8, height: 8)
                            
                            Image(systemName: "chevron.right")
                                .font(.system(size: 12))
                                .foregroundColor(Theme.Colors.secondaryText(for: themeManager.currentTheme).opacity(0.6))
                        }
                    }
                    .padding(.vertical, 16)
                    .padding(.horizontal, 16)
                    .background(
                        RoundedRectangle(cornerRadius: 12)
                            .fill(Theme.Colors.secondaryText(for: themeManager.currentTheme).opacity(0.1))
                    )
                }
            }
            
            Spacer()
            
            // 登出和删除账户按钮区域（只在用户登录时显示）
            if state.isLoggedIn {
                VStack(spacing: 16) {
                    Divider()
                        .background(Theme.Colors.secondaryText(for: themeManager.currentTheme))
                    
                    // Contact us 按钮
                    Button("Contact us".localized) {
                        showingMailComposer = true
                    }
                    .font(Theme.Fonts.songtiRegular(size: 16))
                    .foregroundColor(Theme.Colors.primaryText(for: themeManager.currentTheme))
                    .frame(maxWidth: .infinity)
                    .padding(.vertical, 12)
                    .background(
                        RoundedRectangle(cornerRadius: 8)
                            .stroke(Theme.Colors.primaryText(for: themeManager.currentTheme), lineWidth: 1)
                    )
                    
                    // Sign Out 按钮
                    Button("Sign Out".localized) {
                        state.signOut()
                        withAnimation(.easeInOut) {
                            state.showingSidebar = false
                        }
                    }
                    .font(Theme.Fonts.songtiRegular(size: 16))
                    .foregroundColor(Theme.Colors.primaryText(for: themeManager.currentTheme))
                    .frame(maxWidth: .infinity)
                    .padding(.vertical, 12)
                    .background(
                        RoundedRectangle(cornerRadius: 8)
                            .stroke(Theme.Colors.primaryText(for: themeManager.currentTheme), lineWidth: 1)
                    )
                    
                    // Delete account 链接
                    Button("delete account".localized) {
                        showingDeleteConfirmation = true
                    }
                    .font(.system(size: 14))
                    .foregroundColor(.red.opacity(0.7))
                    .padding(.top, 8)
                    .confirmationDialog(
                        "Delete Account".localized,
                        isPresented: $showingDeleteConfirmation,
                        titleVisibility: .visible
                    ) {
                        Button("Delete Permanently".localized, role: .destructive) {
                            deleteAccount()
                        }
                        Button("Cancel".localized, role: .cancel) { }
                    } message: {
                        Text("This action cannot be undone. All your data will be permanently deleted.".localized)
                    }
                }
                .padding(.bottom, 40)
            }
        }
        .padding(.horizontal, 24)
        .frame(maxWidth: .infinity, maxHeight: .infinity)
        .background(Theme.Colors.background(for: themeManager.currentTheme))
        .sheet(isPresented: $showingPersonalInfo) {
            PersonalInfoView()
                .environmentObject(state)
                .environmentObject(themeManager)
        }
        .sheet(isPresented: $showingLanguageSettings) {
            LanguageSettingView()
                .environmentObject(state)
                .environmentObject(themeManager)
        }
        .sheet(isPresented: $showingAppearanceSettings) {
            AppearanceSettingView()
                .environmentObject(state)
                .environmentObject(themeManager)
        }
        .sheet(isPresented: $showingNetworkSettings) {
            NetworkSettingsView()
                .environmentObject(state)
                .environmentObject(themeManager)
        }
        .alert("Delete Error".localized, isPresented: $showingDeleteAlert) {
            Button("OK".localized) { }
        } message: {
            Text(deleteError ?? "Unknown error occurred".localized)
        }
        .sheet(isPresented: $showingMailComposer) {
            SafeMailComposeView(
                recipients: ["1765591779@qq.com"],
                subject: "",
                messageBody: "I think this function needs improvement".localized
            )
        }
    }
    
    // MARK: - Helper Methods
    private func deleteAccount() {
        Task {
            do {
                try await state.deleteAccount()
                await MainActor.run {
                    withAnimation(.easeInOut) {
                        state.showingSidebar = false
                    }
                }
            } catch {
                await MainActor.run {
                    deleteError = error.localizedDescription
                    showingDeleteAlert = true
                }
            }
        }
    }
}

#Preview {
    SidebarView()
        .environmentObject(AppState())
        .environmentObject(ThemeManager.shared)
} 