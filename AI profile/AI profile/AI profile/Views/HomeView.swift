import SwiftUI

struct HomeView: View {
    @EnvironmentObject var state: AppState
    @EnvironmentObject var themeManager: ThemeManager
    
    var body: some View {
        ZStack(alignment: .bottom) {
            // 背景
            Theme.Colors.background(for: themeManager.currentTheme)
                .ignoresSafeArea()
            
            // 主要内容
            VStack(alignment: .leading, spacing: 8) {
                Spacer()
                
                // 主标题区域
                VStack(alignment: .leading, spacing: 12) {
                    Text("Hello, I'm \(state.localProfileData.displayName)")
                        .font(Theme.Fonts.songtiBold(size: 40))
                        .foregroundColor(Theme.Colors.primaryText(for: themeManager.currentTheme))
                        .multilineTextAlignment(.leading)
                    
                    Text(state.localProfileData.displayOneLineIntro)
                        .font(Theme.Fonts.songtiBold(size: 22))
                        .foregroundColor(Theme.Colors.secondaryText(for: themeManager.currentTheme))
                        .multilineTextAlignment(.leading)
                    
                    // 详细信息
                    Text(state.localProfileData.displayDetailInfo)
                        .font(.system(size: 14, weight: .regular))
                        .foregroundColor(Theme.Colors.secondaryText(for: themeManager.currentTheme).opacity(0.8))
                        .multilineTextAlignment(.leading)
                        .padding(.top, 8)
                }
                .padding(.horizontal, 24)
                
                Spacer()
            }
            
            // 底部 TabBar
            BottomTabBar()
        }
        .onTapGesture {
            if state.showingSidebar {
                withAnimation { state.showingSidebar = false }
            }
        }
    }
}

#Preview {
    HomeView()
        .environmentObject(AppState())
        .environmentObject(ThemeManager.shared)
} 