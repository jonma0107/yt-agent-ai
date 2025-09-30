"""
YouTube Service - Handles video/audio downloading and title extraction.
"""
import os
from pathlib import Path
from typing import Tuple, Optional
from yt_dlp import YoutubeDL
from django.conf import settings

from ..exceptions import YouTubeDownloadException


class YouTubeService:
    """Service for handling YouTube video operations."""
    
    @staticmethod
    def get_title(link: str) -> str:
        """
        Extract the title from a YouTube video.
        
        Args:
            link: YouTube video URL
            
        Returns:
            Video title
            
        Raises:
            YouTubeDownloadException: If title extraction fails
        """
        try:
            ydl_opts = {'quiet': True}
            with YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(link, download=False)
                title = info.get('title', None)
                
            if not title:
                raise YouTubeDownloadException("Could not retrieve YouTube video title.")
                
            return title
        except Exception as e:
            raise YouTubeDownloadException(f"Failed to extract title: {str(e)}")
    
    @staticmethod
    def _sanitize_filename(title: str) -> str:
        """
        Sanitize filename by removing invalid characters.
        
        Args:
            title: Original title
            
        Returns:
            Sanitized filename
        """
        return "".join(c for c in title if c.isalnum() or c in (' ', '_', '-')).rstrip()
    
    @staticmethod
    def download_video_and_audio(link: str, title: str) -> Tuple[str, str]:
        """
        Download both video (mp4) and audio (mp3) from YouTube.
        
        Args:
            link: YouTube video URL
            title: Video title for filename
            
        Returns:
            Tuple of (video_file_path, audio_file_path)
            
        Raises:
            YouTubeDownloadException: If download fails
        """
        try:
            safe_title = YouTubeService._sanitize_filename(title)
            video_path = settings.MEDIA_ROOT / f"{safe_title}_video"
            audio_path = settings.MEDIA_ROOT / f"{safe_title}_audio"
            
            # Download video as .mp4
            video_opts = {
                'format': 'mp4',
                'outtmpl': str(video_path) + '.mp4',
                'quiet': True,
            }
            with YoutubeDL(video_opts) as ydl:
                ydl.download([link])
            video_file = str(video_path) + '.mp4'
            
            # Download audio as .mp3
            audio_opts = {
                'format': 'bestaudio/best',
                'outtmpl': str(audio_path),
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
                'quiet': True,
            }
            with YoutubeDL(audio_opts) as ydl:
                ydl.download([link])
            audio_file = str(audio_path) + '.mp3'
            
            # Verify files were downloaded
            if not os.path.exists(video_file) or os.path.getsize(video_file) == 0:
                raise YouTubeDownloadException("Failed to download video file or file is empty.")
            if not os.path.exists(audio_file) or os.path.getsize(audio_file) == 0:
                raise YouTubeDownloadException("Failed to download audio file or file is empty.")
            
            return video_file, audio_file
            
        except YouTubeDownloadException:
            raise
        except Exception as e:
            raise YouTubeDownloadException(f"Download failed: {str(e)}")
    
    @staticmethod
    def download_audio_only(link: str) -> str:
        """
        Download only audio from YouTube (legacy method).
        
        Args:
            link: YouTube video URL
            
        Returns:
            Path to downloaded audio file
            
        Raises:
            YouTubeDownloadException: If download fails
        """
        try:
            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': os.path.join(settings.MEDIA_ROOT, '%(title)s.%(ext)s'),
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
                'quiet': True,
            }
            
            with YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(link, download=True)
                file_path = ydl.prepare_filename(info)
                base, ext = os.path.splitext(file_path)
                new_file = f"{base}.mp3"
            
            return new_file
        except Exception as e:
            raise YouTubeDownloadException(f"Audio download failed: {str(e)}") 