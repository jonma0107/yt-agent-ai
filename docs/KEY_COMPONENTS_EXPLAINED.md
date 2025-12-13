# Explicación de Archivos Clave y Decisiones Técnicas

Este documento profundiza en los componentes auxiliares del sistema, la estrategia de limpieza de datos, la configuración del entorno y el rol de la base de datos. Sirve como complemento a la documentación de Arquitectura.

## 🗂️ 1. Archivos de Utilidad y Mantenimiento

### `cleanup_media.py`
**Propósito:** Mantener la higiene del servidor eliminando archivos temporales antiguos.
**Funcionamiento:**
- Escanea el directorio `media/`.
- Identifica archivos (`.mp4`, `.mp3`, `.txt`) que tienen más de **1 hora** de antigüedad.
- Los elimina para liberar espacio en disco.
**Contexto:** Dado que la aplicación descarga video y audio para cada solicitud, el disco del servidor se llenaría rápidamente sin este script. Es esencial para la **sostenibilidad operativa** de la app.

### `crontab`
**Propósito:** Automatizar la ejecución periódica de tareas de mantenimiento.
**Contenido:**
```cron
*/30 * * * * python /backend/cleanup_media.py >> /var/log/cron.log 2>&1
```
**Explicación:** Configura al sistema (dentro del contenedor Docker) para ejecutar el script `cleanup_media.py` cada **30 minutos**. Esto garantiza que la limpieza sea automática y transparente, previniendo el desbordamiento de almacenamiento.

### `django_setup.py`
**Propósito:** Permitir que scripts externos (como `app.py` de Streamlit) usen el ORM y modelos de Django.
**Lógica:**
1. Configura la variable de entorno `DJANGO_SETTINGS_MODULE`.
2. Llama a `django.setup()`.
**Importancia:** Streamlit es una aplicación independiente de Django. Sin este archivo, Streamlit no podría importar `translationPost` ni guardar datos en la base de datos de Django. Actúa como el **puente** entre el Frontend (Streamlit) y el Backend (Django).

---

## 🏗️ 2. Modularización de Servicios (`translation_generator_app/services/`)

La lógica de negocio se ha desacoplado completamente de las Vistas (Views) para seguir el **Principio de Responsabilidad Única (SRP)**.

### ¿Por qué modularizar?
En versiones anteriores, una sola función gigante hacía todo: descargaba, transcribía y traducía. Esto era difícil de leer, probar y mantener.

### Estructura Actual:
1.  **`youtube_service.py`**:
    *   **Responsabilidad:** Solo interactúa con `yt-dlp`.
    *   **Detalle:** Maneja headers anti-bot, descarga física de archivos y sanitización de nombres. No sabe nada de IA.
2.  **`transcription_service.py`**:
    *   **Responsabilidad:** Solo interactúa con AssemblyAI.
    *   **Detalle:** Sube el audio y devuelve texto crudo. No sabe de dónde vino el audio ni para qué se usará.
3.  **`translation_service.py`**:
    *   **Responsabilidad:** Solo interactúa con OpenAI y lógica de texto.
    *   **Detalle:** Detecta idiomas y decide si traducir o solo formatear. Es pura manipulación de texto.

**Beneficio:** Si mañana queremos cambiar AssemblyAI por Whisper, solo tocamos `transcription_service.py`. El resto del sistema ni se entera.

---

## ⚠️ 3. Manejo de Errores (`translation_generator_app/exceptions.py`)

Se implementó una jerarquía de excepciones personalizada para dejar de usar respuestas genéricas como "Error 500".

*   **`YouTubeDownloadException`**: "No pudimos descargar el video (quizás es privado)".
*   **`TranscriptionException`**: "Falló el servicio de voz a texto".
*   **`TranslationException`**: "OpenAI no respondió o falló la API key".

Esto permite que la UI (Streamlit) muestre mensajes **específicos y accionables** al usuario, en lugar de un "Algo salió mal" genérico.

---

## 💾 4. Base de Datos: Rol y Uso

### ¿Por qué es necesaria?
Aunque la app parece procesar en tiempo real y mostrar el resultado, necesitamos persistencia para:
1.  **Historial y Auditoría:** Saber qué videos se han procesado.
2.  **Análisis:** Entender qué canciones o idiomas son populares.
3.  **Depuración:** Si algo falla, el registro en BD puede ayudar (aunque actualmente guardamos al final del éxito).

### Modelo `translationPost`
*   **`youtube_title`**: Título del video.
*   **`youtube_link`**: URL original.
*   **`generated_content`**: El resultado final (traducido/formateado).
*   **`created_at`**: Fecha de procesamiento.

### Ciclo de Vida del Dato
1.  El usuario solicita una canción en Streamlit.
2.  Los servicios procesan todo en memoria/archivos temporales.
3.  **Solo al final**, si todo fue exitoso, el orquestador (en `app.py`) crea una entrada en `translationPost`.
4.  Actualmente, estos datos son de **escritura** (Logging/History). La aplicación no lee estos datos para mostrarlos al usuario (no hay un "feed" de traducciones anteriores), pero la arquitectura está lista para esa funcionalidad si se necesitara.
