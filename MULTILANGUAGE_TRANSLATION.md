# Multi-Language Translation Feature

## Overview

The YouTube Agent now supports translation to multiple languages with intelligent language detection. The system automatically detects if the source video is already in the target language and only formats the text instead of translating it.

## Supported Languages

| Language | Code | Native Name |
|----------|------|-------------|
| Spanish | `es` | Español |
| English | `en` | English |
| French | `fr` | Français |
| German | `de` | Deutsch |
| Italian | `it` | Italiano |
| Portuguese | `pt` | Português |
| Russian | `ru` | Русский |
| Japanese | `ja` | 日本語 |
| Korean | `ko` | 한국어 |
| Chinese | `zh` | 中文 |
| Arabic | `ar` | العربية |

## How It Works

### 1. Language Detection
The system automatically detects the language of the transcribed audio using OpenAI's language detection capabilities.

### 2. Intelligent Translation
- **If the detected language matches the target language**: The text is only formatted into song verses without translation.
- **If the detected language differs from the target language**: The text is translated to the target language and formatted.

### 3. Contextual Translation
The translation is not literal word-by-word. Instead, it:
- Maintains the meaning, sentiment, and naturalness
- Adapts idiomatic expressions and cultural phrases
- Preserves the poetic rhythm and verse structure
- Finds equivalent expressions that convey the same idea

## Using the Feature

### Streamlit Interface

1. **Select Target Language**:
   - Open the sidebar
   - Under "Translation Language", select your desired target language
   - The interface will show a hint: "If the song is already in [language], it will only be formatted, not translated."

2. **Process Video**:
   - Enter the YouTube URL
   - Enter your OpenAI API Key
   - Click "Generate Translation"

3. **View Results**:
   - The original transcription (formatted)
   - The translation in your selected language (or formatted original if already in that language)

### REST API

**Endpoint**: `POST /api/generate-translation`

**Request Body**:
```json
{
    "link": "https://youtube.com/watch?v=...",
    "openai_api_key": "sk-...",
    "target_language": "fr"
}
```

**Parameters**:
- `link` (required): YouTube video URL
- `openai_api_key` (required): Your OpenAI API key
- `target_language` (optional): Target language code (default: "es")

**Response**:
```json
{
    "content": "translated text...",
    "title": "video title",
    "original_transcription": "formatted original text...",
    "video_file": "/path/to/video.mp4",
    "audio_file": "/path/to/audio.mp3",
    "target_language": "fr"
}
```

## Examples

### Example 1: English Song → French Translation
- **Input**: English song
- **Target Language**: French (`fr`)
- **Result**: 
  - Original: Formatted English lyrics
  - Translation: Natural French translation

### Example 2: Spanish Song → Spanish (No Translation)
- **Input**: Spanish song
- **Target Language**: Spanish (`es`)
- **Result**: 
  - Original: Formatted Spanish lyrics
  - Translation: Same as original (no translation needed)

### Example 3: Japanese Song → Portuguese Translation
- **Input**: Japanese song
- **Target Language**: Portuguese (`pt`)
- **Result**: 
  - Original: Formatted Japanese lyrics
  - Translation: Natural Portuguese translation

## Technical Implementation

### Service Architecture

**TranslationService** (`translation_generator_app/services/translation_service.py`):
- `detect_language(text)`: Detects the language of the text
- `format_text_as_verses(text)`: Formats text into song verses without changing language
- `translate_text(text, target_language)`: Translates text to the specified language
- `process_transcription(original_text, target_language)`: Main method that orchestrates detection, formatting, and translation

### Key Features

1. **Language Normalization**: Handles various language code formats (e.g., 'spa' → 'es')
2. **Validation**: Ensures only supported languages are used
3. **Smart Prompts**: Uses language-specific prompts for better translation quality
4. **Error Handling**: Comprehensive exception handling with custom exceptions

## Configuration

No additional configuration is required. The feature is enabled by default with the following preferences:

- **Default Language**: Spanish (`es`)
- **Supported Models**: GPT-4o, GPT-5-nano, GPT-4-turbo, GPT-3.5-turbo
- **Temperature**: 
  - Formatting: 0.3 (more consistent)
  - Translation: 0.7 (more creative and natural)

## Notes

- The quality of translation depends on the OpenAI model available in your API key
- Language detection uses the first 500 characters of the transcription for efficiency
- All translations maintain the song verse structure for readability 