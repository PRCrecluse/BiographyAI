import SwiftUI

struct HomeTopSwitchView: View {
    @EnvironmentObject var state: AppState
    @EnvironmentObject var themeManager: ThemeManager
    
    var body: some View {
        HStack(spacing: 0) {
            Button {
                withAnimation(.easeInOut(duration: 0.2)) {
                    state.currentSection = .about
                }
            } label: {
                Text("About".localized)
                    .font(.system(size: 14, weight: .medium))
                    .foregroundColor(state.currentSection == .about ? Theme.Colors.primaryText(for: themeManager.currentTheme) : Theme.Colors.primaryText(for: themeManager.currentTheme).opacity(0.6))
                    .padding(.horizontal, 12)
                    .padding(.vertical, 6)
            }
            
            Button {
                withAnimation(.easeInOut(duration: 0.2)) {
                    state.currentSection = .assets
                }
            } label: {
                Text("Assets".localized)
                    .font(.system(size: 14, weight: .medium))
                    .foregroundColor(state.currentSection == .assets ? Theme.Colors.primaryText(for: themeManager.currentTheme) : Theme.Colors.primaryText(for: themeManager.currentTheme).opacity(0.6))
                    .padding(.horizontal, 12)
                    .padding(.vertical, 6)
            }
        }
        .background(
            Capsule()
                .fill(Theme.Colors.secondaryText(for: themeManager.currentTheme).opacity(0.2))
        )
    }
}

struct MainView: View {
    @EnvironmentObject var state: AppState
    @EnvironmentObject var themeManager: ThemeManager
    
    var body: some View {
        ZStack {
            // 主要内容
            ZStack {
                HomeView()
                    .opacity(state.currentSection == .about ? 1 : 0)
                    .animation(.easeInOut(duration: 0.25), value: state.currentSection)
                    .allowsHitTesting(state.currentSection == .about)
                    .id("HomeView")
                
                AssetsView()
                    .opacity(state.currentSection == .assets ? 1 : 0)
                    .animation(.easeInOut(duration: 0.25), value: state.currentSection)
                    .allowsHitTesting(state.currentSection == .assets)
                    .id("AssetsView")
            }
            .blur(radius: state.showingSidebar ? 3 : 0)
            .animation(.easeInOut(duration: 0.3), value: state.showingSidebar)
            
            // 半透明遮罩
            if state.showingSidebar {
                Color.black.opacity(0.3)
                    .ignoresSafeArea()
                    .onTapGesture {
                        withAnimation {
                            state.showingSidebar = false
                        }
                    }
                    .transition(.opacity)
                    .animation(.easeInOut(duration: 0.3), value: state.showingSidebar)
            }
            
            // 侧边栏
            HStack {
                if state.showingSidebar {
                    SidebarView()
                        .frame(width: UIScreen.main.bounds.width * 0.85)
                        .transition(.move(edge: .leading))
                }
                Spacer()
            }
            .animation(.easeInOut(duration: 0.3), value: state.showingSidebar)
            
            // 悬浮的头像按钮和切换按钮 - 始终在最上层
            VStack {
                HStack {
                    Button {
                        withAnimation(.easeInOut) {
                            state.showingSidebar.toggle()
                        }
                    } label: {
                        Circle()
                            .fill(Theme.Colors.secondaryText(for: themeManager.currentTheme).opacity(0.3))
                            .frame(width: 40, height: 40)
                            .overlay(
                                Group {
                                    if state.showingSidebar {
                                        Image(systemName: "xmark")
                                            .font(.system(size: 20))
                                            .foregroundColor(Theme.Colors.primaryText(for: themeManager.currentTheme))
                                    } else {
                                        Image(systemName: "person.fill")
                                            .font(.system(size: 20))
                                            .foregroundColor(Theme.Colors.primaryText(for: themeManager.currentTheme))
                                    }
                                }
                            )
                    }
                    
                    Spacer()
                    
                    // About|Assets 切换按钮
                    if !state.showingSidebar {
                        HomeTopSwitchView()
                    }
                }
                .padding(.horizontal, 24)
                .padding(.top, 20)
                Spacer()
            }
        }
        .background(Theme.Colors.background(for: themeManager.currentTheme))
        .sheet(isPresented: $state.showingBiographyGenerator) {
            BiographyGeneratorView()
                .environmentObject(state)
                .environmentObject(themeManager)
        }
        .gesture(
            DragGesture()
                .onEnded { value in
                    let threshold: CGFloat = 100
                    if value.translation.width > threshold && !state.showingSidebar {
                        withAnimation {
                            state.showingSidebar = true
                        }
                    } else if value.translation.width < -threshold && state.showingSidebar {
                        withAnimation {
                            state.showingSidebar = false
                        }
                    }
                }
        )
        .preferredColorScheme(themeManager.currentTheme.colorScheme)
    }
}

#Preview {
    MainView()
        .environmentObject(AppState())
        .environmentObject(ThemeManager.shared)
} 