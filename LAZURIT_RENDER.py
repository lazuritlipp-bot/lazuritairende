import streamlit as st
import requests
import base64
from streamlit_image_select import image_select

# --- КОНФИГУРАЦИЯ ---
st.set_page_config(page_title="LAZURIT AI Render", layout="wide")

BASE_URL = "https://lzrt-nocode.gpt.mws.ru/api/v1/run/bf1dc235-5c36-4bba-8d7e-a88cd5e19bd6?stream=false"
LOGO_PATH = "logo2.png"
BACKGROUND_PATH = "background.png"

# --- ФУНКЦИИ ПОМОЩНИКИ ---
@st.cache_data
def _read_b64(path):
    try:
        with open(path, "rb") as fh:
            return base64.b64encode(fh.read()).decode()
    except Exception:
        return ""

def image_to_base64(image_bytes):
    return base64.b64encode(image_bytes).decode('utf-8')

def process_image(img_b64, user_prompt):
    combined_input = f"{user_prompt}|||data:image/jpeg;base64,{img_b64}"
    payload = {"input_value": combined_input, "output_type": "chat", "input_type": "chat"}
    headers = {
        "Authorization": f"Bearer {APPLICATION_TOKEN}", 
        "x-api-key": APPLICATION_TOKEN, 
        "Content-Type": "application/json"
    }
    return requests.post(BASE_URL, json=payload, headers=headers, timeout=180).json()

# --- ЭКРАН АВТОРИЗАЦИИ ---
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
        [data-testid="stSidebar"], [data-testid="stSidebarCollapsedControl"], header {{ display: none !important; }}
        .stApp {{ {bg_css} }}
        .block-container {{ padding-top: 0 !important; max-width: 100% !important; }}
        
        /* Карточка входа */
        div[data-testid="stForm"] {{
            position: fixed; top: 50%; left: 50%; transform: translate(-50%, -50%);
            width: 420px; max-width: 92vw;
            background: rgba(30, 30, 32, 0.92);
            backdrop-filter: blur(16px);
            border-radius: 20px;
            padding: 35px !important;
            border: 1px solid rgba(255,255,255,0.1);
            box-shadow: 0 20px 50px rgba(0,0,0,0.5);
            z-index: 999;
        }}
        /* Стили инпута */
        div[data-testid="stForm"] input {{
            background: rgba(255,255,255,0.08) !important;
            color: white !important;
            border: 1px solid rgba(255,255,255,0.15) !important;
            border-radius: 10px;
            height: 48px;
        }}
        div[data-testid="stForm"] label {{
            color: #ddd;
            font-size: 14px;
        }}
        /* Кнопка Войти на всю ширину */
        div[data-testid="stFormSubmitButton"] button {{
            width: 100% !important;
            height: 50px !important;
            background: linear-gradient(90deg, #A78BFA, #F87171) !important;
            color: white !important;
            border: none !important;
            border-radius: 10px !important;
            font-weight: 600;
            margin-top: 20px;
        }}
        .login-logo {{ display: block; margin: 0 auto 25px; max-width: 200px; width: 80%; }}
        </style>
        """, unsafe_allow_html=True)

        with st.form("login_form", clear_on_submit=False):
            if logo_b64:
                st.markdown(f"<img src='data:image/png;base64,{logo_b64}' class='login-logo'>", unsafe_allow_html=True)
            
            st.markdown("<p style='text-align:center; color:#aaa; margin-bottom:20px;'>Введите код доступа</p>", unsafe_allow_html=True)
            
            pwd = st.text_input("Код", type="password")
            
            if st.form_submit_button("Войти", use_container_width=True):
                users_data = st.secrets.get("users", {})
                if pwd in users_data:
                    u = users_data[pwd]
                    st.session_state.authenticated = True
                    st.session_state.user_role = u.get("name", "User")
                    st.session_state.user_api_key = u.get("key", "")
                    st.rerun()
                else:
                    st.error("❌ Неверный код")
        st.stop()

check_password()
APPLICATION_TOKEN = st.session_state.user_api_key

# --- ГЛОБАЛЬНЫЕ СТИЛИ ДЛЯ ОСНОВНОГО ИНТЕРФЕЙСА ---
st.markdown("""
<style>
    /* Фон */
    .stApp { background-color: #F3F4F6; }
    
    /* Убираем отступы сверху */
    .block-container { padding-top: 1rem !important; padding-bottom: 2rem !important; max-width: 100% !important; }
    
    /* ШАПКА: Используем Flex, чтобы колонки стояли ровно */
    .main-header-wrapper {
        background-color: white;
        padding: 18px 30px;
        border-radius: 16px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 24px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.03);
        border: 1px solid #E5E7EB;
        height: 90px;
    }

    /* Текст слева */
    .header-text h1 { margin: 0; font-size: 22px; color: #111827; }
    .header-text p { margin: 4px 0 0 0; font-size: 14px; color: #6B7280; }

    /* Блок справа (Логотип + Выход) */
    .header-right-block {
        display: flex;
        align-items: center;
        gap: 25px;
        height: 100%;
    }
    
    .header-logo-img {
        height: 65px !important;
        object-fit: contain;
    }

    /* Кнопка выхода */
    .btn-logout-small {
        background-color: transparent;
        color: #9CA3AF;
        border: 1px solid #E5E7EB;
        padding: 8px 20px;
        border-radius: 12px;
        cursor: pointer;
        font-size: 13px;
        transition: all 0.2s;
        white-space: nowrap;
    }
    .btn-logout-small:hover {
        background-color: #FEF2F2;
        color: #EF4444;
        border-color: #FECACA;
    }

    /* Стили карточек */
    .card-box { 
        background: white; 
        border-radius: 16px; 
        padding: 22px; 
        border: 1px solid #E5E7EB; 
        margin-bottom: 16px; 
        box-shadow: 0 2px 10px rgba(0,0,0,0.02);
    }
    .card-title { 
        font-size: 16px; 
        font-weight: 700; 
        color: #374151; 
        margin-top: 0;
        margin-bottom: 15px;
        display: block;
        border-bottom: 1px solid #F3F4F6;
        padding-bottom: 10px;
    }

    /* Основная большая кнопка */
    div.stButton > button[kind="primary"] {
        width: 100% !important;
        height: 56px !important;
        border-radius: 12px !important;
        background: linear-gradient(to right, #A78BFA, #F87171) !important;
        color: white !important;
        font-weight: 700 !important;
        font-size: 16px !important;
        border: none !important;
        margin-top: 10px;
    }
    
    /* Пустое место под результат */
    .empty-placeholder {
        border: 2px dashed #D1D5DB;
        border-radius: 16px;
        height: 500px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        color: #9CA3AF;
        background: #FAFAFA;
    }
</style>
""", unsafe_allow_html=True)

# --- ЛОГИКА ВЫХОДА (ОБРАБОТКА НАЖАТИЯ) ---
if "action_logout" not in st.session_state:
    st.session_state.action_logout = False

def perform_logout():
    st.session_state.clear() # Полностью очищаем сессию
    st.rerun()

# --- ДАННЫЕ ---
BASE_PROMPT = (
    "Masterpiece, 8k resolution, photorealistic interior photography, Architectural Digest style. "
    "Maintain original color palette and materials strictly. "
    "Enhance textures without changing colors. Cinematic lighting."
)
PRESETS = {
    "Студия": f"Professional studio lighting. {BASE_PROMPT}",
    "День": f"Natural bright daylight. {BASE_PROMPT}",
    "Вечер": f"Warm cozy evening light. {BASE_PROMPT}",
    "Акссесуары": f"{BASE_PROMPT}", # Можно поправить опечатку в названии ключа если нужно
}

if 'history' not in st.session_state: st.session_state.history = []
if 'current_prompt' not in st.session_state: st.session_state.current_prompt = PRESETS["Студия"]

# --- РЕНДЕРИНГ ШАПКИ (СТАБИЛЬНЫЙ МЕТОД) ---

# Обертка для всего блока шапки
st.markdown('<div class="main-header-wrapper">', unsafe_allow_html=True)

# Создаем две части: Левая (Текст) и Правая (Лого + Кнопка)
# ratio [2.5, 1] значит что левая часть больше правой
col_head_left, col_head_right = st.columns([2.5, 1], gap="small")

with col_head_left:
    st.markdown(f"""
        <div class="header-text">
            <h1>Привет, <b>{st.session_state.user_role}</b></h1>
            <p>Lazurit AI Interior Visualizer</p>
        </div>
    """, unsafe_allow_html=True)

with col_head_right:
    # Используем внутренние колонки чтобы Логотип и Кнопка были рядом
    c_logo, c_btn = st.columns([2, 1.2], gap="small")
    
    with c_logo:
        logo_b64_main = _read_b64(LOGO_PATH)
        if logo_b64_main:
             st.image(f"data:image/png;base64,{logo_b64_main}", width=160) 
    
    with c_btn:
        # Кнопка выхода (через native Streamlit)
        # use_container_width=True делает её на всю ширину своей маленькой колонки
        if st.button("🚪 Выйти", key="btn_logout_main", use_container_width=True):
            perform_logout()

st.markdown('</div>', unsafe_allow_html=True)

# Разделитель визуальный
st.markdown("""<div style="height: 10px;"></div>""", unsafe_allow_html=True)


# --- РАБОЧАЯ ОБЛАСТЬ ---
col_left, col_mid, col_hist = st.columns([2.2, 2.2, 0.6])

with col_left:
    st.markdown('<div class="card-box"><span class="card-title">1. Загрузить фото</span>', unsafe_allow_html=True)
    uploaded_file = st.file_uploader("Перетащите файл", type=['png', 'jpg', 'jpeg'], label_visibility="collapsed")
    if uploaded_file:
        st.image(uploaded_file, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="card-box"><span class="card-title">2. Стиль освещения</span>', unsafe_allow_html=True)
    
    icons = ["icons/studio.png", "icons/den.png", "icons/vecher.png", "icons/acsesoar.png"]
    icon_keys = list(PRESETS.keys())
    
    selected_idx = image_select(label="", images=icons, captions=None, use_container_width=False, return_value="index")
    
    if selected_idx is not None:
         st.session_state.current_prompt = PRESETS[icon_keys[selected_idx]]

    prompt_text = st.text_area("Промпт (можно править)", value=st.session_state.current_prompt, height=120)
    
    gen_button = st.button("ГЕНЕРИРОВАТЬ AI", type="primary", key="gen_btn")

    if gen_button:
        if uploaded_file:
            with st.spinner("Обработка..."):
                try:
                    bytes_data = uploaded_file.getvalue()
                    b64_img = image_to_base64(bytes_data)
                    
                    resp = process_image(b64_img, prompt_text)
                    
                    if 'outputs' in resp:
                        txt = resp['outputs'][0]['outputs'][0]['results']['message']['text']
                        raw = txt.split("|||")[1] if "|||" in txt else txt
                        if "base64," in raw: raw = raw.split("base64,")[1]
                        
                        img_out = base64.b64decode(raw.replace('"','').strip())
                        st.session_state.history.insert(0, img_out)
                        st.success("Готово!")
                        st.rerun()
                    else:
                        st.error("API вернуло пустой ответ")
                except Exception as e:
                    st.error(f"Ошибка: {str(e)}")
        else:
            st.warning("Сначала загрузите изображение")
            
    st.markdown('</div>', unsafe_allow_html=True)

with col_mid:
    st.markdown('<div class="card-box">', unsafe_allow_html=True)
    if st.session_state.history:
        st.image(st.session_state.history[0], use_container_width=True, caption="Последний результат")
    else:
        st.markdown("""
        <div class="empty-placeholder">
            <h3 style="margin:0; color:#CBD5E1;">Фото результата</h3>
            <p style="margin:10px 0 0 0; font-size:13px;">Загрузите фото и нажмите генерацию</p>
        </div>
        """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

with col_hist:
    st.markdown("**История**")
    # Показываем последние 5 (текущий исключаем, тк он в центре)
    for i, img_bytes in enumerate(st.session_state.history[1:6]):
        st.image(img_bytes, use_container_width=True)
