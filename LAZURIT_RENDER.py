import streamlit as st
import requests
import base64

# --- ИНИЦИАЛИЗАЦИЯ ---
st.set_page_config(page_title="LAZURIT AI Render", layout="wide", initial_sidebar_state="collapsed")

# --- КОНФИГУРАЦИЯ ---
BASE_URL = "https://lzrt-nocode.gpt.mws.ru/api/v1/run/bf1dc235-5c36-4bba-8d7e-a88cd5e19bd6?stream=false"
LOGO_PATH = "logo2.png"
BACKGROUND_PATH = "background.png"

@st.cache_data
def _read_b64(path):
    try:
        with open(path, "rb") as fh:
            return base64.b64encode(fh.read()).decode()
    except Exception:
        return ""

def image_to_base64(image_bytes):
    return base64.b64encode(image_bytes).decode("utf-8")

# --- ЭКРАН ВХОДА ---
def check_password():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
        st.session_state.user_role = ""
        st.session_state.user_api_key = ""

    if not st.session_state.authenticated:
        bg_b64 = _read_b64(BACKGROUND_PATH)
        logo_b64 = _read_b64(LOGO_PATH)
        bg_css = (
            f"background: url('data:image/png;base64,{bg_b64}') center/cover no-repeat fixed, #0E1117;"
            if bg_b64 else "background: #0E1117;"
        )
        st.markdown(f"""
            <style>
            [data-testid="stSidebar"], [data-testid="stSidebarCollapsedControl"], header, [data-testid="stHeader"] {{
                display: none !important;
            }}
            .stApp {{ {bg_css} }}
            .block-container {{ padding: 0 !important; max-width: 100% !important; }}
            div[data-testid="stForm"] {{
                position: fixed; top: 50%; left: 50%; transform: translate(-50%, -50%);
                width: 420px; max-width: 92vw; height: auto !important; min-height: 0 !important;
                background: rgba(30, 30, 32, 0.82) !important;
                backdrop-filter: blur(14px); border-radius: 22px; padding: 28px 32px 24px !important;
                box-shadow: 0 24px 70px rgba(0, 0, 0, 0.55);
                border: 1px solid rgba(255, 255, 255, 0.08) !important; z-index: 9999;
            }}
            div[data-testid="stForm"] label {{ color: #FFFFFF !important; }}
            div[data-testid="stForm"] input {{
                background: rgba(255,255,255,0.06) !important; color: white !important;
                border: 1px solid rgba(255,255,255,0.12) !important; border-radius: 10px !important;
                height: 46px !important;
            }}
            div[data-testid="stForm"] [data-testid="stFormSubmitButton"] button {{
                background: linear-gradient(90deg, #A78BFA 0%, #F87171 100%) !important;
                color: white !important; border: none !important; height: 50px !important;
                border-radius: 10px !important; width: 100% !important;
            }}
            .login-logo {{ display: block; margin: 0 auto 14px; width: 78%; max-width: 320px; }}
            .login-subtitle {{ color: rgba(255,255,255,0.85); text-align: center; font-size: 14px; margin: 0 0 22px; }}
            </style>""", unsafe_allow_html=True)

        with st.form("login_form", clear_on_submit=False):
            if logo_b64:
                st.markdown(f"<img class='login-logo' src='data:image/png;base64,{logo_b64}'>", unsafe_allow_html=True)
            st.markdown("<p class='login-subtitle'>Введите ваш персональный код доступа.</p>", unsafe_allow_html=True)
            pwd = st.text_input("Код доступа", type="password", placeholder="Введите код")
            if st.form_submit_button("Войти", use_container_width=True):
                users_data = st.secrets.get("users", {})
                if pwd in users_data:
                    ui = users_data[pwd]
                    st.session_state.authenticated = True
                    st.session_state.user_role = ui.get("name", "Сотрудник")
                    st.session_state.user_api_key = ui.get("key", "")
                    st.rerun()
                else:
                    st.error("❌ Код не опознан")
        st.stop()

check_password()
APPLICATION_TOKEN = st.session_state.user_api_key

def logout():
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()

# --- ДАННЫЕ ---
BASE_PHOTO_PROMPT = (
    "Masterpiece, 8k resolution, photorealistic interior photography, Architectural Digest style. "
    "Maintain the original color palette and materials of the furniture strictly. "
    "Enhance existing textures (wood grain, stone, fabric) without changing their color. "
    "Replace flat lighting with professional cinematic studio lighting and realistic global illumination. "
    "Add natural soft sunlight and deep realistic shadows to create depth. "
    "High-contrast, sharp details, realistic reflections."
)

PROMPT_PRESETS = {
    "Студия": f"Professional architectural studio lighting, balanced fills. {BASE_PHOTO_PROMPT}",
    "День": f"Natural bright daylight from windows, soft sun rays. {BASE_PHOTO_PROMPT}",
    "Вечер": f"Warm cozy evening light, mix of interior lamps and dusk. {BASE_PHOTO_PROMPT}",
    "Аксессуары": f"{BASE_PHOTO_PROMPT}",
    "Свой промт": "",
}

PRESET_NAMES = ["Студия", "День", "Вечер", "Аксессуары"]
PRESET_ICONS = ["studio.png", "den.png", "vecher.png", "acsesoar.png"]

if "history" not in st.session_state: st.session_state.history = []
if "sel_idx" not in st.session_state: st.session_state.sel_idx = 0
if "prompt_text" not in st.session_state: st.session_state.prompt_text = PROMPT_PRESETS[PRESET_NAMES[0]]
if "last_response" not in st.session_state: st.session_state.last_response = ""

def process_image(img_b64_val, user_prompt):
    combined_input = f"{user_prompt}|||data:image/jpeg;base64,{img_b64_val}"
    payload = {"input_value": combined_input, "output_type": "chat", "input_type": "chat"}
    headers = {"Authorization": f"Bearer {APPLICATION_TOKEN}", "x-api-key": APPLICATION_TOKEN, "Content-Type": "application/json"}
    return requests.post(BASE_URL, json=payload, headers=headers).json()

# --- CSS ДЛЯ ИКОНОК: используем селектор button[key="..."] ---
icon_css_parts = []
for i in range(4):
    b64 = _read_b64(PRESET_ICONS[i])
    if not b64:
        continue
    key_name = f"preset_btn_{i}"
    is_active = (st.session_state.sel_idx == i)
    border_color = "#B8906D" if is_active else "#D4C4B0"
    border_width = "2.5px" if is_active else "1.5px"
    shadow = "0 0 0 3px rgba(184,144,109,0.15)" if is_active else "0 4px 12px rgba(0,0,0,0.04)"

    icon_css_parts.append(f"""
    div.stButton:has(button[key="{key_name}"]) button {{
        width: 70px !important;
        height: 70px !important;
        min-height: 70px !important;
        border-radius: 50% !important;
        background-image: url('data:image/png;base64,{b64}') !important;
        background-size: 36px 36px !important;
        background-repeat: no-repeat !important;
        background-position: center center !important;
        background-color: #FFFFFF !important;
        border: {border_width} solid {border_color} !important;
        box-shadow: {shadow} !important;
        color: transparent !important;
        font-size: 0px !important;
        line-height: 0 !important;
        padding: 0 !important;
        overflow: hidden !important;
        transition: all 0.2s ease !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
    }}
    div.stButton:has(button[key="{key_name}"]) button p {{
        display: none !important;
    }}
    div.stButton:has(button[key="{key_name}"]) button:hover {{
        border-color: #B8906D !important;
        transform: scale(1.05) !important;
        box-shadow: 0 6px 16px rgba(0,0,0,0.1) !important;
    }}
    """)

icon_css = "\n".join(icon_css_parts)

# CSS для кнопки "Свой промт"
svoi_b64 = _read_b64("svoi.png")
custom_active = st.session_state.sel_idx == -1
custom_border = "#B8906D" if custom_active else "#D4C4B0"
custom_shadow = "0 0 0 3px rgba(184,144,109,0.15)" if custom_active else "none"

svoi_bg_css = ""
if svoi_b64:
    svoi_bg_css = f"""
        background-image: url('data:image/png;base64,{svoi_b64}') !important;
        background-size: 20px !important;
        background-repeat: no-repeat !important;
        background-position: 16px center !important;
        padding-left: 44px !important;
    """

logo_b64_main = _read_b64(LOGO_PATH)

st.markdown(f"""
    <style>
    .stApp {{ background-color: #E8E8E1; }}
    header, [data-testid="stHeader"], [data-testid="stToolbar"] {{
        display: none !important; visibility: hidden !important; height: 0 !important;
    }}
    .block-container {{
        padding-top: 1.2rem !important; max-width: 100% !important;
        padding-left: 2rem !important; padding-right: 2rem !important;
    }}

    .custom-header {{
        background: white; padding: 15px 30px 45px 30px; border-radius: 12px;
        position: relative; border: 1px solid #D1D1D1; min-height: 100px;
    }}
    .header-logo {{
        height: 80px !important; position: absolute; right: 30px;
        top: 50%; transform: translateY(-50%);
    }}

    div.element-container:has(.logout-marker) {{ display: none; }}
    div.element-container:has(.logout-marker) + div.element-container {{
        margin-top: -58px !important; margin-left: 30px !important;
        margin-bottom: 25px !important; position: relative; z-index: 10; width: fit-content;
    }}
    div.element-container:has(.logout-marker) + div.element-container button {{
        background: transparent !important; color: #666 !important;
        border: 1px solid #ccc !important; border-radius: 8px !important; height: 32px !important;
    }}
    div.element-container:has(.logout-marker) + div.element-container button:hover {{
        background: #FF4B4B !important; color: white !important;
    }}

    .card {{
        background: #F8F9FA; border-radius: 20px; padding: 20px;
        border: 1px solid #E0E0E0; margin-bottom: 15px;
    }}
    .card > b {{ color: #000 !important; }}
    div[data-testid="stTextArea"] textarea {{ border-radius: 16px !important; }}

    /* КРУГЛЫЕ ИКОНКИ-КНОПКИ */
    {icon_css}

    /* КНОПКА СВОЙ ПРОМТ */
    div.stButton:has(button[key="custom_prompt_btn"]) button {{
        width: 100% !important;
        height: 48px !important;
        border-radius: 999px !important;
        background-color: #FFFFFF !important;
        border: 2px solid {custom_border} !important;
        box-shadow: {custom_shadow} !important;
        color: #4E5966 !important;
        font-weight: 700 !important;
        font-size: 13px !important;
        transition: all 0.2s !important;
        text-align: center !important;
        {svoi_bg_css}
    }}
    div.stButton:has(button[key="custom_prompt_btn"]) button:hover {{
        border-color: #B8906D !important;
        color: #B8906D !important;
    }}

    /* КНОПКА ГЕНЕРАЦИИ */
    button[kind="primary"] {{
        background: linear-gradient(90deg, #A78BFA 0%, #F87171 100%) !important;
        color: white !important; height: 55px !important; font-weight: bold !important;
        border-radius: 16px !important; font-size: 17px !important;
    }}

    .empty-result-card {{
        height: 600px; display: flex; flex-direction: column;
        align-items: center; justify-content: center; color: #888;
        border: 2px dashed #CCC; border-radius: 24px;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- ШАПКА ---
st.markdown(f"""
    <div class="custom-header">
        <div style="color: #444; font-size: 18px;"><b>{st.session_state.user_role}!</b> Добро пожаловать в Lazurit AI Render</div>
        <img src="data:image/png;base64,{logo_b64_main}" class="header-logo">
    </div>
    """, unsafe_allow_html=True)

st.markdown('<div class="logout-marker"></div>', unsafe_allow_html=True)
if st.button("🚪 Выйти", key="logout_btn"):
    logout()

# --- РАБОЧАЯ ОБЛАСТЬ ---
col_left, col_main, col_hist = st.columns([1.2, 2.75, 0.45], gap="small")

with col_left:
    st.markdown('<div class="card"><b>1. Загрузка</b>', unsafe_allow_html=True)
    f = st.file_uploader("upload", label_visibility="collapsed")
    if f:
        st.image(f, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="card"><b>2. Освещение</b>', unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4, gap="small")
    for i, col in enumerate([c1, c2, c3, c4]):
        with col:
            if st.button(PRESET_NAMES[i], key=f"preset_btn_{i}"):
                st.session_state.sel_idx = i
                st.session_state.prompt_text = PROMPT_PRESETS[PRESET_NAMES[i]]
                st.rerun()

    if st.button("СВОЙ ПРОМТ (задание)", key="custom_prompt_btn", use_container_width=True):
        st.session_state.sel_idx = -1
        st.session_state.prompt_text = PROMPT_PRESETS["Свой промт"]
        st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)

    user_text = st.text_area("ТЗ промпта:", key="prompt_text", height=200)

    if st.button("ГЕНЕРИРОВАТЬ AI ИЗОБРАЖЕНИЕ", use_container_width=True, type="primary"):
        if f:
            with st.spinner("Генерация..."):
                try:
                    f.seek(0)
                    res = process_image(image_to_base64(f.read()), user_text)
                    if "outputs" in res:
                        msg = res["outputs"][0]["outputs"][0]["results"]["message"]["text"]
                        st.session_state.last_response = msg
                        raw_data = msg.split("|||")[1] if "|||" in msg else msg
                        if "base64," in raw_data:
                            raw_data = raw_data.split("base64,")[1]
                        img_bytes = base64.b64decode(raw_data.replace('"', "").strip())
                        st.session_state.history.insert(0, img_bytes)
                        st.session_state.history = st.session_state.history[:10]
                        st.rerun()
                    else:
                        st.error("API не вернул изображение.")
                        st.session_state.last_response = str(res)
                except Exception as e:
                    st.error(f"Ошибка: {e}")
        else:
            st.warning("Загрузите фото!")

with col_main:
    if st.session_state.history:
        st.markdown('<div class="card" style="padding: 10px;">', unsafe_allow_html=True)
        st.image(st.session_state.history[0], use_container_width=True, caption="Результат")
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.markdown("""
            <div class="card empty-result-card">
                <h1 style="color: #bbb; font-weight: bold;">Результат генерации</h1>
                <p style="color: #ccc;">Загрузите изображение для начала работы</p>
            </div>
        """, unsafe_allow_html=True)

with col_hist:
    st.markdown("<b>История</b>", unsafe_allow_html=True)
    for img in st.session_state.history[1:6]:
        st.image(img, use_container_width=True)

if st.session_state.last_response:
    with st.expander("🛠 Лог"):
        st.text(st.session_state.last_response)
