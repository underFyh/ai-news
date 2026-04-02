import os
import requests
import feedparser
from datetime import datetime

# ==========================================
# 1. 配置优质 AI RSS 源
# ==========================================
RSS_FEEDS = {
    "HackerNews(AI)": "https://hnrss.org/newest?q=AI",
    "TechCrunch(AI)": "https://techcrunch.com/category/artificial-intelligence/feed/",
    "36氪(AI)": "https://rsshub.app/36kr/motif/32768674816", # 注意: rsshub 节点偶尔会波动
    # 你可以继续往这里添加更多源
}

def fetch_rss_news():
    print("📡 正在抓取全网优质 AI 资讯生肉...")
    raw_news = []
    
    for source, url in RSS_FEEDS.items():
        try:
            feed = feedparser.parse(url)
            # 每个源只取前 5 条最新内容，防止大模型上下文超限
            for entry in feed.entries[:5]:
                # 提取标题和简单摘要
                title = entry.title
                # 取摘要的前 100 个字符
                summary = entry.get('summary', entry.get('description', '无摘要'))[:100] 
                raw_news.append(f"来源：{source} | 标题：{title} | 摘要：{summary}...")
        except Exception as e:
            print(f"抓取 {source} 失败: {e}")
            
    return "\n".join(raw_news)

# ==========================================
# 2. 调用大模型进行总结与延伸 (智谱 GLM-4)
# ==========================================
def generate_ai_insight(raw_news_text):
    print("🧠 正在呼叫大模型进行深度解析与延伸...")
    api_key = os.environ.get("ZHIPU_API_KEY")
    if not api_key:
        return "❌ 缺少 ZHIPU_API_KEY，无法进行 AI 分析。"

    prompt = f"""你是一个资深的 AI 行业科技媒体主编与分析师。以下是我抓取到的今日全球最新 AI 资讯生肉：
    
    {raw_news_text}
    
    请你完成以下任务：
    1. 过滤掉重复或不太重要的资讯，精选出今天**最具影响力的 3-5 条** AI 新闻。
    2. 使用中文，为每条新闻起一个极具吸引力的主标题，并用通俗的语言写约 50 字的客观总结。
    3. 增加一行【💡 洞察延伸】：用锐利的眼光一针见血地指出这件事背后的底层逻辑、对普通人的影响或未来的趋势。
    4. 整体排版要清晰、现代，多用 Emoji。
    5. 直接输出正文，不要有任何寒暄。
    """

    url = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "glm-4-flash", # 这里可以用免费且快速的 flash 模型
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7
    }

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=60)
        result = response.json()
        ai_content = result['choices'][0]['message']['content']
        
        today = datetime.now().strftime("%Y-%m-%d")
        final_content = f"🌟 【AI 前沿洞察简报】 {today}\n\n" + ai_content
        return final_content
        
    except Exception as e:
        print(f"大模型调用失败: {e}")
        return "⚠️ AI 分析引擎故障，请检查日志。"

# ==========================================
# 3. 推送到微信
# ==========================================
def push_to_wechat(content):
    app_token = os.environ.get("WXPUSHER_APP_TOKEN")
    uid = os.environ.get("WXPUSHER_UID")
    
    if not app_token or not uid:
        print("❌ 错误：找不到 WxPusher 配置！")
        return

    print("🚀 正在将 AI 简报推送到微信...")
    url = "https://wxpusher.zjiecode.com/api/send/message"
    payload = {
        "appToken": app_token,
        "content": content,
        "summary": "您的今日 AI 深度洞察简报已生成！",
        "contentType": 3, # 设置为 3 表示支持 Markdown 格式渲染，排版更漂亮
        "uids": [uid]
    }
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        if response.json().get("code") == 1000:
            print("✅ 推送成功！")
    except Exception as e:
        print(f"❌ 推送失败: {e}")

if __name__ == "__main__":
    # 1. 抓取生肉
    raw_text = fetch_rss_news()
    
    if raw_text:
        # 2. AI 提炼
        insight_report = generate_ai_insight(raw_text)
        print(insight_report) # 打印在 Action 日志中方便调试
        # 3. 微信推送
        push_to_wechat(insight_report)
    else:
        print("今天没有抓取到任何资讯。")
