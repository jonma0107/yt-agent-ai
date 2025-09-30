"""
Custom exceptions for the translation generator app.
"""


class TranslationGeneratorException(Exception):
    """Base exception for all translation generator errors."""
    pass


class YouTubeDownloadException(TranslationGeneratorException):
    """Raised when YouTube download fails."""
    pass


class TranscriptionException(TranslationGeneratorException):
    """Raised when transcription fails."""
    pass


class TranslationException(TranslationGeneratorException):
    """Raised when translation/formatting fails."""
    pass


class InvalidDataException(TranslationGeneratorException):
    """Raised when input data is invalid."""
    pass 