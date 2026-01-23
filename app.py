import streamlit as st
from openai import OpenAI
import json

# --- 1. 页面配置 ---
st.set_page_config(
    page_title="lovestory",
    page_icon="💘",
    layout="centered"
)

# --- CSS 美化 (精准隐藏右上角，保留左侧箭头) ---
st.markdown("""
<style>
    header {visibility: visible !important;}
    [data-testid="stToolbar"] {visibility: hidden !important; display: none !important;}
    footer {visibility: hidden !important; display: none !important;}
    [data-testid="stSidebarCollapsedControl"] {visibility: visible !important; display: block !important;}
</style>
""", unsafe_allow_html=True)

# --- 2. 核心功能：独立会话管理 (Session State) ---
if "all_chats" not in st.session_state:
    st.session_state.all_chats = {
        "默认对话": []  # 每个人进来都有一个默认的空白对话
    }

if "current_chat_id" not in st.session_state:
    st.session_state.current_chat_id = "默认对话"

# --- 3. 侧边栏：超级控制台 ---
with st.sidebar:
    st.title("📂 档案管理")
    st.caption("注：数据保存在当前浏览器中，刷新网页会清空。请及时点击下方按钮下载回忆。")
    
    # === A. 存档切换 ===
    chat_list = list(st.session_state.all_chats.keys())
    
    # 防止删光了报错，兜底逻辑
    if not chat_list:
        st.session_state.all_chats = {"默认对话": []}
        st.session_state.current_chat_id = "默认对话"
        chat_list = ["默认对话"]
        
    if st.session_state.current_chat_id not in chat_list:
        st.session_state.current_chat_id = chat_list[0]

    selected_chat = st.selectbox("切换对话", chat_list, index=chat_list.index(st.session_state.current_chat_id))
    
    if selected_chat != st.session_state.current_chat_id:
        st.session_state.current_chat_id = selected_chat
        st.rerun()

    # 新建/删除
    col1, col2 = st.columns(2)
    with col1:
        new_name = st.text_input("新对话名", placeholder="如:霸总篇", label_visibility="collapsed")
        if st.button("➕ 新建"):
            if new_name and new_name not in st.session_state.all_chats:
                st.session_state.all_chats[new_name] = []
                st.session_state.current_chat_id = new_name
                st.rerun()
    with col2:
        if st.button("🗑️ 删除"):
            if len(st.session_state.all_chats) > 1:
                del st.session_state.all_chats[st.session_state.current_chat_id]
                st.session_state.current_chat_id = list(st.session_state.all_chats.keys())[0]
                st.rerun()
            else:
                st.toast("至少保留一个对话哦")

    # === B. 导出回忆 (下载功能) ===
    # 把当前对话转成文本供下载
    current_chat_history = st.session_state.all_chats[st.session_state.current_chat_id]
    history_str = ""
    for msg in current_chat_history:
        role = "Ta" if msg["role"] == "assistant" else "我"
        history_str += f"{role}: {msg['content']}\n\n"
    
    st.download_button(
        label="📥 下载当前聊天记录",
        data=history_str,
        file_name=f"{st.session_state.current_chat_id}_回忆.txt",
        mime="text/plain"
    )

    st.markdown("---")
    st.title("⚙️ 恋爱设定局")

    # API Key
    api_key = ""
    try:
        if "DEEPSEEK_API_KEY" in st.secrets:
            api_key = st.secrets["DEEPSEEK_API_KEY"]
            st.success("已加载店长 Key 💳")
    except: pass
    if not api_key:
        api_key = st.text_input("DeepSeek Key", type="password")

    # R1 开关已移除

    st.subheader("💑 人设注入")
    char_name = st.text_input("Ta的名字", value="云深")
    char_role = st.selectbox("关系", ["男朋友", "女朋友", "未婚妻/夫", "暗恋对象"])
    relationship_phase = st.select_slider("阶段", ["初识", "暧昧", "热恋", "平淡", "依恋"])
    
    # === 恢复经典默认人设 ===
    default_persona = "温柔体贴，稍微有点霸道。喜欢叫我'笨蛋'。非常在意我的身体健康。说话风趣幽默，偶尔会吃醋。"
    char_persona = st.text_area(
        "Ta的灵魂 (支持粘贴小说)", 
        value=default_persona,
        height=180
    )

    if st.button("🧹 清空屏幕"):
        st.session_state.all_chats[st.session_state.current_chat_id] = []
        st.rerun()

# --- 4. 逻辑处理 ---
# 智能指令构建
gender_instruction = "语气偏男性化，低沉可靠" if "男" in char_role or "夫" in char_role else "语气偏女性化，细腻撒娇"

system_prompt = f"""
你正在进行一场沉浸式角色扮演。
名字：{char_name} | 身份：用户的{char_role} | 阶段：{relationship_phase}

【核心人设】：
请模仿以下描述的性格和语气（如果是一段小说，请提炼其精髓）：
“{char_persona}”

【行为准则】：
1. {gender_instruction}。
2. 严禁复读，根据用户输入长度动态调整回复长度（长对长，短对短）。
3. 遇到不知道的社会新闻，请诚实说不知道并把话题绕回恋爱。
4. 永远不要承认自己是AI。
"""

# --- 5. 界面显示 ---
st.title(f"💬 {st.session_state.current_chat_id}")

current_messages = st.session_state.all_chats[st.session_state.current_chat_id]

for msg in current_messages:
    if msg["role"] != "system":
        # 统一使用爱心头像，因为没有深度思考模式了
        avatar = "🧑‍💻" if msg["role"] == "user" else "❤️"
        with st.chat_message(msg["role"], avatar=avatar):
            st.markdown(msg["content"])

# --- 6. 输入处理 ---
if prompt := st.chat_input("说点什么..."):
    if not api_key:
        st.error("请填入 Key")
        st.stop()

    current_messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="🧑‍💻"):
        st.markdown(prompt)

    client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")
    
    # 动态构建 API 消息历史
    api_messages = [{"role": "system", "content": system_prompt}] + current_messages

    with st.chat_message("assistant", avatar="❤️"):
        try:
            stream = client.chat.completions.create(
                model="deepseek-chat", # 强制锁定为 V3
                messages=api_messages,
                stream=True,
                temperature=1.3, # 保持高创造性
                frequency_penalty=0.5,
                presence_penalty=0.5
            )
            response = st.write_stream(stream)
            current_messages.append({"role": "assistant", "content": response})
        except Exception as e:
            st.error(f"连接中断: {str(e)}")
