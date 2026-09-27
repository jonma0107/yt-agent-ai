"""
Class-Based Views for Content Analysis API (DRF).

Throttling (DRF ScopedRateThrottle, scope 'report'): limits how often the
expensive generate-report operation can be called per user/IP.
Rate configured in settings.py (REPORT_THROTTLE_RATE).
"""
import json
import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
import environ

from ..models import translationPost
from ..services import YouTubeService, TranscriptionService, AnalysisService
from .views_auth import SessionNoCSRF
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


class ContentAnalysisView(APIView):
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
    Response (429):
        {"detail": "Request was throttled..."}
    """

    throttle_scope = 'report'
    authentication_classes = [SessionNoCSRF]
    permission_classes = []

    def post(self, request):
        """
        Handle POST request to generate content report from YouTube video.

        Args:
            request: DRF HTTP request

        Returns:
            Response with analysis result or error
        """
        if not request.user.is_authenticated:
            return Response(
                {'error': 'Authentication required. Log in via POST /login/.'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        try:
            data = request.data if isinstance(request.data, dict) else {}
            validated_data = TranslationRequestValidator.validate(data)

            result = self._process_video(
                yt_link=validated_data['link'],
                gemini_api_key=validated_data['gemini_api_key']
            )

            return Response({
                'report': result['report'],
                'title': result['title'],
                'original_transcription': result['original_transcription'],
                'transcription_file': result['transcription_file']
            }, status=status.HTTP_200_OK)

        except InvalidDataException as e:
            logger.warning(f"Invalid data: {str(e)}")
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        except YouTubeDownloadException as e:
            logger.error(f"YouTube download error: {str(e)}")
            return Response({'error': f"Download failed: {str(e)}"},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except TranscriptionException as e:
            logger.error(f"Transcription error: {str(e)}")
            return Response({'error': f"Transcription failed: {str(e)}"},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except AnalysisException as e:
            logger.error(f"Analysis error: {str(e)}")
            return Response({'error': f"Analysis failed: {str(e)}"},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except TranslationGeneratorException as e:
            logger.error(f"General error: {str(e)}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except Exception:
            logger.exception("Unexpected error")
            return Response({'error': 'An unexpected error occurred'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def get(self, request):
        """Handle GET request - return method not allowed."""
        return Response({'error': 'Method not allowed. Use POST.'},
                        status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def _parse_request_data(self, request) -> dict:
        """
        Parse JSON data from request body.

        Args:
            request: DRF HTTP request

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
def generate_report(request):
    """
    Legacy function-based view wrapper for ContentAnalysisView.

    This is kept for backwards compatibility.
    Use ContentAnalysisView.as_view() instead.
    """
    view = ContentAnalysisView.as_view()
    return view(request)
