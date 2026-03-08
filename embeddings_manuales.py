import fitz
import re
from sentence_transformers import SentenceTransformer
from supabase import create_client
import time

# ==========================================
# CONFIGURACIÓN
# ==========================================

SUPABASE_URL = "tu URL de Supabase"
SUPABASE_KEY = "tu clave de Supabase"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

print("Cargando modelo de embeddings...")
model = SentenceTransformer('BAAI/bge-large-en-v1.5')

# ==========================================
# LIMPIEZA DE TEXTO
# ==========================================

def limpiar_texto(texto):

    texto = re.sub(r'file:///.*?\n', '', texto)
    texto = re.sub(r'\d{2}/\d{2}/\d{4}.*?\n', '', texto)
    texto = re.sub(r'\n{2,}', '\n', texto)

    return texto.strip()

# ==========================================
# EXTRACCIÓN POR BLOQUES (MUY IMPORTANTE)
# ==========================================

def extraer_texto_por_bloques(doc):

    texto_total = ""

    for pagina in doc:

        bloques = pagina.get_text("blocks")

        # ordenar bloques según posición en la página
        bloques = sorted(bloques, key=lambda b: (b[1], b[0]))

        for bloque in bloques:

            texto = bloque[4].strip()

            if len(texto) > 20:
                texto_total += texto + "\n"

        texto_total += "\n"

    return texto_total

# ==========================================
# FUNCIÓN PRINCIPAL DE CARGA
# ==========================================

def cargar_manual(
        pdf_path,
        categoria,
        controlador=None,
        modelo_robot=None,
        letra_error=None):

    print(f"\n--- Procesando {pdf_path} ---")

    doc = fitz.open(pdf_path)

    texto_completo = extraer_texto_por_bloques(doc)

    doc.close()

    texto_completo = limpiar_texto(texto_completo)

    # ==========================================
    # CONFIGURACIÓN DE CHUNKS
    # ==========================================

    chunk_size = 1200
    overlap = 300

    chunks = []

    for i in range(0, len(texto_completo), chunk_size - overlap):

        chunk = texto_completo[i:i + chunk_size]

        if len(chunk.strip()) > 150:
            chunks.append(chunk.strip())

    print(f"Fragmentos generados: {len(chunks)}")

    # ==========================================
    # PREPARAR TEXTO PARA BGE
    # ==========================================

    chunks_prefixed = [
        "Represent this sentence for searching relevant technical manual passages: " + c
        for c in chunks
    ]

    print("Generando embeddings...")

    embeddings = model.encode(
        chunks_prefixed,
        batch_size=32,
        show_progress_bar=True
    )

    # ==========================================
    # PREPARAR DATOS PARA SUPABASE
    # ==========================================

    rows = []

    for idx, (texto, embedding) in enumerate(zip(chunks, embeddings)):
        
        rows.append({
            "content": texto,
            "embedding": embedding.tolist(),
            "categoria": categoria,
            "controlador": controlador,
            "modelo_robot": modelo_robot,
            "letra_error": letra_error,
            "chunk_index": idx,
            "metadata": {
                "chunk_size": chunk_size,
                "overlap": overlap,
                "source": pdf_path
            }
        })

    # ==========================================
    # INSERT MASIVO (MUCHO MÁS RÁPIDO)
    # ==========================================

    print("Subiendo embeddings a Supabase...")

    supabase.table("manuales_fanuc").insert(rows).execute()

    print("✅ Carga finalizada")

# ==========================================
# EJECUCIÓN
# ==========================================

if __name__ == "__main__":

    # 1️⃣ Manual errores A-Z
    cargar_manual(
        "ERROR A.pdf",
        categoria="errores",
        letra_error="A"
    )
    cargar_manual(
        "ERROR B.pdf",
        categoria="errores",
        letra_error="B"
    )
    cargar_manual(
        "ERROR C.pdf",
        categoria="errores",
        letra_error="C"
    )
    cargar_manual(
        "ERROR D.pdf",
        categoria="errores",
        letra_error="D"
    )
    cargar_manual(
        "ERROR E.pdf",
        categoria="errores",
        letra_error="E"
    )
    cargar_manual(
        "ERROR F.pdf",
        categoria="errores",
        letra_error="F"
    )
    cargar_manual(
        "ERROR G.pdf",
        categoria="errores",
        letra_error="G"
    )
    cargar_manual(
        "ERROR H.pdf",
        categoria="errores",
        letra_error="H"
    )
    cargar_manual(
        "ERROR I.pdf",
        categoria="errores",
        letra_error="I"
    )
    cargar_manual(
        "ERROR J.pdf",
        categoria="errores",
        letra_error="J"
    )
    cargar_manual(
        "ERROR L.pdf",
        categoria="errores",
        letra_error="L"
    )
    cargar_manual(
        "ERROR M.pdf",
        categoria="errores",
        letra_error="M"
    )
    cargar_manual(
        "ERROR O.pdf",
        categoria="errores",
        letra_error="O"
    )
    cargar_manual(
        "ERROR P.pdf",
        categoria="errores",
        letra_error="P"
    )
    cargar_manual(
        "ERROR Q.pdf",
        categoria="errores",
        letra_error="Q"
    )
    cargar_manual(
        "ERROR R.pdf",
        categoria="errores",
        letra_error="R"
    )
    cargar_manual(
        "ERROR S.pdf",
        categoria="errores",
        letra_error="S"
    )
    cargar_manual(
        "ERROR T.pdf",
        categoria="errores",
        letra_error="T"
    )
    cargar_manual(
        "ERROR V.pdf",
        categoria="errores",
        letra_error="V"
    )
    cargar_manual(
        "ERROR W.pdf",
        categoria="errores",
        letra_error="W"
    )


    # 2️⃣ Controller R-J3iB
    cargar_manual(
        "Manual Controller Maintenance - R-J3iB.pdf",
        categoria="mantenimiento_controlador",
        controlador="R-J3iB"
    )

    # 3️⃣ Controller R-30iA
    cargar_manual(
        "Manual Controller Maintenance - R30iA.pdf",
        categoria="mantenimiento_controlador",
        controlador="R-30iA"
    )

    # 4️⃣ Manual mecánico robot
    cargar_manual(
        "Manual M410iB450 - R30iA.pdf",
        categoria="mantenimiento_robot",
        modelo_robot="M-410iB/450"
    )