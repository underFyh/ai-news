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
    "36氪(AI)": "https://rsshub.app/36kr/motif/32768674816", 
    # 你可以在这里自由添加更多你喜欢的优质 RSS 源
}

def fetch_rss_news():
    print("📡 正在抓取全网优质 AI 资讯生肉...")
    raw_news = []
    
    for source, url in RSS_FEEDS.items():
        try:
            feed = feedparser.parse(url)
            # 每个源取前 5 条最新内容，避免生肉太长导致大模型处理超时或丢失焦点
            for entry in feed.entries[:5]:
                title = entry.title
                # 提取摘要，限制 100 个字符
                summary = entry.get('summary', entry.get('description', '无摘要'))[:100] 
                raw_news.append(f"来源：{source} | 标题：{title} | 摘要：{summary}...")
        except Exception as e:
            print(f"抓取 {source} 失败: {e}")
            
    return "\n".join(raw_news)

# ==========================================
# 2. 调用 DeepSeek 进行深度洞察与总结
# ==========================================
def generate_ai_insight_with_deepseek(raw_news_text):
    print("🧠 正在呼叫 DeepSeek 挖掘项目灵感与时代趋势...")
    
    api_key = os.environ.get("DEEPSEEK_API_KEY")
    if not api_key:
        return "❌ 缺少 DEEPSEEK_API_KEY，无法进行 AI 分析。请检查 GitHub Secrets！"

    # 【终极版 Prompt】宏观趋势 + 人类影响 + 核心事件 + 开发者破局 + 普通人行动
    prompt = f"""你是一个兼具“顶级科技分析师”、“敏锐独立开发者”和“AI 普及布道师”三重身份的专家。
    以下是我今天抓取到的全球最新 AI 资讯生肉：
    
    {raw_news_text}
    
    请你深度咀嚼这些信息，【连点成线】，并严格按照以下 Markdown 格式输出一份极具洞察力的内参：

    ## 🌐 今日 AI 趋势脉络
    [请仔细阅读所有新闻，提取出今天最核心的 1-2 个底层趋势。这些看似独立的新闻，背后共同指向了什么技术演进或商业博弈？用 100 字左右一针见血地指出。]

    ## 🌍 时代切片与人类影响
    [基于上述趋势，分析它对整个社会形态、特定行业或旧有秩序会产生什么具体冲击？谁的饭碗面临危机？谁的效率将迎大爆发？用犀利、接地气的话语写约 100 字。]

    ## 📰 核心事件速览
    [精选出支撑上述趋势的 3 条最重要的新闻，每条用一句话（核心事件 + 关键数据/节点）概括]
    1. 
    2. 
    3. 

    ## 💡 独立开发者的破局点
    [作为 Indie Hacker，在这个趋势下我们可以切入做什么？给出 1-2 个极其具体、切中细分痛点的“小微项目（Micro-SaaS/浏览器插件/自动化流）”点子。专挑巨头看不上的脏活累活和极度垂直的场景。]

    ## 🚀 普通人的上车指南
    [针对不懂代码的普通人，在今天的这些 AI 趋势下，他们能具体做些什么来享受红利或避免被淘汰？给出 1-2 个极具操作性的建议（例如：去体验某类特定的工具、调整某种日常工作流等），让他们立刻就能动起手来。]
    
    注意：排版要呼吸感强，多用 Emoji，语气要冷静、专业、极具洞察力且鼓舞人心。
    """

    url = "https://api.deepseek.com/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "deepseek-chat", # 使用性价比极高的 V3 模型
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7, # 0.7 适合发散性思维与总结
        "max_tokens": 1500
    }

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=60)
        
        if response.status_code != 200:
            print(f"DeepSeek API 报错: {response.text}")
            return f"⚠️ DeepSeek 接口异常，状态码: {response.status_code}"
            
        result = response.json()
        ai_content = result['choices'][0]['message']['content']
        
        today = datetime.now().strftime("%Y-%m-%d")
        final_content = f"🌟 **【AI 前沿洞察与灵感内参】 {today}**\n\n" + ai_content
        return final_content
        
    except Exception as e:
        print(f"DeepSeek 调用失败: {e}")
        return "⚠️ AI 分析引擎故障，请检查日志。"

# ==========================================
# 3. 推送到微信 (WxPusher)
# ==========================================
def push_to_wechat(content):
    app_token = os.environ.get("WXPUSHER_APP_TOKEN")
    uid = os.environ.get("WXPUSHER_UID")
    
    if not app_token or not uid:
        print("❌ 错误：找不到 WxPusher 的配置信息！")
        return

    print("🚀 正在将 AI 深度简报推送到微信...")
    url = "https://wxpusher.zjiecode.com/api/send/message"
    payload = {
        "appToken": app_token,
        "content": content,
        "summary": "🚀 您的专属 AI 深度洞察与项目灵感已送达！", 
        "contentType": 3, # ⚠️ 必须是 3，表示支持 Markdown 渲染，这样推送到微信上排版才好看
        "uids": [uid]
    }
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        result = response.json()
        
        if result.get("code") == 1000:
            print("✅ 推送成功！请打开微信查看。")
        else:
            print(f"❌ 推送失败：{result}")
    except Exception as e:
        print(f"❌ 请求 WxPusher 失败: {e}")

# ==========================================
# 4. 主程序执行入口
# ==========================================
if __name__ == "__main__":
    # 1. 抓取 RSS 生肉
    raw_text = fetch_rss_news()
    
    if raw_text and raw_text.strip():
        # 2. DeepSeek 提炼与思考
        insight_report = generate_ai_insight_with_deepseek(raw_text)
        print("========== 最终生成的 AI 简报 ==========")
        print(insight_report) 
        print("========================================")
        
        # 3. 微信推送
        push_to_wechat(insight_report)
    else:
        print("今天没有抓取到任何有效资讯，跳过推送。")
