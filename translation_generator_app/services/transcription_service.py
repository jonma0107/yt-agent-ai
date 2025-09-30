"""
Transcription Service - Handles audio transcription using AssemblyAI.
"""
import assemblyai as aai
from pathlib import Path
from django.conf import settings
from typing import Optional

from ..exceptions import TranscriptionException


class TranscriptionService:
    """Service for handling audio transcription."""
    
    def __init__(self, api_key: str):
        """
        Initialize the transcription service.
        
        Args:
            api_key: AssemblyAI API key
        """
        self.api_key = api_key
        aai.settings.api_key = api_key
    
    def transcribe_audio(self, audio_file: str, title: str) -> str:
        """
        Transcribe audio file using AssemblyAI.
        
        Args:
            audio_file: Path to audio file
            title: Title for saving transcription
            
        Returns:
            Transcribed text
            
        Raises:
            TranscriptionException: If transcription fails
        """
        try:
            transcriber = aai.Transcriber()
            transcript = transcriber.transcribe(audio_file)
            
            if not transcript or not hasattr(transcript, 'text') or not transcript.text:
                raise TranscriptionException("Transcription returned empty result.")
            
            # Save transcription to file
            self._save_transcription(transcript.text, title)
            
            return transcript.text
            
        except TranscriptionException:
            raise
        except Exception as e:
            raise TranscriptionException(f"Transcription failed: {str(e)}")
    
    @staticmethod
    def _save_transcription(text: str, title: str) -> Path:
        """
        Save transcription to a text file.
        
        Args:
            text: Transcribed text
            title: Title for filename
            
        Returns:
            Path to saved file
        """
        safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '_', '-')).rstrip()
        transcript_file = settings.MEDIA_ROOT / f"{safe_title}.txt"
        
        with open(transcript_file, "w", encoding="utf-8") as f:
            f.write(text)
        
        return transcript_file 