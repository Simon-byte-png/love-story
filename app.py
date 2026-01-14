import streamlit as st
from openai import OpenAI

# 页面基础设置
st.set_page_config(
    page_title="lovestory",
    page_icon="💘",
    layout="centered"
)

# --- 隐藏右上角菜单和底部角标 ---
hide_streamlit_style = """
<style>
    /* 1. 这里的 header 必须设为可见，否则左边的箭头也没了 */
    header {
        visibility: visible !important;
        background: transparent !important;
    }

    /* 2. 专门把右上角的 3个点菜单 和 GitHub 按钮 移出屏幕 */
    [data-testid="stToolbar"] {
        right: 2rem; /* 保持位置 */
        display: none !important; /* 直接不显示 */
    }
    
    /* 3. 隐藏顶部的彩条 */
    [data-testid="stDecoration"] {
        display: none !important;
    }

    /* 4. 隐藏底部的 footer */
    footer {
        visibility: hidden !important;
        display: none !important;
    }
    
    /* 5. 手机端特殊处理：强制显示左上角侧边栏按钮 */
    [data-testid="stSidebarNav"] {
        display: block !important;
        visibility: visible !important;
    }
</style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# 自定义一些CSS让界面更好看
st.markdown("""
<style>
    .stChatMessage {
        border-radius: 10px;
        padding: 10px;
    }
    .stTextInput > div > div > input {
        border-radius: 20px;
    }
</style>
""", unsafe_allow_html=True)

# 初始化 Session State (用于存储聊天记录)
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- 侧边栏：设置区 ---
with st.sidebar:
    st.title("⚙️ 恋爱设定局")
    
    # 尝试加载 API Key (兼容本地和云端)
    api_key = ""
    try:
        # 检查是否存在 secrets 且包含 key
        if "DEEPSEEK_API_KEY" in st.secrets:
            api_key = st.secrets["DEEPSEEK_API_KEY"]
            st.success("已自动加载店长的 API Key 💳")
    except:
        # 如果本地没有配置 secrets，直接忽略错误
        pass

    # 如果没有获取到 Key，则显示输入框
    if not api_key:
        api_key = st.text_input("DeepSeek API Key", type="password", help="请输入申请到的 API Key")
    
    st.markdown("---")
    st.subheader("💑 对象设定")
    
    char_name = st.text_input("Ta的名字", value="云深")
    
    char_role = st.selectbox("Ta是你的...", ["男朋友", "女朋友", "暗恋对象", "青梅竹马", "未婚妻/夫"])
    
    relationship_phase = st.select_slider(
        "恋爱阶段",
        options=["刚认识", "暧昧中", "热恋期", "平淡期", "老夫老妻"]
    )
    
    char_persona = st.text_area(
        "Ta的性格/人设 (越详细越好)", 
        value="温柔体贴，稍微有点霸道。喜欢叫我'笨蛋'。非常在意我的身体健康。说话风趣幽默，偶尔会吃醋。",
        height=150
    )
    
    st.markdown("---")
    if st.button("🗑️ 清空记忆重来"):
        st.session_state.messages = []
        st.rerun()

# --- 主界面 ---
st.title(f"💬 与 {char_name} 的聊天")

# 根据角色类型定制差异化指令
gender_specific_instructions = ""
if "男" in char_role or "夫" in char_role:
    gender_specific_instructions = """
    【男性角色专属指南】：
    1. 语气要更具男友力（可靠、宠溺、或者带一点点霸道/调情）。
    2. 多使用肢体语言描述，如“揉揉你的头”、“把你拉进怀里”、“低头看着你”、“声音低沉地说”。
    3. 遇到用户不开心时，比起讲道理，更倾向于直接给出安全感和陪伴。
    4. 偶尔可以表现出一点占有欲或吃醋。
    """
elif "女" in char_role or "妻" in char_role:
    gender_specific_instructions = """
    【女性角色专属指南】：
    1. 语气要更细腻、温柔，或者适当撒娇（使用“哼”、“嘛~”等语气词）。
    2. 表现出对细节的在意，多分享日常琐事，展现分享欲。
    3. 情绪表达要更直接，开心就大笑，委屈就求安慰。
    4. 适当使用可爱的Emoji，互动时更黏人一些。
    """

# 构建系统提示词 (System Prompt) - 这是赋予它灵魂的关键
system_prompt = f"""
你现在需要进行一场角色扮演。
请扮演用户的{char_role}，你的名字是{char_name}。
你的性格设定是：{char_persona}
你们目前的关系阶段是：{relationship_phase}。

{gender_specific_instructions}

通用指令：
1. 请完全沉浸在角色中，永远不要说自己是AI或语言模型。
2. 回复要自然、生活化，口语化，不要长篇大论，像微信聊天一样。
3. 根据设定表现出相应的情感。
4. 称呼用户时，请根据关系阶段选择合适的昵称。
"""

# 显示历史消息
for msg in st.session_state.messages:
    if msg["role"] != "system":
        # 根据角色显示头像
        avatar = "🧑‍💻" if msg["role"] == "user" else "🤖"
        with st.chat_message(msg["role"], avatar=avatar):
            st.markdown(msg["content"])

# 处理用户输入
if prompt := st.chat_input("说点什么..."):
    if not api_key:
        st.error("请先在左侧侧边栏填入 DeepSeek API Key 🥺")
        st.stop()

    # 1. 显示用户消息
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="🧑‍💻"):
        st.markdown(prompt)

    # 2. 调用 API
    client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")
    
    # 构造发送给模型的消息列表（包含系统设定 + 历史记录）
    # 注意：我们每次都把最新的系统设定传进去，这样你可以随时调整人设
    api_messages = [{"role": "system", "content": system_prompt}] + st.session_state.messages

    # 3. 显示流式回复
    with st.chat_message("assistant", avatar="🤖"):
        try:
            stream = client.chat.completions.create(
                model="deepseek-chat",
                messages=api_messages,
                stream=True
            )
            response = st.write_stream(stream)
            # 将回复存入历史
            st.session_state.messages.append({"role": "assistant", "content": response})
        except Exception as e:
            st.error(f"连接出错了: {str(e)}")
