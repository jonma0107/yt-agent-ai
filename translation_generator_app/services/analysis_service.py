"""
Analysis Service - Handles content analysis and report generation using Google Gemini.
"""
import time
from typing import Dict, List
import google.generativeai as genai
from django.conf import settings

from ..exceptions import AnalysisException

CHUNK_SIZE = 8000
MAX_CHARS = 30000

# Model fallback chain mapped from live quota snapshot (2026-09-25)
# Format: RPM used/limit, TPM used/limit, RPD used/limit
# Sorted by RPD remaining desc, then RPM remaining desc
# If a model returns 429 RESOURCE_EXHAUSTED, _try_with_fallback retries with next
PREFERRED_MODELS = [
    # Tier 1: 500 RPD, 15 RPM - untouched, highest daily capacity
    'gemini-3.5-flash-lite',      # 0/15 RPM, 0/250K TPM, 0/500 RPD -> 500 left, 15 RPM headroom
    'gemini-3.1-flash-lite',      # 0/15 RPM, 0/250K TPM, 0/500 RPD -> 500 left, 15 RPM headroom

    # Tier 2: 20 RPD, 10 RPM - untouched
    'gemini-2.5-flash-lite',      # 0/10 RPM, 0/250K TPM, 0/20 RPD  -> 20 left, 10 RPM

    # Tier 3: 20 RPD, 5 RPM - untouched (0/5 = 5 RPM headroom)
    'gemini-2.5-flash',           # 0/5 RPM, 0/250K TPM, 0/20 RPD   -> 20 left
    'gemini-3-flash',             # 0/5 RPM, 0/250K TPM, 0/20 RPD   -> 20 left
    'gemini-3.7-flash',           # 0/5 RPM, 0/250K TPM, 0/20 RPD   -> 20 left

    # Tier 4: 20 RPD, partially used - still available
    'gemini-3.8-flash',           # 1/5 RPM, 556/250K TPM, 1/20 RPD -> 19 left, 4 RPM headroom
    'gemini-3.5-flash',           # 2/5 RPM, 63.13K/250K TPM, 6/20 RPD -> 14 left, 3 RPM headroom

    # Tier 5: Over-quota but kept as last resort before ultimate fallback
    'gemini-3.6-flash',           # 4/5 RPM, 124.17K/250K TPM, 21/20 RPD -> -1 RPD (exhausted), 1 RPM headroom
    'gemini-flash-latest',        # alias, maps to latest available

    # Tier 6: Ultimate fallback - Gemma 14.4K RPD, 30 RPM (massive quota, lower quality but available)
    'gemma-4-26b-a4b-it',         # 0/30 RPM, 0/14.4K RPD -> 14400 left
    'gemma-4-31b-it',             # 0/30 RPM, 0/14.4K RPD -> 14400 left
]


class AnalysisService:
    """
    Service for handling text analysis and content report generation.

    Uses PREFERRED_MODELS fallback chain (first entry is the default model).
    """

    SINGLE_PROMPT = (
        "Analiza la siguiente transcripción completa de un video de YouTube y genera "
        "un Reporte de Contenido detallado con las siguientes secciones:\n\n"
        "1. **Temas Principales Tratados**: Enumera y describe brevemente cada tema central.\n\n"
        "2. **Argumento / Resumen Narrativo**: Describe la narrativa completa del video.\n\n"
        "3. **Opiniones o Puntos de Vista Expresados**: Identifica posturas y perspectivas.\n\n"
        "4. **Datos o Hechos Clave**: Extrae datos, cifras, nombres, fechas.\n\n"
        "5. **Conclusión / Veredicto Final**: Resume la postura general y el mensaje final.\n\n"
        "Responde en español.\n\nTRANSCRIPCIÓN:\n\n"
    )

    ANALYSIS_PROMPT = (
        "Analiza esta parte de una transcripción de video de YouTube y genera "
        "un análisis con las siguientes secciones:\n\n"
        "1. **Temas Principales**: Enumera y describe brevemente los temas centrales.\n\n"
        "2. **Argumento**: Describe la narrativa brevemente.\n\n"
        "3. **Opiniones**: Identifica posturas y perspectivas.\n\n"
        "4. **Datos Clave**: Extrae datos, cifras, nombres.\n\n"
        "5. **Conclusiones**: Resume el mensaje de esta parte.\n\n"
        "Responde en español. Transcripción:\n\n"
    )

    FINAL_PROMPT = (
        "Combina los análisis parciales y genera un Reporte de Contenido final "
        "con estas secciones:\n\n"
        "1. **Temas Principales**: Resume todos los temas.\n\n"
        "2. **Argumento**: Narrativa completa del video.\n\n"
        "3. **Opiniones**: Consolida todas las posturas.\n\n"
        "4. **Datos Clave**: Todos los datos y hechos.\n\n"
        "5. **Conclusión Final**: Mensaje general del video.\n\n"
        "Responde en español.\n\n--- ANÁLISIS PARCIALES ---\n\n"
    )

    def __init__(self, api_key: str):
        genai.configure(api_key=api_key)
        self.api_key = api_key

    def _try_with_fallback(self, prompt: str, max_tokens: int, timeout: int = 120) -> str:
        """Try generation with fallback models on quota/availability errors."""
        last_error = None
        for model_name in PREFERRED_MODELS:
            try:
                model = genai.GenerativeModel(model_name)
                response = model.generate_content(
                    prompt,
                    generation_config={
                        'temperature': 0.5,
                        'max_output_tokens': max_tokens,
                    },
                    request_options={"timeout": timeout},
                )
                if not response or not response.candidates:
                    raise AnalysisException("Gemini returned empty response.")
                return response.candidates[0].content.parts[0].text
            except Exception as e:
                msg = str(e)
                # Retryable: quota exhausted, rate limit, model not available
                is_retryable = (
                    '429' in msg
                    or 'quota' in msg.lower()
                    or 'RESOURCE_EXHAUSTED' in msg
                    or '404' in msg
                    or 'not found' in msg.lower()
                    or 'not available' in msg.lower()
                )
                if is_retryable:
                    last_error = e
                    delay = 2
                    if 'retry in' in msg.lower():
                        try:
                            import re
                            m = re.search(r'retry in (\d+)', msg)
                            if m:
                                delay = int(m.group(1)) + 1
                        except:
                            pass
                    time.sleep(min(delay, 5))
                    continue
                raise
        raise AnalysisException(f"All models quota exceeded or unavailable: {last_error}")

    def _chunk_text(self, text: str, chunk_size: int = CHUNK_SIZE, max_chars: int = MAX_CHARS) -> List[str]:
        original_len = len(text)
        if len(text) > max_chars:
            text = text[:max_chars]
        truncated_notice = ""
        if original_len > max_chars:
            truncated_notice = f"\n\n[NOTA: Texto truncado a {max_chars} caracteres]"
        chunks = []
        for i in range(0, len(text), chunk_size):
            chunks.append(text[i:i + chunk_size])
        if truncated_notice:
            chunks[-1] += truncated_notice
        return chunks if chunks else [text[:chunk_size]]

    def _analyze_chunk(self, chunk_text: str, chunk_number: int, total_chunks: int) -> str:
        prompt = self.ANALYSIS_PROMPT + f"[Parte {chunk_number}/{total_chunks}]\n{chunk_text}"
        try:
            return self._try_with_fallback(prompt, max_tokens=1024, timeout=120)
        except AnalysisException:
            raise
        except Exception as e:
            msg = str(e)
            if '504' in msg or 'Deadline' in msg or 'timeout' in msg.lower():
                raise AnalysisException(
                    f"Tiempo de espera agotado en parte {chunk_number}/{total_chunks}. "
                    "Intenta con un video más corto."
                )
            raise AnalysisException(f"Error analizando parte {chunk_number}: {msg}")

    def generate_report(self, transcription_text: str) -> Dict[str, str]:
        try:
            if not transcription_text or not transcription_text.strip():
                raise AnalysisException("La transcripción está vacía.")

            # For short texts, do single call to save quota
            if len(transcription_text) <= CHUNK_SIZE:
                prompt = self.SINGLE_PROMPT + transcription_text[:MAX_CHARS]
                report = self._try_with_fallback(prompt, max_tokens=4096, timeout=180)
                return {'report': report}

            # For longer texts, chunk and combine
            chunks = self._chunk_text(transcription_text)
            total_chunks = len(chunks)
            if total_chunks == 0:
                raise AnalysisException("La transcripción está vacía.")

            # If only 1 chunk after truncation, single call
            if total_chunks == 1:
                prompt = self.SINGLE_PROMPT + chunks[0]
                report = self._try_with_fallback(prompt, max_tokens=4096, timeout=180)
                return {'report': report}

            partial_analyses = []
            for i, chunk in enumerate(chunks):
                analysis = self._analyze_chunk(chunk, i + 1, total_chunks)
                partial_analyses.append(analysis)

            combined_text = "\n\n--- FIN DE LA PARTE ---\n\n".join(partial_analyses)
            final_prompt = self.FINAL_PROMPT + combined_text
            report = self._try_with_fallback(final_prompt, max_tokens=4096, timeout=180)
            return {'report': report}

        except AnalysisException:
            raise
        except Exception as e:
            msg = str(e)
            if '429' in msg or 'quota' in msg.lower():
                raise AnalysisException(
                    "Se agotó la cuota gratuita de Gemini. Intenta en unos minutos "
                    "o usa un video más corto."
                )
            if '504' in msg or 'Deadline' in msg or 'timeout' in msg.lower():
                raise AnalysisException(
                    "El análisis excedió el tiempo de espera. Intenta con un video más corto."
                )
            raise AnalysisException(f"Content analysis failed: {msg}")
