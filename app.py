import django_setup
import os
import logging

# Initialize Django before importing any Django models
django_setup.setup()

import streamlit as st
from django.conf import settings
import environ

from translation_generator_app.models import translationPost
from translation_generator_app.services import YouTubeService, TranscriptionService, TranslationService
from translation_generator_app.exceptions import (
    YouTubeDownloadException,
    TranscriptionException,
    TranslationException,
    TranslationGeneratorException
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
env = environ.Env()
environ.Env.read_env()
AAI_API_KEY = env('AAI_API_KEY')


def process_youtube_video_with_services(yt_link: str, openai_api_key: str, target_language: str = 'es') -> dict:
    """
    Process YouTube video using the new service architecture.
    
    Args:
        yt_link: YouTube video URL
        openai_api_key: OpenAI API key for translation
        target_language: Target language code for translation (default: 'es')
        
    Returns:
        Dictionary with processing results
        
    Raises:
        YouTubeDownloadException: If download fails
        TranscriptionException: If transcription fails
        TranslationException: If translation fails
    """
    # Initialize services
    youtube_service = YouTubeService()
    transcription_service = TranscriptionService(api_key=AAI_API_KEY)
    translation_service = TranslationService(api_key=openai_api_key)
    
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
    
    # Step 4: Format and translate
    logger.info(f"Processing translation and formatting (target language: {target_language})")
    processed_text = translation_service.process_transcription(original_text, target_language=target_language)
    logger.info("Translation complete")
    
    # Step 5: Save to database
    translation = translationPost.objects.create(
        youtube_title=title,
        youtube_link=yt_link,
        generated_content=processed_text['translated']
    )
    translation.save()
    logger.info(f"Saved translation to database, ID: {translation.id}")
    
    # Prepare transcript file path
    safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '_', '-')).rstrip()
    transcription_file = settings.MEDIA_ROOT / f"{safe_title}.txt"
    
    return {
        "title": title,
        "translation": processed_text['translated'],
        "original_transcription": processed_text['original'],
        "video_file": video_file,
        "audio_file": audio_file,
        "transcription_file": str(transcription_file),
        "target_language": target_language
    }


def main():
    st.title("YouTube Agent")
    st.write("Translate and get the lyrics of your favorite song from YouTube. Download the video and audio of your favorite song from YouTube.")

    with st.sidebar:
        st.header("Configuration")
        openai_api_key = st.text_input("OpenAI API Key", type="password")
        st.info("This app uses OpenAI models. Please ensure your API key has access to at least one of the following: `gpt-4o`, `gpt-5-nano`, `gpt-4-turbo`, or `gpt-3.5-turbo`.")
        
        st.divider()
        
        st.subheader("Translation Language")
        
        # Language selector
        language_options = {
            'Español 🇪🇸': 'es',
            'English 🇬🇧': 'en',
            'Français 🇫🇷': 'fr',
            'Deutsch 🇩🇪': 'de',
            'Italiano 🇮🇹': 'it',
            'Português 🇵🇹': 'pt',
            'Русский 🇷🇺': 'ru',
            '日本語 🇯🇵': 'ja',
            '한국어 🇰🇷': 'ko',
            '中文 🇨🇳': 'zh',
            'العربية 🇸🇦': 'ar',
        }
        
        selected_language_name = st.selectbox(
            "Select target translation language:",
            options=list(language_options.keys()),
            index=0  # Default to Spanish
        )
        
        target_language = language_options[selected_language_name]
        
        st.info(f"💡 If the song is already in {selected_language_name.split()[0]}, it will only be formatted, not translated.")
        
        st.divider()
        
        if st.button("Clear Chat"):
            # Clear the results from the session state
            if 'result' in st.session_state:
                del st.session_state.result
            st.rerun()

    youtube_url = st.text_input("Enter YouTube URL")

    if st.button("Generate Translation"):
        if not openai_api_key:
            st.error("Please enter your OpenAI API key in the sidebar.")
        elif not youtube_url:
            st.error("Please enter a YouTube URL.")
        else:
            with st.spinner("Processing..."):
                try:
                    # Use the new service-based architecture with selected language
                    st.session_state.result = process_youtube_video_with_services(
                        youtube_url, 
                        openai_api_key, 
                        target_language=target_language
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
                        
                except TranslationException as e:
                    st.error(f"❌ Translation Error: {str(e)}")
                    logger.error(f"Translation error: {str(e)}")
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
        st.success("Translation Generated!")
        st.subheader("Title")
        st.write(result['title'])
        
        # Get language name for display
        lang_code = result.get('target_language', 'es')
        lang_display_names = {
            'es': 'Español',
            'en': 'English',
            'fr': 'Français',
            'de': 'Deutsch',
            'it': 'Italiano',
            'pt': 'Português',
            'ru': 'Русский',
            'ja': '日本語',
            'ko': '한국어',
            'zh': '中文',
            'ar': 'العربية',
        }
        target_lang_name = lang_display_names.get(lang_code, lang_code.upper())
        
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Original Transcription")
            st.text_area("", result['original_transcription'], height=300)

        with col2:
            st.subheader(f"Translation / {target_lang_name}")
            st.text_area("", result['translation'], height=300)


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