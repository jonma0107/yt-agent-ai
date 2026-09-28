# YT-AGENT-AI

<img width="1751" height="725" alt="image" src="https://github.com/user-attachments/assets/ee14b2a0-9208-4886-8543-ac45ee0b0cf4" />

<img width="1760" height="744" alt="image" src="https://github.com/user-attachments/assets/d989c36b-1837-4268-9b3b-2c90d22ec9d5" />

<img width="1358" height="933" alt="image" src="https://github.com/user-attachments/assets/1f0ec2c7-afc7-435e-a85f-3243e69c2a6a" />

<img width="1358" height="933" alt="image" src="https://github.com/user-attachments/assets/487a3b07-71ce-4395-9923-da99b63b615c" />

<img width="1788" height="741" alt="image" src="https://github.com/user-attachments/assets/9aaa02f7-dbac-4a9b-870b-ab79d8d38d09" />

<img width="1726" height="700" alt="image" src="https://github.com/user-attachments/assets/7e9ffaf6-3a79-4f9b-9fcc-667632a5d95d" />

<img width="1726" height="700" alt="image" src="https://github.com/user-attachments/assets/9762172c-be5e-47b2-b747-5c67c2ed3cf2" />

<img width="1719" height="925" alt="image" src="https://github.com/user-attachments/assets/8d3996bd-9ce0-4625-90f9-2e7d22dfe803" />

<img width="1719" height="925" alt="image" src="https://github.com/user-attachments/assets/b16ce2e3-5989-45be-9c5f-30f7aebff823" />

<img width="1820" height="926" alt="image" src="https://github.com/user-attachments/assets/9326d266-6408-44c0-a77b-d79c9e61e005" />







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
     SECRET_KEY=tu_secret_key_django
     DEBUG=True
     DB_NAME=postgres
     DB_USER=postgres
     DB_PASS=postgres
     DB_HOST=db
     ```

     > **API Keys:** la clave de AssemblyAI (`AAI_API_KEY`) vive en el servidor vía `.env`
     > porque la transcripción nunca la pide al usuario. En cambio, la clave de Google Gemini
     > **no** va en el `.env`: cada usuario la ingresa en el sidebar de Streamlit
     > (campo "Gemini API Key") o la envía en el payload del endpoint REST (`gemini_api_key`).

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
     *   **Admin Django**: [http://localhost:8000/admin](http://localhost:8000/admin)

---

## 🔐 Autenticación y Usuarios

La app usa el sistema de usuarios nativo de Django. Tanto Streamlit como el
endpoint `POST /generate-report/` exigen iniciar sesión.

> **Streamlit es un cliente HTTP de la API:** `app.py` no importa servicios
> ni usa Django; llama a `POST /login/`, `POST /generate-report/` y
> `POST /logout/` con `requests`, guardando la cookie de sesión. Por eso
> la autenticación y el throttling protegen también el uso vía Streamlit.
> La URL del backend se configura con `BACKEND_URL` (por defecto
> `http://localhost:8000`; en Docker Compose el frontend la recibe como
> `http://backend:8000`).

1.  **Crear el superusuario (una sola vez):**

     ```bash
     python manage.py createsuperuser
     ```

2.  **Crear usuarios adicionales:** entra al admin con el superusuario
    (`/admin/` → *Users* → *Add user*) y asígnales usuario y contraseña.
    Esos mismos usuarios sirven para Streamlit y para la API.

3.  **Usar la API:**

     ```bash
     # Iniciar sesión (guarda la cookie de sesión con -c)
     curl -c cookies.txt -X POST http://localhost:8000/login/ \
       -H "Content-Type: application/json" \
       -d '{"username": "usuario", "password": "secreto"}'

     # Generar reporte (reutiliza la cookie con -b)
     curl -b cookies.txt -X POST http://localhost:8000/generate-report/ \
       -H "Content-Type: application/json" \
       -d '{"link": "https://youtube.com/watch?v=...", "gemini_api_key": "AI..."}'

     # Cerrar sesión
     curl -b cookies.txt -X POST http://localhost:8000/logout/
     ```

4.  **Throttling (DRF):** la API limita el ritmo de peticiones para proteger
    el login (fuerza bruta) y el reporte (operación costosa). Se configura en
    `ai_translation/settings.py` (`REST_FRAMEWORK`) y se ajusta por entorno
    sin tocar código:

     ```ini
     LOGIN_THROTTLE_RATE=5/min
     REPORT_THROTTLE_RATE=10/hour
     ```

     Al exceder el límite, la API responde `429` con `{"detail": "Request was throttled..."}`.

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
