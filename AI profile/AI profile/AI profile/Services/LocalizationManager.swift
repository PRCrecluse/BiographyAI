import Foundation

class LocalizationManager: ObservableObject {
    static let shared = LocalizationManager()
    
    @Published var currentLanguage: String = "en" {
        didSet {
            UserDefaults.standard.set(currentLanguage, forKey: "app_language")
            setLanguage(currentLanguage)
        }
    }
    
    private var bundle: Bundle = Bundle.main
    
    private init() {
        loadSavedLanguage()
    }
    
    private func loadSavedLanguage() {
        currentLanguage = UserDefaults.standard.string(forKey: "app_language") ?? "en"
        setLanguage(currentLanguage)
    }
    
    private func setLanguage(_ language: String) {
        guard let path = Bundle.main.path(forResource: language, ofType: "lproj"),
              let bundle = Bundle(path: path) else {
            // Fall back to English if language bundle not found
            if let path = Bundle.main.path(forResource: "en", ofType: "lproj"),
               let englishBundle = Bundle(path: path) {
                self.bundle = englishBundle
            } else {
                self.bundle = Bundle.main
            }
            return
        }
        self.bundle = bundle
    }
    
    func localizedString(for key: String, comment: String = "") -> String {
        return bundle.localizedString(forKey: key, value: nil, table: nil)
    }
}

// MARK: - String Extension for easy localization
extension String {
    var localized: String {
        return LocalizationManager.shared.localizedString(for: self)
    }
} 