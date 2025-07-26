import SwiftUI
import MessageUI

struct MailComposeView: UIViewControllerRepresentable {
    let recipients: [String]
    let subject: String
    let messageBody: String
    @Environment(\.dismiss) private var dismiss
    
    func makeUIViewController(context: Context) -> MFMailComposeViewController {
        let mailComposer = MFMailComposeViewController()
        mailComposer.setToRecipients(recipients)
        mailComposer.setSubject(subject)
        mailComposer.setMessageBody(messageBody, isHTML: false)
        mailComposer.mailComposeDelegate = context.coordinator
        return mailComposer
    }
    
    func updateUIViewController(_ uiViewController: MFMailComposeViewController, context: Context) {
        // 不需要更新
    }
    
    func makeCoordinator() -> Coordinator {
        Coordinator(self)
    }
    
    class Coordinator: NSObject, MFMailComposeViewControllerDelegate {
        let parent: MailComposeView
        
        init(_ parent: MailComposeView) {
            self.parent = parent
        }
        
        func mailComposeController(_ controller: MFMailComposeViewController, didFinishWith result: MFMailComposeResult, error: Error?) {
            parent.dismiss()
        }
    }
}

// 检查设备是否支持邮件功能的辅助视图
struct MailUnavailableView: View {
    @Environment(\.dismiss) private var dismiss
    
    var body: some View {
        NavigationView {
            VStack(spacing: 20) {
                Image(systemName: "mail.slash")
                    .font(.system(size: 64))
                    .foregroundColor(.secondary)
                
                Text("Mail Unavailable".localized)
                    .font(.title2)
                    .fontWeight(.semibold)
                
                Text("Mail is not configured on this device. Please set up mail in Settings or contact us at: 1765591779@qq.com".localized)
                    .multilineTextAlignment(.center)
                    .foregroundColor(.secondary)
                    .padding(.horizontal)
            }
            .navigationTitle("Contact".localized)
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button("Done".localized) {
                        dismiss()
                    }
                }
            }
        }
    }
}

// 带错误处理的邮件视图包装器
struct SafeMailComposeView: View {
    let recipients: [String]
    let subject: String
    let messageBody: String
    
    var body: some View {
        if MFMailComposeViewController.canSendMail() {
            MailComposeView(recipients: recipients, subject: subject, messageBody: messageBody)
        } else {
            MailUnavailableView()
        }
    }
} 