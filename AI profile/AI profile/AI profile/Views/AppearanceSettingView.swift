import SwiftUI

struct AppearanceSettingView: View {
    @EnvironmentObject var state: AppState
    @EnvironmentObject var themeManager: ThemeManager
    @Environment(\.dismiss) private var dismiss
    @State private var selectedTheme: AppTheme = .system
    
    var body: some View {
        NavigationView {
            VStack(alignment: .leading, spacing: 20) {
                // 标题
                VStack(alignment: .leading, spacing: 8) {
                    Text("Appearance".localized)
                        .font(Theme.Fonts.songtiBold(size: 24))
                        .foregroundColor(Theme.Colors.primaryText(for: themeManager.currentTheme))
                    
                    Text("Choose your preferred theme".localized)
                        .font(.system(size: 14))
                        .foregroundColor(Theme.Colors.secondaryText(for: themeManager.currentTheme).opacity(0.7))
                }
                .padding(.top, 20)
                
                Divider()
                    .background(Theme.Colors.secondaryText(for: themeManager.currentTheme))
                
                // 主题选择
                VStack(alignment: .leading, spacing: 16) {
                    ForEach(AppTheme.allCases, id: \.self) { theme in
                        Button {
                            selectedTheme = theme
                        } label: {
                            HStack {
                                // 主题图标和名称
                                VStack(alignment: .leading, spacing: 4) {
                                    HStack {
                                        Image(systemName: theme.icon)
                                            .font(.system(size: 18))
                                            .foregroundColor(Theme.Colors.primaryText(for: themeManager.currentTheme))
                                        
                                        Text(theme.displayName)
                                            .font(Theme.Fonts.songtiRegular(size: 16))
                                            .foregroundColor(Theme.Colors.primaryText(for: themeManager.currentTheme))
                                    }
                                    
                                    Text(theme.description)
                                        .font(.system(size: 12))
                                        .foregroundColor(Theme.Colors.secondaryText(for: themeManager.currentTheme).opacity(0.7))
                                }
                                
                                Spacer()
                                
                                // 选中状态
                                Image(systemName: selectedTheme == theme ? "checkmark.circle.fill" : "circle")
                                    .font(.system(size: 20))
                                    .foregroundColor(selectedTheme == theme ? Theme.Colors.rose : Theme.Colors.secondaryText(for: themeManager.currentTheme).opacity(0.4))
                            }
                            .padding(.vertical, 16)
                            .padding(.horizontal, 16)
                            .background(
                                RoundedRectangle(cornerRadius: 12)
                                    .fill(selectedTheme == theme ? Theme.Colors.rose.opacity(0.1) : Theme.Colors.secondaryText(for: themeManager.currentTheme).opacity(0.05))
                            )
                        }
                    }
                }
                
                Spacer()
                
                // 保存按钮
                VStack(spacing: 16) {
                    Divider()
                        .background(Theme.Colors.secondaryText(for: themeManager.currentTheme))
                    
                    Button("Save".localized) {
                        saveThemeSelection()
                        dismiss()
                    }
                    .font(Theme.Fonts.songtiRegular(size: 16))
                    .foregroundColor(.white)
                    .frame(maxWidth: .infinity)
                    .padding(.vertical, 12)
                    .background(Color(red: 0xd9/255.0, green: 0xbf/255.0, blue: 0xbf/255.0))
                    .cornerRadius(8)
                }
                .padding(.bottom, 40)
            }
            .padding(.horizontal, 24)
            .frame(maxWidth: .infinity, maxHeight: .infinity)
            .background(Theme.Colors.background(for: themeManager.currentTheme))
            .navigationBarHidden(true)
            .onAppear {
                selectedTheme = themeManager.currentTheme
            }
        }
        .preferredColorScheme(themeManager.currentTheme.colorScheme)
    }
    
    private func saveThemeSelection() {
        themeManager.setTheme(selectedTheme)
        print("主题已设置为: \(selectedTheme)")
    }
}

#Preview {
    AppearanceSettingView()
        .environmentObject(AppState())
        .environmentObject(ThemeManager.shared)
} 