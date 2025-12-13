# Arquitectura Backend YT-AGENT-AI

## 📋 Tabla de Contenidos
- [Descripción General](#descripción-general)
- [Patrón de Arquitectura](#patrón-de-arquitectura)
- [Estructura de Directorios](#estructura-de-directorios)
- [Componentes Principales](#componentes-principales)
- [Flujo de Ejecución](#flujo-de-ejecución)
- [Soporte Multiidioma](#soporte-multiidioma)
- [Referencia API](#referencia-api)

## 📖 Descripción General

El backend de **YT-AGENT-AI** está construido utilizando un enfoque de **Clean Architecture**, asegurando separación de responsabilidades, testabilidad y mantenibilidad. La lógica central está desacoplada del framework (Django) y de la UI (Streamlit), residiendo en **Servicios** dedicados.

Principios arquitectónicos clave:
*   **Capa de Servicios**: Encapsula la lógica de negocio (descarga de YouTube, Transcripción, Traducción).
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
        Streamlit[Streamlit UI (app.py)]
        API[Vista API Django]
    end
    
    EntryPoint --> Streamlit
    EntryPoint --> API
    
    Streamlit --> Orchestrator
    API --> Orchestrator
    
    subgraph "Capa de Servicio (Lógica de Negocio)"
        Orchestrator[Orquestación de Servicios]
        YT[YouTubeService]
        AI_Trans[TranscriptionService (AssemblyAI)]
        AI_Transl[TranslationService (OpenAI)]
    end
    
    Orchestrator --> YT
    YT --> Files[Archivos Media (MP4/MP3)]
    
    Orchestrator --> AI_Trans
    AI_Trans --> Text[Transcripción Cruda]
    
    Orchestrator --> AI_Transl
    AI_Transl --> Final[Texto Formateado y Traducido]
    
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
│   │   └── translation_service.py    # integración con OpenAI
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

*   **`TranslationService`**: Interactúa con OpenAI (GPT-4o/Turbo).
    *   **Detección de Idioma**: Detecta automáticamente el idioma de origen.
    *   **Traducción Inteligente**: 
        *   Si `origen == destino`: Formatea el texto en versos/estrofas.
        *   Si `origen != destino`: Formatea Y traduce preservando el significado/rima.

### 2. Interfaz Streamlit (`app.py`)

El frontend es un contenedor ligero alrededor de la Capa de Servicio. **No** contiene lógica de negocio.

*   **Llamada Directa a Servicio**: En lugar de llamar a la API de Django vía HTTP, importa los Servicios directamente (ya que comparten el mismo contenedor/código base).
*   **Gestión de Estado**: Usa `st.session_state` para persistir resultados entre re-ejecuciones.
*   **Manejo de Errores**: Captura excepciones personalizadas específicas (`YouTubeDownloadException`, etc.) para mostrar mensajes de error amigables al usuario.

### 3. Excepciones Personalizadas (`exceptions.py`)

*   `TranslationGeneratorException` (Base)
    *   `YouTubeDownloadException`
    *   `TranscriptionException`
    *   `TranslationException`
    *   `InvalidDataException`

## 🔄 Flujo de Ejecución

1.  **Entrada**: El usuario proporciona URL de YouTube y API Key de OpenAI.
2.  **Descarga**: `YouTubeService` descarga medios a `media/`.
3.  **Transcripción**: `TranscriptionService` envía audio a AssemblyAI y obtiene texto.
4.  **Procesamiento**: `TranslationService` analiza el texto:
    *   Detecta idioma (e.g., 'en').
    *   Compara con destino (e.g., 'es').
    *   Genera la salida final.
5.  **Persistencia**: resultado guardado en PostgreSQL vía Django ORM.
6.  **Visualización**: Resultados mostrados en UI con botones de descarga.

## 🌍 Soporte Multiidioma

El sistema actualmente soporta **11 idiomas** con capacidades completas de detección y traducción.

| Código | Idioma | Nombre Nativo |
|--------|----------|-------------|
| `es` | Español | Español |
| `en` | Inglés | English |
| `fr` | Francés | Français |
| `de` | Alemán | Deutsch |
| `it` | Italiano | Italiano |
| `pt` | Portugués | Português |
| `ru` | Ruso | Русский |
| `ja` | Japonés | 日本語 |
| `ko` | Coreano | 한국어 |
| `zh` | Chino | 中文 |
| `ar` | Árabe | العربية |

## 📚 Referencia API

Aunque la app Streamlit es la interfaz principal, el backend expone un endpoint REST:

**Endpoint:** `POST /api/generate-translation/`

**Payload:**
```json
{
    "link": "https://youtube.com/watch?v=...",
    "openai_api_key": "sk-...",
    "target_language": "fr" 
}
```

**Respuesta:**
```json
{
    "content": "Texto traducido...",
    "title": "Título del Video",
    "original_transcription": "Texto original...",
    "video_file": "/ruta/al/video.mp4",
    "audio_file": "/ruta/al/audio.mp3",
    "target_language": "fr"
}
```