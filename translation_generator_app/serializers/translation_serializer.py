"""
Request validators for content analysis API.
"""
import re
from typing import Dict, Any
from ..exceptions import InvalidDataException


class TranslationRequestValidator:
    """Validator for content analysis request data."""
    
    YOUTUBE_REGEX = re.compile(
        r'(https?://)?(www\.)?(youtube\.com/watch\?v=|youtu\.be/|youtube\.com/embed/)[\w-]+'
    )
    
    @staticmethod
    def validate(data: Dict[str, Any]) -> Dict[str, str]:
        """
        Validate content analysis request data.
        
        Args:
            data: Request data dictionary
            
        Returns:
            Dictionary with validated 'link' and 'gemini_api_key'
            
        Raises:
            InvalidDataException: If validation fails
        """
        if 'link' not in data:
            raise InvalidDataException("Missing required field: 'link'")
        
        if 'gemini_api_key' not in data:
            raise InvalidDataException("Missing required field: 'gemini_api_key'")
        
        link = data['link']
        api_key = data['gemini_api_key']
        
        if not isinstance(link, str) or not link.strip():
            raise InvalidDataException("Field 'link' must be a non-empty string")
        
        if not TranslationRequestValidator.YOUTUBE_REGEX.match(link):
            raise InvalidDataException("Invalid YouTube URL format")
        
        if not isinstance(api_key, str) or not api_key.strip():
            raise InvalidDataException("Field 'gemini_api_key' must be a non-empty string")
        
        if len(api_key) < 20:
            raise InvalidDataException("Invalid Gemini API key format")
        
        return {
            'link': link.strip(),
            'gemini_api_key': api_key.strip()
        }