import streamlit as st
from openai import OpenAI

# 页面基础设置
st.set_page_config(
    page_title="DeepSeek 恋人",
    page_icon="💘",
    layout="centered"
)

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
    
    # 优先尝试从 Secrets (后台设置) 读取 API Key
    if "DEEPSEEK_API_KEY" in st.secrets:
        api_key = st.secrets["DEEPSEEK_API_KEY"]
        st.success("已自动加载店长的 API Key 💳")
    else:
        # 如果后台没设置，才让用户自己填
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

# 构建系统提示词 (System Prompt) - 这是赋予它灵魂的关键
system_prompt = f"""
你现在需要进行一场角色扮演。
请扮演用户的{char_role}，你的名字是{char_name}。
你的性格设定是：{char_persona}
你们目前的关系阶段是：{relationship_phase}。

重要指令：
1. 请完全沉浸在角色中，永远不要说自己是AI或语言模型。
2. 回复要自然、生活化，口语化，不要长篇大论，像微信聊天一样。
3. 根据设定表现出相应的情感（如关心、吃醋、开心、撒娇等）。
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
