import SwiftUI

struct LanguageSettingView: View {
    @EnvironmentObject var state: AppState
    @EnvironmentObject var themeManager: ThemeManager
    @Environment(\.dismiss) private var dismiss
    @StateObject private var localizationManager = LocalizationManager.shared
    @State private var selectedLanguage: String = ""
    
    var body: some View {
        NavigationView {
            VStack(alignment: .leading, spacing: 20) {
                // 标题
                VStack(alignment: .leading, spacing: 8) {
                    Text("Language setting".localized)
                        .font(Theme.Fonts.songtiBold(size: 24))
                        .foregroundColor(Theme.Colors.primaryText(for: themeManager.currentTheme))
                    
                    Text("Choose your preferred language".localized)
                        .font(.system(size: 14))
                        .foregroundColor(Theme.Colors.secondaryText(for: themeManager.currentTheme).opacity(0.7))
                }
                .padding(.top, 20)
                
                Divider()
                    .background(Theme.Colors.secondaryText(for: themeManager.currentTheme))
                
                // 语言选择
                VStack(alignment: .leading, spacing: 16) {
                    ForEach(supportedLanguages, id: \.code) { language in
                        Button {
                            selectedLanguage = language.code  
                        } label: {
                            HStack {
                                // 语言名称和标识
                                VStack(alignment: .leading, spacing: 4) {
                                    Text(language.name)
                                        .font(Theme.Fonts.songtiRegular(size: 16))
                                        .foregroundColor(Theme.Colors.primaryText(for: themeManager.currentTheme))
                                    Text(language.nativeName)
                                        .font(.system(size: 12))
                                        .foregroundColor(Theme.Colors.secondaryText(for: themeManager.currentTheme).opacity(0.7))
                                }
                                
                                Spacer()
                                
                                // 选中状态
                                Image(systemName: selectedLanguage == language.code ? "checkmark.circle.fill" : "circle")
                                    .font(.system(size: 20))
                                    .foregroundColor(selectedLanguage == language.code ? Theme.Colors.rose : Theme.Colors.secondaryText(for: themeManager.currentTheme).opacity(0.4))
                            }
                            .padding(.vertical, 16)
                            .padding(.horizontal, 16)
                            .background(
                                RoundedRectangle(cornerRadius: 12)
                                    .fill(selectedLanguage == language.code ? Theme.Colors.rose.opacity(0.1) : Theme.Colors.secondaryText(for: themeManager.currentTheme).opacity(0.05))
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
                        saveLanguageSelection()
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
                selectedLanguage = localizationManager.currentLanguage
            }
        }
        .preferredColorScheme(themeManager.currentTheme.colorScheme)
    }
    
    private let supportedLanguages = [
        LanguageOption(code: "en", name: "English", nativeName: "English"),
        LanguageOption(code: "fr", name: "French", nativeName: "Français"),
        LanguageOption(code: "it", name: "Italian", nativeName: "Italiano"),
        LanguageOption(code: "pt", name: "Portuguese", nativeName: "Português"),
        LanguageOption(code: "es", name: "Spanish", nativeName: "Español")
    ]
    
    private func saveLanguageSelection() {
        localizationManager.currentLanguage = selectedLanguage
        print("语言已设置为: \(selectedLanguage)")
    }
}

struct LanguageOption {
    let code: String
    let name: String
    let nativeName: String
}

#Preview {
    LanguageSettingView()
        .environmentObject(AppState())
        .environmentObject(ThemeManager.shared)
} 