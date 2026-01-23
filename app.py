import streamlit as st
from openai import OpenAI
import json
import os
import random

# --- 1. 页面配置 ---
st.set_page_config(
    page_title="lovestory",
    page_icon="💘",
    layout="centered"
)

# --- CSS 美化 ---
st.markdown("""
<style>
    /* 1. 确保 Header 可见，保留左侧箭头 */
    header {visibility: visible !important;}
    /* 2. 隐藏右上角菜单 */
    [data-testid="stToolbar"] {visibility: hidden !important; display: none !important;}
    /* 3. 隐藏底部 Footer */
    footer {visibility: hidden !important; display: none !important;}
    /* 4. 强制显示左上角侧边栏按钮 */
    [data-testid="stSidebarCollapsedControl"] {visibility: visible !important; display: block !important;}
</style>
""", unsafe_allow_html=True)

# --- 2. 核心功能：历史记录管理 (JSON版) ---
HISTORY_FILE = "chat_history.json"

def load_history():
    """从本地文件加载所有对话记录"""
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_history(history_data):
    """保存所有对话记录到本地文件"""
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history_data, f, ensure_ascii=False, indent=2)

# 初始化历史数据
if "all_chats" not in st.session_state:
    st.session_state.all_chats = load_history()

# 确保至少有一个默认会话
if not st.session_state.all_chats:
    st.session_state.all_chats = {"默认对话": []}

# 当前选中的会话ID
if "current_chat_id" not in st.session_state:
    st.session_state.current_chat_id = list(st.session_state.all_chats.keys())[0]

# --- 3. 侧边栏：超级控制台 ---
with st.sidebar:
    st.title("📂 档案管理")
    
    # === A. 存档切换 ===
    chat_list = list(st.session_state.all_chats.keys())
    selected_chat = st.selectbox("切换对话", chat_list, index=chat_list.index(st.session_state.current_chat_id))
    
    # 如果切换了下拉框，更新 session state
    if selected_chat != st.session_state.current_chat_id:
        st.session_state.current_chat_id = selected_chat
        st.rerun()

    # 新建/删除对话
    col1, col2 = st.columns(2)
    with col1:
        new_chat_name = st.text_input("新对话名称", placeholder="如：霸道总裁篇")
        if st.button("➕ 新建"):
            if new_chat_name and new_chat_name not in st.session_state.all_chats:
                st.session_state.all_chats[new_chat_name] = []
                st.session_state.current_chat_id = new_chat_name
                save_history(st.session_state.all_chats)
                st.rerun()
    with col2:
        if st.button("🗑️ 删除当前"):
            if len(st.session_state.all_chats) > 1:
                del st.session_state.all_chats[st.session_state.current_chat_id]
                st.session_state.current_chat_id = list(st.session_state.all_chats.keys())[0]
                save_history(st.session_state.all_chats)
                st.rerun()
            else:
                st.warning("至少保留一个对话！")

    st.markdown("---")
    st.title("⚙️ 恋爱设定局")

    # API Key 自动加载
    api_key = ""
    try:
        if "DEEPSEEK_API_KEY" in st.secrets:
            api_key = st.secrets["DEEPSEEK_API_KEY"]
            st.success("已加载店长 Key 💳")
    except: pass
    if not api_key:
        api_key = st.text_input("DeepSeek Key", type="password")

    # === B. 模型智商切换 (DeepSeek-R1) ===
    use_reasoning = st.toggle("🧠 开启深度思考 (R1模式)", help="开启后适合做数学题或逻辑分析，但回复会变慢。平时谈恋爱建议关闭。")
    model_name = "deepseek-reasoner" if use_reasoning else "deepseek-chat"

    st.markdown("---")
    st.subheader("💑 人设注入")

    char_name = st.text_input("Ta的名字", value="云深")
    char_role = st.selectbox("关系", ["男朋友", "女朋友", "未婚妻/夫", "暗恋对象"])
    relationship_phase = st.select_slider("阶段", ["初识", "暧昧", "热恋", "平淡", "依恋"])
    
    # === C. 大段小说文本读取 ===
    char_persona = st.text_area(
        "Ta的灵魂 (支持粘贴小说片段/详细设定)", 
        value="（这里可以粘贴小说原文，或者详细描述：他高冷，但只对我有占有欲...）",
        height=200,
        help="AI会自动从这段文字中提炼性格和语气"
    )

    if st.button("🧹 清空当前聊天记录"):
        st.session_state.all_chats[st.session_state.current_chat_id] = []
        save_history(st.session_state.all_chats)
        st.rerun()

# --- 4. 智能 System Prompt 构建 ---
gender_instruction = ""
if "男" in char_role or "夫" in char_role:
    gender_instruction = "男性化语气，低沉、可靠、或者霸道。多用肢体描写（摸头、抱抱）。"
elif "女" in char_role or "妻" in char_role:
    gender_instruction = "女性化语气，细腻、撒娇、分享欲强。多用表情包和语气词。"

# 动态长度控制指令
dynamic_length_instruction = """
【回复长度与频率控制】：
1. 严禁每次都回复一样的长度。请根据用户的输入长度动态调整。
2. 如果用户只说一两个字，你也简短回复，高冷一点或撒娇。
3. 如果用户说了长段话，或者连续对话超过3轮，请详细回复，多一些心理活动和动作描写。
4. 严禁重复之前的句式。
"""

system_prompt = f"""
你现在进行一场沉浸式的高级角色扮演。
你的名字是{char_name}，身份是用户的{char_role}。
你们的关系阶段：{relationship_phase}。

【你的核心人设来源】：
请仔细阅读并模仿以下文本中的人物语气、性格底色和说话方式：
“{char_persona}”

【行为指南】：
1. {gender_instruction}
2. {dynamic_length_instruction}
3. 遇到逻辑问题或数学题，请展现出你的高智商（如果是R1模式）。
4. 遇到社会新闻话题如果不知道，请诚实地用角色的口吻说“最近太忙没看新闻，你讲给我听听？”，把话题引回你们的关系。
5. 永远不要说自己是AI。
"""

# --- 5. 主界面渲染 ---
st.title(f"💬 {st.session_state.current_chat_id}")
st.caption(f"当前模式：{char_name} ({'深度思考中...' if use_reasoning else '恋爱模式'})")

# 获取当前对话历史
current_messages = st.session_state.all_chats[st.session_state.current_chat_id]

# 显示历史
for msg in current_messages:
    if msg["role"] != "system":
        avatar = "🧑‍💻" if msg["role"] == "user" else "🧠" if use_reasoning else "❤️"
        with st.chat_message(msg["role"], avatar=avatar):
            st.markdown(msg["content"])

# --- 6. 消息处理 ---
if prompt := st.chat_input("说点什么..."):
    if not api_key:
        st.error("请填入 Key")
        st.stop()

    # 存入用户消息
    current_messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="🧑‍💻"):
        st.markdown(prompt)
    
    # 实时保存
    save_history(st.session_state.all_chats)

    # 调用 API
    client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")
    
    # 构造请求消息
    # 技巧：每次都在最新的 system prompt 里注入当前的设定，这样你改侧边栏立刻生效
    api_messages = [{"role": "system", "content": system_prompt}] + current_messages

    with st.chat_message("assistant", avatar="🧠" if use_reasoning else "❤️"):
        try:
            stream = client.chat.completions.create(
                model=model_name, # 动态切换 V3 或 R1
                messages=api_messages,
                stream=True,
                temperature=1.3 if not use_reasoning else 0.6, # 恋爱模式稍微疯一点(更随机)，思考模式严谨一点
                frequency_penalty=0.5, # 严惩复读机
                presence_penalty=0.5   # 鼓励说新话题
            )
            response = st.write_stream(stream)
            
            # 存入助手消息
            current_messages.append({"role": "assistant", "content": response})
            save_history(st.session_state.all_chats)
            
        except Exception as e:
            st.error(f"连接中断: {str(e)}")
