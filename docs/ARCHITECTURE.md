# Translation Generator App - Arquitectura

## 📋 Tabla de Contenidos
- [Descripción General](#descripción-general)
- [Arquitectura](#arquitectura)
- [Estructura de Directorios](#estructura-de-directorios)
- [Componentes](#componentes)
- [Flujo de Ejecución](#flujo-de-ejecución)
- [API Reference](#api-reference)
- [Testing](#testing)

## 📖 Descripción General

La aplicación Translation Generator ha sido completamente refactorizada siguiendo principios de **Clean Architecture** y **SOLID**. El código ahora está organizado en servicios independientes, vistas basadas en clases (CBV), validadores, y excepciones personalizadas.

### Mejoras Implementadas

✅ **Separación de Responsabilidades**: Cada servicio tiene una única responsabilidad  
✅ **Código Testeable**: Servicios independientes fáciles de probar  
✅ **Manejo de Errores Robusto**: Excepciones específicas por tipo de error  
✅ **Validación de Datos**: Validación centralizada de entrada  
✅ **Logging Integrado**: Trazabilidad completa del procesamiento  
✅ **Type Hints**: Código autodocumentado con anotaciones de tipo  

## 🏗️ Arquitectura

```
┌─────────────┐
│   Request   │
└──────┬──────┘
       │
       v
┌──────────────────────┐
│ TranslationGenerator │ (Class-Based View)
│       View          │ - Validación
└──────────────────────┘ - Orquestación
       │
       ├──────────────────────────────────────┐
       │                                      │
       v                                      v
┌─────────────────┐              ┌────────────────────┐
│  YouTubeService │              │ TranslationService │
│                 │              │                    │
│ - get_title()   │              │ - format_text()    │
│ - download()    │              │ - translate()      │
└─────────────────┘              └────────────────────┘
       │
       v
┌──────────────────────┐
│ TranscriptionService │
│                      │
│ - transcribe_audio() │
└──────────────────────┘
       │
       v
┌──────────────┐
│   Database   │
└──────────────┘
```

## 📁 Estructura de Directorios

```
translation_generator_app/
├── __init__.py
├── admin.py
├── apps.py
├── models.py
├── urls.py
├── ARCHITECTURE.md           # Este archivo
│
├── exceptions.py             # Excepciones personalizadas
│
├── services/                 # Capa de servicios
│   ├── __init__.py
│   ├── youtube_service.py    # Lógica de YouTube
│   ├── transcription_service.py  # Lógica de AssemblyAI
│   └── translation_service.py    # Lógica de OpenAI
│
├── serializers/             # Validadores
│   ├── __init__.py
│   └── translation_serializer.py
│
├── views/                   # Vistas
│   └── views_app.py        # CBV principal
│
└── migrations/
    └── ...
```

## 🧩 Componentes

### 1. Excepciones (`exceptions.py`)

Jerarquía de excepciones personalizadas:

```python
TranslationGeneratorException (Base)
├── YouTubeDownloadException
├── TranscriptionException
├── TranslationException
└── InvalidDataException
```

**Uso**: Permite capturar y manejar errores específicos en diferentes niveles.

### 2. Servicios (`services/`)

#### **YouTubeService** (`youtube_service.py`)
Maneja toda la interacción con YouTube:

```python
class YouTubeService:
    @staticmethod
    def get_title(link: str) -> str
        """Extrae el título del video"""
    
    @staticmethod
    def download_video_and_audio(link: str, title: str) -> Tuple[str, str]
        """Descarga video (MP4) y audio (MP3)"""
```

#### **TranscriptionService** (`transcription_service.py`)
Maneja la transcripción con AssemblyAI:

```python
class TranscriptionService:
    def __init__(self, api_key: str)
    
    def transcribe_audio(self, audio_file: str, title: str) -> str
        """Transcribe audio y guarda el archivo .txt"""
```

#### **TranslationService** (`translation_service.py`)
Maneja formateo y traducción multiidioma con OpenAI:

```python
class TranslationService:
    SUPPORTED_LANGUAGES = ['es', 'en', 'fr', 'de', 'it', 'pt', 'ru', 'ja', 'ko', 'zh', 'ar']
    
    def __init__(self, api_key: str)
    
    def detect_language(self, text: str) -> str
        """Detecta el idioma del texto automáticamente"""
    
    def format_text_as_verses(self, text: str) -> str
        """Formatea texto en versos sin cambiar idioma"""
    
    def translate_text(self, text: str, target_language: str = 'es') -> str
        """Traduce a cualquier idioma soportado y formatea en versos"""
    
    def translate_to_spanish(self, text: str) -> str
        """Traduce a español (deprecated - usa translate_text)"""
    
    def process_transcription(self, original_text: str, target_language: str = 'es') -> Dict[str, str]
        """Detecta idioma, formatea original y traduce si es necesario"""
```

**Idiomas Soportados**: Español, English, Français, Deutsch, Italiano, Português, Русский, 日本語, 한국어, 中文, العربية

### 3. Validadores (`serializers/`)

#### **TranslationRequestValidator** (`translation_serializer.py`)

```python
class TranslationRequestValidator:
    SUPPORTED_LANGUAGES = ['es', 'en', 'fr', 'de', 'it', 'pt', 'ru', 'ja', 'ko', 'zh', 'ar']
    
    @staticmethod
    def validate(data: Dict[str, Any]) -> Dict[str, str]
        """Valida link de YouTube, API key y idioma objetivo (opcional)"""
```

Validaciones:
- ✅ Campos requeridos presentes (`link`, `openai_api_key`)
- ✅ URL de YouTube válida (regex)
- ✅ API key con formato correcto
- ✅ Idioma objetivo válido (opcional, default: 'es')
- ✅ Solo acepta idiomas soportados

### 4. Vista Basada en Clases (`views/views_app.py`)

#### **TranslationGeneratorView**

```python
class TranslationGeneratorView(View):
    def post(self, request)
        """Procesa POST request"""
    
    def get(self, request)
        """Retorna 405 Method Not Allowed"""
    
    def _parse_request_data(self, request) -> dict
        """Parsea JSON del request"""
    
    def _process_video(self, yt_link: str, openai_api_key: str) -> dict
        """Orquesta el procesamiento completo"""
```

**Características**:
- CSRF exempt (decorador)
- Manejo granular de excepciones
- Logging integrado
- Responses estructurados

## 🔄 Flujo de Ejecución

### 1. Request Recibido
```
POST /api/generate-translation/
{
    "link": "https://youtube.com/watch?v=...",
    "openai_api_key": "sk-...",
    "target_language": "fr"  // Opcional, default: "es"
}
```

### 2. Validación
```python
# TranslationRequestValidator valida:
- Campos requeridos ✓
- Formato de URL ✓
- Formato de API key ✓
- Idioma objetivo válido ✓ (opcional)
```

### 3. Procesamiento (Orquestado por la Vista)

```python
# 1. YouTubeService
title = youtube_service.get_title(yt_link)
video_file, audio_file = youtube_service.download_video_and_audio(yt_link, title)

# 2. TranscriptionService  
original_text = transcription_service.transcribe_audio(audio_file, title)

# 3. TranslationService (con detección automática de idioma)
processed_text = translation_service.process_transcription(
    original_text, 
    target_language=target_language  # 'es', 'fr', 'de', etc.
)
# Internamente:
# - Detecta idioma del audio
# - Si idioma detectado == target_language: solo formatea
# - Si idioma detectado != target_language: formatea + traduce
# Returns: {'original': formatted_text, 'translated': text_in_target_language}

# 4. Guardar en BD
translation = translationPost.objects.create(...)
```

### 4. Response
```json
{
    "content": "texto traducido al idioma objetivo...",
    "title": "título del video",
    "original_transcription": "texto original formateado...",
    "video_file": "/path/to/video.mp4",
    "audio_file": "/path/to/audio.mp3",
    "target_language": "fr"
}
```

## 📚 API Reference

### Endpoint

```
POST /api/generate-translation/
```

### Request Body

| Campo | Tipo | Requerido | Descripción |
|-------|------|-----------|-------------|
| `link` | string | ✅ | URL del video de YouTube |
| `openai_api_key` | string | ✅ | API key de OpenAI |
| `target_language` | string | ❌ | Código de idioma objetivo (default: 'es'). Valores: es, en, fr, de, it, pt, ru, ja, ko, zh, ar |

### Response (200 OK)

```json
{
    "content": "string (texto en idioma objetivo)",
    "title": "string",
    "original_transcription": "string (texto original formateado)",
    "video_file": "string",
    "audio_file": "string",
    "target_language": "string (código de idioma)"
}
```

### Errores

| Código | Excepción | Descripción |
|--------|-----------|-------------|
| `400` | InvalidDataException | Datos de entrada inválidos |
| `500` | YouTubeDownloadException | Error en descarga de YouTube |
| `500` | TranscriptionException | Error en transcripción |
| `500` | TranslationException | Error en traducción/formateo |
| `500` | TranslationGeneratorException | Error general |

## 🧪 Testing

### Ejemplo de Test Unitario para Servicio

```python
# tests/test_youtube_service.py
from django.test import TestCase
from translation_generator_app.services import YouTubeService
from translation_generator_app.exceptions import YouTubeDownloadException

class YouTubeServiceTest(TestCase):
    
    def test_get_title_success(self):
        service = YouTubeService()
        title = service.get_title("https://youtube.com/watch?v=...")
        self.assertIsNotNone(title)
        self.assertIsInstance(title, str)
    
    def test_get_title_invalid_url(self):
        service = YouTubeService()
        with self.assertRaises(YouTubeDownloadException):
            service.get_title("invalid-url")
```

### Ejemplo de Test de Integración

```python
# tests/test_views.py
from django.test import TestCase, Client
import json

class TranslationGeneratorViewTest(TestCase):
    
    def setUp(self):
        self.client = Client()
    
    def test_post_valid_request(self):
        data = {
            "link": "https://youtube.com/watch?v=...",
            "openai_api_key": "sk-..."
        }
        response = self.client.post(
            '/api/generate-translation/',
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn('content', response.json())
    
    def test_post_missing_fields(self):
        response = self.client.post(
            '/api/generate-translation/',
            data=json.dumps({}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
```

## 🌍 Funcionalidad Multiidioma

### Idiomas Soportados

La aplicación ahora soporta traducción a **11 idiomas diferentes**:

| Código | Idioma | Nombre Nativo |
|--------|--------|---------------|
| `es` | Español | Español |
| `en` | English | English |
| `fr` | Français | Français |
| `de` | Deutsch | Deutsch |
| `it` | Italiano | Italiano |
| `pt` | Português | Português |
| `ru` | Русский | Русский |
| `ja` | 日本語 | 日本語 |
| `ko` | 한국어 | 한국어 |
| `zh` | 中文 | 中文 |
| `ar` | العربية | العربية |

### Características Inteligentes

1. **Detección Automática de Idioma**
   - El sistema detecta automáticamente el idioma del audio transcrito
   - Usa los primeros 500 caracteres para eficiencia

2. **Traducción Condicional**
   - Si el idioma detectado es igual al idioma objetivo: **solo formatea**
   - Si el idioma detectado es diferente: **formatea + traduce**

3. **Traducción Contextual**
   - No hace traducciones literales palabra por palabra
   - Adapta expresiones idiomáticas y culturales
   - Mantiene el sentimiento, ritmo y estructura poética

4. **Normalización de Códigos**
   - Maneja variaciones de códigos de idioma (e.g., 'spa' → 'es')

### Ejemplo de Uso

**Request con idioma francés**:
```json
{
    "link": "https://youtube.com/watch?v=...",
    "openai_api_key": "sk-...",
    "target_language": "fr"
}
```

**Procesamiento**:
```python
# 1. Transcribe audio → "Hello world..." (detecta: inglés)
# 2. Idioma detectado (en) != idioma objetivo (fr)
# 3. Formatea original en inglés + Traduce al francés
# 4. Retorna ambos
```

**Response**:
```json
{
    "original_transcription": "Hello world\nIt's a beautiful day",
    "content": "Bonjour le monde\nC'est une belle journée",
    "target_language": "fr"
}
```

### Integración en Streamlit

El selector de idioma en la interfaz Streamlit permite:
- Selección visual con banderas (🇪🇸 🇬🇧 🇫🇷 etc.)
- Hint informativo: "If the song is already in [language], it will only be formatted"
- Título dinámico que cambia según el idioma seleccionado

📄 **Ver `MULTILANGUAGE_TRANSLATION.md` para documentación completa.**

## 🚀 Próximas Mejoras Sugeridas

1. **Async/Await**: Convertir operaciones I/O a asíncronas
2. **Celery Tasks**: Procesamiento en background
3. **Django REST Framework**: Mejores serializers y viewsets
4. **Redis Cache**: Cachear resultados de transcripción
5. **Rate Limiting**: Limitar requests por usuario
6. **Webhooks**: Notificaciones de procesamiento completado
7. **File Cleanup**: Limpieza automática de archivos media
8. ~~**Soporte Multiidioma**~~ ✅ **COMPLETADO** (11 idiomas)

## 📝 Notas de Migración

### Desde la Versión Anterior

La función `generate_translation` legacy sigue disponible para compatibilidad pero internamente usa la nueva vista basada en clases:

```python
# Antigua forma (aún funciona)
generate_translation(request)

# Nueva forma (recomendada)
TranslationGeneratorView.as_view()(request)
```

**Ventajas de CBV**:
- Mejor organización del código
- Reutilización mediante herencia
- Decoradores a nivel de método
- Testing más sencillo

---

**Desarrollado con 💙 siguiendo Clean Architecture** 