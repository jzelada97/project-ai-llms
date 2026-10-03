# Generador de contenido con LLMs

PoC para Digital Content: genera texto listo para publicar (Blog, Twitter/X, Instagram, LinkedIn)
adaptado a la audiencia, usando **prompt engineering + LangChain** y una interfaz **Streamlit**.
Coste cero: Groq (capa gratuita) o Ollama (local).

> Nivel Esencial del proyecto [project-ai-llms](https://github.com/Factoria-F5-madrid/project-ai-llms).

## Instalación

```bash
python -m venv .venv
.venv\Scripts\activate        # Linux/Mac: source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env          # y rellena GROQ_API_KEY (https://console.groq.com/keys)
streamlit run app.py
```

Con Ollama en vez de Groq: instala [Ollama](https://ollama.com), `ollama pull llama3.2` y pon `LLM_PROVIDER=ollama` en `.env`.

## Uso

Elige tema, plataforma, audiencia, tono y longitud, y pulsa **Generar**. También desde terminal:

```bash
python scripts/try_generate.py "Beneficios de dormir 8 horas" LinkedIn General
```

## Arquitectura

```
app.py (Streamlit) → generator.py → PROMPT | llm | StrOutputParser()   (cadena LangChain)
                                      prompts.py   llm.py (Groq/Ollama)
```

| Archivo | Responsabilidad |
|---|---|
| `src/content_generator/config.py` | Lee `.env` / `st.secrets` y valida |
| `src/content_generator/llm.py` | Fábrica del modelo (Groq u Ollama) |
| `src/content_generator/prompts.py` | Reglas por plataforma, audiencia, tono y longitud |
| `src/content_generator/generator.py` | Validación, cadena LCEL y errores legibles |

Añadir una plataforma = una entrada nueva en `PLATFORM_RULES`.

## Tests

```bash
pip install -r requirements-dev.txt
pytest
```

Usan un modelo falso: no necesitan red ni API key.

## Seguridad

La API key solo va en `.env` (ignorado por git) o en los Secrets de Streamlit Cloud. Nunca la subas al repo.
