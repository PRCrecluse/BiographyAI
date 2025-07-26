import SwiftUI

struct Theme {
    struct Colors {
        // 动态颜色，根据ThemeManager的设置返回不同值
        static func background(for theme: AppTheme) -> Color {
            switch theme {
            case .light:
                return Color(hex: "faf4f4")
            case .dark:
                return .black
            case .system:
                return Color(UIColor.systemBackground)
            }
        }
        
        static func primaryText(for theme: AppTheme) -> Color {
            switch theme {
            case .light:
                return .black
            case .dark:
                return .white
            case .system:
                return Color(UIColor.label)
            }
        }
        
        static func secondaryText(for theme: AppTheme) -> Color {
            switch theme {
            case .light:
                return Color(white: 0.3)
            case .dark:
                return Color(white: 0.7)
            case .system:
                return Color(UIColor.secondaryLabel)
            }
        }
        
        // 底部导航渐变色 - 根据主题模式动态调整
        static func roseGradient(for theme: AppTheme) -> LinearGradient {
            switch theme {
            case .light:
                return LinearGradient(
                    colors: [
                        Color(hex: "f4cccc"),
                        Color(hex: "edd8d8")
                    ], 
                    startPoint: .bottom, 
                    endPoint: .top
                )
            case .dark:
                return LinearGradient(
                    colors: [
                        Color(red: 0x8c/255.0, green: 0x71/255.0, blue: 0x71/255.0),
                        Color(red: 0x51/255.0, green: 0x47/255.0, blue: 0x47/255.0)
                    ], 
                    startPoint: .bottom, 
                    endPoint: .top
                )
            case .system:
                return LinearGradient(
                    colors: [
                        Color(UIColor { traitCollection in
                            traitCollection.userInterfaceStyle == .dark ? 
                            UIColor(red: 0x8c/255.0, green: 0x71/255.0, blue: 0x71/255.0, alpha: 1.0) :
                            UIColor(Color(hex: "f4cccc"))
                        }),
                        Color(UIColor { traitCollection in
                            traitCollection.userInterfaceStyle == .dark ? 
                            UIColor(red: 0x51/255.0, green: 0x47/255.0, blue: 0x47/255.0, alpha: 1.0) :
                            UIColor(Color(hex: "edd8d8"))
                        })
                    ], 
                    startPoint: .bottom, 
                    endPoint: .top
                )
            }
        }
        
        static let rose = Color(red: 227/255, green: 110/255, blue: 129/255)
        
        // 按钮渐变色：#f23e3e → #cc9595 → #8a8989
        static let buttonGradient = LinearGradient(
            colors: [
                Color(red: 0xf2/255.0, green: 0x3e/255.0, blue: 0x3e/255.0),
                Color(red: 0xcc/255.0, green: 0x95/255.0, blue: 0x95/255.0),
                Color(red: 0x8a/255.0, green: 0x89/255.0, blue: 0x89/255.0)
            ], 
            startPoint: .leading, 
            endPoint: .trailing
        )
        
        // 便捷访问器，基于当前主题
        static var background: Color {
            background(for: ThemeManager.shared.currentTheme)
        }
        
        static var primaryText: Color {
            primaryText(for: ThemeManager.shared.currentTheme)
        }
        
        static var secondaryText: Color {
            secondaryText(for: ThemeManager.shared.currentTheme)
        }
        
        static var roseGradient: LinearGradient {
            roseGradient(for: ThemeManager.shared.currentTheme)
        }
    }

    struct Fonts {
        static func songtiBold(size: CGFloat) -> Font {
            // 如果华文宋体字体不可用，回退到系统字体
            if UIFont(name: "STSongti-SC-Bold", size: size) != nil {
                return Font.custom("STSongti-SC-Bold", size: size)
            } else {
                return Font.system(size: size, weight: .bold, design: .serif)
            }
        }

        static func songtiRegular(size: CGFloat) -> Font {
            // 如果华文宋体字体不可用，回退到系统字体
            if UIFont(name: "STSongti-SC-Regular", size: size) != nil {
                return Font.custom("STSongti-SC-Regular", size: size)
            } else {
                return Font.system(size: size, weight: .regular, design: .serif)
            }
        }
    }
}

// MARK: - Color Extensions
extension Color {
    // 从十六进制字符串创建颜色
    init(hex: String) {
        let hex = hex.trimmingCharacters(in: CharacterSet.alphanumerics.inverted)
        var int: UInt64 = 0
        Scanner(string: hex).scanHexInt64(&int)
        let a, r, g, b: UInt64
        switch hex.count {
        case 3: // RGB (12-bit)
            (a, r, g, b) = (255, (int >> 8) * 17, (int >> 4 & 0xF) * 17, (int & 0xF) * 17)
        case 6: // RGB (24-bit)
            (a, r, g, b) = (255, int >> 16, int >> 8 & 0xFF, int & 0xFF)
        case 8: // ARGB (32-bit)
            (a, r, g, b) = (int >> 24, int >> 16 & 0xFF, int >> 8 & 0xFF, int & 0xFF)
        default:
            (a, r, g, b) = (1, 1, 1, 0)
        }

        self.init(
            .sRGB,
            red: Double(r) / 255,
            green: Double(g) / 255,
            blue:  Double(b) / 255,
            opacity: Double(a) / 255
        )
    }
}

// MARK: - Theme-aware View Modifier
struct ThemedView: ViewModifier {
    @StateObject private var themeManager = ThemeManager.shared
    
    func body(content: Content) -> some View {
        content
            .background(Theme.Colors.background(for: themeManager.currentTheme))
            .foregroundColor(Theme.Colors.primaryText(for: themeManager.currentTheme))
            .preferredColorScheme(themeManager.currentTheme.colorScheme)
    }
}

extension View {
    func themedBackground() -> some View {
        modifier(ThemedView())
    }
} 