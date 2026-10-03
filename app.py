"""Interfaz web (Streamlit). Ejecutar con:  streamlit run app.py"""

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

import streamlit as st  # noqa: E402

from content_generator.config import ConfigError  # noqa: E402
from content_generator.generator import (  # noqa: E402
    EXTRA_MAX_CHARS,
    TOPIC_MAX_CHARS,
    ContentRequest,
    GenerationError,
    generate_content,
)
from content_generator.prompts import (  # noqa: E402
    AUDIENCE_RULES,
    LENGTHS,
    PLATFORM_RULES,
    TONE_RULES,
)

COOLDOWN_SECONDS = 5  # evita ráfagas que agoten la cuota gratuita

st.set_page_config(page_title="Generador de contenido", page_icon="✍️")
st.title("✍️ Generador de contenido con IA")
st.caption("Dime el tema, la plataforma y la audiencia, y te escribo el texto listo para publicar.")

with st.form("request"):
    topic = st.text_input("Tema", max_chars=TOPIC_MAX_CHARS, placeholder="Ej: Beneficios de dormir 8 horas")
    col1, col2 = st.columns(2)
    platform = col1.selectbox("Plataforma", list(PLATFORM_RULES))
    audience = col2.selectbox("Audiencia", list(AUDIENCE_RULES))
    tone = col1.selectbox("Tono", list(TONE_RULES), index=1)
    length = col2.selectbox("Longitud", list(LENGTHS), index=1)
    extra = st.text_area("Instrucciones adicionales (opcional)", max_chars=EXTRA_MAX_CHARS)
    submitted = st.form_submit_button("Generar", type="primary")

if submitted:
    wait = COOLDOWN_SECONDS - (time.time() - st.session_state.get("last_call", 0))
    if wait > 0:
        st.warning(f"Espera {wait:.0f} s antes de generar de nuevo.")
    else:
        st.session_state["last_call"] = time.time()
        try:
            with st.spinner("Generando..."):
                st.session_state["result"] = generate_content(
                    ContentRequest(topic, platform, audience, tone, length, extra)
                )
        except (ConfigError, GenerationError) as exc:
            st.session_state.pop("result", None)
            st.error(str(exc))

if "result" in st.session_state:
    result = st.session_state["result"]
    st.subheader("Resultado")
    st.markdown(result)
    with st.expander("Texto plano (para copiar)"):
        st.code(result, language=None, wrap_lines=True)
    st.download_button("Descargar .md", result, file_name="contenido.md", mime="text/markdown")
