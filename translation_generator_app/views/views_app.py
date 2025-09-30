"""
Class-Based Views for Translation Generator API.
"""
import json
import logging
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import environ

from ..models import translationPost
from ..services import YouTubeService, TranscriptionService, TranslationService
from ..serializers import TranslationRequestValidator
from ..exceptions import (
    TranslationGeneratorException,
    YouTubeDownloadException,
    TranscriptionException,
    TranslationException,
    InvalidDataException
)

# Configure logging
logger = logging.getLogger(__name__)

# Load environment variables
env = environ.Env()
environ.Env.read_env()

# Access the API key from environment variables
AAI_API_KEY = env('AAI_API_KEY')


class TranslationGeneratorView(View):
    """
    Class-based view for processing YouTube videos: download, transcribe, and translate.
    
    Endpoint: POST /api/generate-translation
    
    Request Body:
        {
            "link": "https://youtube.com/watch?v=...",
            "openai_api_key": "sk-...",
            "target_language": "es" (optional, default: "es")
        }
    
    Supported languages: es, en, fr, de, it, pt, ru, ja, ko, zh, ar
    
    Response:
        {
            "content": "translated text...",
            "title": "video title",
            "original_transcription": "original text...",
            "video_file": "/path/to/video.mp4",
            "audio_file": "/path/to/audio.mp3",
            "target_language": "es"
        }
    """
    
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        """Disable CSRF for this view."""
        return super().dispatch(*args, **kwargs)
    
    def post(self, request):
        """
        Handle POST request to generate translation from YouTube video.
        
        Args:
            request: Django HTTP request
            
        Returns:
            JsonResponse with translation result or error
        """
        try:
            # Parse and validate request data
            data = self._parse_request_data(request)
            validated_data = TranslationRequestValidator.validate(data)
            
            # Process the video
            result = self._process_video(
                yt_link=validated_data['link'],
                openai_api_key=validated_data['openai_api_key'],
                target_language=validated_data.get('target_language', 'es')
            )
            
            return JsonResponse({
                'content': result['translation'],
                'title': result['title'],
                'original_transcription': result['original_transcription'],
                'video_file': result['video_file'],
                'audio_file': result['audio_file'],
                'target_language': result.get('target_language', 'es')
            }, status=200)
            
        except InvalidDataException as e:
            logger.warning(f"Invalid data: {str(e)}")
            return JsonResponse({'error': str(e)}, status=400)
        
        except YouTubeDownloadException as e:
            logger.error(f"YouTube download error: {str(e)}")
            return JsonResponse({'error': f"Download failed: {str(e)}"}, status=500)
        
        except TranscriptionException as e:
            logger.error(f"Transcription error: {str(e)}")
            return JsonResponse({'error': f"Transcription failed: {str(e)}"}, status=500)
        
        except TranslationException as e:
            logger.error(f"Translation error: {str(e)}")
            return JsonResponse({'error': f"Translation failed: {str(e)}"}, status=500)
        
        except TranslationGeneratorException as e:
            logger.error(f"General error: {str(e)}")
            return JsonResponse({'error': str(e)}, status=500)
        
        except Exception as e:
            logger.exception(f"Unexpected error: {str(e)}")
            return JsonResponse({'error': 'An unexpected error occurred'}, status=500)
    
    def get(self, request):
        """Handle GET request - return method not allowed."""
        return JsonResponse({'error': 'Method not allowed. Use POST.'}, status=405)
    
    def _parse_request_data(self, request) -> dict:
        """
        Parse JSON data from request body.
        
        Args:
            request: Django HTTP request
            
        Returns:
            Parsed JSON data
            
        Raises:
            InvalidDataException: If JSON parsing fails
        """
        try:
            return json.loads(request.body)
        except json.JSONDecodeError:
            raise InvalidDataException("Invalid JSON data")
    
    def _process_video(self, yt_link: str, openai_api_key: str, target_language: str = 'es') -> dict:
        """
        Process YouTube video: download, transcribe, and translate.
        
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


# Legacy function-based view support (if needed for backwards compatibility)
@csrf_exempt
def generate_translation(request):
    """
    Legacy function-based view wrapper for TranslationGeneratorView.
    
    This is kept for backwards compatibility.
    Use TranslationGeneratorView.as_view() instead.
    """
    view = TranslationGeneratorView.as_view()
    return view(request)

