import SwiftUI

struct PersonalInfoView: View {
    @EnvironmentObject var state: AppState
    @EnvironmentObject var themeManager: ThemeManager
    @Environment(\.dismiss) private var dismiss
    @State private var name = ""
    @State private var oneLineIntro = ""
    @State private var profession = ""
    @State private var education = ""
    @State private var link = ""
    
    var body: some View {
        NavigationView {
            VStack(alignment: .leading, spacing: 20) {
                // 标题
                VStack(alignment: .leading, spacing: 8) {
                    Text("Personal info".localized)
                        .font(Theme.Fonts.songtiBold(size: 24))
                        .foregroundColor(Theme.Colors.primaryText(for: themeManager.currentTheme))
                    
                    Text("Update your personal information".localized)
                        .font(.system(size: 14))
                        .foregroundColor(Theme.Colors.secondaryText(for: themeManager.currentTheme).opacity(0.7))
                }
                .padding(.top, 20)
                
                Divider()
                    .background(Theme.Colors.secondaryText(for: themeManager.currentTheme))
                
                // 输入字段
                VStack(alignment: .leading, spacing: 16) {
                    inputField("Name".localized, text: $name)
                    inputField("One-line intro".localized, text: $oneLineIntro)
                    inputField("Profession".localized, text: $profession)
                    inputField("Education/Experience".localized, text: $education, required: false)
                    inputField("Link".localized, text: $link, required: false)
                }
                
                Spacer()
                
                // 保存按钮
                VStack(spacing: 16) {
                    Divider()
                        .background(Theme.Colors.secondaryText(for: themeManager.currentTheme))
                    
                    Button("Save".localized) {
                        saveProfile()
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
                loadCurrentProfile()
            }
        }
        .preferredColorScheme(themeManager.currentTheme.colorScheme)
    }
    
    private func inputField(_ title: String, text: Binding<String>, required: Bool = true) -> some View {
        VStack(alignment: .leading, spacing: 8) {
            HStack {
                Text(title)
                    .font(Theme.Fonts.songtiRegular(size: 16))
                    .foregroundColor(Theme.Colors.primaryText(for: themeManager.currentTheme))
                if required {
                    Text("*")
                        .foregroundColor(Theme.Colors.rose)
                }
            }
            TextField("Enter \(title)".localized, text: text)
                .textFieldStyle(PlainTextFieldStyle())
                .padding(.horizontal, 12)
                .padding(.vertical, 10)
                .background(
                    RoundedRectangle(cornerRadius: 8)
                        .fill(Theme.Colors.secondaryText(for: themeManager.currentTheme).opacity(0.1))
                )
                .foregroundColor(Theme.Colors.primaryText(for: themeManager.currentTheme))
        }
    }
    
    private func loadCurrentProfile() {
        // 从AppState中的本地数据加载
        let localData = state.localProfileData
        name = localData.name
        oneLineIntro = localData.oneLineIntro
        profession = localData.profession
        education = localData.education
        link = localData.link
        
        // 如果AppState中的数据为空，尝试从其他源加载
        if name.isEmpty && oneLineIntro.isEmpty && profession.isEmpty && education.isEmpty && link.isEmpty {
            // 首先从LocalStorageManager加载
            let localProfile = LocalStorageManager.shared.fetchUserProfile()
            name = localProfile.name
            oneLineIntro = localProfile.oneLineIntro
            profession = localProfile.profession
            education = localProfile.education
            link = localProfile.link
            
            // 如果仍然为空，从当前用户信息加载
            if name.isEmpty && oneLineIntro.isEmpty && profession.isEmpty && education.isEmpty && link.isEmpty {
                if let user = state.currentUser {
                    name = user.name
                }
                if let card = state.currentBusinessCard {
                    oneLineIntro = card.whatIAmDoing
                    profession = card.professionEducation
                }
            }
        }
    }
    
    private func saveProfile() {
        // 更新AppState中的本地数据，这会自动更新首页显示
        state.updateLocalProfileData(
            name: name,
            oneLineIntro: oneLineIntro,
            profession: profession,
            education: education,
            link: link
        )
        
        // 保存到本地存储（通过LocalStorageManager）
        LocalStorageManager.shared.saveUserProfile(
            name: name,
            oneLineIntro: oneLineIntro,
            profession: profession,
            education: education,
            link: link
        )
        
        // 更新应用状态中的用户和名片信息
        if let currentUser = state.currentUser {
            // 创建更新后的用户对象
            let updatedUser = UserProfile(
                id: currentUser.id,
                name: name.isEmpty ? currentUser.name : name,
                email: currentUser.email,
                companyId: currentUser.companyId,
                createdAt: currentUser.createdAt,
                updatedAt: Date()
            )
            
            // 更新应用状态
            state.currentUser = updatedUser
            
            // 创建或更新名片信息
            let updatedCard = BusinessCard(
                id: state.currentBusinessCard?.id ?? UUID().uuidString,
                userId: currentUser.id,
                whatIAmDoing: oneLineIntro,
                peopleIWantToMeet: "",
                professionEducation: profession,
                personalLinks: [:],
                createdAt: state.currentBusinessCard?.createdAt ?? Date(),
                updatedAt: Date()
            )
            
            state.currentBusinessCard = updatedCard
            
            // 异步保存到Supabase
            Task {
                do {
                    try await SupabaseService.shared.updateProfile(updatedUser)
                    if let existingCard = state.currentBusinessCard {
                        try await SupabaseService.shared.updateBusinessCard(existingCard)
                    } else {
                        _ = try await SupabaseService.shared.createBusinessCard(
                            userId: currentUser.id,
                            whatIAmDoing: oneLineIntro,
                            peopleIWantToMeet: "",
                            professionEducation: profession
                        )
                    }
                    print("数据已保存到服务器")
                } catch {
                    print("保存到服务器失败: \(error)")
                }
            }
        }
        
        print("保存信息: \(name), \(oneLineIntro), \(profession), \(education), \(link)")
    }
}

#Preview {
    PersonalInfoView()
        .environmentObject(AppState())
        .environmentObject(ThemeManager.shared)
} 