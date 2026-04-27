import streamlit as st
import requests
import base64
from streamlit_image_select import image_select

# --- ИНИЦИАЛИЗАЦИЯ ---
st.set_page_config(page_title="LAZURIT AI Render", layout="wide")

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
            if bg_b64
            else "background: #0E1117;"
        )
        st.markdown(
            f"""
            <style>
            [data-testid="stSidebar"], [data-testid="stSidebarCollapsedControl"], header {{ display: none !important; }}
            .stApp {{ {bg_css} }}
            .block-container {{ padding-top: 0 !important; padding-bottom: 0 !important; max-width: 100% !important; }}

            div[data-testid="stForm"] {{
                position: fixed; top: 50%; left: 50%; transform: translate(-50%, -50%);
                width: 420px; max-width: 92vw; height: auto !important; min-height: 0 !important;
                background: rgba(30, 30, 32, 0.82) !important;
                backdrop-filter: blur(14px); -webkit-backdrop-filter: blur(14px);
                border-radius: 22px; padding: 28px 32px 24px !important;
                box-shadow: 0 24px 70px rgba(0, 0, 0, 0.55);
                border: 1px solid rgba(255, 255, 255, 0.08) !important; z-index: 9999;
            }}
            div[data-testid="stForm"] > div, div[data-testid="stForm"] [data-testid="stVerticalBlock"] {{
                height: auto !important; min-height: 0 !important; gap: 0.6rem !important;
            }}
            div[data-testid="stForm"] label {{ color: #FFFFFF !important; font-weight: 500; font-size: 14px; }}
            div[data-testid="stForm"] [data-testid="stTextInput"] > div {{ background: transparent !important; border: none !important; }}
            div[data-testid="stForm"] input {{
                background: rgba(255, 255, 255, 0.06) !important; color: #FFFFFF !important;
                border: 1px solid rgba(255, 255, 255, 0.12) !important; border-radius: 10px !important;
                height: 46px !important; padding: 0 14px !important; width: 100% !important;
            }}
            div[data-testid="stForm"] input::placeholder {{ color: rgba(255, 255, 255, 0.45) !important; }}
            div[data-testid="stForm"] [data-testid="stTextInput"] button {{
                background: transparent !important; color: rgba(255, 255, 255, 0.7) !important;
                border: none !important; box-shadow: none !important; width: auto !important;
                height: auto !important; padding: 0 8px !important;
            }}
            div[data-testid="stForm"] [data-testid="stTextInput"] button:hover {{ background: rgba(255, 255, 255, 0.06) !important; color: #FFFFFF !important; }}
            div[data-testid="stForm"] [data-testid="stTextInput"] button svg {{ fill: currentColor !important; }}

            div[data-testid="stForm"] [data-testid="stFormSubmitButton"] button {{
                background: linear-gradient(90deg, #A78BFA 0%, #F87171 100%) !important;
                color: white !important; border: none !important; height: 50px !important;
                font-weight: 600 !important; font-size: 16px !important; border-radius: 10px !important;
                width: 100% !important; margin-top: 6px; display: block !important;
            }}
            div[data-testid="stForm"] [data-testid="stFormSubmitButton"] button p {{
                width: 100% !important; text-align: center !important; margin: 0 !important;
            }}
            .login-logo {{ display: block; margin: 0 auto 14px; width: 78%; max-width: 320px; }}
            .login-subtitle {{ color: rgba(255, 255, 255, 0.85); text-align: center; font-size: 14px; margin: 0 0 22px; }}
            </style>
            """,
            unsafe_allow_html=True,
        )

        with st.form("login_form", clear_on_submit=False):
            if logo_b64:
                st.markdown(f"<img class='login-logo' src='data:image/png;base64,{logo_b64}' alt='LAZURIT' />", unsafe_allow_html=True)
            else:
                st.markdown("<h2 style='color:#FFFFFF;text-align:center;margin:0 0 12px;'>LAZURIT</h2>", unsafe_allow_html=True)

            st.markdown("<p class='login-subtitle'>Введите ваш персональный код доступа.</p>", unsafe_allow_html=True)

            pwd = st.text_input("Код доступа", type="password", placeholder="Введите код")
            submitted = st.form_submit_button("Войти", use_container_width=True)

            if submitted:
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

# --- СТИЛИ РАБОЧЕЙ ОБЛАСТИ ---
st.markdown("""
    <style>
    .stApp { background-color: #E8E8E1; }
    .block-container { padding-top: 1rem !important; max-width: 100% !important; padding-left: 2rem !important; padding-right: 2rem !important; }
    
    /* ИЗМЕНЕННАЯ ШАПКА - Даем место под кнопку */
    .custom-header { 
        background-color: white; 
        padding: 15px 30px 45px 30px; /* Увеличен отступ снизу для кнопки */
        border-radius: 12px; 
        position: relative; /* Чтобы логотип зафиксировать абсолютно */
        margin-bottom: 0px; 
        border: 1px solid #D1D1D1; 
        min-height: 100px; 
    }
    .header-logo { 
        height: 80px !important; 
        width: auto !important; 
        max-width: 250px; 
        object-fit: contain; 
        position: absolute;
        right: 30px;
        top: 50%;
        transform: translateY(-50%); /* Логотип всегда строго по центру справа */
    }
    
    /* МАГИЯ: ТЯНЕМ КНОПКУ ВЫХОДА ВНУТРЬ ШАПКИ */
    div.element-container:has(.logout-marker) { display: none; }
    div.element-container:has(.logout-marker) + div.element-container {
        margin-top: -60px !important; /* Тянем кнопку вверх, внутрь шапки */
        margin-left: 30px !important; /* Выравниваем по тексту */
        margin-bottom: 25px !important; /* Отступ до нижних блоков */
        position: relative;
        z-index: 10;
        width: fit-content;
    }
    div.element-container:has(.logout-marker) + div.element-container button {
        background: transparent !important;
        color: #888 !important;
        border: 1px solid #ccc !important;
        border-radius: 6px !important;
        min-height: 30px !important;
        height: 30px !important;
        padding: 0 12px !important;
        font-size: 13px !important;
        transition: all 0.2s;
    }
    div.element-container:has(.logout-marker) + div.element-container button:hover {
        background: #FF4B4B !important;
        color: white !important;
        border-color: #FF4B4B !important;
    }

    /* ОСТАЛЬНЫЕ СТИЛИ */
    .card { background-color: #F8F9FA; border-radius: 15px; padding: 20px; border: 1px solid #E0E0E0; margin-bottom: 15px; }
    .card > b { color: #000000 !important; }
    div[data-testid="stHorizontalBlock"] button { background-color: #FFFFFF !important; color: #333 !important; border: 1px solid #CCC !important; font-size: 12px !important; padding: 4px 6px !important; }
    iframe[title*="streamlit_image_select"] { background: transparent !important; }
    div.stButton > button:first-child[kind="primary"] { background: linear-gradient(90deg, #A78BFA 0%, #F87171 100%) !important; color: white !important; border: none !important; height: 55px !important; font-size: 18px !important; font-weight: bold !important; }
    .empty-result-card { height: 600px; display: flex; flex-direction: column; align-items: center; justify-content: center; color: #888; border: 2px dashed #CCC; }
    </style>
    """, unsafe_allow_html=True)

# --- ПРОМПТЫ ---
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

if 'history' not in st.session_state: st.session_state.history = []
if 'current_prompt' not in st.session_state: st.session_state.current_prompt = next(iter(PROMPT_PRESETS.values()))
if 'last_response' not in st.session_state: st.session_state.last_response = ""

def process_image(img_b64, user_prompt):
    combined_input = f"{user_prompt}|||data:image/jpeg;base64,{img_b64}"
    payload = {"input_value": combined_input, "output_type": "chat", "input_type": "chat"}
    headers = {"Authorization": f"Bearer {APPLICATION_TOKEN}", "x-api-key": APPLICATION_TOKEN, "Content-Type": "application/json"}
    return requests.post(BASE_URL, json=payload, headers=headers).json()

# --- ШАПКА (чистый HTML, логотип закреплен справа) ---
logo_b64_main = _read_b64(LOGO_PATH)
st.markdown(f"""
    <div class="custom-header">
        <div style="color: #444; font-size: 18px; margin-bottom: 5px;"><b>{st.session_state.user_role}!</b> Добро пожаловать в Lazurit AI Render</div>
        <img src="data:image/png;base64,{logo_b64_main}" class="header-logo">
    </div>
    """, unsafe_allow_html=True)

# --- КНОПКА ВЫХОДА (втягивается внутрь шапки через CSS-маркер) ---
st.markdown('<div class="logout-marker"></div>', unsafe_allow_html=True)
if st.button("🚪 Выйти", key="logout_btn"):
    logout()

# --- РАБОЧАЯ ОБЛАСТЬ ---
col_left, col_main, col_hist = st.columns([2.2, 2.2, 0.6])

with col_left:
    st.markdown('<div class="card"><b>1. Загрузка</b>', unsafe_allow_html=True)
    f = st.file_uploader("upload", label_visibility="collapsed")
    if f: st.image(f, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="card"><b>2. Освещение</b>', unsafe_allow_html=True)
    PRESET_NAMES = ["Студия", "День", "Вечер", "Аксессуары"]
    PRESET_PATHS = [
        "icons/studio.png",
        "icons/den.png",
        "icons/vecher.png",
        "icons/acsesoar.png",
    ]

    selected_idx = image_select(
        label="",
        images=PRESET_PATHS,
        captions=None,
        use_container_width=False,
        return_value="index",
        key="preset_image_select",
    )

    if selected_idx is not None and st.session_state.get("_preset_idx") != selected_idx:
        st.session_state.current_prompt = PROMPT_PRESETS[PRESET_NAMES[selected_idx]]
        st.session_state._preset_idx = selected_idx
        st.rerun()

    if st.button("Свой промт", key="custom_prompt_btn", use_container_width=True):
        st.session_state.current_prompt = PROMPT_PRESETS.get("Свой промт", "")
        st.session_state._preset_idx = None
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    user_text = st.text_area("ТЗ промпта:", value=st.session_state.current_prompt, height=200)

    if st.button("ГЕНЕРИРОВАТЬ AI ИЗОБРАЖЕНИЕ", use_container_width=True, type="primary"):
        if f:
            with st.spinner("Генерация..."):
                try:
                    f.seek(0)
                    res = process_image(image_to_base64(f.read()), user_text)
                    if 'outputs' in res:
                        msg = res['outputs'][0]['outputs'][0]['results']['message']['text']
                        st.session_state.last_response = msg
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
