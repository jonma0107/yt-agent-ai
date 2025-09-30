"""
Request validators for translation API.
"""
import re
from typing import Dict, Any
from ..exceptions import InvalidDataException


class TranslationRequestValidator:
    """Validator for translation request data."""
    
    YOUTUBE_REGEX = re.compile(
        r'(https?://)?(www\.)?(youtube\.com/watch\?v=|youtu\.be/|youtube\.com/embed/)[\w-]+'
    )
    
    SUPPORTED_LANGUAGES = ['es', 'en', 'fr', 'de', 'it', 'pt', 'ru', 'ja', 'ko', 'zh', 'ar']
    
    @staticmethod
    def validate(data: Dict[str, Any]) -> Dict[str, str]:
        """
        Validate translation request data.
        
        Args:
            data: Request data dictionary
            
        Returns:
            Dictionary with validated 'link', 'openai_api_key', and optionally 'target_language'
            
        Raises:
            InvalidDataException: If validation fails
        """
        # Check required fields
        if 'link' not in data:
            raise InvalidDataException("Missing required field: 'link'")
        
        if 'openai_api_key' not in data:
            raise InvalidDataException("Missing required field: 'openai_api_key'")
        
        link = data['link']
        api_key = data['openai_api_key']
        target_language = data.get('target_language', 'es')  # Default to Spanish
        
        # Validate link format
        if not isinstance(link, str) or not link.strip():
            raise InvalidDataException("Field 'link' must be a non-empty string")
        
        # Validate YouTube URL
        if not TranslationRequestValidator.YOUTUBE_REGEX.match(link):
            raise InvalidDataException("Invalid YouTube URL format")
        
        # Validate API key
        if not isinstance(api_key, str) or not api_key.strip():
            raise InvalidDataException("Field 'openai_api_key' must be a non-empty string")
        
        if len(api_key) < 20:  # Basic sanity check
            raise InvalidDataException("Invalid OpenAI API key format")
        
        # Validate target language (optional)
        if not isinstance(target_language, str):
            raise InvalidDataException("Field 'target_language' must be a string")
        
        target_language = target_language.strip().lower()
        if target_language not in TranslationRequestValidator.SUPPORTED_LANGUAGES:
            raise InvalidDataException(
                f"Unsupported language: '{target_language}'. "
                f"Supported languages: {', '.join(TranslationRequestValidator.SUPPORTED_LANGUAGES)}"
            )
        
        return {
            'link': link.strip(),
            'openai_api_key': api_key.strip(),
            'target_language': target_language
        } 