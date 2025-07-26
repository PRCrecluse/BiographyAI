import SwiftUI

struct AuthView: View {
    @EnvironmentObject var state: AppState
    @State private var showingRegister = false
    @State private var showingLogin = false
    
    var body: some View {
        ZStack {
            // 背景
            Theme.Colors.background
                .ignoresSafeArea()
            
            VStack(spacing: 0) {
                Spacer()
                
                // Logo或标题区域
                VStack(spacing: 20) {
                    Circle()
                        .fill(Theme.Colors.secondaryText.opacity(0.3))
                        .frame(width: 100, height: 100)
                        .overlay(
                            Image(systemName: "person.circle")
                                .font(.system(size: 60))
                                .foregroundColor(Theme.Colors.primaryText)
                        )
                    
                                    Text("Biography AI")
                    .font(Theme.Fonts.songtiBold(size: 32))
                    .foregroundColor(Theme.Colors.primaryText)
                    .padding(.top, 20)
                }
                
                Spacer()
                
                // 认证按钮
                VStack(spacing: 16) {
                    // 注册按钮
                    Button {
                        showingRegister = true
                    } label: {
                        Text("Sign Up")
                            .font(Theme.Fonts.songtiRegular(size: 16))
                            .foregroundColor(Theme.Colors.primaryText)
                            .frame(maxWidth: .infinity)
                            .padding(.vertical, 12)
                            .background(
                                RoundedRectangle(cornerRadius: 25)
                                    .fill(Theme.Colors.secondaryText.opacity(0.2))
                            )
                    }
                    
                    // 登录按钮
                    Button {
                        showingLogin = true
                    } label: {
                        Text("Sign In")
                            .font(Theme.Fonts.songtiRegular(size: 16))
                            .foregroundColor(Theme.Colors.primaryText)
                            .frame(maxWidth: .infinity)
                            .padding(.vertical, 12)
                            .background(
                                RoundedRectangle(cornerRadius: 25)
                                    .stroke(Theme.Colors.primaryText, lineWidth: 1)
                            )
                    }
                }
                .padding(.horizontal, 40)
                .padding(.bottom, 80)
            }
        }
        .sheet(isPresented: $showingRegister) {
            RegisterView()
        }
        .sheet(isPresented: $showingLogin) {
            LoginView()
        }
    }
}

struct RegisterView: View {
    @Environment(\.dismiss) private var dismiss
    @EnvironmentObject var state: AppState
    @State private var email = ""
    @State private var password = ""
    @State private var confirmPassword = ""
    @State private var isLoading = false
    @State private var errorMessage = ""
    @State private var showError = false
    
    var body: some View {
        NavigationView {
            VStack(spacing: 20) {
                Text("Create Account")
                    .font(Theme.Fonts.songtiBold(size: 24))
                    .foregroundColor(Theme.Colors.primaryText)
                    .padding(.top, 40)
                
                VStack(spacing: 16) {
                    TextField("Email", text: $email)
                        .textFieldStyle(RoundedBorderTextFieldStyle())
                        .keyboardType(.emailAddress)
                        .autocapitalization(.none)
                    
                    SecureField("Password", text: $password)
                        .textFieldStyle(RoundedBorderTextFieldStyle())
                    
                    SecureField("Confirm Password", text: $confirmPassword)
                        .textFieldStyle(RoundedBorderTextFieldStyle())
                }
                .padding(.horizontal, 40)
                
                Button("Sign Up") {
                    handleRegister()
                }
                .font(Theme.Fonts.songtiRegular(size: 16))
                .foregroundColor(.white)
                .frame(maxWidth: .infinity)
                .padding(.vertical, 12)
                .background(isLoading ? AnyShapeStyle(Color.gray) : AnyShapeStyle(Theme.Colors.buttonGradient))
                .cornerRadius(25)
                .padding(.horizontal, 40)
                .disabled(isLoading)
                
                if isLoading {
                    ProgressView()
                        .progressViewStyle(CircularProgressViewStyle(tint: Theme.Colors.rose))
                        .padding(.top, 10)
                }
                
                if showError {
                    Text(errorMessage)
                        .font(Theme.Fonts.songtiRegular(size: 14))
                        .foregroundColor(.red)
                        .padding(.horizontal, 40)
                        .padding(.top, 10)
                }
                
                Spacer()
            }
            .background(Theme.Colors.background)
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button("Cancel") {
                        dismiss()
                    }
                    .foregroundColor(Theme.Colors.primaryText)
                }
            }
        }
    }
    
    private func handleRegister() {
        // 验证输入
        guard !email.isEmpty, !password.isEmpty, !confirmPassword.isEmpty else {
            showErrorMessage("Please fill in all fields")
            return
        }
        
        guard password == confirmPassword else {
            showErrorMessage("Passwords do not match")
            return
        }
        
        guard password.count >= 6 else {
            showErrorMessage("Password must be at least 6 characters")
            return
        }
        
        isLoading = true
        showError = false
        
        Task {
            do {
                let _ = try await SupabaseService.shared.signUp(email: email, password: password)
                
                await MainActor.run {
                    // Don't auto-login after registration
                    // User needs to confirm email and then sign in
                    isLoading = false
                    
                    // Show success message
                    showErrorMessage("Registration successful! Please check your email to confirm your account, then sign in.")
                    
                    // Dismiss after a delay to show the success message
                    DispatchQueue.main.asyncAfter(deadline: .now() + 2) {
                        dismiss()
                    }
                }
            } catch {
                await MainActor.run {
                    isLoading = false
                    showErrorMessage(error.localizedDescription)
                }
            }
        }
    }
    
    private func showErrorMessage(_ message: String) {
        errorMessage = message
        showError = true
        
        // 3秒后自动隐藏错误信息
        DispatchQueue.main.asyncAfter(deadline: .now() + 3) {
            showError = false
        }
    }
}

struct LoginView: View {
    @Environment(\.dismiss) private var dismiss
    @EnvironmentObject var state: AppState
    @State private var email = ""
    @State private var password = ""
    @State private var isLoading = false
    @State private var errorMessage = ""
    @State private var showError = false
    
    var body: some View {
        NavigationView {
            VStack(spacing: 20) {
                Text("Sign In")
                    .font(Theme.Fonts.songtiBold(size: 24))
                    .foregroundColor(Theme.Colors.primaryText)
                    .padding(.top, 40)
                
                VStack(spacing: 16) {
                    TextField("Email", text: $email)
                        .textFieldStyle(RoundedBorderTextFieldStyle())
                        .keyboardType(.emailAddress)
                        .autocapitalization(.none)
                    
                    SecureField("Password", text: $password)
                        .textFieldStyle(RoundedBorderTextFieldStyle())
                }
                .padding(.horizontal, 40)
                
                Button("Sign In") {
                    handleLogin()
                }
                .font(Theme.Fonts.songtiRegular(size: 16))
                .foregroundColor(.white)
                .frame(maxWidth: .infinity)
                .padding(.vertical, 12)
                .background(isLoading ? AnyShapeStyle(Color.gray) : AnyShapeStyle(Theme.Colors.buttonGradient))
                .cornerRadius(25)
                .padding(.horizontal, 40)
                .disabled(isLoading)
                
                if isLoading {
                    ProgressView()
                        .progressViewStyle(CircularProgressViewStyle(tint: Theme.Colors.rose))
                        .padding(.top, 10)
                }
                
                if showError {
                    Text(errorMessage)
                        .font(Theme.Fonts.songtiRegular(size: 14))
                        .foregroundColor(.red)
                        .padding(.horizontal, 40)
                        .padding(.top, 10)
                }
                
                Spacer()
            }
            .background(Theme.Colors.background)
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button("Cancel") {
                        dismiss()
                    }
                    .foregroundColor(Theme.Colors.primaryText)
                }
            }
        }
    }
    
    private func handleLogin() {
        // 验证输入
        guard !email.isEmpty, !password.isEmpty else {
            showErrorMessage("Please enter email and password")
            return
        }
        
        isLoading = true
        showError = false
        
        Task {
            do {
                let user = try await SupabaseService.shared.signIn(email: email, password: password)
                
                await MainActor.run {
                    state.currentUser = user
                    state.isLoggedIn = true
                    isLoading = false
                    dismiss()
                }
            } catch {
                await MainActor.run {
                    isLoading = false
                    showErrorMessage(error.localizedDescription)
                }
            }
        }
    }
    
    private func showErrorMessage(_ message: String) {
        errorMessage = message
        showError = true
        
        // 3秒后自动隐藏错误信息
        DispatchQueue.main.asyncAfter(deadline: .now() + 3) {
            showError = false
        }
    }
}

#Preview {
    AuthView()
        .environmentObject(AppState())
} 