1.视频理解模型：
Doubao-1.5-thinking-vision-pro
（1）RestAPI调用示例：

pip install --upgrade "openai>=1.0"

curl https://ark.cn-beijing.volces.com/api/v3/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer defc42c9-5a80-41cf-833c-3e3b0f4446f7" \
  -d $'{
    "model": "doubao-1-5-thinking-vision-pro-250428",
    "messages": [
        {
            "content": [
                {
                    "text": "图片主要讲了什么?",
                    "type": "text"
                },
                {
                    "image_url": {
                        "url": "https://ark-project.tos-cn-beijing.ivolces.com/images/view.jpeg"
                    },
                    "type": "image_url"
                }
            ],
            "role": "user"
        }
    ]
}'
（2）OpenAI SDK调用示例：
import os
from openai import OpenAI

# 请确保您已将 API Key 存储在环境变量 ARK_API_KEY 中
# 初始化Ark客户端，从环境变量中读取您的API Key
client = OpenAI(
    # 此为默认路径，您可根据业务所在地域进行配置
    base_url="https://ark.cn-beijing.volces.com/api/v3",
    # 从环境变量中获取您的 API Key。此为默认方式，您可根据需要进行修改
    api_key=os.environ.get("ARK_API_KEY"),
)

response = client.chat.completions.create(
    # 指定您创建的方舟推理接入点 ID，此处已帮您修改为您的推理接入点 ID
    model="doubao-1-5-thinking-vision-pro-250428",
    messages=[
        {
            "role": "user",
            "content": [
                {
                    "type": "image_url",
                    "image_url": {
                        "url": "https://ark-project.tos-cn-beijing.ivolces.com/images/view.jpeg"
                    },
                },
                {"type": "text", "text": "这是哪里？"},
            ],
        }
    ],
)

print(response.choices[0])

2.文本优化/生成模型：
RestAPI调用示例：
curl https://ark.cn-beijing.volces.com/api/v3/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer defc42c9-5a80-41cf-833c-3e3b0f4446f7" \
  -d $'{
    "model": "doubao-seed-1-6-thinking-250615",
    "messages": [
        {
            "content": [
                {
                    "text": "图片主要讲了什么?",
                    "type": "text"
                },
                {
                    "image_url": {
                        "url": "https://ark-project.tos-cn-beijing.ivolces.com/images/view.jpeg"
                    },
                    "type": "image_url"
                }
            ],
            "role": "user"
        }
    ]
}'
