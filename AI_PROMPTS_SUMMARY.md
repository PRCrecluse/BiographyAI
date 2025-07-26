# AI 提示词总结文档

## 概述
本文档总结了AI Profile项目中所有AI大模型提示词的位置、用途和内容。

## 提示词分布

### 1. 主要AI服务提示词
**位置**: `agent/services/ai_service.py`

#### 1.1 传记生成提示词 (第264行)
```python
async def generate_biography_text(self, image_analyses: List[str], user_requirements: str = "", style: str = "warm") -> str:
```

**提示词内容**:
```
作为一位专业的个人传记撰写师，请根据以下图片分析内容，为用户撰写一篇温馨感人的个人传记。

用户要求：{user_requirements}

图片分析内容：
{图片分析结果列表}

撰写要求：
1. 根据图片内容推断人物的生活经历和重要时刻
2. 按时间顺序组织内容，形成完整的人生故事  
3. 突出人物的成长历程、重要关系和人生感悟
4. 语言风格：{style}（温馨/专业/文学性）
5. 字数控制在1500-2500字
6. 只使用图片中实际存在的内容，不添加虚构元素
7. 每个重要阶段对应相关图片内容
```

#### 1.2 章节标题生成提示词 (第295行)
```python
async def generate_chapter_titles(self, biography_text: str) -> List[str]:
```

**提示词内容**:
```
请为以下传记内容生成5-8个章节标题，要求：
1. 标题简洁有力，富有感情色彩
2. 体现人生的重要阶段和转折点
3. 每个标题不超过10个字
4. 按时间顺序排列

传记内容：{biography_text}

请只返回章节标题列表，每行一个标题：
```

### 2. 文本生成工具提示词
**位置**: `agent/tools/text_generator.py`

#### 2.1 结构化传记生成 (第60行)
```python
async def _split_into_sections(self, content: str, image_analyses: List[ImageAnalysisResult]) -> List[BiographySection]:
```

**提示词内容**:
```
请将以下个人传记内容分解为逻辑清晰的章节。

传记内容：{content}

请以JSON格式返回章节信息：
{
    "sections": [
        {
            "title": "章节标题",
            "content": "章节内容",
            "order": 1,
            "style": "paragraph",
            "related_images": ["图片1", "图片2"]
        }
    ]
}

要求：
1. 每个章节都要有清晰的主题
2. 内容要连贯，逻辑清晰  
3. 为每个章节匹配相关的图片
4. 章节顺序要合理
```

#### 2.2 时间线传记生成 (第121行)
```python
async def generate_timeline_biography(self, image_analyses: List[ImageAnalysisResult], user_requirements: str) -> List[BiographySection]:
```

**提示词内容**:
```
请根据以下按时间顺序排列的图片分析结果，创建一个时间线式的个人传记。

图片分析（按时间顺序）：{sorted_analyses}

用户要求：{user_requirements}

请创建一个时间线式的传记，每个时间段为一个章节。
以JSON格式返回：
{
    "timeline_sections": [
        {
            "period": "时间段描述",
            "title": "章节标题", 
            "content": "章节内容",
            "images": ["相关图片路径"],
            "key_events": ["关键事件1", "关键事件2"]
        }
    ]
}
```

#### 2.3 故事式传记生成 (第186行)
```python
async def generate_story_style_biography(self, image_analyses: List[ImageAnalysisResult], user_requirements: str) -> str:
```

**系统提示词**:
```
你是一位专业的故事撰写人，擅长将真实的生活经历转化为引人入胜的故事。
请根据图片分析结果，撰写一篇故事式的个人传记。

要求：
1. 使用第三人称或第一人称叙述
2. 包含生动的细节描写
3. 具有故事性的开头、发展、高潮、结尾
4. 语言优美，富有感染力
5. 每个重要情节都要与图片内容呼应
```

#### 2.4 传记引言生成 (第285行)
```python
async def generate_introduction(self, image_analyses: List[ImageAnalysisResult]) -> str:
```

**提示词内容**:
```
请根据以下图片分析结果，为个人传记撰写一段引人入胜的引言。

图片分析摘要：{image_analyses}

要求：
1. 引言要简洁有力，能够吸引读者
2. 概括传记的主要内容和主题
3. 设置悬念，引导读者继续阅读
4. 字数控制在100-200字之间
```

#### 2.5 传记结语生成 (第305行)
```python
async def generate_conclusion(self, biography_content: str) -> str:
```

**提示词内容**:
```
请根据以下传记内容，撰写一段深刻的结语。

传记内容摘要：{biography_content}

要求：
1. 总结传记的主要主题和意义
2. 表达对未来的展望或感悟
3. 语言要富有哲理性和感染力
4. 字数控制在100-200字之间
```

### 3. 演示代理提示词
**位置**: `agent/demo_agent.py`

#### 3.1 传记内容生成 (第98行)
使用了与主服务相同的生成逻辑，调用 `generate_biography()` 函数。

### 4. Web应用基础模板
**位置**: `agent/enhanced_web_app.py`

#### 4.1 基础传记内容模板 (第101行)
当AI服务不可用时的备用方案，包含多语言模板：

**中文模板**:
```
intro: "这是我的人生故事，一段充满回忆、成长和美好时光的旅程，用照片记录下珍贵的瞬间。"
chapter_titles: ["童年时光", "求学岁月", "家庭生活", "人生旅途", "成长收获", "感悟思考"]
```

**英文模板**:
```
intro: "This is my life story, a journey filled with memories, growth, and beautiful moments captured in photographs."
chapter_titles: ["Early Years", "School Days", "Family Time", "Adventures", "Achievements", "Reflections"]
```

**意大利语模板**:
```
intro: "Questa è la mia storia di vita, un viaggio pieno di ricordi, crescita e momenti belli catturati nelle fotografie."
chapter_titles: ["Primi Anni", "Anni di Scuola", "Tempo in Famiglia", "Avventure", "Conquiste", "Riflessioni"]
```

## 5. AI模型配置
**位置**: `agent/config/ai_models.yaml`

### 5.1 传记设置配置 (第216行)
```yaml
biography_settings:
  default_style: "warm"
  max_length: 2500
  min_length: 1500
  
  supported_styles:
    - "warm"        # 温馨
    - "professional" # 专业
    - "literary"    # 文学性
    - "storytelling" # 故事性
  
  chapters:
    min_chapters: 3
    max_chapters: 8
    auto_generate_titles: true
  
  image_processing:
    max_images: 20
    supported_formats: ["jpg", "jpeg", "png", "webp"]
    max_file_size: "10MB"
```

### 5.2 使用场景配置 (第238行)
```yaml
scenarios:
  biography_writing:
    primary_model: "openai.gpt4"
    vision_model: "openai.gpt4_vision"
    optimization_model: "anthropic.claude3"
    
  image_analysis:
    primary_model: "openai.gpt4_vision"
    fallback_models: ["anthropic.claude3_vision", "alibaba.qwen_vl"]
    
  text_optimization:
    primary_model: "anthropic.claude3"
    fallback_models: ["openai.gpt4", "alibaba.qwen_max"]
```

## 6. 移动端Swift代码
**位置**: `AI profile/AI profile/AI profile/Services/AgentService.swift`

移动端通过HTTP API调用后端服务，不直接包含AI提示词，但包含API请求结构：

```swift
struct BiographyCreateRequest: Codable {
    let userRequirements: String
    let templateStyle: String
    let language: String
}
```

## 总结

### 核心提示词特点：
1. **严格控制内容真实性**: 所有提示词都强调"只使用图片中实际存在的内容，不添加虚构元素"
2. **支持多种风格**: warm(温馨)、professional(专业)、literary(文学性)、storytelling(故事性)
3. **结构化输出**: 使用JSON格式确保输出结构化
4. **多语言支持**: 支持中文、英文、意大利语等多种语言
5. **长度控制**: 严格控制字数范围(1500-2500字)

### 改进建议：
1. **增强用户定制**: 可以根据用户反馈动态调整提示词
2. **上下文记忆**: 在对话过程中保持上下文信息
3. **质量评估**: 添加生成内容质量评估机制
4. **个性化调优**: 根据用户偏好调整生成风格

---

*文档生成时间: 2024年7月1日*
*项目版本: AI Profile v2.0* 