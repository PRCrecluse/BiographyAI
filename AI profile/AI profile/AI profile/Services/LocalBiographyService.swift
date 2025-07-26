import Foundation
import UIKit
import PDFKit

// MARK: - 本地传记生成服务 (备用方案)
class LocalBiographyService: ObservableObject {
    static let shared = LocalBiographyService()
    
    @Published var isGenerating = false
    @Published var progress: Double = 0.0
    @Published var errorMessage: String?
    
    private init() {}
    
    // MARK: - 主要生成方法
    func generateBiography(
        from images: [UIImage],
        userRequirements: String,
        language: String = "zh-CN"
    ) async -> Result<URL, LocalBiographyError> {
        
        await MainActor.run {
            self.isGenerating = true
            self.progress = 0.0
            self.errorMessage = nil
        }
        
        do {
            // 步骤1: 分析图片 (20%)
            await updateProgress(0.2, message: "正在分析图片...")
            let imageAnalyses = analyzeImages(images)
            
            // 步骤2: 生成传记内容 (60%)
            await updateProgress(0.6, message: "正在生成传记内容...")
            let biographyContent = generateBiographyContent(
                imageAnalyses: imageAnalyses,
                userRequirements: userRequirements,
                language: language
            )
            
            // 步骤3: 创建PDF (90%)
            await updateProgress(0.9, message: "正在生成PDF...")
            let pdfURL = try createPDF(content: biographyContent, images: images)
            
            // 步骤4: 生成缩略图 (93%)
            await updateProgress(0.93, message: "正在生成缩略图...")
            let thumbnailImage = generateThumbnail(for: images.first, title: "本地生成传记")
            
            // 步骤5: 保存Biography对象 (95%)
            await updateProgress(0.95, message: "正在保存传记...")
            let biographyId = "local_\(Int(Date().timeIntervalSince1970))"
            
            // 保存缩略图
            var thumbnailPath: String? = nil
            if let thumbnail = thumbnailImage {
                do {
                    let thumbnailFileName = "\(biographyId)_thumbnail.png"
                    let documentsPath = FileManager.default.urls(for: .documentDirectory, in: .userDomainMask)[0]
                    let biographiesDir = documentsPath.appendingPathComponent("Biographies")
                    try FileManager.default.createDirectory(at: biographiesDir, withIntermediateDirectories: true)
                    let thumbnailURL = biographiesDir.appendingPathComponent(thumbnailFileName)
                    
                    if let thumbnailData = thumbnail.pngData() {
                        try thumbnailData.write(to: thumbnailURL)
                        thumbnailPath = thumbnailURL.path
                        print("✅ 缩略图已保存: \(thumbnailURL.path)")
                    }
                } catch {
                    print("❌ 保存缩略图失败: \(error)")
                }
            }
            
            let biography = Biography(
                id: biographyId,
                title: "本地生成传记",
                content: biographyContent,
                pdfPath: pdfURL.path,
                thumbnailPath: thumbnailPath,
                createdAt: Date(),
                updatedAt: Date()
            )
            
            // 保存到LocalStorageManager
            do {
                try LocalStorageManager.shared.saveBiography(biography)
                print("✅ 传记已保存到本地存储管理器，可在Assets页面查看")
            } catch {
                print("❌ 保存传记到存储管理器失败: \(error)")
                // 不抛出错误，因为PDF已经生成成功
            }
            
            // 完成 (100%)
            await updateProgress(1.0, message: "传记生成完成")
            
            await MainActor.run {
                self.isGenerating = false
            }
            
            return .success(pdfURL)
            
        } catch {
            await MainActor.run {
                self.isGenerating = false
                self.errorMessage = error.localizedDescription
            }
            return .failure(.generationFailed(error.localizedDescription))
        }
    }
    
    // MARK: - 图片分析 (本地实现)
    private func analyzeImages(_ images: [UIImage]) -> [String] {
        var analyses: [String] = []
        
        for (index, image) in images.enumerated() {
            let analysis = generateImageAnalysis(image: image, index: index)
            analyses.append(analysis)
        }
        
        return analyses
    }
    
    private func generateImageAnalysis(image: UIImage, index: Int) -> String {
        let size = image.size
        let isPortrait = size.height > size.width
        
        var analysis = "图片\(index + 1): "
        
        if isPortrait {
            analysis += "这是一张竖向照片"
        } else {
            analysis += "这是一张横向照片"
        }
        
        switch index {
        case 0:
            analysis += "。这可能是一张重要的纪念照片，记录了人生中的特殊时刻。"
        case 1:
            analysis += "。这张照片展现了日常生活的一个侧面，反映了个人的生活方式。"
        default:
            analysis += "。这张照片为个人传记增添了丰富的视觉元素。"
        }
        
        return analysis
    }
    
    // MARK: - 传记内容生成
    private func generateBiographyContent(
        imageAnalyses: [String],
        userRequirements: String,
        language: String
    ) -> String {
        
        switch language {
        case "zh-CN":
            return generateChineseBiography(imageAnalyses: imageAnalyses, userRequirements: userRequirements)
        case "en":
            return generateEnglishBiography(imageAnalyses: imageAnalyses, userRequirements: userRequirements)
        default:
            return generateChineseBiography(imageAnalyses: imageAnalyses, userRequirements: userRequirements)
        }
    }
    
    private func generateChineseBiography(imageAnalyses: [String], userRequirements: String) -> String {
        var biography = """
        个人传记
        
        根据您的要求："\(userRequirements)"，我们为您创建了这份个人传记。
        
        """
        
        // 为每张图片生成对应的人生片段
        for (index, imageAnalysis) in imageAnalyses.enumerated() {
            let segment = generateLifeSegmentFromImage(imageAnalysis: imageAnalysis, index: index, totalImages: imageAnalyses.count, userRequirements: userRequirements)
            biography += segment
            
            // 在片段之间添加适当的连接
            if index < imageAnalyses.count - 1 {
                biography += "\n\n"
            }
        }
        
        // 添加结语，将所有片段串联起来
        biography += "\n\n" + generateConnectingConclusion(imageCount: imageAnalyses.count)
        
        // 添加生成信息
        biography += "\n\n---\n"
        biography += "生成时间：\(DateFormatter.localizedString(from: Date(), dateStyle: .full, timeStyle: .short))\n"
        
        return biography
    }
    
    // MARK: - 基于图片的人生片段生成
    private func generateLifeSegmentFromImage(imageAnalysis: String, index: Int, totalImages: Int, userRequirements: String) -> String {
        // 根据图片分析内容生成对应的人生片段
        let timePhrase = generateTimePhrase(for: index, total: totalImages)
        let storySegment = generateStoryFromImageAnalysis(imageAnalysis, userRequirements: userRequirements)
        let connection = generateConnectionPhrase(for: index, total: totalImages)
        
        return """
        \(timePhrase)
        
        \(storySegment)
        
        \(connection)
        """
    }
    
    private func generateTimePhrase(for index: Int, total: Int) -> String {
        let phrases = [
            "在人生的早期阶段",
            "随着时间的推移",
            "在成长的过程中",
            "人生的中期阶段",
            "在这个重要的时期",
            "随着阅历的丰富",
            "在人生的这个阶段",
            "时光流转到了这个时期"
        ]
        
        if index < phrases.count {
            return phrases[index]
        } else {
            return "在人生的这个珍贵时刻"
        }
    }
    
    private func generateStoryFromImageAnalysis(_ analysis: String, userRequirements: String) -> String {
        // 根据图片分析内容生成故事
        let analysisLower = analysis.lowercased()
        let requirementsLower = userRequirements.lowercased()
        
        var story = analysis // 以图片分析为基础
        
        // 根据分析内容添加情感和背景
        if analysisLower.contains("学习") || analysisLower.contains("书") || analysisLower.contains("study") {
            story += "这个时期的学习经历不仅仅是知识的积累，更是个人成长的重要基石。每一次的学习都在塑造着未来的自己，为人生的下一个阶段做着准备。"
        } else if analysisLower.contains("工作") || analysisLower.contains("职业") || analysisLower.contains("work") {
            story += "在职业生涯中，这个阶段展现了专业的成长和个人的坚持。每一个挑战都是成长的机会，每一个成就都是努力的回报。"
        } else if analysisLower.contains("家庭") || analysisLower.contains("家人") || analysisLower.contains("family") {
            story += "家庭是人生中最温暖的港湾，这些珍贵的时光记录了亲情的温暖和家的意义。在这里，找到了内心的安宁和生活的真谛。"
        } else if analysisLower.contains("旅行") || analysisLower.contains("风景") || analysisLower.contains("travel") {
            story += "旅行不仅仅是对外界的探索，更是对内心的发现。每一次的出行都带来新的视野和体验，丰富了人生的阅历和内涵。"
        } else if analysisLower.contains("朋友") || analysisLower.contains("聚会") || analysisLower.contains("friend") {
            story += "友谊是人生路上的珍贵财富，这些共同的回忆见证了成长的足迹和友情的深厚。在朋友的陪伴下，人生变得更加丰富多彩。"
        } else {
            // 默认情况，添加通用的情感描述
            story += "这个时刻承载着特殊的意义，记录了人生中一个重要的片段。每一个细节都值得珍藏，每一个瞬间都在讲述着独特的故事。"
        }
        
        return story
    }
    
    private func generateConnectionPhrase(for index: Int, total: Int) -> String {
        if index == total - 1 {
            // 最后一张图片，不需要连接词
            return ""
        }
        
        let connections = [
            "这段经历为后续的人生道路奠定了基础。",
            "随着时间的推移，人生迎来了新的篇章。",
            "这些珍贵的回忆成为了继续前行的动力。",
            "人生的旅程继续向前，带来了新的机遇和挑战。",
            "在这个基础上，人生迎来了更加精彩的阶段。",
            "这些经历成为了人生智慧的源泉。",
            "带着这些美好的回忆，人生的故事继续展开。"
        ]
        
        if index < connections.count {
            return connections[index]
        } else {
            return "这段经历成为了人生中不可缺少的一部分。"
        }
    }
    
    private func generateConnectingConclusion(imageCount: Int) -> String {
        return """
        结语
        
        这\(imageCount)个珍贵的人生片段，如同一幅幅精美的画卷，共同织成了一个完整而独特的人生故事。每一个阶段都有其独特的价值和意义，每一个瞬间都值得被永远珍藏。
        
        从这些图像中，我们看到了一个人的成长轨迹，感受到了生活的丰富多彩。这些真实的经历和真挚的情感，构成了一个有血有肉、有笑有泪的人生故事。
        
        愿这份传记能够成为珍贵的纪念，记录下这些美好的时光，也为未来的日子提供温暖的回忆和前进的动力。
        """
    }
    
    // MARK: - 用户需求解析（保留作为辅助功能）
    private func parseUserRequirements(_ requirements: String) -> [String: String] {
        var parsedInfo: [String: String] = [:]
        
        // 提取关键词和主题
        let lowercased = requirements.lowercased()
        
        // 检测职业相关信息
        if lowercased.contains("工程师") || lowercased.contains("engineer") {
            parsedInfo["profession"] = "工程师"
        } else if lowercased.contains("医生") || lowercased.contains("doctor") {
            parsedInfo["profession"] = "医生"
        } else if lowercased.contains("教师") || lowercased.contains("teacher") {
            parsedInfo["profession"] = "教师"
        } else if lowercased.contains("艺术家") || lowercased.contains("artist") {
            parsedInfo["profession"] = "艺术家"
        }
        
        // 检测兴趣爱好
        if lowercased.contains("旅行") || lowercased.contains("travel") {
            parsedInfo["hobby"] = "旅行"
        } else if lowercased.contains("音乐") || lowercased.contains("music") {
            parsedInfo["hobby"] = "音乐"
        } else if lowercased.contains("运动") || lowercased.contains("sport") {
            parsedInfo["hobby"] = "运动"
        } else if lowercased.contains("阅读") || lowercased.contains("reading") {
            parsedInfo["hobby"] = "阅读"
        }
        
        // 检测性格特征
        if lowercased.contains("开朗") || lowercased.contains("cheerful") {
            parsedInfo["personality"] = "开朗"
        } else if lowercased.contains("内向") || lowercased.contains("introverted") {
            parsedInfo["personality"] = "内向"
        } else if lowercased.contains("乐观") || lowercased.contains("optimistic") {
            parsedInfo["personality"] = "乐观"
        }
        
        // 保存原始需求
        parsedInfo["original"] = requirements
        
        return parsedInfo
    }
    
    // MARK: - 传记章节生成函数
    private func generateOpeningSection(parsedInfo: [String: String], userRequirements: String) -> String {
        let profession = parsedInfo["profession"] ?? "独特的个体"
        return """
        根据您的要求："\(userRequirements)"，我们为您创建了这份个人传记。
        
        每个人的人生都是一部独特的传记，充满了珍贵的回忆、重要的时刻和深刻的经历。作为一名\(profession)，这个人的人生轨迹展现了独特的魅力和价值。
        """
    }
    
    private func generateEarlyLifeSection(imageAnalyses: [String], parsedInfo: [String: String]) -> String {
        let firstImage = imageAnalyses.first ?? "一张珍贵的照片记录了早年的时光"
        return """
        \(firstImage)
        
        这些早年的记忆如同珍贵的宝石，闪烁着纯真和希望的光芒。每一个瞬间都在塑造着独特的个性，为未来的人生道路奠定了坚实的基础。
        """
    }
    
    private func generateGrowthSection(parsedInfo: [String: String], imageAnalyses: [String]) -> String {
        let profession = parsedInfo["profession"] ?? "自己的道路"
        let hobby = parsedInfo["hobby"] ?? "各种兴趣爱好"
        
        var section = "在成长的过程中，逐渐发现了对\(profession)的热爱，同时也培养了对\(hobby)的浓厚兴趣。"
        
        if imageAnalyses.count > 1 {
            section += "\n\n" + imageAnalyses[1]
        }
        
        section += "\n\n这个阶段的经历塑造了坚韧的性格和积极的人生态度，为后续的人生发展积累了宝贵的经验。"
        
        return section
    }
    
    private func generateImportantMomentsSection(imageAnalyses: [String], parsedInfo: [String: String]) -> String {
        var section = "人生中总有一些时刻格外珍贵，它们如同明亮的星星，照亮了前进的道路。\n\n"
        
        // 使用剩余的图片分析
        for (index, analysis) in imageAnalyses.dropFirst(2).enumerated() {
            section += "\(analysis)\n\n"
            if index < imageAnalyses.count - 3 {
                section += "这个时刻标志着人生的一个重要转折点，带来了新的机遇和挑战。\n\n"
            }
        }
        
        return section
    }
    
    private func generatePersonalitySection(parsedInfo: [String: String]) -> String {
        let personality = parsedInfo["personality"] ?? "独特"
        let profession = parsedInfo["profession"] ?? "工作"
        
        return """
        作为一个\(personality)的人，在\(profession)领域展现出了独特的才华和坚持不懈的精神。这种性格特质不仅在工作中发挥了重要作用，也在人际关系和生活的各个方面都产生了积极的影响。
        
        正是这些个人特质，让这个人在面对挑战时能够保持冷静，在机遇面前能够果断行动，在困难时期能够坚持不懈。
        """
    }
    
    private func generateReflectionSection(parsedInfo: [String: String]) -> String {
        let hobby = parsedInfo["hobby"] ?? "生活的美好"
        
        return """
        回顾人生的历程，每一个阶段都有其独特的价值和意义。从早年的懵懂青涩，到现在的成熟稳重，这个过程充满了学习、成长和自我发现。
        
        通过\(hobby)，找到了生活的平衡和内心的宁静。这些经历教会了如何欣赏生活中的美好，如何在忙碌中保持内心的平静，如何在挑战中找到成长的机会。
        """
    }
    
    private func generateConclusionSection(parsedInfo: [String: String]) -> String {
        return """
        人生如画，每个瞬间都值得珍藏。这份传记通过图像和文字，记录了一段珍贵的人生历程。每一张照片都承载着特殊的意义，每一个故事都诉说着独特的经历。
        
        未来的道路还很长，但有了这些珍贵的回忆作为基础，相信前方的路会更加精彩。愿这份传记能够成为人生路上的一盏明灯，照亮前进的方向，也成为后人了解这段美好人生的珍贵资料。
        """
    }
    
    // MARK: - English Biography Generation Functions
    private func parseUserRequirementsEnglish(_ requirements: String) -> [String: String] {
        var parsedInfo: [String: String] = [:]
        
        let lowercased = requirements.lowercased()
        
        // Detect profession
        if lowercased.contains("engineer") {
            parsedInfo["profession"] = "engineer"
        } else if lowercased.contains("doctor") {
            parsedInfo["profession"] = "doctor"
        } else if lowercased.contains("teacher") {
            parsedInfo["profession"] = "teacher"
        } else if lowercased.contains("artist") {
            parsedInfo["profession"] = "artist"
        }
        
        // Detect hobbies
        if lowercased.contains("travel") {
            parsedInfo["hobby"] = "travel"
        } else if lowercased.contains("music") {
            parsedInfo["hobby"] = "music"
        } else if lowercased.contains("sport") {
            parsedInfo["hobby"] = "sports"
        } else if lowercased.contains("reading") {
            parsedInfo["hobby"] = "reading"
        }
        
        // Detect personality
        if lowercased.contains("cheerful") {
            parsedInfo["personality"] = "cheerful"
        } else if lowercased.contains("introverted") {
            parsedInfo["personality"] = "introverted"
        } else if lowercased.contains("optimistic") {
            parsedInfo["personality"] = "optimistic"
        }
        
        parsedInfo["original"] = requirements
        return parsedInfo
    }
    
    private func generateOpeningSectionEnglish(parsedInfo: [String: String], userRequirements: String) -> String {
        let profession = parsedInfo["profession"] ?? "unique individual"
        return """
        This biography has been created based on your requirements: "\(userRequirements)"
        
        Every person's life is a unique story filled with precious memories, important moments, and meaningful experiences. As a \(profession), this person's life journey showcases distinctive charm and value.
        """
    }
    
    private func generateEarlyLifeSectionEnglish(imageAnalyses: [String], parsedInfo: [String: String]) -> String {
        let firstImage = imageAnalyses.first ?? "A precious photo captures the early years"
        return """
        \(firstImage)
        
        These early memories shine like precious gems, radiating innocence and hope. Each moment helped shape a unique personality, laying a solid foundation for the future life path.
        """
    }
    
    private func generateGrowthSectionEnglish(parsedInfo: [String: String], imageAnalyses: [String]) -> String {
        let profession = parsedInfo["profession"] ?? "chosen path"
        let hobby = parsedInfo["hobby"] ?? "various interests"
        
        var section = "During the growth process, gradually discovered a passion for \(profession), while also developing a strong interest in \(hobby)."
        
        if imageAnalyses.count > 1 {
            section += "\n\n" + imageAnalyses[1]
        }
        
        section += "\n\nThis stage of experience shaped a resilient character and positive life attitude, accumulating valuable experience for future life development."
        
        return section
    }
    
    private func generateImportantMomentsSectionEnglish(imageAnalyses: [String], parsedInfo: [String: String]) -> String {
        var section = "There are always some moments in life that are particularly precious, like bright stars illuminating the path forward.\n\n"
        
        for (index, analysis) in imageAnalyses.dropFirst(2).enumerated() {
            section += "\(analysis)\n\n"
            if index < imageAnalyses.count - 3 {
                section += "This moment marked an important turning point in life, bringing new opportunities and challenges.\n\n"
            }
        }
        
        return section
    }
    
    private func generatePersonalitySectionEnglish(parsedInfo: [String: String]) -> String {
        let personality = parsedInfo["personality"] ?? "unique"
        let profession = parsedInfo["profession"] ?? "work"
        
        return """
        As a \(personality) person, demonstrated unique talent and persistent spirit in the \(profession) field. These personality traits not only played an important role in work, but also had a positive impact on interpersonal relationships and all aspects of life.
        
        It is these personal qualities that enable this person to remain calm when facing challenges, act decisively when opportunities arise, and persevere during difficult times.
        """
    }
    
    private func generateReflectionSectionEnglish(parsedInfo: [String: String]) -> String {
        let hobby = parsedInfo["hobby"] ?? "life's beauty"
        
        return """
        Looking back on life's journey, each stage has its unique value and meaning. From the naive youth of early years to the mature stability of now, this process is filled with learning, growth, and self-discovery.
        
        Through \(hobby), found life's balance and inner peace. These experiences taught how to appreciate life's beauty, how to maintain inner calm in busyness, and how to find growth opportunities in challenges.
        """
    }
    
    private func generateConclusionSectionEnglish(parsedInfo: [String: String]) -> String {
        return """
        Life is like a painting, every moment is worth treasuring. This biography records a precious life journey through images and words. Each photo carries special meaning, and each story tells a unique experience.
        
        The road ahead is still long, but with these precious memories as a foundation, the path forward will surely be more exciting. May this biography serve as a beacon on life's journey, illuminating the way forward and becoming valuable material for future generations to understand this beautiful life.
        """
    }
    
    private func generateEnglishBiography(imageAnalyses: [String], userRequirements: String) -> String {
        var biography = """
        Personal Biography
        
        This biography has been created based on your requirements: "\(userRequirements)"
        
        """
        
        // Generate a life segment for each image
        for (index, imageAnalysis) in imageAnalyses.enumerated() {
            let segment = generateLifeSegmentFromImageEnglish(imageAnalysis: imageAnalysis, index: index, totalImages: imageAnalyses.count, userRequirements: userRequirements)
            biography += segment
            
            // Add appropriate connections between segments
            if index < imageAnalyses.count - 1 {
                biography += "\n\n"
            }
        }
        
        // Add conclusion that connects all segments
        biography += "\n\n" + generateConnectingConclusionEnglish(imageCount: imageAnalyses.count)
        
        // Add generation info
        biography += "\n\n---\n"
        biography += "Generated on: \(DateFormatter.localizedString(from: Date(), dateStyle: .full, timeStyle: .short))\n"
        
        return biography
    }
    
    // MARK: - English Image-Based Life Segment Generation
    private func generateLifeSegmentFromImageEnglish(imageAnalysis: String, index: Int, totalImages: Int, userRequirements: String) -> String {
        // Generate corresponding life segment based on image analysis content
        let timePhrase = generateTimePhraseEnglish(for: index, total: totalImages)
        let storySegment = generateStoryFromImageAnalysisEnglish(imageAnalysis, userRequirements: userRequirements)
        let connection = generateConnectionPhraseEnglish(for: index, total: totalImages)
        
        return """
        \(timePhrase)
        
        \(storySegment)
        
        \(connection)
        """
    }
    
    private func generateTimePhraseEnglish(for index: Int, total: Int) -> String {
        let phrases = [
            "In the early stages of life",
            "As time progressed",
            "During the growth process",
            "In the middle period of life",
            "During this important time",
            "With enriched experiences",
            "At this stage of life",
            "As time flowed to this period"
        ]
        
        if index < phrases.count {
            return phrases[index]
        } else {
            return "At this precious moment in life"
        }
    }
    
    private func generateStoryFromImageAnalysisEnglish(_ analysis: String, userRequirements: String) -> String {
        // Generate story based on image analysis content
        let analysisLower = analysis.lowercased()
        let requirementsLower = userRequirements.lowercased()
        
        var story = analysis // Base on image analysis
        
        // Add emotion and background based on analysis content
        if analysisLower.contains("study") || analysisLower.contains("book") || analysisLower.contains("learning") {
            story += " This period of learning experience was not just about accumulating knowledge, but also an important cornerstone of personal growth. Each learning experience was shaping the future self, preparing for the next stage of life."
        } else if analysisLower.contains("work") || analysisLower.contains("career") || analysisLower.contains("job") {
            story += " In the professional career, this stage demonstrated professional growth and personal persistence. Every challenge was an opportunity for growth, and every achievement was a reward for hard work."
        } else if analysisLower.contains("family") || analysisLower.contains("home") || analysisLower.contains("relatives") {
            story += " Family is the warmest harbor in life, and these precious moments recorded the warmth of kinship and the meaning of home. Here, inner peace and the true meaning of life were found."
        } else if analysisLower.contains("travel") || analysisLower.contains("scenery") || analysisLower.contains("journey") {
            story += " Travel is not just exploration of the outside world, but also discovery of the inner self. Each journey brought new perspectives and experiences, enriching life's experiences and depth."
        } else if analysisLower.contains("friend") || analysisLower.contains("gathering") || analysisLower.contains("social") {
            story += " Friendship is precious wealth on life's journey, and these shared memories witnessed the footprints of growth and the depth of friendship. With friends' companionship, life became more colorful and rich."
        } else {
            // Default case, add general emotional description
            story += " This moment carried special meaning, recording an important segment of life. Every detail was worth treasuring, and every instant was telling a unique story."
        }
        
        return story
    }
    
    private func generateConnectionPhraseEnglish(for index: Int, total: Int) -> String {
        if index == total - 1 {
            // Last image, no connection needed
            return ""
        }
        
        let connections = [
            "This experience laid the foundation for the subsequent life path.",
            "As time progressed, life welcomed a new chapter.",
            "These precious memories became the motivation to continue forward.",
            "Life's journey continued ahead, bringing new opportunities and challenges.",
            "On this foundation, life welcomed an even more exciting stage.",
            "These experiences became the source of life's wisdom.",
            "Carrying these beautiful memories, life's story continued to unfold."
        ]
        
        if index < connections.count {
            return connections[index]
        } else {
            return "This experience became an indispensable part of life."
        }
    }
    
    private func generateConnectingConclusionEnglish(imageCount: Int) -> String {
        return """
        Conclusion
        
        These \(imageCount) precious life segments, like exquisite paintings, together weave a complete and unique life story. Each stage has its unique value and meaning, and every moment deserves to be treasured forever.
        
        From these images, we see a person's growth trajectory and feel the richness and diversity of life. These real experiences and sincere emotions constitute a life story full of flesh and blood, laughter and tears.
        
        May this biography serve as a precious memorial, recording these beautiful times, and also providing warm memories and motivation for future days.
        """
    }
    
    // MARK: - PDF生成
    private func createPDF(content: String, images: [UIImage]) throws -> URL {
        let pageRect = CGRect(x: 0, y: 0, width: 595, height: 842) // A4 size
        let renderer = UIGraphicsPDFRenderer(bounds: pageRect)
        
        let pdfData = renderer.pdfData { context in
            // 第一页：封面页
            context.beginPage()
            drawCoverPage(in: pageRect, images: images)
            
            // 第二页及后续页：传记内容
            context.beginPage()
            drawBiographyContent(in: pageRect, content: content, images: images)
        }
        
        // 保存PDF文件
        let fileName = "biography_local_\(Int(Date().timeIntervalSince1970)).pdf"
        let documentsPath = FileManager.default.urls(for: .documentDirectory, in: .userDomainMask)[0]
        let pdfURL = documentsPath.appendingPathComponent(fileName)
        
        try pdfData.write(to: pdfURL)
        return pdfURL
    }
    
    // MARK: - 封面页绘制
    private func drawCoverPage(in rect: CGRect, images: [UIImage]) {
        // 设置封面背景色（淡蓝色渐变效果）
        let context = UIGraphicsGetCurrentContext()!
        let colors = [UIColor(red: 0.7, green: 0.85, blue: 1.0, alpha: 1.0).cgColor,
                     UIColor(red: 0.5, green: 0.7, blue: 0.9, alpha: 1.0).cgColor]
        let colorSpace = CGColorSpaceCreateDeviceRGB()
        let gradient = CGGradient(colorsSpace: colorSpace, colors: colors as CFArray, locations: nil)!
        
        context.drawLinearGradient(gradient, start: CGPoint(x: 0, y: 0), end: CGPoint(x: 0, y: rect.height), options: [])
        
        // 绘制标题
        let titleFont = UIFont.boldSystemFont(ofSize: 28)
        let title = "个人传记 Personal Biography"
        let titleAttributes: [NSAttributedString.Key: Any] = [
            .font: titleFont,
            .foregroundColor: UIColor.white
        ]
        
        let titleSize = title.size(withAttributes: titleAttributes)
        let titleRect = CGRect(x: (rect.width - titleSize.width) / 2, y: 150, width: titleSize.width, height: titleSize.height)
        title.draw(in: titleRect, withAttributes: titleAttributes)
        
        // 绘制主图片（如果有的话）
        if let mainImage = images.first {
            let imageSize: CGFloat = 200
            let imageRect = CGRect(x: (rect.width - imageSize) / 2, y: 250, width: imageSize, height: imageSize)
            
            // 绘制图片阴影
            context.setShadow(offset: CGSize(width: 2, height: 2), blur: 5, color: UIColor.black.withAlphaComponent(0.3).cgColor)
            
            // 绘制圆角图片
            let path = UIBezierPath(roundedRect: imageRect, cornerRadius: 10)
            path.addClip()
            mainImage.draw(in: imageRect)
        }
        
        // 绘制副标题
        let subtitleFont = UIFont.systemFont(ofSize: 16)
        let subtitle = "我的人生旅程 A Journey Through Life"
        let subtitleAttributes: [NSAttributedString.Key: Any] = [
            .font: subtitleFont,
            .foregroundColor: UIColor.white.withAlphaComponent(0.9)
        ]
        
        let subtitleSize = subtitle.size(withAttributes: subtitleAttributes)
        let subtitleRect = CGRect(x: (rect.width - subtitleSize.width) / 2, y: 500, width: subtitleSize.width, height: subtitleSize.height)
        subtitle.draw(in: subtitleRect, withAttributes: subtitleAttributes)
        
        // 绘制日期
        let dateFont = UIFont.systemFont(ofSize: 14)
        let dateFormatter = DateFormatter()
        dateFormatter.dateStyle = .long
        let dateString = dateFormatter.string(from: Date())
        let dateAttributes: [NSAttributedString.Key: Any] = [
            .font: dateFont,
            .foregroundColor: UIColor.white.withAlphaComponent(0.8)
        ]
        
        let dateSize = dateString.size(withAttributes: dateAttributes)
        let dateRect = CGRect(x: (rect.width - dateSize.width) / 2, y: 600, width: dateSize.width, height: dateSize.height)
        dateString.draw(in: dateRect, withAttributes: dateAttributes)
    }
    
    // MARK: - 传记内容绘制
    private func drawBiographyContent(in rect: CGRect, content: String, images: [UIImage]) {
        let titleFont = UIFont.boldSystemFont(ofSize: 24)
        let bodyFont = UIFont.systemFont(ofSize: 12)
        
        var yPosition: CGFloat = 50
        
        // 绘制标题
        let title = "个人传记"
        let titleAttributes: [NSAttributedString.Key: Any] = [
            .font: titleFont,
            .foregroundColor: UIColor.black
        ]
        
        let titleSize = title.size(withAttributes: titleAttributes)
        let titleRect = CGRect(x: (rect.width - titleSize.width) / 2, y: yPosition, width: titleSize.width, height: titleSize.height)
        title.draw(in: titleRect, withAttributes: titleAttributes)
        yPosition += titleSize.height + 30
        
        // 绘制第一张图片
        if let firstImage = images.first {
            let imageSize: CGFloat = 200
            let imageRect = CGRect(x: (rect.width - imageSize) / 2, y: yPosition, width: imageSize, height: imageSize)
            firstImage.draw(in: imageRect)
            yPosition += imageSize + 20
        }
        
        // 绘制内容
        let contentAttributes: [NSAttributedString.Key: Any] = [
            .font: bodyFont,
            .foregroundColor: UIColor.black
        ]
        
        let contentRect = CGRect(x: 50, y: yPosition, width: rect.width - 100, height: rect.height - yPosition - 50)
        content.draw(in: contentRect, withAttributes: contentAttributes)
    }
    
    private func updateProgress(_ progress: Double, message: String) async {
        await MainActor.run {
            self.progress = progress
        }
        try? await Task.sleep(nanoseconds: 200_000_000)
    }
    
    // MARK: - 缩略图生成
    private func generateThumbnail(for image: UIImage?, title: String) -> UIImage? {
        let thumbnailSize = CGSize(width: 300, height: 400)
        let renderer = UIGraphicsImageRenderer(size: thumbnailSize)
        
        return renderer.image { context in
            // 背景色
            UIColor.systemBackground.setFill()
            context.fill(CGRect(origin: .zero, size: thumbnailSize))
            
            // 如果有图片，绘制图片
            if let image = image {
                let imageRect = CGRect(x: 20, y: 20, width: thumbnailSize.width - 40, height: 200)
                image.draw(in: imageRect)
            }
            
            // 绘制标题
            let titleFont = UIFont.boldSystemFont(ofSize: 16)
            let titleAttributes: [NSAttributedString.Key: Any] = [
                .font: titleFont,
                .foregroundColor: UIColor.label
            ]
            
            let titleRect = CGRect(x: 20, y: thumbnailSize.height - 100, width: thumbnailSize.width - 40, height: 80)
            title.draw(in: titleRect, withAttributes: titleAttributes)
            
            // 绘制本地标识
            let localBadgeFont = UIFont.systemFont(ofSize: 12)
            let localBadgeAttributes: [NSAttributedString.Key: Any] = [
                .font: localBadgeFont,
                .foregroundColor: UIColor.systemBlue
            ]
            
            let localBadge = "本地生成"
            let badgeRect = CGRect(x: 20, y: thumbnailSize.height - 30, width: thumbnailSize.width - 40, height: 20)
            localBadge.draw(in: badgeRect, withAttributes: localBadgeAttributes)
        }
    }
}

// MARK: - 错误类型
enum LocalBiographyError: LocalizedError {
    case noImages
    case generationFailed(String)
    case pdfCreationFailed
    
    var errorDescription: String? {
        switch self {
        case .noImages:
            return "请至少选择一张图片"
        case .generationFailed(let reason):
            return "传记生成失败: \(reason)"
        case .pdfCreationFailed:
            return "PDF创建失败"
        }
    }
} 