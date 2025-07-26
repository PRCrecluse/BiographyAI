import SwiftUI

struct RootView: View {
    @StateObject private var appState = AppState()
    @EnvironmentObject private var themeManager: ThemeManager
    
    var body: some View {
        Group {
            if !appState.isAppStartupComplete {
                // 启动加载屏幕
                startupLoadingView
            } else if appState.isLoggedIn {
                MainView()
            } else {
                AuthView()
            }
        }
        .environmentObject(appState)
        .preferredColorScheme(themeManager.currentTheme.colorScheme)
    }
    
    // MARK: - 启动加载视图
    private var startupLoadingView: some View {
        ZStack {
            Theme.Colors.background(for: themeManager.currentTheme)
                .ignoresSafeArea()
            
            VStack(spacing: 24) {
                // Logo或标题
                Circle()
                    .fill(Theme.Colors.secondaryText(for: themeManager.currentTheme).opacity(0.3))
                    .frame(width: 100, height: 100)
                    .overlay(
                        Image(systemName: "person.circle")
                            .font(.system(size: 60))
                            .foregroundColor(Theme.Colors.primaryText(for: themeManager.currentTheme))
                    )
                
                Text("Biography AI")
                    .font(Theme.Fonts.songtiBold(size: 32))
                    .foregroundColor(Theme.Colors.primaryText(for: themeManager.currentTheme))
                
                // 加载指示器
                ProgressView()
                    .progressViewStyle(CircularProgressViewStyle(tint: Theme.Colors.primaryText(for: themeManager.currentTheme)))
                    .scaleEffect(1.2)
                
                Text("Loading your data...")
                    .font(.system(size: 14))
                    .foregroundColor(Theme.Colors.secondaryText(for: themeManager.currentTheme).opacity(0.7))
            }
        }
    }
}

#Preview {
    RootView()
        .environmentObject(ThemeManager.shared)
} 