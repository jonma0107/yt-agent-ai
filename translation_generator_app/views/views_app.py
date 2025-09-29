from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.conf import settings
import json

from yt_dlp import YoutubeDL
import os
import assemblyai as aai
from ..models import translationPost
import environ
import openai
from openai import OpenAI

# Load environment variables from .env
env = environ.Env()
environ.Env.read_env()

# Access the API key from environment variables
AAI_API_KEY = env('AAI_API_KEY')

# Access the API key from environment variables
OPENAI_API_KEY = env('OPENAI_API_KEY')


def process_youtube_video(yt_link, openai_api_key):
    """
    Downloads, transcribes, and summarizes a YouTube video.
    """
    # Initialize OpenAI client with user-provided key
    client = OpenAI(api_key=openai_api_key)

    try:
        title = yt_title(yt_link)
        if not title:
            raise Exception("Could not retrieve YouTube video title.")

        video_file, audio_file = download_video_and_audio(yt_link, title)

        # Check if files were downloaded
        if not os.path.exists(video_file) or os.path.getsize(video_file) == 0:
            raise Exception("Failed to download video file or file is empty.")
        if not os.path.exists(audio_file) or os.path.getsize(audio_file) == 0:
            raise Exception("Failed to download audio file or file is empty.")

    except Exception as e:
        raise Exception(f"Error during download: {e}")

    try:
        transcription_data = get_transcription(audio_file, title, client)
        if not transcription_data:
            raise Exception("Failed to get transcript")

        translation_content = transcription_data['translated']
        original_content = transcription_data['original']

        # Save to database
        translation = translationPost.objects.create(
            youtube_title=title,
            youtube_link=yt_link,
            generated_content=translation_content
        )
        translation.save()

        # The audio file is no longer deleted to allow for download.
        # delete_audio_file(audio_file)

        return {
            "title": title,
            "translation": translation_content,
            "original_transcription": original_content,
            "video_file": video_file,
            "audio_file": audio_file,
            "transcription_file": settings.MEDIA_ROOT / f"{''.join(c for c in title if c.isalnum() or c in (' ', '_', '-')).rstrip()}.txt"
        }
    except Exception as e:
        raise Exception(f"Error during transcription: {e}")


def delete_audio_file(filepath):
    """ Delete the audio file if it exists. """
    try:
        if os.path.exists(filepath):
            os.remove(filepath)
            print(f"File deleted: {filepath}")
        else:
            print(f"File not found: {filepath}")
    except Exception as e:
        print(f"Error when deleting file: {e}")

def download_video_and_audio(link, title):
    safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '_', '-')).rstrip()
    video_path = settings.MEDIA_ROOT / f"{safe_title}_video"
    audio_path = settings.MEDIA_ROOT / f"{safe_title}_audio"

    # Descargar video .mp4
    video_opts = {
        'format': 'mp4',
        'outtmpl': str(video_path) + '.mp4',
    }
    with YoutubeDL(video_opts) as ydl:
        ydl.download([link])
    video_file = str(video_path) + '.mp4'

    # Descargar audio .mp3
    audio_opts = {
        'format': 'bestaudio/best',
        'outtmpl': str(audio_path),  # sin extensión, yt-dlp la añade
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }
    with YoutubeDL(audio_opts) as ydl:
        ydl.download([link])
    audio_file = str(audio_path) + '.mp3'

    return video_file, audio_file

def get_transcription(audio_file, title, client):
    aai.settings.api_key = AAI_API_KEY
    transcriber = aai.Transcriber()
    transcript = transcriber.transcribe(audio_file)

    if transcript and hasattr(transcript, 'text') and transcript.text:
        original_text = transcript.text
        # Guardar la transcripción original en un archivo .txt
        safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '_', '-')).rstrip()
        transcript_file = settings.MEDIA_ROOT / f"{safe_title}.txt"
        with open(transcript_file, "w", encoding="utf-8") as f:
            f.write(original_text)

        # (Opcional) Si quieres seguir devolviendo la traducción, puedes traducir aquí:
        
        try:
            # 1. Get available models
            available_models = [model.id for model in client.models.list().data]
            
            # 2. Find a suitable model from a preferred list
            preferred_models = ['gpt-4o', 'gpt-5-nano', 'gpt-4-turbo', 'gpt-3.5-turbo']
            selected_model = None
            for model in preferred_models:
                if model in available_models:
                    selected_model = model
                    break
            
            if not selected_model:
                raise Exception("No suitable OpenAI model found for your API key. Requires gpt-4o, gpt-5-nano, gpt-4-turbo, or gpt-3.5-turbo.")

            messages = [
                {"role": "system", "content": "Eres un excelente traductor al idioma español."},
                {"role": "user", "content": f"Transcribe en forma de canción osea en versos el siguiente texto:\n\n{original_text}"}
            ]
            response = client.chat.completions.create(
                model=selected_model,
                messages=messages,
                max_tokens=4096,
                temperature=0.7,
                stream=False
            )
            translated_text = response.choices[0].message.content.strip()
        except Exception as e:
            print(f"Error al traducir la transcripción: {e}")
            return None

        # Devuelve la traducción (o el original si prefieres)
        return {'original': original_text, 'translated': translated_text}
    else:
        return None

@csrf_exempt
def generate_translation(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            yt_link = data['link']
            openai_api_key = data['openai_api_key'] # Assuming key is passed in request
        except (KeyError, json.JSONDecodeError):
            return JsonResponse({'error': 'Invalid data sent'}, status=400)

        try:
            result = process_youtube_video(yt_link, openai_api_key)
            return JsonResponse({'content': result['translation']})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    else:
        return JsonResponse({'error': 'Invalid request method'}, status=405)

def yt_title(link):
    ydl_opts = {}
    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(link, download=False)  # Only extracts information without downloading
        title = info.get('title', None)
    return title

def download_audio(link):
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': os.path.join(settings.MEDIA_ROOT, '%(title)s.%(ext)s'),
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }

    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(link, download=True)
        file_path = ydl.prepare_filename(info)
        base, ext = os.path.splitext(file_path)
        new_file = f"{base}.mp3"

    return new_file

# DeepSeek client configuration
# client = openai.OpenAI(api_key=os.environ.get("OPENAI_API_KEY"), base_url="https://api.openai.com/v1")

# OpenAI client configuration
# client = openai.OpenAI(
#     api_key=os.environ.get("OPENAI_API_KEY"),
#     base_url="https://api.openai.com/v1",
# )

