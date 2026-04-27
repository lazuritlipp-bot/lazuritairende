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
        bg_css = f"background: url('data:image/png;base64,{bg_b64}') center/cover no-repeat fixed, #0E1117;" if bg_b64 else "background: #0E1117;"
        st.markdown(f"""
            <style>
            [data-testid="stSidebar"], [data-testid="stSidebarCollapsedControl"], header, [data-testid="stHeader"] {{ display: none !important; }}
            .stApp {{ {bg_css} }}
            .block-container {{ padding: 0 !important; max-width: 100% !important; }}
            div[data-testid="stForm"] {{
                position: fixed; top: 50%; left: 50%; transform: translate(-50%, -50%);
                width: 420px; background: rgba(30, 30, 32, 0.82) !important;
                backdrop-filter: blur(14px); border-radius: 22px; padding: 30px !important;
                box-shadow: 0 24px 70px rgba(0, 0, 0, 0.55); border: 1px solid rgba(255, 255, 255, 0.08) !important;
            }}
            div[data-testid="stForm"] input {{ background: rgba(255, 255, 255, 0.06) !important; color: white !important; border-radius: 10px !important; }}
            div[data-testid="stForm"] button {{ background: linear-gradient(90deg, #A78BFA 0%, #F87171 100%) !important; color: white !important; border-radius: 10px !important; height: 50px !important; }}
            </style>
            """, unsafe_allow_html=True)

        with st.form("login_form"):
            if logo_b64: st.markdown(f"<img style='width:300px; display:block; margin: 0 auto 20px;' src='data:image/png;base64,{logo_b64}'>", unsafe_allow_html=True)
            pwd = st.text_input("Код доступа", type="password")
            if st.form_submit_button("Войти", use_container_width=True):
                users_data = st.secrets.get("users", {})
                if pwd in users_data:
                    st.session_state.authenticated = True
                    st.session_state.user_role = users_data[pwd].get("name")
                    st.session_state.user_api_key = users_data[pwd].get("key")
                    st.rerun()
                else: st.error("❌ Ошибка")
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
    "Свой промт": ""
}

PRESET_ICONS = ["studio.png", "den.png", "vecher.png", "acsesoar.png"]
PRESET_NAMES = ["Студия", "День", "Вечер", "Аксессуары"]

if 'history' not in st.session_state: st.session_state.history = []
if 'sel_idx' not in st.session_state: st.session_state.sel_idx = 0
if 'current_prompt' not in st.session_state: st.session_state.current_prompt = PROMPT_PRESETS["Студия"]

# --- СТИЛИ ОСНОВНОГО ИНТЕРФЕЙСА ---
st.markdown(f"""
    <style>
    .stApp {{ background-color: #E8E8E1; }}
    header, [data-testid="stHeader"] {{ display: none !important; }}
    .block-container {{ padding-top: 1.2rem !important; max-width: 100% !important; padding-left: 2rem !important; padding-right: 2rem !important; }}
    
    .custom-header {{ background: white; padding: 15px 30px 45px 30px; border-radius: 12px; position: relative; border: 1px solid #D1D1D1; min-height: 100px; }}
    .header-logo {{ height: 80px !important; position: absolute; right: 30px; top: 50%; transform: translateY(-50%); }}

    /* Кнопка выхода */
    div.element-container:has(.logout-marker) {{ display: none; }}
    div.element-container:has(.logout-marker) + div.element-container {{
        margin-top: -58px !important; margin-left: 30px !important; position: relative; z-index: 100;
    }}
    div.element-container:has(.logout-marker) + div.element-container button {{
        background: transparent !important; color: #666 !important; border: 1px solid #ccc !important; border-radius: 8px !important; height: 32px !important;
    }}

    .card {{ background: #F8F9FA; border-radius: 20px; padding: 20px; border: 1px solid #E0E0E0; margin-bottom: 15px; }}
    .card > b {{ color: #000 !important; }}

    /* --- СТИЛИЗАЦИЯ ИКОНОК И ПРОЗРАЧНЫХ КНОПОК --- */
    
    .preset-wrapper {{
        position: relative;
        width: 70px;
        height: 70px;
        margin: 0 auto;
    }}

    /* Визуальный слой (иконка) */
    .visual-icon {{
        position: absolute;
        inset: 0;
        background: white;
        border: 2px solid #D4C4B0;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 1;
        transition: 0.2s;
    }}
    .preset-wrapper:hover .visual-icon {{ border-color: #B8906D; transform: scale(1.05); }}
    .active-preset .visual-icon {{ border: 2.5px solid #B8906D; box-shadow: 0 0 10px rgba(184, 144, 109, 0.3); }}

    /* Слой кнопки Streamlit (прозрачный поверх) */
    .preset-wrapper .stButton button {{
        position: absolute !important;
        inset: 0 !important;
        width: 70px !important;
        height: 70px !important;
        background: transparent !important;
        color: transparent !important;
        border: none !important;
        box-shadow: none !important;
        z-index: 10 !important;
        padding: 0 !important;
        cursor: pointer !important;
    }}

    /* Свой промт (Овальная кнопка) */
    .custom-prompt-container {{
        position: relative;
        width: 100%;
        height: 50px;
        margin-top: 15px;
    }}
    .visual-custom-box {{
        position: absolute;
        inset: 0;
        background: white;
        border: 2px solid #D4C4B0;
        border-radius: 50px;
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 1;
        font-weight: bold;
        color: #4E5966;
        font-size: 13px;
    }}
    .custom-prompt-container:hover .visual-custom-box {{ border-color: #B8906D; }}
    .active-custom .visual-custom-box {{ border: 2.5px solid #B8906D; }}

    .custom-prompt-container .stButton button {{
        position: absolute !important;
        inset: 0 !important;
        width: 100% !important;
        height: 50px !important;
        background: transparent !important;
        color: transparent !important;
        border: none !important;
        z-index: 10 !important;
    }}

    /* Главная кнопка */
    div.stButton > button[kind="primary"] {{ 
        background: linear-gradient(90deg, #A78BFA 0%, #F87171 100%) !important; 
        color: white !important; height: 55px !important; font-weight: bold !important; border-radius: 16px !important; width: 100% !important;
    }}
    
    .empty-result-card {{ height: 600px; display: flex; flex-direction: column; align-items: center; justify-content: center; color: #888; border: 2px dashed #CCC; border-radius: 24px; }}
    </style>
    """, unsafe_allow_html=True)

# --- ШАПКА ---
logo_b64_main = _read_b64(LOGO_PATH)
st.markdown(f"""
    <div class="custom-header">
        <div style="color: #444; font-size: 18px;"><b>{st.session_state.user_role}!</b> Добро пожаловать в Lazurit AI Render</div>
        <img src="data:image/png;base64,{logo_b64_main}" class="header-logo">
    </div>
    """, unsafe_allow_html=True)

st.markdown('<div class="logout-marker"></div>', unsafe_allow_html=True)
if st.button("🚪 Выйти"):
    for key in list(st.session_state.keys()): del st.session_state[key]
    st.rerun()

# --- РАБОЧАЯ ОБЛАСТЬ ---
col_left, col_main, col_hist = st.columns([1.2, 2.75, 0.45], gap="small")

with col_left:
    st.markdown('<div class="card"><b>1. Загрузка</b>', unsafe_allow_html=True)
    f = st.file_uploader("upload", label_visibility="collapsed")
    if f: st.image(f, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="card"><b>2. Освещение</b>', unsafe_allow_html=True)
    
    # 4 КРУГЛЫЕ КНОПКИ
    cols = st.columns(4)
    for i in range(4):
        with cols[i]:
            active_class = "active-preset" if st.session_state.sel_idx == i else ""
            icon_b64 = _read_b64(PRESET_ICONS[i])
            st.markdown(f"""
                <div class="preset-wrapper {active_class}">
                    <div class="visual-icon">
                        <img src="data:image/png;base64,{icon_b64}" style="width:35px;">
                    </div>
                </div>
                """, unsafe_allow_html=True)
            # Прозрачная кнопка ПОВЕРХ
            if st.button(" ", key=f"btn_{i}"):
                st.session_state.sel_idx = i
                st.session_state.current_prompt = PROMPT_PRESETS[PRESET_NAMES[i]]
                st.rerun()

    # ОВАЛЬНАЯ КНОПКА "СВОЙ ПРОМТ"
    custom_active = "active-custom" if st.session_state.sel_idx == -1 else ""
    svoi_icon_b64 = _read_b64("svoi.png")
    st.markdown(f"""
        <div class="custom-prompt-container {custom_active}">
            <div class="visual-custom-box">
                <img src="data:image/png;base64,{svoi_icon_b64}" style="height:20px; margin-right:10px;">
                СВОЙ ПРОМТ (задание)
            </div>
        </div>
        """, unsafe_allow_html=True)
    if st.button(" ", key="btn_custom"):
        st.session_state.sel_idx = -1
        st.session_state.current_prompt = PROMPT_PRESETS["Свой промт"]
        st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

    user_text = st.text_area("ТЗ промпта:", value=st.session_state.current_prompt, height=200)

    if st.button("ГЕНЕРИРОВАТЬ AI ИЗОБРАЖЕНИЕ", use_container_width=True, type="primary"):
        if f:
            with st.spinner("Генерация..."):
                try:
                    f.seek(0)
                    combined_input = f"{user_text}|||data:image/jpeg;base64,{base64.b64encode(f.read()).decode()}"
                    res = requests.post(BASE_URL, json={"input_value": combined_input, "output_type": "chat", "input_type": "chat"}, 
                                        headers={"Authorization": f"Bearer {APPLICATION_TOKEN}", "x-api-key": APPLICATION_TOKEN, "Content-Type": "application/json"}).json()
                    if 'outputs' in res:
                        msg = res['outputs'][0]['outputs'][0]['results']['message']['text']
                        raw_data = msg.split("|||")[1] if "|||" in msg else msg
                        if "base64," in raw_data: raw_data = raw_data.split("base64,")[1]
                        st.session_state.history.insert(0, base64.b64decode(raw_data.replace('"', '').strip()))
                        st.rerun()
                except Exception as e: st.error(f"Ошибка: {e}")
        else: st.warning("Загрузите фото!")

with col_main:
    if st.session_state.history:
        st.markdown('<div class="card" style="padding: 10px;">', unsafe_allow_html=True)
        st.image(st.session_state.history[0], use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="card empty-result-card"><h1>Результат</h1></div>', unsafe_allow_html=True)

with col_hist:
    st.markdown("<b>История</b>", unsafe_allow_html=True)
    for img in st.session_state.history[1:6]: st.image(img, use_container_width=True)
