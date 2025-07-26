import Foundation
import StoreKit
import Combine

class InAppPurchaseService: NSObject, ObservableObject {
    static let shared = InAppPurchaseService()
    
    // 产品ID - 需要在App Store Connect中配置
    static let pdfGenerationProductID = "com.aiprofile.pdf_generation"
    
    @Published var products: [Product] = []
    @Published var purchasedProductIDs: Set<String> = []
    @Published var isPurchasing = false
    @Published var purchaseError: String?
    
    private var productsLoaded = false
    private var updates: Task<Void, Never>? = nil
    
    override init() {
        super.init()
        
        // 监听交易更新
        updates = newTransactionListenerTask()
        
        // 延迟产品加载，避免阻塞应用启动
        Task.detached(priority: .utility) { [weak self] in
            // 延迟5秒后加载，让应用先完成启动
            try? await Task.sleep(nanoseconds: 5_000_000_000)
            await self?.requestProducts()
            await self?.updatePurchasedProducts()
        }
    }
    
    deinit {
        updates?.cancel()
    }
    
    // MARK: - 产品获取
    func requestProducts() async {
        do {
            let storeProducts = try await Product.products(for: [InAppPurchaseService.pdfGenerationProductID])
            
            await MainActor.run {
                self.products = storeProducts
                self.productsLoaded = true
            }
            
            print("✅ 成功加载内购产品: \(storeProducts.count) 个")
            for product in storeProducts {
                print("产品: \(product.id) - \(product.displayName) - \(product.displayPrice)")
            }
        } catch {
            print("❌ 加载内购产品失败: \(error)")
            await MainActor.run {
                self.purchaseError = "无法加载产品信息"
            }
        }
    }
    
    // MARK: - 购买处理
    func purchasePDFGeneration() async -> Bool {
        guard let product = products.first(where: { $0.id == InAppPurchaseService.pdfGenerationProductID }) else {
            await MainActor.run {
                self.purchaseError = "产品不可用"
            }
            return false
        }
        
        await MainActor.run {
            self.isPurchasing = true
            self.purchaseError = nil
        }
        
        do {
            let result = try await product.purchase()
            
            switch result {
            case .success(let verificationResult):
                // 验证交易
                let transaction = try checkVerified(verificationResult)
                
                // 更新购买状态
                await updatePurchasedProducts()
                
                // 完成交易
                await transaction.finish()
                
                await MainActor.run {
                    self.isPurchasing = false
                }
                
                print("✅ 购买成功: \(transaction.productID)")
                return true
                
            case .userCancelled:
                await MainActor.run {
                    self.isPurchasing = false
                    self.purchaseError = "用户取消了购买"
                }
                print("❌ 用户取消购买")
                return false
                
            case .pending:
                await MainActor.run {
                    self.isPurchasing = false
                    self.purchaseError = "购买正在等待确认"
                }
                print("⏳ 购买等待中")
                return false
                
            @unknown default:
                await MainActor.run {
                    self.isPurchasing = false
                    self.purchaseError = "未知的购买结果"
                }
                return false
            }
        } catch {
            await MainActor.run {
                self.isPurchasing = false
                self.purchaseError = "购买失败: \(error.localizedDescription)"
            }
            print("❌ 购买失败: \(error)")
            return false
        }
    }
    
    // MARK: - 交易监听
    private func newTransactionListenerTask() -> Task<Void, Never> {
        Task.detached { [weak self] in
            for await result in Transaction.updates {
                do {
                    guard let strongSelf = self else { continue }
                    let transaction = try strongSelf.checkVerified(result)
                    await strongSelf.updatePurchasedProducts()
                    await transaction.finish()
                } catch {
                    print("❌ 交易验证失败: \(error)")
                }
            }
        }
    }
    
    // MARK: - 购买状态更新
    func updatePurchasedProducts() async {
        var updatedProductIDs = Set<String>()
        
        for await result in Transaction.currentEntitlements {
            do {
                let transaction = try checkVerified(result)
                
                switch transaction.productType {
                case .consumable:
                    // 消耗性产品，每次购买都允许使用
                    break
                case .nonConsumable:
                    // 非消耗性产品，永久拥有
                    updatedProductIDs.insert(transaction.productID)
                case .autoRenewable:
                    // 自动续费订阅
                    updatedProductIDs.insert(transaction.productID)
                case .nonRenewable:
                    // 非自动续费订阅
                    updatedProductIDs.insert(transaction.productID)
                default:
                    break
                }
            } catch {
                print("❌ 交易验证失败: \(error)")
            }
        }
        
        await MainActor.run {
            self.purchasedProductIDs = updatedProductIDs
        }
    }
    
    // MARK: - 交易验证
    func checkVerified<T>(_ result: VerificationResult<T>) throws -> T {
        switch result {
        case .unverified:
            throw StoreError.failedVerification
        case .verified(let safe):
            return safe
        }
    }
    
    // MARK: - 辅助方法
    var pdfGenerationProduct: Product? {
        return products.first { $0.id == InAppPurchaseService.pdfGenerationProductID }
    }
    
    var pdfGenerationPrice: String {
        return pdfGenerationProduct?.displayPrice ?? "$6.00"
    }
    
    // 检查用户是否有生成PDF的权限（消耗性产品每次都需要购买）
    func canGeneratePDF() -> Bool {
        // 对于消耗性产品，我们不检查历史购买，每次都需要购买
        // 这里返回false意味着总是需要购买
        return false
    }
    
    // MARK: - 恢复购买
    func restorePurchases() async {
        do {
            try await AppStore.sync()
            await updatePurchasedProducts()
        } catch {
            await MainActor.run {
                self.purchaseError = "恢复购买失败: \(error.localizedDescription)"
            }
        }
    }
}

// MARK: - 错误类型
enum StoreError: Error {
    case failedVerification
}

extension StoreError: LocalizedError {
    var errorDescription: String? {
        switch self {
        case .failedVerification:
            return "交易验证失败"
        }
    }
} 