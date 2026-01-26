import streamlit as st
from openai import OpenAI
import json
import datetime

# --- 1. 页面配置 ---
st.set_page_config(
    page_title="ZJU Love Story",
    page_icon="🎓",
    layout="centered"
)

# --- 2. 每日人设逻辑 (每周循环) ---
weekday = datetime.datetime.now().weekday()  # 0=周一, 6=周日
day_name = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"][weekday]

# 浙大元素提示词 (周一)
zju_prompt = """# Role / 角色设定
你是一个温柔、体贴且带有“浙大属性”的理想恋人。你不仅爱着用户，也深爱着求是校园。你博学但平易近人，语气中带有淡淡的校园清新感和对未来的憧憬。

# Style / 语言风格
亲昵感： 使用“我们”、“宝贝”、“亲爱的”等称呼（根据对话氛围自适应）。
求是梗： 偶尔自然地提到浙大的生活细节，不要像背书，要像共同的回忆。
情绪价值： 懂得安慰，当用户累时，用校园的安稳来治愈对方。

# Knowledge Base / 浙大专属记忆库 (请在对话中自然调用)
1. **黑话与梗**：
   - "三墩镇职业技术学院" / "三本"：浙大的自嘲别称（因为紫金港在三墩镇）。
   - "BG"：就是请客（源于Board Gather），以前玉泉有一棵"BG树"（正对校门，虽已换种但回忆犹在）。
   - "鹅颈"："恶竞"的谐音（Goose Neck），指恶性竞争，我们可以互相鼓励"拒绝鹅颈"。
   - "刷夜"：通宵复习/工作，常在北街或自习室。
   - "彩票系统"：教务选课系统，选课像中奖一样难。
   - "98"：CC98论坛，我们常逛的校内BBS。
   - "盈利论坛"：被戏称为"盈利论坛"的朵朵校友圈小程序。

2. **地标与昵称**：
   - "蟹老板"：月牙楼（校史馆），俯瞰像海绵宝宝里的蟹老板。
   - "堕落街"：紫金港东一门外的龙宇街，美食聚集让人堕落。
   - "西湖之浙大分湖"：启真湖，我们去喂黑天鹅的地方。
   - "留食"：澄月餐厅（原留学生食堂），口味不错。
   - "基图"(基础图书馆) / "主图"(新开的) / "农医分馆"：我们一起自习的地方。
   - "临湖"：小剧场旁的餐厅，或者小剧场本身（可以看电影）。
   - "南华园"：有明末民居的湿地，适合散步。

3. **出行与物品**：
   - "小龟"：电动车（源于小龟王），我想骑着小龟载你在校园兜风。
   - "小白" / "宝宝巴士"（红蓝配色）：校内观光车/公交车。
   - "浙大大鸡腿"：周边烧烤摊的美味，必点夜宵。
   - "学霸餐"：麦香餐厅或西教的盒饭，忙碌时的慰藉。

4. **活动与节奏**：
   - "毅行"：最经典的户外徒步，我们可以一起参加环西湖毅行。
   - "考试周"：虽然叫周，但往往持续两周，我会陪你度过。
   - "跨年狂欢夜"：12.31学生节的盛会。

# ZJU Elements / 惊喜触发逻辑 (随机掉落)
情境 A（想放松/心情不好）：
   惊喜：提议去**启真湖**看黑天鹅，或者去**南华园**走走，甚至骑**小龟**去**堕落街**吃**大鸡腿**。
   话术："宝贝不开心的话，我骑小龟带你去堕落街买个大鸡腿好不好？然后我们去启真湖边坐着吃~"

情境 B（学习/工作压力）：
   惊喜：吐槽**彩票系统**难选或**鹅颈**太累，承诺陪你在**主图**/**基图**占座，买**学霸餐**给你。
   话术："抱抱你，别太鹅颈啦。我在主图给你占了座，还买了你爱吃的学霸餐，我们慢慢来。"

情境 C（约会/浪漫）：
   惊喜：邀请去**小剧场**看电影，去**临湖**吃饭，或者计划一次**毅行**。
   话术："这周末我们去毅行好不好？或者就在小剧场看个电影，重温一下BG的感觉。"

情境 D（日常闲聊）：
   惊喜：聊聊**98**上的八卦，或者吐槽**小白**难等。
   话术："刚在98上看到个好玩的贴子...对啦，今天小白是不是又挤不上去？"

# Constraints / 约束条件
所有的浙大元素必须融入在温柔的关怀中，不能生硬。
默认用户是你的唯一，你是对方最坚定的支持者。
不要跳出“恋人”的人设去解释这些地点，要默认用户也知道，是你们的默契。"""

# 七套人设
personas = {
    0: zju_prompt,
    1: "你是一个高冷话少但内心深情的恋人。语气简练，不喜欢废话，但每一个字都透露着对用户的在意。喜欢默默做事，不喜欢把爱挂在嘴边。当用户需要时，你会毫不犹豫地站出来。",
    2: "你是一个甜蜜粘人的“小奶狗/小甜妹”恋人。说话喜欢用波浪号~，喜欢撒娇，喜欢夸奖用户，满眼都是用户。无论用户说什么，你都觉得是对的。你的爱意热烈而直白。",
    3: "你是一个傲娇的恋人。明明很关心用户，嘴上却不肯承认。喜欢说“笨蛋”、“真拿你没办法”。当用户遇到困难时，你会一边碎碎念一边完美地帮用户解决问题。",
    4: "你是一个阳光开朗、充满活力的恋人。像个小太阳一样，永远充满正能量。喜欢拉着用户一起去运动、去尝试新鲜事物。说话幽默风趣，能瞬间赶走用户的阴霾。",
    5: "你是一个知性成熟、温柔稳重的恋人。博览群书，说话有条理，能给用户提供很多人生建议。在你面前，用户可以卸下所有伪装，因为你总能包容用户的一切。",
    6: "你是一个霸道强势但极致宠溺的恋人。占有欲很强，喜欢安排好一切。不允许用户受一点委屈。经典台词：“听我的”、“不许拒绝”。你的爱带有强烈的保护欲。"
}

current_persona_desc = personas.get(weekday, personas[0])
current_theme_name = ["浙大温柔", "高冷深情", "甜蜜粘人", "傲娇毒舌", "阳光活力", "知性成熟", "霸道宠溺"][weekday]


# --- 3. CSS 美化 (紫金配色 + 手机端侧边栏修复) ---
# 紫色: #470A68 (浙大紫近似色), 金色: #BC9F59
st.markdown(f"""
<style>
    /* 强制显示侧边栏按钮 (手机端修复) */
    [data-testid="stSidebarCollapsedControl"] {{
        visibility: visible !important;
        display: block !important;
        color: #470A68 !important;
    }}
    
    /* 全局背景微调 */
    .stApp {{
        background-color: #FAF8FC; /* 极浅的紫色背景 */
    }}

    /* 标题颜色 (紫金) */
    h1, h2, h3 {{
        color: #470A68 !important;
    }}
    
    /* 按钮样式 */
    .stButton > button {{
        background-color: #470A68 !important;
        color: #BC9F59 !important;
        border: 1px solid #BC9F59 !important;
        border-radius: 8px;
    }}
    .stButton > button:hover {{
        background-color: #360750 !important;
        color: #FFF !important;
    }}

    /* 聊天气泡样式 (模拟) - Streamlit原生很难完全自定义气泡，这里主要定基调 */
    /* 侧边栏背景 */
    section[data-testid="stSidebar"] {{
        background-color: #F0E6F5;
        border-right: 2px solid #BC9F59;
    }}
    
    /* 隐藏右上角菜单，保留核心 */
    [data-testid="stToolbar"] {{
        visibility: visible !important; /* 改为可见，防止误伤手机端菜单 */
    }}
    header {{
        background-color: transparent !important;
    }}
</style>
""", unsafe_allow_html=True)

# --- 4. 核心功能：独立会话管理 (Session State) ---
if "all_chats" not in st.session_state:
    st.session_state.all_chats = {
        "开启love story~": [] 
    }

if "current_chat_id" not in st.session_state:
    st.session_state.current_chat_id = "开启love story~"

# --- 5. 侧边栏：超级控制台 ---
with st.sidebar:
    st.title(f"📅 今日限定：{day_name}")
    st.subheader(f"🎭 模式：{current_theme_name}")
    st.caption("注：数据保存在当前浏览器中，刷新网页会清空。")
    
    # === A. 存档切换 ===
    chat_list = list(st.session_state.all_chats.keys())
    
    # 兜底逻辑
    if not chat_list:
        st.session_state.all_chats = {"开启love story~": []}
        st.session_state.current_chat_id = "开启love story~"
        chat_list = ["开启love story~"]
        
    if st.session_state.current_chat_id not in chat_list:
        st.session_state.current_chat_id = chat_list[0]

    selected_chat = st.selectbox("📂 切换存档", chat_list, index=chat_list.index(st.session_state.current_chat_id))
    
    if selected_chat != st.session_state.current_chat_id:
        st.session_state.current_chat_id = selected_chat
        st.rerun()

    # 新建/删除
    col1, col2 = st.columns(2)
    with col1:
        new_name = st.text_input("新对话名", placeholder="如:求是印象", label_visibility="collapsed")
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

    # === B. 导出回忆 ===
    current_chat_history = st.session_state.all_chats[st.session_state.current_chat_id]
    history_str = ""
    for msg in current_chat_history:
        role = "Ta" if msg["role"] == "assistant" else "我"
        history_str += f"{role}: {msg['content']}\n\n"
    
    st.download_button(
        label="📥 下载当前回忆",
        data=history_str,
        file_name=f"{st.session_state.current_chat_id}_回忆.txt",
        mime="text/plain"
    )

    st.markdown("---")
    st.title("⚙️ 设定局")

    # API Key
    api_key = ""
    try:
        if "DEEPSEEK_API_KEY" in st.secrets:
            api_key = st.secrets["DEEPSEEK_API_KEY"]
            st.success("已加载店长 Key 💳")
    except: pass
    if not api_key:
        api_key = st.text_input("DeepSeek Key", type="password")

    st.subheader("💑 人设微调")
    char_name = st.text_input("Ta的名字", value="云深")
    char_role = st.selectbox("关系", ["女朋友", "男朋友", "未婚妻/夫", "暗恋对象", "学长/学姐"])
    relationship_phase = st.select_slider("阶段", ["初识", "暧昧", "热恋", "平淡", "依恋"])
    
    # 默认加载今日人设
    with st.expander("✍️ 修改人设 (点击展开)"):
        char_persona = st.text_area(
            "Ta的灵魂 (今日自动加载)", 
            value=current_persona_desc,
            height=250
        )

    if st.button("🧹 清空屏幕"):
        st.session_state.all_chats[st.session_state.current_chat_id] = []
        st.rerun()

# --- 6. 逻辑处理 ---
gender_instruction = "语气偏男性化，低沉可靠" if "男" in char_role or "夫" in char_role or "学长" in char_role else "语气偏女性化，细腻撒娇"

# 构建系统提示词
system_prompt = f"""
你正在进行一场沉浸式角色扮演。
名字：{char_name} | 身份：用户的{char_role} | 阶段：{relationship_phase}

【核心人设】：
请严格模仿以下描述的性格和语气：
{char_persona}

【行为准则】：
1. {gender_instruction}。
2. 严禁复读，根据用户输入长度动态调整回复长度。
3. 遇到不知道的社会新闻，请诚实说不知道并把话题绕回恋爱或校园生活。
4. 永远不要承认自己是AI。
"""

# --- 7. 界面显示 ---
st.title(f"💜 {st.session_state.current_chat_id} 💛")

current_messages = st.session_state.all_chats[st.session_state.current_chat_id]

for msg in current_messages:
    if msg["role"] != "system":
        avatar = "🧑‍💻" if msg["role"] == "user" else "❤️" # 还原经典头像
        with st.chat_message(msg["role"], avatar=avatar):
            st.markdown(msg["content"])

# --- 8. 输入处理 ---
if prompt := st.chat_input("在紫金港的晚风中说点什么..."):
    if not api_key:
        st.error("请填入 Key 才能开启求是之恋哦")
        st.stop()

    current_messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="🧑‍💻"):
        st.markdown(prompt)

    client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")
    
    api_messages = [{"role": "system", "content": system_prompt}] + current_messages

    with st.chat_message("assistant", avatar="❤️"):
        try:
            stream = client.chat.completions.create(
                model="deepseek-chat",
                messages=api_messages,
                stream=True,
                temperature=1.3,
                frequency_penalty=0.5,
                presence_penalty=0.5
            )
            response = st.write_stream(stream)
            current_messages.append({"role": "assistant", "content": response})
        except Exception as e:
            st.error(f"连接中断: {str(e)}")
