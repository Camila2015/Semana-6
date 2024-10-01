import os
import streamlit as st
from bokeh.models.widgets import Button
from bokeh.models import CustomJS
from streamlit_bokeh_events import streamlit_bokeh_events
from PIL import Image
import time
import glob
from gtts import gTTS
from googletrans import Translator

# Estilos personalizados con CSS
st.markdown("""
    <style>
    .stButton button {
        background-color: #4CAF50; 
        color: white;
        border-radius: 12px;
        font-size: 16px;
        padding: 10px 24px;
        cursor: pointer;
        transition: background-color 0.3s ease;
    }
    
    .stButton button:hover {
        background-color: #45a049;
    }

    .header {
        font-family: 'Arial', sans-serif;
        color: #3a3a3a;
        text-align: center;
    }
    
    .subheader {
        color: #6c757d;
        text-align: center;
        margin-bottom: 30px;
    }

    .sidebar .sidebar-content {
        background-color: #f8f9fa;
        padding: 10px;
    }

    .stAudio {
        background-color: #f1f1f1;
        border-radius: 10px;
        padding: 10px;
    }
    
    .spinner {
        border: 4px solid #f3f3f3;
        border-radius: 50%;
        border-top: 4px solid #3498db;
        width: 30px;
        height: 30px;
        -webkit-animation: spin 1s linear infinite; /* Safari */
        animation: spin 1s linear infinite;
        margin: 20px auto;
    }
    
    @-webkit-keyframes spin {
        0% { -webkit-transform: rotate(0deg); }
        100% { -webkit-transform: rotate(360deg); }
    }
    
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    
    </style>
    """, unsafe_allow_html=True)

# Título y subtítulo
st.markdown("<h1 class='header'>TRADUCTOR</h1>", unsafe_allow_html=True)
st.markdown("<h3 class='subheader'>Escucha lo que quieres traducir.</h3>", unsafe_allow_html=True)

# Imagen principal
image = Image.open('OIG7.jpg')
st.image(image, width=300)

with st.sidebar:
    st.subheader("Traductor")
    st.write("Presiona el botón, cuando escuches la señal, habla lo que quieres traducir y luego selecciona la configuración de lenguaje que necesites.")

# Indicaciones para el usuario
st.write("Toca el botón y habla lo que quieres traducir:")

# Botón de reconocimiento de voz
stt_button = Button(label="🎤 Escuchar", width=300, height=50)

# JavaScript para reconocimiento de voz
stt_button.js_on_event("button_click", CustomJS(code="""
    var recognition = new webkitSpeechRecognition();
    recognition.continuous = true;
    recognition.interimResults = true;
 
    recognition.onresult = function (e) {
        var value = "";
        for (var i = e.resultIndex; i < e.results.length; ++i) {
            if (e.results[i].isFinal) {
                value += e.results[i][0].transcript;
            }
        }
        if ( value != "") {
            document.dispatchEvent(new CustomEvent("GET_TEXT", {detail: value}));
        }
    }
    recognition.start();
    """))

# Evento para escuchar la voz
result = streamlit_bokeh_events(
    stt_button,
    events="GET_TEXT",
    key="listen",
    refresh_on_update=False,
    override_height=75,
    debounce_time=0
)

# Procesar la traducción
if result:
    if "GET_TEXT" in result:
        st.write(result.get("GET_TEXT"))
        
    try:
        os.mkdir("temp")
    except:
        pass

    st.title("Texto a Audio")
    translator = Translator()
    
    text = str(result.get("GET_TEXT"))

    # Lenguajes de entrada y salida
    in_lang = st.selectbox(
        "Selecciona el lenguaje de Entrada",
        ("Inglés", "Español", "Italiano", "Coreano", "Mandarín", "Japonés"),
    )

    # Asignación del código de idioma
    lang_dict = {
        "Inglés": "en",
        "Español": "es",
        "Italiano": "it",
        "Coreano": "ko",
        "Mandarín": "zh-cn",
        "Japonés": "ja"
    }
    
    input_language = lang_dict[in_lang]
    
    out_lang = st.selectbox(
        "Selecciona el lenguaje de salida",
        ("Inglés", "Español", "Italiano", "Coreano", "Mandarín", "Japonés"),
    )
    output_language = lang_dict[out_lang]
    
    # Selección del acento inglés
    english_accent = st.selectbox(
        "Selecciona el acento",
        (
            "Defecto",
            "Español",
            "Reino Unido",
            "Estados Unidos",
            "Canadá",
            "Australia",
            "Irlanda",
            "Sudáfrica",
        ),
    )
    
    tld_dict = {
        "Defecto": "com",
        "Español": "com.mx",
        "Reino Unido": "co.uk",
        "Estados Unidos": "com",
        "Canadá": "ca",
        "Australia": "com.au",
        "Irlanda": "ie",
        "Sudáfrica": "co.za"
    }

    tld = tld_dict[english_accent]

    # Función de traducción
    def text_to_speech(input_language, output_language, text, tld):
        translation = translator.translate(text, src=input_language, dest=output_language)
        trans_text = translation.text
        tts = gTTS(trans_text, lang=output_language, tld=tld, slow=False)
        try:
            my_file_name = text[0:20]
        except:
            my_file_name = "audio"
        tts.save(f"temp/{my_file_name}.mp3")
        return my_file_name, trans_text
    
    display_output_text = st.checkbox("Mostrar el texto")

    # Botón para convertir a audio
    if st.button("🎧 Convertir a Audio"):
        with st.spinner('Procesando...'):
            result, output_text = text_to_speech(input_language, output_language, text, tld)
            audio_file = open(f"temp/{result}.mp3", "rb")
            audio_bytes = audio_file.read()

        # Mostrar el audio
        st.markdown(f"## Tu audio:")
        st.audio(audio_bytes, format="audio/mp3", start_time=0)

        # Mostrar el texto traducido si es seleccionado
        if display_output_text:
            st.markdown(f"## Texto de salida:")
            st.write(f" {output_text}")

    # Función para eliminar archivos antiguos
    def remove_files(n):
        mp3_files = glob.glob("temp/*mp3")
        if len(mp3_files) != 0:
            now = time.time()
            n_days = n * 86400
            for f in mp3_files:
                if os.stat(f).st_mtime < now - n_days:
                    os.remove(f)
                    print("Deleted ", f)

    # Eliminar archivos después de 7 días
    remove_files(7)



        
    


