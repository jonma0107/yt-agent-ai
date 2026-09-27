# 🎵 YT-AGENT-AI

<img width="1528" height="783" alt="image" src="https://github.com/user-attachments/assets/359d58a4-ce58-4628-9142-6477742e1420.jpg" />

## 📖 Descripción General

**YT-AGENT-AI** es una aplicación web avanzada que permite analizar videos de YouTube y obtener un **Reporte de Contenido** detallado. Utiliza inteligencia artificial para transcribir el audio y generar un análisis estructurado de lo que se dice en el video.

### ✨ Características Principales

- 🎥 **YouTube Agent**: Descarga video y audio de alta calidad.
- 🎙️ **Transcripción con IA**: Transcripción de voz a texto de alta precisión usando AssemblyAI.
- 📊 **Reporte de Contenido**: Genera un análisis estructurado con Gemini (temas, argumento, opiniones, datos clave, conclusión).
- 🎨 **Interfaz Moderna**: Interfaz Streamlit para una interacción sencilla.
- 🏗️ **Clean Architecture**: Construido con separación de responsabilidades y principios SOLID.
- 🐳 **Dockerized**: Fácil despliegue y desarrollo local.

---

## 🚀 Inicio Rápido

La forma más fácil de ejecutar la aplicación es usando **Docker Compose**.

### Prerrequisitos

- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/install/)
- Google Gemini API Key
- AssemblyAI API Key

### Instalación

1.  **Clonar el repositorio:**

     ```bash
     git clone https://github.com/jonma0107/yt-agent-ai.git
     cd Backend
     ```

2.  **Configuración del Entorno:**

     Crea un archivo `.env` en el directorio raíz:

     ```bash
     cp .env.example .env
     ```

     Actualiza `.env` con tus credenciales:
     ```ini
     AAI_API_KEY=tu_api_key_assemblyai
     GEMINI_API_KEY=tu_api_key_gemini
     SECRET_KEY=tu_secret_key_django
     DEBUG=True
     DB_NAME=postgres
     DB_USER=postgres
     DB_PASS=postgres
     DB_HOST=db
     ```

3.  **Ejecutar con Docker Compose:**

     ```bash
     docker-compose up --build
     ```

     Este comando:
     *   Iniciará la base de datos PostgreSQL.
     *   Construirá e iniciará el servicio Backend (Django).
     *   Construirá e iniciará el servicio Frontend (Streamlit).

4.  **Acceder a la Aplicación:**

     *   **Frontend (Streamlit)**: [http://localhost:8501](http://localhost:8501)
     *   **Backend API**: [http://localhost:8000](http://localhost:8000)

---

## 🏗️ Arquitectura

El proyecto sigue un patrón de **Clean Architecture**. La lógica central está aislada en el directorio `translation_generator_app/services`.

Para profundizar en la estructura del código, flujo de ejecución y servicios, por favor lee:

👉 **[Arquitectura Técnica](./docs/ARCHITECTURE.md)**

👉 **[Componentes Clave y Decisiones Técnicas](./docs/KEY_COMPONENTS_EXPLAINED.md)**

---

## 📚 Reporte de Contenido

El sistema genera un reporte estructurado con las siguientes secciones:

1.  **Temas Principales Tratados**: Enumera y describe cada tema central.
2.  **Argumento / Resumen Narrativo**: Describe la narrativa completa del video.
3.  **Opiniones o Puntos de Vista Expresados**: Identifica posturas y perspectivas.
4.  **Datos o Hechos Clave**: Extrae datos, cifras y afirmaciones factuales.
5.  **Conclusión / Veredicto Final**: Resume la postura general y el mensaje final.

---

## Despliegue

La aplicación está contenerizada y lista para desplegarse.

*   **Imagen Docker**: Construida automáticamente vía GitHub Actions.
*   **Producción**: Puede desplegarse en plataformas como Render, Railway, o AWS ECS usando el `Dockerfile`.
*   **Despliegue del Frontend**: Para desplegar la UI, sobrescribe el comando de inicio del contenedor con `streamlit run app.py`.

---

## Licencia

Este proyecto está bajo la Licencia MIT.

---

**Desarrollado con ❤️ usando Clean Architecture**
