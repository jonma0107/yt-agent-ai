"""
Translation Service - Handles text formatting and translation using OpenAI.
"""
from typing import Dict, List, Optional
from openai import OpenAI

from ..exceptions import TranslationException


class TranslationService:
    """Service for handling text translation and formatting."""
    
    # Preferred models in order of preference
    PREFERRED_MODELS = ['gpt-4o', 'gpt-5-nano', 'gpt-4-turbo', 'gpt-3.5-turbo']
    
    # Supported languages with their codes and names
    SUPPORTED_LANGUAGES = {
        'es': {'name': 'Español', 'native': 'español'},
        'en': {'name': 'English', 'native': 'inglés'},
        'fr': {'name': 'Français', 'native': 'francés'},
        'de': {'name': 'Deutsch', 'native': 'alemán'},
        'it': {'name': 'Italiano', 'native': 'italiano'},
        'pt': {'name': 'Português', 'native': 'portugués'},
        'ru': {'name': 'Русский', 'native': 'ruso'},
        'ja': {'name': '日本語', 'native': 'japonés'},
        'ko': {'name': '한국어', 'native': 'coreano'},
        'zh': {'name': '中文', 'native': 'chino'},
        'ar': {'name': 'العربية', 'native': 'árabe'},
    }
    
    def __init__(self, api_key: str):
        """
        Initialize the translation service.
        
        Args:
            api_key: OpenAI API key
        """
        self.client = OpenAI(api_key=api_key)
        self.selected_model = None
    
    def detect_language(self, text: str) -> str:
        """
        Detect the language of the given text.
        
        Args:
            text: Text to analyze
            
        Returns:
            Language code ('es' for Spanish, 'en' for English, etc.)
            
        Raises:
            TranslationException: If language detection fails
        """
        try:
            model = self._get_available_model()
            
            messages = [
                {
                    "role": "system",
                    "content": "You are a language detection expert. Respond ONLY with the ISO 639-1 language code (e.g., 'es' for Spanish, 'en' for English). Nothing else."
                },
                {
                    "role": "user",
                    "content": f"Detect the language of this text:\n\n{text[:500]}"  # Use first 500 chars
                }
            ]
            
            response = self.client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=10,
                temperature=0.0,
                stream=False
            )
            
            language_code = response.choices[0].message.content.strip().lower()
            return language_code
            
        except Exception as e:
            raise TranslationException(f"Language detection failed: {str(e)}")
    
    def _get_available_model(self) -> str:
        """
        Find the best available model from the preferred list.
        
        Returns:
            Selected model name
            
        Raises:
            TranslationException: If no suitable model is found
        """
        if self.selected_model:
            return self.selected_model
        
        try:
            available_models = [model.id for model in self.client.models.list().data]
            
            for model in self.PREFERRED_MODELS:
                if model in available_models:
                    self.selected_model = model
                    return model
            
            raise TranslationException(
                f"No suitable OpenAI model found. Requires one of: {', '.join(self.PREFERRED_MODELS)}"
            )
        except TranslationException:
            raise
        except Exception as e:
            raise TranslationException(f"Failed to get available models: {str(e)}")
    
    def format_text_as_verses(self, text: str) -> str:
        """
        Format text into song verses without changing language.
        
        Args:
            text: Original text
            
        Returns:
            Formatted text
            
        Raises:
            TranslationException: If formatting fails
        """
        try:
            model = self._get_available_model()
            
            messages = [
                {
                    "role": "system",
                    "content": (
                        "You are an expert in formatting song lyrics. Your task is to organize transcribed text "
                        "into proper song verses with appropriate line breaks and structure. "
                        "DO NOT change the language or translate. DO NOT alter the words. "
                        "Only organize the text into verses, identifying choruses, verses, bridges, etc. "
                        "Keep the original language intact."
                    )
                },
                {
                    "role": "user",
                    "content": f"Format this song transcription into proper verses:\n\n{text}"
                }
            ]
            
            response = self.client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=4096,
                temperature=0.3,  # Lower temperature for more consistent formatting
                stream=False
            )
            
            formatted_text = response.choices[0].message.content.strip()
            return formatted_text
            
        except TranslationException:
            raise
        except Exception as e:
            raise TranslationException(f"Text formatting failed: {str(e)}")
    
    def translate_text(self, text: str, target_language: str = 'es') -> str:
        """
        Translate text to the specified language and format as song verses.
        
        Args:
            text: Original text
            target_language: Target language code (e.g., 'es', 'fr', 'de')
            
        Returns:
            Translated and formatted text
            
        Raises:
            TranslationException: If translation fails
        """
        try:
            # Validate target language
            if target_language not in self.SUPPORTED_LANGUAGES:
                raise TranslationException(
                    f"Unsupported language: {target_language}. "
                    f"Supported languages: {', '.join(self.SUPPORTED_LANGUAGES.keys())}"
                )
            
            model = self._get_available_model()
            lang_info = self.SUPPORTED_LANGUAGES[target_language]
            
            # Create language-specific prompt
            if target_language == 'es':
                system_content = (
                    "Eres un experto traductor de canciones al español. Tu tarea es traducir letras de canciones "
                    "manteniendo el significado, el sentimiento y la naturalidad en español. "
                    "NO hagas traducciones literales palabra por palabra. "
                    "Adapta expresiones idiomáticas y frases para que suenen naturales en español. "
                    "Mantén el ritmo poético y la estructura de versos. "
                    "Si hay juegos de palabras o expresiones culturales, encuentra equivalentes en español que transmitan la misma idea."
                )
                user_content = f"Traduce esta canción al español de forma natural y contextual, organizándola en versos:\n\n{text}"
            else:
                system_content = (
                    f"You are an expert song translator to {lang_info['name']}. Your task is to translate song lyrics "
                    f"while maintaining the meaning, sentiment, and naturalness in {lang_info['name']}. "
                    "DO NOT do literal word-by-word translations. "
                    f"Adapt idiomatic expressions and phrases to sound natural in {lang_info['name']}. "
                    "Maintain the poetic rhythm and verse structure. "
                    f"If there are wordplays or cultural expressions, find equivalents in {lang_info['name']} that convey the same idea."
                )
                user_content = f"Translate this song to {lang_info['name']} in a natural and contextual way, organizing it in verses:\n\n{text}"
            
            messages = [
                {"role": "system", "content": system_content},
                {"role": "user", "content": user_content}
            ]
            
            response = self.client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=4096,
                temperature=0.7,
                stream=False
            )
            
            translated_text = response.choices[0].message.content.strip()
            return translated_text
            
        except TranslationException:
            raise
        except Exception as e:
            raise TranslationException(f"Translation failed: {str(e)}")
    
    def translate_to_spanish(self, text: str) -> str:
        """
        Translate text to Spanish and format as song verses.
        (Deprecated: Use translate_text with target_language='es' instead)
        
        Args:
            text: Original text
            
        Returns:
            Translated and formatted text
            
        Raises:
            TranslationException: If translation fails
        """
        return self.translate_text(text, target_language='es')
    
    def process_transcription(self, original_text: str, target_language: str = 'es') -> Dict[str, str]:
        """
        Process transcription: detect language, format original and translate if needed.
        
        Args:
            original_text: Original transcribed text
            target_language: Target language code for translation (default: 'es' for Spanish)
            
        Returns:
            Dictionary with 'original' (formatted) and 'translated' keys.
            If already in target language, 'translated' will be the same as 'original'.
            
        Raises:
            TranslationException: If processing fails
        """
        try:
            # Detect the language of the transcription
            detected_language = self.detect_language(original_text)
            
            # Format the original text
            formatted_original = self.format_text_as_verses(original_text)
            
            # Normalize language codes (handle variations like 'spa' for Spanish)
            lang_code_mapping = {
                'spa': 'es',
                'eng': 'en',
                'fra': 'fr',
                'deu': 'de',
                'ita': 'it',
                'por': 'pt',
                'rus': 'ru',
                'jpn': 'ja',
                'kor': 'ko',
                'zho': 'zh',
                'ara': 'ar',
            }
            
            normalized_detected = lang_code_mapping.get(detected_language, detected_language)
            
            # Only translate if the detected language is different from target language
            if normalized_detected == target_language:
                # Already in target language, no translation needed
                translated_text = formatted_original
            else:
                # Translate to target language
                translated_text = self.translate_text(original_text, target_language)
            
            return {
                'original': formatted_original,
                'translated': translated_text
            }
        except TranslationException:
            raise
        except Exception as e:
            raise TranslationException(f"Text processing failed: {str(e)}") 