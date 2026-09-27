"""
Class-Based Views for Content Analysis API.
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
from ..services import YouTubeService, TranscriptionService, AnalysisService
from ..serializers import TranslationRequestValidator
from ..exceptions import (
    TranslationGeneratorException,
    YouTubeDownloadException,
    TranscriptionException,
    AnalysisException,
    InvalidDataException
)

# Configure logging
logger = logging.getLogger(__name__)

# Load environment variables
env = environ.Env()
environ.Env.read_env()

AAI_API_KEY = env('AAI_API_KEY')


class ContentAnalysisView(View):
    """
    Class-based view for processing YouTube videos: download, transcribe, and analyze.
    
    Endpoint: POST /generate-report/ (requires login via POST /login/)
    
    Request Body:
        {
            "link": "https://youtube.com/watch?v=...",
            "gemini_api_key": "AI..."
        }
    
    Response:
        {
            "report": "content report...",
            "title": "video title",
            "original_transcription": "original text...",
            "transcription_file": "/path/to/transcript.txt"
        }
    """
    
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        """Disable CSRF for this view."""
        return super().dispatch(*args, **kwargs)
    
    def post(self, request):
        """
        Handle POST request to generate content report from YouTube video.
        
        Args:
            request: Django HTTP request
            
        Returns:
            JsonResponse with analysis result or error
        """
        if not request.user.is_authenticated:
            return JsonResponse(
                {'error': 'Authentication required. Log in via POST /login/.'},
                status=401
            )

        try:
            data = self._parse_request_data(request)
            validated_data = TranslationRequestValidator.validate(data)
            
            result = self._process_video(
                yt_link=validated_data['link'],
                gemini_api_key=validated_data['gemini_api_key']
            )
            
            return JsonResponse({
                'report': result['report'],
                'title': result['title'],
                'original_transcription': result['original_transcription'],
                'transcription_file': result['transcription_file']
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
        
        except AnalysisException as e:
            logger.error(f"Analysis error: {str(e)}")
            return JsonResponse({'error': f"Analysis failed: {str(e)}"}, status=500)
        
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
    
    def _process_video(self, yt_link: str, gemini_api_key: str) -> dict:
        """
        Process YouTube video: download, transcribe, and analyze.
        
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
            "transcription_file": str(transcription_file)
        }


# Legacy function-based view support (if needed for backwards compatibility)
@csrf_exempt
def generate_report(request):
    """
    Legacy function-based view wrapper for ContentAnalysisView.
    
    This is kept for backwards compatibility.
    Use ContentAnalysisView.as_view() instead.
    """
    view = ContentAnalysisView.as_view()
    return view(request)