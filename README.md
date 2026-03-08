<img width="1120" height="678" alt="image" src="https://github.com/user-attachments/assets/f92f25c9-bf1e-401a-a4bf-bdf4eb01c8e6" />

# 🤖 Chatbot RAG Híbrido para Manuales de Robots FANUC

Chatbot basado en **Retrieval-Augmented Generation (RAG)** diseñado para consultar **manuales técnicos de robots industriales FANUC** utilizando búsqueda semántica y modelos de lenguaje.

El sistema permite realizar preguntas en lenguaje natural y obtener respuestas basadas **exclusivamente en el contenido de los manuales técnicos**, evitando respuestas inventadas por el modelo.

Este proyecto demuestra cómo aplicar **Inteligencia Artificial y bases vectoriales** para mejorar el acceso a documentación técnica industrial.

---

# 📌 Descripción del Proyecto

Los manuales de robots industriales suelen ser extensos, complejos y difíciles de navegar durante tareas de programación, mantenimiento o diagnóstico de fallas.

Este proyecto implementa un **chatbot RAG híbrido** que permite consultar los manuales mediante preguntas como:

- ¿Cómo resetear una alarma en un robot FANUC?
- ¿Qué significa el error SRVO-050?
- ¿Cómo realizar la calibración de ejes?
- ¿Cómo configurar un programa en el robot?

El sistema busca los fragmentos más relevantes de los manuales y los utiliza como **contexto para generar respuestas precisas**.

---

# 🧠 Arquitectura del Sistema

El chatbot utiliza una arquitectura **Retrieval-Augmented Generation (RAG)**.

Flujo de funcionamiento:

1. El usuario realiza una pregunta desde la interfaz web.
2. La pregunta se convierte en **embeddings vectoriales**.
3. Se buscan los fragmentos más relevantes en la base vectorial.
4. Los fragmentos recuperados se envían como **contexto al modelo de lenguaje**.
5. El modelo genera una respuesta basada en la documentación.

Esto permite que el modelo responda **utilizando únicamente información real de los manuales**.

---

# 🔎 Estrategia de Recuperación Híbrida

El sistema utiliza una **búsqueda híbrida**, combinando distintos enfoques para mejorar la precisión en documentación técnica:

- Búsqueda semántica mediante **embeddings**
- Búsqueda por **palabras clave**
- Similitud vectorial con **pgvector**

Este enfoque es especialmente útil en documentación técnica donde los **términos exactos son importantes**.

---

# 🧰 Tecnologías Utilizadas

## Backend

- Python

## Interfaz Web

- Streamlit

## Base de Datos Vectorial

- Supabase (PostgreSQL)
- Extensión pgvector

## Modelo de Lenguaje (LLM)

- Google Gemini

## Embeddings

- Gemini Embeddings

## Fuente de Datos

- Manuales técnicos de robots FANUC en formato PDF

---

# 📂 Estructura del Proyecto
fanuc-rag-chatbot/
│
├── app.py
│ Interfaz del chatbot en Streamlit
│
├── embeddings_pipeline.py
│ Procesamiento de documentos y generación de embeddings
│
├── retrieval.py
│ Lógica de búsqueda vectorial
│
├── prompt_builder.py
│ Construcción del prompt con contexto recuperado
│
├── supabase_client.py
│ Conexión y consultas a la base de datos
│
├── data/
│ └── manuals/
│ Manuales técnicos FANUC
│
├── requirements.txt
│
└── README.md

# ⚙️ Instalación

## 1 Clonar el repositorio

```bash
git clone https://github.com/tu_usuario/fanuc-rag-chatbot.git
cd fanuc-rag-chatbot

## 2 Instalar dependencias
```bash
pip install -r requirements.txt

## 3 Configurar variables de entorno
```bash
SUPABASE_URL=tu_supabase_url
SUPABASE_KEY=tu_supabase_key
GEMINI_API_KEY=tu_api_key

# ▶️ Ejecutar la Aplicación
Iniciar la aplicación con Streamlit:
```bash
streamlit run app.py

Luego abrir en el navegador:
```bash
http://localhost:8501

# 🔧 Casos de Uso
```bash

Este chatbot puede utilizarse para:

Consultar errores y alarmas de robots

Buscar procedimientos de programación

Encontrar instrucciones de mantenimiento

Navegar rápidamente manuales técnicos extensos

Este enfoque puede aplicarse también a:

Manuales de maquinaria industrial

Documentación de PLC

Sistemas de mantenimiento

Bases de conocimiento técnicas

# 🚀 Posibles Mejoras Futuras

Algunas extensiones posibles del proyecto:

Soporte para múltiples manuales simultáneamente

Evaluación de calidad del sistema RAG

Memoria conversacional

Implementación de Hybrid Search avanzada

Despliegue en nube (Docker / cloud)

# 🏭 Aplicaciones en Industria

Los sistemas RAG pueden utilizarse en entornos industriales para:

Asistentes de mantenimiento

Soporte técnico automatizado

Sistemas de consulta de documentación técnica

Asistentes de diagnóstico de equipos

Este proyecto demuestra el potencial de IA aplicada al mantenimiento industrial y la ingeniería de confiabilidad.

# 👤 Autor

Gabriel Afredo Regali

