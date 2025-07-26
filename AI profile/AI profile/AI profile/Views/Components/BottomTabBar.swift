import SwiftUI

enum Tab: Int {
    case favorites, add, discover
}

struct BottomTabBar: View {
    @EnvironmentObject var state: AppState
    @EnvironmentObject var themeManager: ThemeManager
    @State private var selected: Tab = .add
    @Namespace private var indicator
    
    var body: some View {
        HStack {
            // 左侧悬浮岛 - Profile + Community
            HStack(spacing: 60) {
                tabButton(icon: "person", tab: .favorites, label: "Profile".localized)
                tabButton(icon: "person.3", tab: .discover, label: "Community".localized)
            }
            .padding(.horizontal, 40)
            .padding(.vertical, 12)
            .background(
                Capsule()
                    .fill(Theme.Colors.roseGradient(for: themeManager.currentTheme))
                    .frame(height: 50)
            )
            
            Spacer().frame(width: 30)
            
            // 右侧圆形添加按钮
            addButton
        }
        .padding(.horizontal, 20)
        .padding(.bottom, 10)
        .alert("Community".localized, isPresented: $state.showingCommunityDevelopmentAlert) {
            Button("OK", role: .cancel) { }
        } message: {
            Text("Under Development".localized)
        }
    }
    
    private func tabButton(icon: String, tab: Tab, label: String? = nil) -> some View {
        Button {
            if tab == .discover {
                // Community功能显示开发中提示
                state.showingCommunityDevelopmentAlert = true
            } else {
                selected = tab
            }
        } label: {
            if let label = label {
                VStack(spacing: 2) {
                    Image(systemName: icon)
                        .font(.system(size: 16, weight: .medium))
                    Text(label)
                        .font(.system(size: 10, weight: .medium))
                }
                .foregroundColor(selected == tab ? Theme.Colors.primaryText(for: themeManager.currentTheme) : Theme.Colors.primaryText(for: themeManager.currentTheme).opacity(0.6))
            } else {
                Image(systemName: icon)
                    .font(.system(size: 20, weight: .medium))
                    .foregroundColor(selected == tab ? Theme.Colors.primaryText(for: themeManager.currentTheme) : Theme.Colors.primaryText(for: themeManager.currentTheme).opacity(0.6))
            }
        }
    }
    
    private var addButton: some View {
        Button {
            // 直接显示Biography生成器
                state.showingBiographyGenerator = true
        } label: {
            Image(systemName: "plus")
                .font(.system(size: 20, weight: .bold))
                .foregroundColor(Theme.Colors.primaryText(for: themeManager.currentTheme))
                .frame(width: 50, height: 50)
                .background(
                    Circle()
                        .fill(Theme.Colors.roseGradient(for: themeManager.currentTheme))
                )
        }
    }
}

#Preview {
    BottomTabBar()
        .environmentObject(AppState())
        .environmentObject(ThemeManager.shared)
} 