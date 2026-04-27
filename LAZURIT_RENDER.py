import streamlit as st
import requests
import base64

# --- ИНИЦИАЛИЗАЦИЯ ---
st.set_page_config(page_title="LAZURIT AI Render", layout="wide", initial_sidebar_state="collapsed")

# Обработка выхода
if st.query_params.get("logout") == "true":
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.query_params.clear()
    st.rerun()

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
    return base64.b64encode(image_bytes).decode('utf-8')

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
            [data-testid="stSidebar"], [data-testid="stSidebarCollapsedControl"], header, [data-testid="stHeader"] {{ display: none !important; }}
            .stApp {{ {bg_css} }}
            .block-container {{ padding-top: 0 !important; padding-bottom: 0 !important; max-width: 100% !important; }}
            </style>
            """, unsafe_allow_html=True)

        with st.form("login_form", clear_on_submit=False):
            if logo_b64:
                st.markdown(f"<img class='login-logo' src='data:image/png;base64,{logo_b64}' alt='LAZURIT' />", unsafe_allow_html=True)
            st.markdown("<p class='login-subtitle'>Введите ваш персональный код доступа.</p>", unsafe_allow_html=True)
            pwd = st.text_input("Код доступа", type="password", placeholder="Введите код")
            if st.form_submit_button("Войти", use_container_width=True):
                users_data = st.secrets.get("users", {})
                if pwd in users_data:
                    user_info = users_data[pwd]
                    st.session_state.authenticated = True
                    st.session_state.user_role = user_info.get("name", "Сотрудник")
                    st.session_state.user_api_key = user_info.get("key", "")
                    st.rerun()
                else:
                    st.error("❌ Код не опознан")
        st.stop()

check_password()
APPLICATION_TOKEN = st.session_state.user_api_key

# --- ФУНКЦИЯ ВЫХОДА ---
def logout():
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()

# --- СТИЛИ ---
st.markdown("""
    <style>
    .stApp { background-color: #E8E8E1; }
    header, [data-testid="stHeader"], [data-testid="stToolbar"] { display: none !important; }

    .block-container { padding-top: 1.2rem !important; max-width: 100% !important; padding-left: 2rem !important; padding-right: 2rem !important; }

    .custom-header { 
        background-color: white; 
        padding: 15px 30px 45px 30px; 
        border-radius: 12px; 
        position: relative; 
        margin-bottom: 20px; 
        border: 1px solid #D1D1D1; 
        min-height: 100px; 
    }
    .header-logo { 
        height: 80px !important; 
        position: absolute; right: 30px; top: 50%; transform: translateY(-50%);
    }

    .card { background-color: #F8F9FA; border-radius: 20px; padding: 20px; border: 1px solid #E0E0E0; margin-bottom: 15px; }
    .card > b { color: #000000 !important; }

    /* === КРУГЛЫЕ ИКОНКИ + ПРОЗРАЧНЫЕ КНОПКИ ПОВЕРХ === */
    .preset-grid {
        display: flex;
        gap: 16px;
        justify-content: center;
        margin: 15px 0 10px 0;
        position: relative;
    }
    .icon-wrapper {
        position: relative;
        width: 78px;
        height: 78px;
    }
    .icon-bg {
        width: 78px;
        height: 78px;
        background: white;
        border: 2px solid #D4C4B0;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: 0 4px 12px rgba(0,0,0,0.06);
        transition: all 0.2s;
    }
    .icon-bg.active {
        border-color: #B8906D;
        box-shadow: 0 0 0 4px rgba(184, 144, 109, 0.15);
    }
    .icon-bg img {
        width: 38px;
        height: 38px;
        object-fit: contain;
    }

    /* Прозрачная кнопка строго поверх иконки */
    .icon-wrapper button {
        position: absolute !important;
        top: 0 !important;
        left: 0 !important;
        width: 100% !important;
        height: 100% !important;
        opacity: 0 !important;
        z-index: 10 !important;
        border-radius: 50% !important;
    }

    /* Кнопка "Свой промт" */
    .custom-prompt-wrapper {
        position: relative;
        margin: 12px 0 8px 0;
    }
    .custom-prompt-bg {
        width: 100%;
        height: 52px;
        background: white;
        border: 2px solid #D4C4B0;
        border-radius: 999px;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 10px;
        font-weight: 600;
        color: #444;
        box-shadow: 0 4px 12px rgba(0,0,0,0.06);
    }
    .custom-prompt-bg img {
        height: 24px;
    }
    .custom-prompt-wrapper button {
        position: absolute !important;
        top: 0 !important;
        left: 0 !important;
        width: 100% !important;
        height: 100% !important;
        opacity: 0 !important;
        z-index: 10 !important;
        border-radius: 999px !important;
    }

    div.stButton > button:first-child[kind="primary"] {
        background: linear-gradient(90deg, #A78BFA 0%, #F87171 100%) !important;
        color: white !important;
        height: 56px !important;
        font-size: 17px !important;
        font-weight: bold !important;
        border-radius: 16px !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- ПРОМПТЫ ---
BASE_PHOTO_PROMPT = "Masterpiece, 8k resolution, photorealistic interior photography, Architectural Digest style. Maintain the original color palette and materials of the furniture strictly. Enhance existing textures (wood grain, stone, fabric) without changing their color. Replace flat lighting with professional cinematic studio lighting and realistic global illumination. Add natural soft sunlight and deep realistic shadows to create depth. High-contrast, sharp details, realistic reflections."

PROMPT_PRESETS = {
    "Студия": f"Professional architectural studio lighting, balanced fills. {BASE_PHOTO_PROMPT}",
    "День": f"Natural bright daylight from windows, soft sun rays. {BASE_PHOTO_PROMPT}",
    "Вечер": f"Warm cozy evening light, mix of interior lamps and dusk. {BASE_PHOTO_PROMPT}",
    "Аксессуары": f"{BASE_PHOTO_PROMPT}",
    "Свой промт": "",
}

if 'history' not in st.session_state: st.session_state.history = []
if 'current_prompt' not in st.session_state: st.session_state.current_prompt = PROMPT_PRESETS["Студия"]
if 'selected_idx' not in st.session_state: st.session_state.selected_idx = 0
if 'last_response' not in st.session_state: st.session_state.last_response = ""

def process_image(img_b64, user_prompt):
    combined_input = f"{user_prompt}|||data:image/jpeg;base64,{img_b64}"
    payload = {"input_value": combined_input, "output_type": "chat", "input_type": "chat"}
    headers = {"Authorization": f"Bearer {APPLICATION_TOKEN}", "x-api-key": APPLICATION_TOKEN, "Content-Type": "application/json"}
    return requests.post(BASE_URL, json=payload, headers=headers).json()

# --- ШАПКА ---
logo_b64_main = _read_b64(LOGO_PATH)
st.markdown(f"""
    <div class="custom-header">
        <div style="color: #444; font-size: 18px;"><b>{st.session_state.user_role}!</b> Добро пожаловать в Lazurit AI Render</div>
        <img src="data:image/png;base64,{logo_b64_main}" class="header-logo">
    </div>
    """, unsafe_allow_html=True)

st.markdown('<div class="logout-marker"></div>', unsafe_allow_html=True)
if st.button("🚪 Выйти", key="logout_btn"):
    logout()

# --- ОСНОВНОЙ ИНТЕРФЕЙС ---
col_left, col_main, col_hist = st.columns([1.1, 3.0, 0.6])

with col_left:
    st.markdown('<div class="card"><b>1. Загрузка</b>', unsafe_allow_html=True)
    f = st.file_uploader("upload", label_visibility="collapsed")
    if f: st.image(f, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="card"><b>2. Освещение</b>', unsafe_allow_html=True)

    # === 4 КРУГЛЫЕ ИКОНКИ ===
    preset_icons = ["icons/studio.png", "icons/den.png", "icons/vecher.png", "icons/acsesoar.png"]
    preset_names = ["Студия", "День", "Вечер", "Аксессуары"]

    st.markdown('<div class="preset-grid">', unsafe_allow_html=True)
    for i, (icon_path, name) in enumerate(zip(preset_icons, preset_names)):
        icon_b64 = _read_b64(icon_path)
        active = "active" if st.session_state.selected_idx == i else ""
        
        st.markdown(f"""
            <div class="icon-wrapper">
                <div class="icon-bg {active}">
                    <img src="data:image/png;base64,{icon_b64}" alt="{name}">
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        if st.button(" ", key=f"preset_{i}"):
            st.session_state.selected_idx = i
            st.session_state.current_prompt = PROMPT_PRESETS[name]
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    # === КНОПКА "СВОЙ ПРОМТ" ===
    svoi_b64 = _read_b64("svoi.png")
    custom_active = "active" if st.session_state.selected_idx == -1 else ""
    
    st.markdown(f"""
        <div class="custom-prompt-wrapper">
            <div class="custom-prompt-bg {custom_active}">
                <img src="data:image/png;base64,{svoi_b64}" alt="Свой промт">
                <span>СВОЙ ПРОМТ (задание)</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    if st.button(" ", key="custom_btn"):
        st.session_state.selected_idx = -1
        st.session_state.current_prompt = PROMPT_PRESETS["Свой промт"]
        st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

    user_text = st.text_area("ТЗ промпта:", value=st.session_state.current_prompt, height=180)

    if st.button("ГЕНЕРИРОВАТЬ AI ИЗОБРАЖЕНИЕ", use_container_width=True, type="primary"):
        if f:
            with st.spinner("Генерация..."):
                try:
                    f.seek(0)
                    res = process_image(image_to_base64(f.read()), user_text)
                    if 'outputs' in res:
                        msg = res['outputs'][0]['outputs'][0]['results']['message']['text']
                        raw_data = msg.split("|||")[1] if "|||" in msg else msg
                        if "base64," in raw_data: raw_data = raw_data.split("base64,")[1]
                        img_bytes = base64.b64decode(raw_data.replace('"', '').strip())
                        st.session_state.history.insert(0, img_bytes)
                        st.rerun()
                except Exception as e:
                    st.error(f"Ошибка: {e}")
        else:
            st.warning("Загрузите фото!")

with col_main:
    if st.session_state.history:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.image(st.session_state.history[0], use_container_width=True, caption="Результат")
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.markdown("""
            <div class="card empty-result-card">
                <h1 style="color:#bbb;">Результат генерации</h1>
                <p style="color:#aaa;">Загрузите изображение для начала работы</p>
            </div>
            """, unsafe_allow_html=True)

with col_hist:
    st.markdown("<b>История</b>", unsafe_allow_html=True)
    for img in st.session_state.history[1:6]:
        st.image(img, use_container_width=True)

if st.session_state.get("last_response"):
    with st.expander("🛠 Лог"):
        st.text(st.session_state.last_response)
