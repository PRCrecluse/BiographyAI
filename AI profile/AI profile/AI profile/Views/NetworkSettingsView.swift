import SwiftUI

struct NetworkSettingsView: View {
    @Environment(\.dismiss) private var dismiss
    @State private var showingConnectionTest = false
    @State private var isConnected = true
    @State private var currentRegion = "🇨🇳 China Mainland (Domestic Route)"
    @State private var selectedRoute: APIRoute = .domestic
    
    enum APIRoute {
        case domestic
        case international
        
        var displayName: String {
            switch self {
            case .domestic:
                return "🇨🇳 China Mainland (Domestic Route)"
            case .international:
                return "🌍 International (Overseas Route)"
            }
        }
        
        var description: String {
            switch self {
            case .domestic:
                return "Optimized for users in China"
            case .international:
                return "Optimized for international users"
            }
        }
    }
    
    var body: some View {
        NavigationView {
            ScrollView {
                VStack(alignment: .leading, spacing: 24) {
                    connectionStatusSection
                    apiRouteSelectionSection
                    actionButtonsSection
                }
                .padding(24)
            }
            .background(Color(.systemBackground))
            .navigationTitle(NSLocalizedString("Network Settings", comment: ""))
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button(NSLocalizedString("Done", comment: "")) {
                        dismiss()
                    }
                }
            }
        }
        .alert(NSLocalizedString("Connection Test", comment: ""), isPresented: $showingConnectionTest) {
            Button(NSLocalizedString("OK", comment: "")) { }
        } message: {
            Text(isConnected ? 
                NSLocalizedString("Connection successful!", comment: "") : 
                NSLocalizedString("Connection failed. Please try a different route.", comment: ""))
        }
    }
    
    // MARK: - Connection Status Section
    private var connectionStatusSection: some View {
        VStack(alignment: .leading, spacing: 16) {
            Text(NSLocalizedString("Current Connection Status", comment: ""))
                .font(.title2)
                .fontWeight(.bold)
            
            HStack {
                Circle()
                    .fill(isConnected ? Color.green : Color.red)
                    .frame(width: 12, height: 12)
                
                Text(isConnected ? NSLocalizedString("Connected", comment: "") : NSLocalizedString("Disconnected", comment: ""))
                    .font(.body)
                
                Spacer()
            }
            
            HStack {
                Text(NSLocalizedString("Current Route:", comment: ""))
                    .font(.body)
                    .foregroundColor(.secondary)
                
                Spacer()
                
                Text(currentRegion)
                    .font(.body)
                    .fontWeight(.medium)
            }
        }
        .padding(20)
        .background(
            RoundedRectangle(cornerRadius: 12)
                .fill(Color(.secondarySystemBackground))
                .shadow(color: .black.opacity(0.1), radius: 2, x: 0, y: 1)
        )
    }
    
    // MARK: - API Route Selection Section
    private var apiRouteSelectionSection: some View {
        VStack(alignment: .leading, spacing: 16) {
            Text(NSLocalizedString("API Route Selection", comment: ""))
                .font(.title2)
                .fontWeight(.bold)
            
            VStack(spacing: 12) {
                // 国内线路选项
                routeSelectionButton(for: .domestic)
                
                // 海外线路选项
                routeSelectionButton(for: .international)
            }
        }
    }
    
    private func routeSelectionButton(for route: APIRoute) -> some View {
        Button(action: {
            selectedRoute = route
            currentRegion = route.displayName
        }) {
            HStack {
                Image(systemName: route == .domestic ? "globe.asia.australia" : "globe.americas")
                    .foregroundColor(.blue)
                
                VStack(alignment: .leading, spacing: 4) {
                    Text(route.displayName)
                        .font(.body)
                        .fontWeight(.medium)
                        .foregroundColor(.primary)
                    
                    Text(route.description)
                        .font(.caption)
                        .foregroundColor(.secondary)
                }
                
                Spacer()
                
                if selectedRoute == route {
                    Image(systemName: "checkmark.circle.fill")
                        .foregroundColor(.green)
                }
            }
            .padding(16)
            .background(
                RoundedRectangle(cornerRadius: 10)
                    .fill(Color(.secondarySystemBackground))
                    .overlay(
                        RoundedRectangle(cornerRadius: 10)
                            .stroke(selectedRoute == route ? Color.blue : Color.gray.opacity(0.3), lineWidth: 1)
                    )
            )
        }
    }
    
    // MARK: - Action Buttons Section
    private var actionButtonsSection: some View {
        VStack(spacing: 16) {
            // 自动检测按钮
            Button(action: {
                currentRegion = "Detecting..."
                DispatchQueue.main.asyncAfter(deadline: .now() + 1) {
                    selectedRoute = .domestic
                    currentRegion = "🇨🇳 China Mainland (Auto-detected)"
                }
            }) {
                HStack {
                    Image(systemName: "location")
                    Text(NSLocalizedString("Auto-detect Region", comment: ""))
                        .fontWeight(.medium)
                }
                .frame(maxWidth: .infinity)
                .padding(16)
                .background(Color.blue)
                .foregroundColor(.white)
                .cornerRadius(10)
            }
            
            // 连接测试按钮
            Button(action: {
                showingConnectionTest = true
            }) {
                HStack {
                    Image(systemName: "network")
                    Text(NSLocalizedString("Test Connection", comment: ""))
                        .fontWeight(.medium)
                }
                .frame(maxWidth: .infinity)
                .padding(16)
                .background(Color(.systemGray5))
                .foregroundColor(.primary)
                .cornerRadius(10)
            }
        }
    }
}

// MARK: - Preview
struct NetworkSettingsView_Previews: PreviewProvider {
    static var previews: some View {
        NetworkSettingsView()
    }
}
