import streamlit as st
import requests
import base64
import platform
import io

# --- КОНФИГУРАЦИЯ ---
BASE_URL = "https://lzrt-nocode.gpt.mws.ru/api/v1/run/bf1dc235-5c36-4bba-8d7e-a88cd5e19bd6?stream=false"
LOGO_PATH = "logo.jpg"

# --- СИСТЕМА ЛИЧНЫХ ДОСТУПОВ ---
def check_password():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
        st.session_state.user_role = ""
        st.session_state.user_api_key = ""

    if not st.session_state.authenticated:
        try:
            with open("background.png", "rb") as f:
                data = f.read()
                b64_bg = base64.b64encode(data).decode()
            
            st.markdown(f"""
                <style>
                .stApp {{
                    background-image: url("data:image/png;base64,{b64_bg}");
                    background-size: cover;
                    background-position: center;
                    background-attachment: fixed;
                }}
                .stApp::before {{
                    content: ""; position: absolute; top: 0; left: 0; width: 100%; height: 100%;
                    background-color: rgba(0, 0, 0, 0.4); z-index: -1;
                }}
                </style>
                """, unsafe_allow_html=True)
        except:
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

check_password()

APPLICATION_TOKEN = st.session_state.user_api_key

# --- СТИЛИЗАЦИЯ ПОД МАКЕТ ---
st.markdown("""
    <style>
    /* Фон приложения как на макете */
    .stApp { background-color: #E8E8E1; }
    
    /* Стилизация карточек */
    [data-testid="stVerticalBlock"] > div:has(div.card) { padding: 0; }
    .card {
        background-color: #F8F9FA;
        border-radius: 20px;
        padding: 25px;
        border: 1px solid #E0E0E0;
        box-shadow: 4px 4px 15px rgba(0,0,0,0.03);
        margin-bottom: 20px;
    }
    
    /* Кастомная кнопка генерации с градиентом */
    div.stButton > button:first-child {
        background: linear-gradient(90deg, #A78BFA 0%, #F87171 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 15px !important;
        height: 60px !important;
        font-size: 20px !important;
    }
    
    /* Шапка приложения */
    .custom-header {
        background-color: white;
        padding: 15px 30px;
        border-radius: 15px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 25px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
    }
    </style>
    """, unsafe_allow_html=True)

# --- ПРОМПТЫ (БЕЗ ИЗМЕНЕНИЙ) ---
BASE_PHOTO_PROMPT = ("Masterpiece, 8k resolution, photorealistic interior photography, Architectural Digest style. Maintain the original color palette and materials of the furniture strictly. Enhance existing textures (wood grain, stone, fabric) without changing their color. Replace flat lighting with professional cinematic studio lighting and realistic global illumination. Add natural soft sunlight and deep realistic shadows to create depth. High-contrast, sharp details, realistic reflections on surfaces. Feel free to completely re-texture surfaces. Add dramatic lighting. Replace the flat lighting of the render with high-contrast studio light. Ensure 100% photorealism, Architectural Digest style. Masterpiece, 8k resolution, photorealistic interior photography. Completely re-texture all surfaces using high-end materials (marble, brushed metal, grain wood). Replace flat CG lighting with realistic global illumination and dramatic cinematic shadows.  Add subtle natural sunlight from windows.  Architectural Digest style, sharp focus, volumetric fog, ray-traced reflections. NO 3D render look, NO flat textures.")

PROMPT_PRESETS = {
    "Базовый промт": f"{BASE_PHOTO_PROMPT}",
    "️Свой промт": f"",
    "Базовый + Дневной свет": f"Natural bright daylight from windows, soft sun rays. {BASE_PHOTO_PROMPT}",
    "Базовый + Студийный свет": f"Professional architectural studio lighting, balanced fills. {BASE_PHOTO_PROMPT}",
    "Базовый + Вечернее освещение": f"Warm cozy evening light, mix of interior lamps and dusk. {BASE_PHOTO_PROMPT}",
    "Базовый + Unreal render style": f"Ultra-realistic Unreal Engine 5.4 Lumen render style. {BASE_PHOTO_PROMPT}",
}

def image_to_base64(image_bytes): return base64.b64encode(image_bytes).decode('utf-8')

def get_base64_logo(path):
    try:
        with open(path, "rb") as f: return base64.b64encode(f.read()).decode()
    except: return ""

def process_image(img_b64, user_prompt):
    combined_input = f"{user_prompt}|||data:image/jpeg;base64,{img_b64}"
    payload = {"input_value": combined_input, "output_type": "chat", "input_type": "chat"}
    headers = {"Authorization": f"Bearer {APPLICATION_TOKEN}", "x-api-key": APPLICATION_TOKEN, "Content-Type": "application/json"}
    return requests.post(BASE_URL, json=payload, headers=headers).json()

# --- ИНТЕРФЕЙС ---
st.set_page_config(page_title="LAZURIT AI Render", layout="wide", page_icon=LOGO_PATH)

if 'history' not in st.session_state: st.session_state.history = []
if 'current_prompt' not in st.session_state: st.session_state.current_prompt = list(PROMPT_PRESETS.values())[0]
if 'last_full_response' not in st.session_state: st.session_state.last_full_response = ""

# Шапка (Header)
logo_b64 = get_base64_logo(LOGO_PATH)
st.markdown(f"""
    <div class="custom-header">
        <div style="color: #555;"><b>{st.session_state.user_role}!</b> Добро пожаловать в Lazurit AI Render</div>
        <div style="font-weight: bold; font-size: 24px; letter-spacing: 2px; color: #333;">LAZURIT</div>
    </div>
    """, unsafe_allow_html=True)

# Основная рабочая область
col1, col2, col3 = st.columns([1.2, 2.5, 0.6])

with col1:
    st.markdown('<div class="card"><b>1. Загрузка данных</b>', unsafe_allow_html=True)
    uploaded_file = st.file_uploader("Выберите фото или рендер", type=['jpg', 'jpeg', 'png'], label_visibility="collapsed")
    if uploaded_file:
        st.image(uploaded_file, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="card"><b>Освещение</b>', unsafe_allow_html=True)
    p_col1, p_col2 = st.columns(2)
    for i, name in enumerate(PROMPT_PRESETS.keys()):
        target_col = p_col1 if i % 2 == 0 else p_col2
        if target_col.button(name, use_container_width=True, key=f"btn_{i}"):
            st.session_state.current_prompt = PROMPT_PRESETS[name]
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
    
    user_prompt = st.text_area("ТЗ промпта:", value=st.session_state.current_prompt, height=200)
    
    if st.button("ГЕНЕРИРОВАТЬ AI ИЗОБРАЖЕНИЕ", use_container_width=True):
        if not uploaded_file:
            st.error("Загрузите изображение!")
        else:
            with st.spinner("Генерация..."):
                try:
                    uploaded_file.seek(0)
                    img_b64 = image_to_base64(uploaded_file.read())
                    result = process_image(img_b64, user_prompt)
                    if 'outputs' in result:
                        msg = result['outputs'][0]['outputs'][0]['results']['message']['text']
                        st.session_state.last_full_response = msg
                        img_data = msg.split("|||")[1] if "|||" in msg else msg
                        raw_b64 = img_data.split("base64,")[1] if "base64," in img_data else img_data
                        out_bytes = base64.b64decode(raw_b64.replace('"', '').strip())
                        st.session_state.history.insert(0, out_bytes)
                        st.rerun()
                except Exception as e:
                    st.error(f"Ошибка: {e}")

with col2:
    st.markdown('<div class="card" style="min-height: 600px; text-align: center;">', unsafe_allow_html=True)
    if st.session_state.history:
        st.image(st.session_state.history[0], caption="Результат генерации", use_container_width=True)
    else:
        st.markdown('<div style="margin-top: 250px; color: #999;"><h3>РЕЗУЛЬТАТ AI ГЕНЕРАЦИИ</h3></div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

with col3:
    st.markdown('<b>История</b>', unsafe_allow_html=True)
    for img in st.session_state.history[1:6]:
        st.image(img, use_container_width=True)
        st.markdown('<div style="margin-bottom: 10px;"></div>', unsafe_allow_html=True)

if st.session_state.last_full_response:
    with st.expander("🛠 Лог промпта"):
        st.text_area("Системный вывод:", value=st.session_state.last_full_response, height=200)
