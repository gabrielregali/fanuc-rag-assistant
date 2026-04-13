# -*- coding: utf-8 -*-
import streamlit as st
from google import genai
from sentence_transformers import SentenceTransformer
from supabase import create_client
import anthropic

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Asistente Técnico FANUC", page_icon="🤖")

SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
ANTHROPIC_API_KEY = st.secrets["ANTHROPIC_API_KEY"]

SIMILARITY_THRESHOLD = 0.55  # Fase de prueba

# --------------------------------------------------
# CACHE DE MODELOS
# --------------------------------------------------

#@st.cache(allow_output_mutation=True)
#def load_models():
#    embedding_model = SentenceTransformer(
#        "BAAI/bge-large-en-v1.5",
#        trust_remote_code=True
#    )
#    gemini_client = genai.Client(api_key=GEMINI_API_KEY)
#    return embedding_model, gemini_client

#ANTHROPIC***************************************
@st.cache(allow_output_mutation=True)
def load_models():
    embedding_model = SentenceTransformer(
        "BAAI/bge-large-en-v1.5",
        trust_remote_code=True
    )
    anthropic_client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    return embedding_model, anthropic_client


@st.cache(allow_output_mutation=True)
def init_supabase():
    return create_client(SUPABASE_URL, SUPABASE_KEY)


#bert_model, gemini_client = load_models()
bert_model, anthropic_client = load_models()
supabase_client = init_supabase()

# --------------------------------------------------
# INTERFAZ
# --------------------------------------------------

st.title("🤖 Asistente Técnico FANUC")
st.write("Consulta técnica documental basada exclusivamente en manuales cargados.")

categoria = st.selectbox(
    "Selecciona el tipo de consulta:",
    #("errores", "mantenimiento_robot", "mantenimiento_controlador")
    ("errores", "mantenimiento_robot")
)

letra_error = None
modelo_robot = None
controlador = None

if categoria == "errores":

    letra_error = st.selectbox(
        "Selecciona la letra del error:",
        list("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
    )

elif categoria == "mantenimiento_robot":

    modelo_robot = st.selectbox(
        "Modelo de robot:",
        ("M-410iB/450",)
    )

#elif categoria == "mantenimiento_controlador":

#    controlador = st.selectbox(
#        "Modelo de controlador:",
#        ("R-30iA", "R-J3iB")
#    )

# --------------------------------------------------
# FORMULARIO
# --------------------------------------------------

with st.form(key='consulta_form'):
    pregunta = st.text_input("Escribe tu consulta técnica:")
    submit_button = st.form_submit_button("Consultar")

# --------------------------------------------------
# LÓGICA RAG
# --------------------------------------------------

if submit_button and pregunta:

    with st.spinner("Buscando información técnica en manuales..."):

        query_text = (
            "Represent this sentence for searching relevant technical manual passages: "
            + pregunta
        )

        query_vector = bert_model.encode(query_text).tolist()

        filtros = {
            "query_embedding": query_vector,
            "query_text": pregunta,
            "f_categoria": categoria,
            "f_letra_error": letra_error,
            "f_modelo_robot": modelo_robot,
            "f_controlador": controlador,
            "match_count": 25
        }

        try:

            res = supabase_client.rpc(
                "buscar_manual_fanuc",
                filtros
            ).execute()

            if not res.data:
                st.warning("NO ENCONTRADO EN EL MANUAL SELECCIONADO")
                st.stop()

            best_score = res.data[0]["similarity"]
            #st.write(f"🔎 Similarity score: {round(best_score,3)}")
            #st.write(res.data[0])

            if best_score < SIMILARITY_THRESHOLD:
                st.error("NO ENCONTRADO EN EL MANUAL SELECCIONADO (Similarity bajo)")
                st.stop()

            # --------------------------------------------------
            # OBTENER INDICES DE CHUNKS (CORREGIDO)
            # --------------------------------------------------

            indices = [
                item["chunk_index"]
                for item in res.data
                if item.get("chunk_index") is not None
            ]

            if not indices:
                st.error("Error: los resultados no contienen chunk_index válido")
                st.stop()

            vecinos = set()

            for idx in indices:
                vecinos.update([
                    idx-6, idx-5, idx-4, idx-3, idx-2, idx-1,
                    idx,
                    idx+1, idx+2, idx+3, idx+4, idx+5, idx+6
                ])

            # --------------------------------------------------
            # RECUPERAR CHUNKS VECINOS (CORREGIDO)
            # --------------------------------------------------

            query = supabase_client.table("manuales_fanuc") \
                .select("content, chunk_index") \
                .eq("categoria", categoria) \
                .in_("chunk_index", list(vecinos))

            if letra_error:
                query = query.eq("letra_error", letra_error)

            if modelo_robot:
                query = query.eq("modelo_robot", modelo_robot)

            if controlador:
                query = query.eq("controlador", controlador)

            extra = query.execute()

            chunks_recuperados = sorted(
                extra.data,
                key=lambda x: x["chunk_index"]
            )

            contexto = "\n---\n".join(
                [item["content"] for item in chunks_recuperados]
            )

        except Exception as e:
            st.error(f"Error en Supabase: {e}")
            st.stop()

        # --------------------------------------------------
        # PROMPT DOCUMENTAL
        # --------------------------------------------------

        instruccion = f"""
Eres un sistema de consulta documental técnica industrial.

INSTRUCCIÓN CRÍTICA:
Debes responder exclusivamente utilizando la información contenida en el CONTEXTO proporcionado.

Reglas obligatorias:
- No utilices conocimiento previo del modelo.
- No completes información faltante.
- No infieras valores técnicos.
- No describas procedimientos estándar si no están explícitamente en el texto.
- No generalices.
- No asumas información externa.
- No actúes como especialista.

Reglas adicionales para manuales técnicos:
- Si el valor numérico exacto no está visible en el contexto pero existe una referencia explícita a una tabla, figura o sección donde se encuentra la información, debes indicarlo claramente.
- No inventes valores numéricos.
- No completes parámetros técnicos si no aparecen en el texto.

Uso del contexto:
- Si un procedimiento aparece dividido entre fragmentos, reconstruye el procedimiento completo utilizando todos los fragmentos del contexto.
- Usa TODOS los fragmentos del contexto disponibles.
- Si un paso parece incompleto, busca la continuación en otros fragmentos.
- No omitas pasos si están presentes en el contexto.
- Si el procedimiento contiene muchos pasos, resume los pasos en forma ordenada sin repetir texto innecesario.
- Mantén los pasos numerados cuando el manual los tenga.

Regla de ausencia de información:
Solo responde "NO ENCONTRADO EN EL MANUAL SELECCIONADO" si no existe ninguna referencia relacionada en el contexto.

Formato obligatorio de respuesta:

Respuesta:
[texto literal basado en el contexto]

Cita textual:
[fragmento exacto copiado del contexto]


CONTEXTO:
{contexto}
"""

        # --------------------------------------------------
        # GENERACIÓN CON GEMINI
        # --------------------------------------------------

        try:

            #response = gemini_client.models.generate_content(
            #    model="gemini-2.5-flash",
            #    contents=f"{instruccion}\n\nPREGUNTA:\n{pregunta}"
            #)

            #answer = response.text

            response = anthropic_client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=1000,
                temperature=0,
                messages=[
                    {
                        "role": "user",
                        "content": f"{instruccion}\n\nPREGUNTA:\n{pregunta}"
                    }
                ]        
            )
            answer = response.content[0].text

        except Exception as e:

            answer = f"Error en Gemini: {e}"

    st.markdown("### 📘 Respuesta Técnica:")
    st.info(answer)
