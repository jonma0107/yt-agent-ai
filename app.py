import django_setup
import os
import logging
from datetime import datetime
from io import BytesIO

# Initialize Django before importing any Django models
django_setup.setup()

import streamlit as st
from django.conf import settings
import environ

from translation_generator_app.models import translationPost
from translation_generator_app.services import YouTubeService, TranscriptionService, AnalysisService
from translation_generator_app.exceptions import (
    YouTubeDownloadException,
    TranscriptionException,
    AnalysisException,
    TranslationGeneratorException
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
env = environ.Env()
environ.Env.read_env()
# Nota: la API key de Gemini la provee cada usuario en el sidebar de Streamlit
# (parametro gemini_api_key), no se lee del entorno.
AAI_API_KEY = env('AAI_API_KEY')


def process_youtube_video_for_analysis(yt_link: str, gemini_api_key: str) -> dict:
    """
    Process YouTube video using the service architecture to generate a content report.

    Args:
        yt_link: YouTube video URL
        gemini_api_key: Google Gemini API key for analysis

    Returns:
        Dictionary with processing results

    Raises:
        YouTubeDownloadException: If download fails
        TranscriptionException: If transcription fails
        AnalysisException: If analysis fails
    """
    youtube_service = YouTubeService()
    transcription_service = TranscriptionService(api_key=AAI_API_KEY)
    analysis_service = AnalysisService(api_key=gemini_api_key)

    # Step 1: Get video title
    logger.info(f"Fetching title for: {yt_link}")
    title = youtube_service.get_title(yt_link)
    logger.info(f"Video title: {title}")

    # Step 2: Download video and audio
    logger.info(f"Downloading video and audio for: {title}")
    video_file, audio_file = youtube_service.download_video_and_audio(yt_link, title)
    logger.info(f"Downloaded - Video: {video_file}, Audio: {audio_file}")

    # Step 3: Transcribe audio
    logger.info(f"Transcribing audio: {audio_file}")
    original_text = transcription_service.transcribe_audio(audio_file, title)
    logger.info(f"Transcription complete, length: {len(original_text)} chars")

    # Step 4: Generate content report
    logger.info("Generating content report")
    result = analysis_service.generate_report(original_text)
    logger.info("Analysis complete")

    # Step 5: Save to database
    analysis_entry = translationPost.objects.create(
        youtube_title=title,
        youtube_link=yt_link,
        generated_content=result['report']
    )
    analysis_entry.save()
    logger.info(f"Saved analysis to database, ID: {analysis_entry.id}")

    # Prepare transcript file path
    safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '_', '-')).rstrip()
    transcription_file = settings.MEDIA_ROOT / f"{safe_title}.txt"

    return {
        "title": title,
        "report": result['report'],
        "original_transcription": original_text,
        "video_file": video_file,
        "audio_file": audio_file,
        "transcription_file": str(transcription_file),
        "youtube_link": yt_link,
    }


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

    # Footer page numbers are handled by FPDF automatically if needed

    # Output to bytes
    # fpdf2: output(dest="S") returns str or bytes depending on version; use BytesIO for consistency
    try:
        # New fpdf2: output with BytesIO
        buf = BytesIO()
        pdf.output(buf)
        return buf.getvalue()
    except Exception:
        out = pdf.output(dest="S")
        if isinstance(out, str):
            return out.encode("latin-1", "replace")
        return bytes(out)


def main():
    st.title("YouTube Agent")
    st.write("Analiza videos de YouTube y obtén un Reporte de Contenido detallado. Transcribe y analiza lo que se dice en tus videos favoritos de YouTube.")

    with st.sidebar:
        st.header("Configuration")
        gemini_api_key = st.text_input("Gemini API Key", type="password")
        st.info("This app uses Google Gemini models to analyze the video content. Please ensure your API key has access to `gemini-3.5-flash`.")

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
            with st.spinner("Processing..."):
                try:
                    st.session_state.result = process_youtube_video_for_analysis(
                        youtube_url,
                        gemini_api_key
                    )

                except YouTubeDownloadException as e:
                    st.error(f"❌ YouTube Download Error: {str(e)}")
                    logger.error(f"YouTube download error: {str(e)}")
                    if 'result' in st.session_state:
                        del st.session_state.result

                except TranscriptionException as e:
                    st.error(f"❌ Transcription Error: {str(e)}")
                    logger.error(f"Transcription error: {str(e)}")
                    if 'result' in st.session_state:
                        del st.session_state.result

                except AnalysisException as e:
                    st.error(f"❌ Analysis Error: {str(e)}")
                    logger.error(f"Analysis error: {str(e)}")
                    if 'result' in st.session_state:
                        del st.session_state.result

                except TranslationGeneratorException as e:
                    st.error(f"❌ Error: {str(e)}")
                    logger.error(f"General error: {str(e)}")
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
        video_file_path = result['video_file']
        with open(video_file_path, "rb") as file:
            st.download_button(
                label="Download Video",
                data=file,
                file_name=os.path.basename(video_file_path),
                mime="video/mp4"
            )

        audio_file_path = result['audio_file']
        with open(audio_file_path, "rb") as file:
            st.download_button(
                label="Download Audio (MP3)",
                data=file,
                file_name=os.path.basename(audio_file_path),
                mime="audio/mpeg"
            )

if __name__ == "__main__":
    main() 