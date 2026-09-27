"""
Custom exceptions for the content analysis app.
"""


class TranslationGeneratorException(Exception):
    """Base exception for all content analysis errors."""
    pass


class YouTubeDownloadException(TranslationGeneratorException):
    """Raised when YouTube download fails."""
    pass


class TranscriptionException(TranslationGeneratorException):
    """Raised when transcription fails."""
    pass


class AnalysisException(TranslationGeneratorException):
    """Raised when content analysis fails."""
    pass


class InvalidDataException(TranslationGeneratorException):
    """Raised when input data is invalid."""
    pass 