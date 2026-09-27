# Arquitectura Backend YT-AGENT-AI

## 📋 Tabla de Contenidos
- [Descripción General](#descripción-general)
- [Patrón de Arquitectura](#patrón-de-arquitectura)
- [Estructura de Directorios](#estructura-de-directorios)
- [Componentes Principales](#componentes-principales)
- [Flujo de Ejecución](#flujo-de-ejecución)
- [Referencia API](#referencia-api)

## 📖 Descripción General

El backend de **YT-AGENT-AI** está construido utilizando un enfoque de **Clean Architecture**, asegurando separación de responsabilidades, testabilidad y mantenibilidad. La lógica central está desacoplada del framework (Django) y de la UI (Streamlit), residiendo en **Servicios** dedicados.

Principios arquitectónicos clave:
*   **Capa de Servicios**: Encapsula la lógica de negocio (descarga de YouTube, Transcripción, Análisis de Contenido).
*   **Vistas Basadas en Clases (CBV)**: Maneja las solicitudes HTTP y el formato de respuesta.
*   **Excepciones Personalizadas**: Proporciona manejo de errores granular.
*   **Principios SOLID**: Aplicados en todo el código base.

## 🏗️ Patrón de Arquitectura

El flujo de datos sigue un camino estricto desde el punto de entrada (UI o API) hacia abajo hasta los servicios y la base de datos.

```mermaid
graph TD
    User[Usuario / Cliente] --> EntryPoint
    
    subgraph "Capa de Entrada"
        EntryPoint{Punto de Entrada}
        Streamlit["Streamlit UI (app.py)"]
        API[Vista API Django]
    end
    
    EntryPoint --> Streamlit
    EntryPoint --> API
    
    Streamlit --> Orchestrator
    API --> Orchestrator
    
    subgraph "Capa de Servicio (Lógica de Negocio)"
        Orchestrator[Orquestación de Servicios]
        YT[YouTubeService]
        AI_Trans[TranscriptionService - AssemblyAI]
        AI_An[AnalysisService - Gemini]
    end
    
    Orchestrator --> YT
    YT --> Files[Archivos Media MP4/MP3]
    
    Orchestrator --> AI_Trans
    AI_Trans --> Text[Transcripción Cruda]
    
    Orchestrator --> AI_An
    AI_An --> Report[Reporte de Contenido]
    
    subgraph "Capa de Datos"
        DB[(PostgreSQL)]
    end
    
    Orchestrator --> DB
```

## 📁 Estructura de Directorios

```
Backend/
├── translation_generator_app/
│   ├── services/                 # Lógica de Negocio central
│   │   ├── __init__.py
│   │   ├── youtube_service.py    # contenedor (wrapper) de yt-dlp
│   │   ├── transcription_service.py  # integración con AssemblyAI
│   │   └── analysis_service.py   # integración con Google Gemini
│   │
│   ├── exceptions.py             # Jerarquía de Excepciones Personalizadas
│   ├── models.py                 # Modelos de base de datos
│   ├── serializers/              # Validación de datos
│   └── views/                    # Vistas de API
│
├── app.py                        # Aplicación Frontend Streamlit
├── Dockerfile                    # Definición del contenedor
├── docker-compose.yml            # Orquestación de desarrollo local
└── manage.py                     # Punto de entrada de Django
```

## 🧩 Componentes Principales

### 1. Servicios (`translation_generator_app/services/`)

*   **`YouTubeService`**: Maneja la extracción de video y audio.
    *   Usa `yt-dlp` con cabeceras personalizadas para evadir detección de bots (errores 403).
    *   Descarga video (MP4) y audio (MP3) por separado.
    *   Sanitiza los nombres de archivo.

*   **`TranscriptionService`**: Interactúa con AssemblyAI.
    *   Sube archivos de audio.
    *   Solicita la transcripción.
    *   Sondea (poll) hasta que se completa.

*   **`AnalysisService`**: Interactúa con Google Gemini.
    *   **Generación de Reporte de Contenido**: Analiza la transcripción completa y genera un reporte estructurado con 5 secciones:
        *   Temas principales tratados
        *   Argumento / resumen narrativo
        *   Opiniones o puntos de vista expresados
        *   Datos o hechos clave
        *   Conclusión / veredicto final
    *   Utiliza el modelo `gemini-3.5-flash` con `temperature=0.7`.

### 2. Interfaz Streamlit (`app.py`)

El frontend es un contenedor ligero alrededor de la Capa de Servicio. **No** contiene lógica de negocio.

*   **Llamada Directa a Servicio**: En lugar de llamar a la API de Django vía HTTP, importa los Servicios directamente (ya que comparten el mismo contenedor/código base).
*   **Gestión de Estado**: Usa `st.session_state` para persistir resultados entre re-ejecuciones.
*   **Manejo de Errores**: Captura excepciones personalizadas específicas (`YouTubeDownloadException`, etc.) para mostrar mensajes de error amigables al usuario.

### 3. Excepciones Personalizadas (`exceptions.py`)

*   `TranslationGeneratorException` (Base)
    *   `YouTubeDownloadException`
    *   `TranscriptionException`
    *   `AnalysisException`
    *   `InvalidDataException`

## 🔄 Flujo de Ejecución

1.  **Entrada**: El usuario proporciona URL de YouTube y API Key de Gemini.
2.  **Descarga**: `YouTubeService` descarga medios a `media/`.
3.  **Transcripción**: `TranscriptionService` envía audio a AssemblyAI y obtiene texto.
4.  **Análisis**: `AnalysisService` envía la transcripción a Gemini y genera un Reporte de Contenido estructurado.
5.  **Persistencia**: resultado guardado en PostgreSQL vía Django ORM.
6.  **Visualización**: Resultados mostrados en UI con botones de descarga.

## 📚 Referencia API

Aunque la app Streamlit es la interfaz principal, el backend expone un endpoint REST:

**Endpoint:** `POST /generate-report/`

**Payload:**
```json
{
    "link": "https://youtube.com/watch?v=...",
    "gemini_api_key": "AI..."
}
```

**Respuesta:**
```json
{
    "report": "Reporte de contenido...",
    "title": "Título del Video",
    "original_transcription": "Texto original...",
    "transcription_file": "/ruta/al/transcript.txt"
}
```