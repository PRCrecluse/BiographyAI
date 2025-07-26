//
//  AI_profileApp.swift
//  AI profile
//
//  Created by 朱怡玮 on 2025/6/27.
//

import SwiftUI

@main
struct AI_profileApp: App {
    @StateObject private var localizationManager = LocalizationManager.shared
    @StateObject private var themeManager = ThemeManager.shared
    
    var body: some Scene {
        WindowGroup {
            RootView()
                .environmentObject(localizationManager)
                .environmentObject(themeManager)
                .preferredColorScheme(themeManager.currentTheme.colorScheme)
                .onAppear {
                    // Apply theme on app launch
                    if let scene = UIApplication.shared.connectedScenes.first as? UIWindowScene {
                        themeManager.applyTheme(to: scene)
                    }
                }
        }
    }
} 