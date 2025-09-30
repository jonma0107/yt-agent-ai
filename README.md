# 🎵 IA TRANSLATION - Backend

<img width="1413" height="888" alt="image" src="https://github.com/user-attachments/assets/4c515a7a-19d8-4051-8842-919b4727d8fe" />

<img width="1853" height="937" alt="image" src="https://github.com/user-attachments/assets/b0f2cc61-2a56-42bf-8404-b04ca25467bc" />

## 📖 Descripción

**IA TRANSLATION** es una aplicación web avanzada que permite traducir y obtener las letras de tus canciones favoritas de YouTube. Utiliza inteligencia artificial para transcribir, formatear y traducir automáticamente las letras de canciones a múltiples idiomas.

### ✨ Características Principales

- 🎥 **Descarga de YouTube**: Descarga video y audio de YouTube
- 🎙️ **Transcripción con IA**: Usa AssemblyAI para transcribir audio
- 🌍 **Traducción Multiidioma**: Soporta 11 idiomas diferentes
- 🤖 **Detección Automática**: Detecta el idioma del audio automáticamente
- 💡 **Traducción Inteligente**: Solo traduce si es necesario
- 🎨 **Interfaz Streamlit**: UI moderna e intuitiva
- 📊 **API REST**: Endpoint completo para integraciones
- 🏗️ **Arquitectura Limpia**: Clean Architecture + SOLID principles

---

## 🌍 Idiomas Soportados

| Idioma | Código | Idioma | Código |
|--------|--------|--------|--------|
| 🇪🇸 Español | `es` | 🇵🇹 Português | `pt` |
| 🇬🇧 English | `en` | 🇷🇺 Русский | `ru` |
| 🇫🇷 Français | `fr` | 🇯🇵 日本語 | `ja` |
| 🇩🇪 Deutsch | `de` | 🇰🇷 한국어 | `ko` |
| 🇮🇹 Italiano | `it` | 🇨🇳 中文 | `zh` |
| - | - | 🇸🇦 العربية | `ar` |

---

## 🚀 Inicio Rápido

### Requisitos Previos

- Python 3.8+
- PostgreSQL
- AssemblyAI API Key
- OpenAI API Key

### Instalación

```bash
# Clonar el repositorio
git clone <repository-url>
cd Backend

# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
cp .env.example .env
# Editar .env con tus API keys

# Ejecutar migraciones
python manage.py migrate

# Iniciar servidor Django
python manage.py runserver

# En otra terminal, iniciar Streamlit
streamlit run app.py
```

---

## 📚 Documentación Completa

Toda la documentación del proyecto está organizada en la carpeta [`docs/`](./docs/):

### 📋 Índice de Documentación

1. **[ARCHITECTURE.md](./docs/ARCHITECTURE.md)** - Arquitectura técnica completa
2. **[REFACTORING_COMPLETE.md](./docs/REFACTORING_COMPLETE.md)** - Resumen de refactorización
3. **[STREAMLIT_INTEGRATION.md](./docs/STREAMLIT_INTEGRATION.md)** - Integración Streamlit
4. **[MULTILANGUAGE_TRANSLATION.md](./docs/MULTILANGUAGE_TRANSLATION.md)** - Guía multiidioma
5. **[SETTINGS_CLEANUP_COMPLETE.md](./docs/SETTINGS_CLEANUP_COMPLETE.md)** - Configuración Django
6. **[DOCUMENTATION_UPDATE.md](./docs/DOCUMENTATION_UPDATE.md)** - Registro de cambios

📌 **Ver el [README completo de documentación](./docs/README.md)** para guías detalladas y referencias.

---

## 🔌 API Reference

### Endpoint Principal

```http
POST /api/generate-translation/
Content-Type: application/json

{
    "link": "https://youtube.com/watch?v=...",
    "openai_api_key": "sk-...",
    "target_language": "fr"  // Opcional, default: "es"
}
```

### Respuesta

```json
{
    "content": "Texto traducido...",
    "title": "Título del video",
    "original_transcription": "Texto original formateado...",
    "video_file": "/path/to/video.mp4",
    "audio_file": "/path/to/audio.mp3",
    "target_language": "fr"
}
```

---

## 🏗️ Arquitectura

```
Backend/
├── ai_translation/          # Configuración Django
├── translation_generator_app/
│   ├── services/           # Lógica de negocio
│   │   ├── youtube_service.py
│   │   ├── transcription_service.py
│   │   └── translation_service.py
│   ├── serializers/        # Validadores
│   ├── views/             # Vistas CBV
│   └── exceptions.py      # Excepciones personalizadas
├── docs/                  # 📚 Documentación completa
├── media/                 # Archivos generados
├── app.py                # Interfaz Streamlit
└── manage.py             # Django CLI
```

### Servicios Principales

- **YouTubeService**: Descarga de videos de YouTube
- **TranscriptionService**: Transcripción con AssemblyAI  
- **TranslationService**: Traducción y formateo con OpenAI

---

## 🛠️ Tecnologías

- **Backend**: Django 4.1, Django REST Framework
- **Frontend**: Streamlit
- **Base de Datos**: PostgreSQL
- **IA/ML**: 
  - AssemblyAI (transcripción)
  - OpenAI GPT-4 (traducción)
- **Descarga**: yt-dlp
- **Servidor**: Gunicorn + Whitenoise

---

## 🔐 Variables de Entorno

```bash
# .env
AAI_API_KEY=your_assemblyai_api_key
SECRET_KEY=your_django_secret_key
DEBUG=True
DB_NAME=your_db_name
DB_USER=your_db_user
DB_PASS=your_db_password
DB_HOST=localhost
```

---

## 📊 Métricas del Proyecto

| Métrica | Valor |
|---------|-------|
| **Idiomas Soportados** | 11 🌍 |
| **Servicios** | 3 |
| **Excepciones Personalizadas** | 5 |
| **Arquitectura** | Clean Architecture + SOLID |
| **Type Hints** | 100% |
| **Logging** | 100% |
| **Documentación** | 64KB |

---

## 🤝 Contribuir

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

---

## 📝 Licencia

Este proyecto está bajo la Licencia MIT.

---

## 📞 Soporte

Para soporte y preguntas:
- 📚 Consulta la [documentación completa](./docs/README.md)
- 🐛 Reporta bugs en Issues
- 💡 Sugiere features en Discussions

---

**Desarrollado con ❤️ usando Clean Architecture y SOLID principles**

*Última actualización: Septiembre 30, 2025*

