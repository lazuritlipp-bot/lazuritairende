import streamlit as st
import requests
import base64
import platform
import io

# --- КОНФИГУРАЦИЯ ---
BASE_URL = "https://lzrt-nocode.gpt.mws.ru/api/v1/run/bf1dc235-5c36-4bba-8d7e-a88cd5e19bd6?stream=false"
LOGO_PATH = "logo2.jpg" 

# --- СИСТЕМА ЛИЧНЫХ ДОСТУПОВ ---
def check_password():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
        st.session_state.user_role = ""
        st.session_state.user_api_key = ""

    if not st.session_state.authenticated:
        st.markdown("<style>.stApp { background-color: #0E1117; }</style>", unsafe_allow_html=True)
        st.sidebar.title("🔐 LAZURIT AI Render")
        pwd = st.sidebar.text_input("Введите код доступа:", type="password")
        if st.sidebar.button("Войти", use_container_width=True):
            users_data = st.secrets.get("users", {})
            if pwd in users_data:
                user_info = users_data[pwd]
                st.session_state.authenticated = True
                st.session_state.user_role = user_info.get("name", "Сотрудник")
                st.session_state.user_api_key = user_info.get("key", "")
                st.rerun()
            else:
                st.sidebar.error("❌ Код не опознан")
        st.stop()

# --- ИНИЦИАЛИЗАЦИЯ СТРАНИЦЫ ---
st.set_page_config(page_title="LAZURIT AI Render", layout="wide")
check_password()
APPLICATION_TOKEN = st.session_state.user_api_key

# --- ФУНКЦИИ ---
def image_to_base64(image_bytes): return base64.b64encode(image_bytes).decode('utf-8')

def get_base64_logo(path):
    try:
        with open(path, "rb") as f: return base64.b64encode(f.read()).decode()
    except: return ""

def process_image(img_b64, user_prompt):
    combined_input = f"{user_prompt}|||data:image/jpeg;base64,{img_b64}"
    payload = {"input_value": combined_input, "output_type": "chat", "input_type": "chat"}
    headers = {"Authorization": f"Bearer {APPLICATION_TOKEN}", "Content-Type": "application/json"}
    return requests.post(BASE_URL, json=payload, headers=headers).json()

# --- СТИЛИЗАЦИЯ ---
logo_b64 = get_base64_logo(LOGO_PATH)
st.markdown(f"""
    <style>
    .stApp {{ background-color: #E8E8E1; }}
    .block-container {{ padding-top: 2rem !important; padding-left: 3rem !important; padding-right: 3rem !important; }}
    
    /* Исправление шапки */
    .custom-header {{
        background-color: white;
        padding: 15px 25px;
        border-radius: 15px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 25px;
        border: 1px solid #D1D1D1;
    }}
    .header-text {{ color: #333 !important; font-size: 20px; font-weight: bold; margin: 0; }}
    
    /* Карточки интерфейса */
    .card {{
        background-color: #F8F9FA;
        border-radius: 15px;
        padding: 20px;
        border: 1px solid #E0E0E0;
        margin-bottom: 20px;
        color: #333 !important;
    }}
    
    /* Кнопка генерации */
    div.stButton > button {{
        background: linear-gradient(90deg, #A78BFA 0%, #F87171 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        height: 60px !important;
        font-weight: bold !important;
        font-size: 18px !important;
    }}
    
    /* Белые поля у кнопок освещения */
    .stButton button {{ border-radius: 8px !important; color: #333; }}
    </style>
    
    <div class="custom-header">
        <div class="header-text">{st.session_state.user_role}! Добро пожаловать в Lazurit AI Render</div>
        <img src="data:image/jpeg;base64,{logo_b64}" style="height: 45px;">
    </div>
    """, unsafe_allow_html=True)

# --- ДАННЫЕ ПРОМПТОВ ---
BASE_PHOTO_PROMPT = ("Masterpiece, 8k resolution, photorealistic interior photography, Architectural Digest style. Maintain the original color palette and materials of the furniture strictly. Enhance existing textures (wood grain, stone, fabric) without changing their color. Replace flat lighting with professional cinematic studio lighting and realistic global illumination. Add natural soft sunlight and deep realistic shadows to create depth. High-contrast, sharp details, realistic reflections on surfaces. Feel free to completely re-texture surfaces. Add dramatic lighting. Replace the flat lighting of the render with high-contrast studio light. Ensure 100% photorealism, Architectural Digest style. Masterpiece, 8k resolution, photorealistic interior photography. Completely re-texture all surfaces using high-end materials (marble, brushed metal, grain wood). Replace flat CG lighting with realistic global illumination and dramatic cinematic shadows. Add subtle natural sunlight from windows. Architectural Digest style, sharp focus, volumetric fog, ray-traced reflections. NO 3D render look, NO flat textures.")

PROMPT_PRESETS = {
    "Базовый промт": BASE_PHOTO_PROMPT,
    "Дневной свет": f"Natural bright daylight from windows, soft sun rays. {BASE_PHOTO_PROMPT}",
    "Студийный свет": f"Professional architectural studio lighting, balanced fills. {BASE_PHOTO_PROMPT}",
    "Вечер": f"Warm cozy evening light, mix of interior lamps and dusk. {BASE_PHOTO_PROMPT}"
}

if 'history' not in st.session_state: st.session_state.history = []
if 'current_prompt' not in st.session_state: st.session_state.current_prompt = PROMPT_PRESETS["Базовый промт"]

# --- ОСНОВНОЙ ИНТЕРФЕЙС ---
col_left, col_main, col_right = st.columns([1.2, 2.5, 0.6])

with col_left:
    st.markdown('<div class="card"><b>1. Загрузка данных</b>', unsafe_allow_html=True)
    up_file = st.file_uploader("file", label_visibility="collapsed")
    if up_file: st.image(up_file)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="card"><b style="color:#333">💡 Освещение</b>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    for i, name in enumerate(PROMPT_PRESETS.keys()):
        target = c1 if i < 2 else c2
        if target.button(name, use_container_width=True):
            st.session_state.current_prompt = PROMPT_PRESETS[name]
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    user_text = st.text_area("Текст промпта:", value=st.session_state.current_prompt, height=200)
    
    if st.button("ГЕНЕРИРОВАТЬ AI ИЗОБРАЖЕНИЕ", use_container_width=True):
        if up_file:
            with st.spinner("Генерация..."):
                try:
                    up_file.seek(0)
                    img_b64 = image_to_base64(up_file.read())
                    res = process_image(img_b64, user_text)
                    if 'outputs' in res:
                        msg = res['outputs'][0]['outputs'][0]['results']['message']['text']
                        img_data = msg.split("|||")[1] if "|||" in msg else msg
                        raw = img_data.split("base64,")[1] if "base64," in img_data else img_data
                        out_bytes = base64.b64decode(raw.replace('"', '').strip())
                        st.session_state.history.insert(0, out_bytes)
                        st.rerun()
                except Exception as e: st.error(f"Ошибка: {e}")

with col_main:
    st.markdown('<div class="card" style="min-height: 600px; text-align: center;">', unsafe_allow_html=True)
    if st.session_state.history:
        st.image(st.session_state.history[0], use_container_width=True)
    else:
        st.markdown('<h3 style="color: #BBB; margin-top: 250px;">РЕЗУЛЬТАТ AI ГЕНЕРАЦИИ</h3>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

with col_right:
    st.markdown('<div style="text-align: center; color: #555; margin-bottom: 10px;"><b>История</b></div>', unsafe_allow_html=True)
    for h_img in st.session_state.history[1:7]:
        st.image(h_img, use_container_width=True)
        st.markdown('<div style="margin-bottom: 10px;"></div>', unsafe_allow_html=True)

# Лог промпта удален
