import SwiftUI

enum AppTheme: String, CaseIterable {
    case system = "system"
    case light = "light"
    case dark = "dark"
    
    var displayName: String {
        switch self {
        case .system:
            return "System".localized
        case .light:
            return "Light".localized
        case .dark:
            return "Dark".localized
        }
    }
    
    var description: String {
        switch self {
        case .system:
            return "Follow system setting".localized
        case .light:
            return "Always light theme".localized
        case .dark:
            return "Always dark theme".localized
        }
    }
    
    var icon: String {
        switch self {
        case .system:
            return "gear"
        case .light:
            return "sun.max"
        case .dark:
            return "moon"
        }
    }
    
    var colorScheme: ColorScheme? {
        switch self {
        case .system:
            return nil
        case .light:
            return .light
        case .dark:
            return .dark
        }
    }
}

class ThemeManager: ObservableObject {
    static let shared = ThemeManager()
    
    @Published var currentTheme: AppTheme = .system {
        didSet {
            UserDefaults.standard.set(currentTheme.rawValue, forKey: "app_theme")
        }
    }
    
    private init() {
        loadSavedTheme()
    }
    
    private func loadSavedTheme() {
        let savedTheme = UserDefaults.standard.string(forKey: "app_theme") ?? "system"
        currentTheme = AppTheme(rawValue: savedTheme) ?? .system
    }
    
    func setTheme(_ theme: AppTheme) {
        currentTheme = theme
    }
    
    func applyTheme(to scene: UIWindowScene) {
        scene.windows.forEach { window in
            window.overrideUserInterfaceStyle = currentTheme.colorScheme?.uiInterfaceStyle ?? .unspecified
        }
    }
}

// MARK: - Helper Extensions
extension ColorScheme {
    var uiInterfaceStyle: UIUserInterfaceStyle {
        switch self {
        case .light:
            return .light
        case .dark:
            return .dark
        @unknown default:
            return .unspecified
        }
    }
} 