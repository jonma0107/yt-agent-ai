"""
YouTube Agent - Streamlit frontend.

This is a pure HTTP client of the Django API. It holds no business logic:
- Auth: POST /login/ (session cookie kept in a requests.Session).
- Analysis: POST /generate-report/ (auth + throttling enforced server-side).
- Media downloads: fetched from the API's /media/ URLs with the session.
- Report PDF: generated locally with fpdf2.

Configuration (environment):
- BACKEND_URL: Django API base URL. Default http://localhost:8000.
  In Docker Compose the frontend reaches the backend as http://backend:8000.
- API_TIMEOUT: seconds to wait for /generate-report/ (default 900).
"""
import logging
import os
from datetime import datetime
from io import BytesIO

import environ
import requests
import streamlit as st

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
env = environ.Env()
environ.Env.read_env()
BACKEND_URL = env('BACKEND_URL', default='http://localhost:8000').rstrip('/')
# Nota: la API key de Gemini la provee cada usuario en el sidebar de Streamlit
# (parametro gemini_api_key), no se lee del entorno.
API_TIMEOUT = int(env('API_TIMEOUT', default='900'))


class ApiError(Exception):
    """Raised when the backend API answers with an error."""

    def __init__(self, message: str, status_code: int = 0):
        super().__init__(message)
        self.status_code = status_code


def _parse_api_error(response: requests.Response, default: str) -> str:
    """Extract a friendly message from an API error response."""
    try:
        data = response.json()
        return data.get('error') or data.get('detail') or default
    except ValueError:
        return default


def api_login(username: str, password: str) -> None:
    """
    Log in against POST /login/ and keep the session cookie.

    Raises:
        ApiError: on invalid credentials, throttling or connection issues.
    """
    session = requests.Session()
    try:
        response = session.post(
            f'{BACKEND_URL}/login/',
            json={'username': username, 'password': password},
            timeout=30,
        )
    except requests.ConnectionError:
        raise ApiError(f'No se pudo conectar con el backend ({BACKEND_URL}).')

    if response.status_code == 200:
        st.session_state.api_session = session
        st.session_state.authenticated_user = username
        logger.info(f"Streamlit login via API: {username}")
        return
    if response.status_code == 429:
        raise ApiError('Demasiados intentos. Espera un momento e inténtalo de nuevo.', 429)
    raise ApiError(_parse_api_error(response, 'Credenciales inválidas.'), response.status_code)


def api_logout() -> None:
    """Close the backend session and clear local state."""
    session = st.session_state.get('api_session')
    if session is not None:
        try:
            session.post(f'{BACKEND_URL}/logout/', timeout=15)
        except requests.RequestException as e:
            logger.warning(f"API logout failed (clearing local session anyway): {e}")
    for key in ('authenticated_user', 'api_session', 'result'):
        st.session_state.pop(key, None)


def api_generate_report(yt_link: str, gemini_api_key: str) -> dict:
    """
    Call POST /generate-report/ and return the parsed result.

    Auth and throttling are enforced server-side (401/429).

    Raises:
        ApiError: on any API or connection error.
    """
    session = st.session_state.get('api_session')
    if session is None:
        raise ApiError('Sesión expirada. Inicia sesión de nuevo.', 401)

    try:
        response = session.post(
            f'{BACKEND_URL}/generate-report/',
            json={'link': yt_link, 'gemini_api_key': gemini_api_key},
            timeout=API_TIMEOUT,
        )
    except requests.ConnectionError:
        raise ApiError(f'No se pudo conectar con el backend ({BACKEND_URL}).')
    except requests.Timeout:
        raise ApiError('El análisis tardó demasiado. Intenta con un video más corto.')

    if response.status_code == 200:
        data = response.json()
        data['youtube_link'] = yt_link
        return data
    if response.status_code == 401:
        raise ApiError('Sesión expirada. Inicia sesión de nuevo.', 401)
    if response.status_code == 429:
        raise ApiError(
            'Límite de reportes excedido. Espera e inténtalo de nuevo.', 429)
    raise ApiError(
        _parse_api_error(response, 'El backend devolvió un error inesperado.'),
        response.status_code)


def api_download_media(media_url: str) -> bytes:
    """
    Fetch a /media/ file from the backend with the session.

    Raises:
        ApiError: if the download fails.
    """
    session = st.session_state.get('api_session')
    if session is None:
        raise ApiError('Sesión expirada. Inicia sesión de nuevo.', 401)
    try:
        response = session.get(f'{BACKEND_URL}{media_url}', timeout=300)
    except requests.RequestException as e:
        raise ApiError(f'No se pudo descargar el archivo: {e}')
    if response.status_code != 200:
        raise ApiError(f'No se pudo descargar el archivo (HTTP {response.status_code}).',
                       response.status_code)
    return response.content


def generate_report_pdf(report_text: str, title: str, youtube_url: str = "") -> bytes:
    """Generate PDF bytes for the content report."""
    try:
        from fpdf import FPDF
    except ImportError:
        raise ImportError("fpdf2 is required for PDF generation. Install with: pip install fpdf2")

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    # Title
    pdf.set_font("Helvetica", "B", 16)
    # Encode-safe for latin-1: replace unsupported chars
    safe_title = title.encode("latin-1", "replace").decode("latin-1")
    pdf.multi_cell(0, 10, safe_title, align="C")
    pdf.ln(2)

    if youtube_url:
        pdf.set_font("Helvetica", "", 8)
        pdf.set_text_color(100, 100, 100)
        safe_url = youtube_url.encode("latin-1", "replace").decode("latin-1")
        pdf.multi_cell(0, 5, safe_url, align="C")
        pdf.ln(1)
        pdf.set_text_color(0, 0, 0)

    pdf.set_font("Helvetica", "", 8)
    pdf.set_text_color(80, 80, 80)
    pdf.cell(0, 5, f"Generado: {datetime.now().strftime('%Y-%m-%d %H:%M')}", align="C", ln=True)
    pdf.ln(4)
    pdf.set_draw_color(200, 200, 200)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(6)
    pdf.set_text_color(0, 0, 0)

    # Body with basic markdown handling
    pdf.set_font("Helvetica", "", 10)
    for raw_line in report_text.split("\n"):
        line = raw_line.rstrip()
        stripped = line.strip()

        if not stripped:
            pdf.ln(3)
            continue

        if stripped.startswith("#"):
            level = len(stripped) - len(stripped.lstrip("#"))
            text = stripped.lstrip("#").strip().strip("*").strip()
            if text:
                safe_text = text.encode("latin-1", "replace").decode("latin-1")
                pdf.set_font("Helvetica", "B", 13 if level == 1 else 11)
                pdf.set_text_color(31, 111, 173)
                pdf.multi_cell(0, 7, safe_text)
                pdf.set_text_color(0, 0, 0)
                pdf.set_font("Helvetica", "", 10)
                pdf.ln(1)
            continue

        if stripped in ("---", "***", "___"):
            pdf.ln(2)
            pdf.set_draw_color(200, 200, 200)
            pdf.line(10, pdf.get_y(), 200, pdf.get_y())
            pdf.ln(4)
            continue

        # Bold line like **Text**
        if stripped.startswith("**") and stripped.endswith("**") and len(stripped) > 4:
            safe_text = stripped.strip("*").strip().encode("latin-1", "replace").decode("latin-1")
            pdf.set_font("Helvetica", "B", 10)
            pdf.multi_cell(0, 6, safe_text)
            pdf.set_font("Helvetica", "", 10)
            pdf.ln(1)
            continue

        # Regular line - strip markdown ** for inline bold
        clean = line.replace("**", "")
        safe_clean = clean.encode("latin-1", "replace").decode("latin-1")
        # Preserve bullet
        pdf.multi_cell(0, 6, safe_clean)
        pdf.ln(0.5)

    # Output to bytes
    # fpdf2: output with BytesIO for consistency across versions
    try:
        buf = BytesIO()
        pdf.output(buf)
        return buf.getvalue()
    except Exception:
        out = pdf.output(dest="S")
        if isinstance(out, str):
            return out.encode("latin-1", "replace")
        return bytes(out)


def _require_login() -> bool:
    """
    Show a login screen until the user authenticates via the API.

    Returns:
        True if the user is authenticated, False otherwise.
    """
    if st.session_state.get('authenticated_user'):
        return True

    st.title("YouTube Agent")
    st.write("Inicia sesión con tu usuario para continuar.")

    with st.form("login_form"):
        username = st.text_input("Usuario")
        password = st.text_input("Contraseña", type="password")
        submitted = st.form_submit_button("Iniciar sesión")

    if submitted:
        if not username or not password:
            st.error("Ingresa usuario y contraseña.")
        else:
            try:
                api_login(username, password)
                st.rerun()
            except ApiError as e:
                st.error(f"❌ {e}")
                logger.warning(f"Failed Streamlit login attempt for username: {username}")

    return False


def main():
    if not _require_login():
        return

    st.title("YouTube Agent")
    st.write("Analiza videos de YouTube y obtén un Reporte de Contenido detallado. Transcribe y analiza lo que se dice en tus videos favoritos de YouTube.")

    with st.sidebar:
        st.header("Configuration")
        st.write(f"Sesión: **{st.session_state.authenticated_user}**")
        if st.button("Cerrar sesión"):
            logger.info(f"Streamlit logout: {st.session_state.authenticated_user}")
            api_logout()
            st.rerun()
        gemini_api_key = st.text_input("Gemini API Key", type="password")
        st.info("This app uses Google Gemini models with automatic fallback. Please ensure your API key has access to the Flash models (e.g. `gemini-3.5-flash-lite`).")

        st.divider()

        if st.button("Clear Chat"):
            if 'result' in st.session_state:
                del st.session_state.result
            st.rerun()

    youtube_url = st.text_input("Enter YouTube URL")

    if st.button("Generate Content Report"):
        if not gemini_api_key:
            st.error("Please enter your Gemini API key in the sidebar.")
        elif not youtube_url:
            st.error("Please enter a YouTube URL.")
        else:
            with st.spinner("Processing... (puede tardar varios minutos)"):
                try:
                    st.session_state.result = api_generate_report(
                        youtube_url,
                        gemini_api_key
                    )

                except ApiError as e:
                    st.error(f"❌ {e}")
                    logger.error(f"API error ({e.status_code}): {e}")
                    if 'result' in st.session_state:
                        del st.session_state.result

                except Exception as e:
                    st.error(f"❌ An unexpected error occurred: {str(e)}")
                    logger.exception(f"Unexpected error: {str(e)}")
                    if 'result' in st.session_state:
                        del st.session_state.result

    # If there are results in the session state, display them
    if 'result' in st.session_state:
        result = st.session_state.result
        st.success("Content Report Generated!")
        st.subheader("Title")
        st.write(result['title'])

        st.subheader("Original Transcription")
        st.text_area("", result['original_transcription'], height=300)

        st.subheader("Reporte de Contenido")
        st.text_area("", result['report'], height=500)

        # PDF download for the report
        try:
            safe_title = "".join(c for c in result['title'] if c.isalnum() or c in (' ', '_', '-')).rstrip()[:60] or "reporte"
            pdf_bytes = generate_report_pdf(
                result['report'],
                result['title'],
                youtube_url=result.get('youtube_link', ''),
            )
            st.download_button(
                label="Download Report (PDF)",
                data=pdf_bytes,
                file_name=f"{safe_title}.pdf",
                mime="application/pdf",
            )
        except Exception as e:
            logger.error(f"PDF generation failed: {e}")
            st.warning("No se pudo generar el PDF del reporte.")

        st.subheader("Downloads")
        for label, url_key, mime in (
            ("Download Video", "video_url", "video/mp4"),
            ("Download Audio (MP3)", "audio_url", "audio/mpeg"),
        ):
            media_url = result.get(url_key)
            if not media_url:
                continue
            file_name = os.path.basename(media_url)
            try:
                st.download_button(
                    label=label,
                    data=api_download_media(media_url),
                    file_name=file_name,
                    mime=mime,
                )
            except ApiError as e:
                st.warning(f"No se pudo preparar {label.lower()}: {e}")

if __name__ == "__main__":
    main()
