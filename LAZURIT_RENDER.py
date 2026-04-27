import streamlit as st
import requests
import base64
import platform
import io

# --- КОНФИГУРАЦИЯ ---
BASE_URL = "https://lzrt-nocode.gpt.mws.ru/api/v1/run/bf1dc235-5c36-4bba-8d7e-a88cd5e19bd6?stream=false"
LOGO_PATH = "logo2.jpg" # Убедись, что этот файл есть в репозитории

# --- ФУНКЦИИ ---
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

# --- СИСТЕМА ЛИЧНЫХ ДОСТУПОВ ---
def check_password():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
        st.session_state.user_role = ""
        st.session_state.user_api_key = ""

    if not st.session_state.authenticated:
        # Установка фона для входа
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

# --- УСТАНОВКА КОНФИГУРАЦИИ СТРАНИЦЫ ---
st.set_page_config(page_title="LAZURIT AI Render", layout="wide", page_icon=LOGO_PATH)

# Запускаем проверку
check_password()
APPLICATION_TOKEN = st.session_state.user_api_key

# --- СТИЛИЗАЦИЯ ПОД МАКЕТ (Исправлено) ---
st.markdown("""
    <style>
    /* Убираем стандартные отступы, чтобы не было "белых полей" */
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 1rem !important;
        padding-left: 1rem !important;
        padding-right: 1rem !important;
    }
    
    .stApp { background-color: #E8E8E1; }
    
    /* Уменьшаем шрифты для узкой колонки */
    html, body, [class*="st-"] { font-size: 14px !important; }
    .stFileUploader label { display: none; } /* Прячем текст загрузчика */
    
    /* Стилизация карточек */
    .card {
        background-color: #F8F9FA;
        border-radius: 15px;
        padding: 15px;
        border: 1px solid #E0E0E0;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.03);
        margin-bottom: 15px;
    }
    
    /* Кастомная кнопка генерации с градиентом */
    div.stButton > button {
        background: linear-gradient(90deg, #A78BFA 0%, #F87171 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        height: 50px !important;
        font-size: 16px !important;
        font-weight: bold !important;
    }
    
    /* Шапка приложения */
    .custom-header {
        background-color: white;
        padding: 10px 20px;
        border-radius: 15px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 15px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    }
    </style>
    """, unsafe_allow_html=True)

# --- ПРОМПТЫ (БЕЗ ИЗМЕНЕНИЙ) ---
BASE_PHOTO_PROMPT = ("Masterpiece, 8k resolution, photorealistic interior photography, Architectural Digest style. Maintain the original color palette and materials of the furniture strictly. Enhance existing textures (wood grain, stone, fabric) without changing their color. Replace flat lighting with professional cinematic studio lighting and realistic global illumination. Add natural soft sunlight and deep realistic shadows to create depth. High-contrast, sharp details, realistic reflections on surfaces. Feel free to completely re-texture surfaces. Add dramatic lighting. Replace the flat lighting of the render with high-contrast studio light. Ensure 100% photorealism, Architectural Digest style. Masterpiece, 8k resolution, photorealistic interior photography. Completely re-texture all surfaces using high-end materials (marble, brushed metal, grain wood). Replace flat CG lighting with realistic global illumination and dramatic cinematic shadows.  Add subtle natural sunlight from windows.  Architectural Digest style, sharp focus, volumetric fog, ray-traced reflections. NO 3D render look, NO flat textures.")

PROMPT_PRESETS = {
    "Базовый промт": BASE_PHOTO_PROMPT,
    "Студийный свет": f"Professional architectural studio lighting, balanced fills. {BASE_PHOTO_PROMPT}",
    "Дневной свет": f"Natural bright daylight from windows, soft sun rays. {BASE_PHOTO_PROMPT}",
    "Вечер": f"Warm cozy evening light, mix of interior lamps and dusk. {BASE_PHOTO_PROMPT}"
}

# --- ИНИЦИАЛИЗАЦИЯ ИСТОРИИ ---
if 'history' not in st.session_state: st.session_state.history = []
if 'current_prompt' not in st.session_state: st.session_state.current_prompt = list(PROMPT_PRESETS.values())[0]

# Шапка (Header)
logo_b64 = get_base64_logo(LOGO_PATH)
st.markdown(f"""
    <div class="custom-header">
        <div style="color: #555; font-size: 16px;"><b>{st.session_state.user_role}!</b> Добро пожаловать</div>
        <img src="data:image/jpeg;base64,{logo_b64}" style="height: 40px;">
    </div>
    """, unsafe_allow_html=True)

# --- ИНТЕРФЕЙС: РАЗДЕЛЕНИЕ НА КОЛОНКИ ---
# Теперь колонки занимают меньше места, а результат больше.
col_control, col_result = st.columns([1.1, 2.9])

with col_control:
    # Блок загрузки
    st.markdown('<div class="card"><b>1. Загрузка данных</b>', unsafe_allow_html=True)
    uploaded_file = st.file_uploader("file", type=['jpg', 'jpeg', 'png'])
    if uploaded_file:
        st.image(uploaded_file, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Блок пресетов света
    st.markdown('<div class="card"><b>Освещение</b>💡', unsafe_allow_html=True)
    p_col1, p_col2 = st.columns(2)
    for i, name in enumerate(PROMPT_PRESETS.keys()):
        # Распределяем по 2 кнопки в ряд
        target_col = p_col1 if i % 2 == 0 else p_col2
        if target_col.button(name, use_container_width=True, key=f"btn_{i}"):
            st.session_state.current_prompt = PROMPT_PRESETS[name]
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Текст промпта
    user_prompt = st.text_area("Текст промпта:", value=st.session_state.current_prompt, height=200)
    
    # Кнопка генерации (стилизована)
    gen_btn = st.button("ГЕНЕРИРОВАТЬ AI ИЗОБРАЖЕНИЕ", use_container_width=True)

with col_result:
    # Белая карточка для результата
    st.markdown('<div class="card" style="min-height: 600px; padding: 10px;">', unsafe_allow_html=True)
    
    if gen_btn:
        if not uploaded_file:
            st.error("❌ Загрузите изображение в блоке 1.")
        else:
            with st.spinner("Создаем шедевр..."):
                try:
                    uploaded_file.seek(0)
                    img_bytes = uploaded_file.read()
                    img_b64 = image_to_base64(img_bytes)
                    result = process_image(img_b64, user_prompt)
                    
                    if 'outputs' in result:
                        msg = result['outputs'][0]['outputs'][0]['results']['message']['text']
                        img_data = msg.split("|||")[1] if "|||" in msg else msg
                        raw_b64 = img_data.split("base64,")[1] if "base64," in img_data else img_data
                        # Убираем кавычки
                        clean_b64 = raw_b64.replace('"', '').replace("'", "").strip()
                        out_bytes = base64.b64decode(clean_b64)
                        
                        # Сохраняем и показываем
                        st.session_state.history.insert(0, out_bytes)
                        # Обрезаем историю, если слишком большая
                        if len(st.session_state.history) > 6: st.session_state.history.pop()
                        st.rerun()
                    else:
                        st.error("Ошибка API: Проверьте ключ.")
                except Exception as e:
                    st.error(f"Ошибка: {e}")
    
    # Показ результата или заглушки
    if st.session_state.history:
        st.image(st.session_state.history[0], caption="Готовый результат", use_container_width=True)
    else:
        # Пытаемся поймать, если он ещё не сгенерировал ничего
        if not gen_btn:
            st.markdown('<div style="text-align: center; margin-top: 250px; color: #BBB;"><h3>РЕЗУЛЬТАТ AI ГЕНЕРАЦИИ</h3></div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# История переехала в конец, чтобы не ломать верстку в узкой колонке
if len(st.session_state.history) > 1:
    st.divider()
    st.write("🕒 **История генераций**")
    hist_cols = st.columns(len(st.session_state.history[1:6]))
    for idx, img in enumerate(st.session_state.history[1:6]):
        with hist_cols[idx]:
            st.image(img, use_container_width=True)
