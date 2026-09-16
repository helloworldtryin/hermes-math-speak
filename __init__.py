"""math-speak plugin — hear LaTeX math as words, not symbols.

Registers:
- ``math_speak_text`` tool (toolset ``tts``): rewrite LaTeX math spans in a
  string to spoken English. Zero dependencies.
- ``mathspeak`` TTS provider: converts math, then synthesizes with Microsoft
  Edge TTS (requires the ``edge-tts`` package). Select with
  ``hermes config set tts.provider mathspeak``.
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
import threading
from typing import Any, Dict, Optional

from mathtext import speak_math

logger = logging.getLogger(__name__)

MATH_SPEAK_TOOL_SCHEMA = {
    "name": "math_speak_text",
    "description": (
        "Rewrite LaTeX math ($...$, $$...$$, \\(...\\), \\[...\\]) in text as "
        "spoken English for TTS/read-aloud. Use before speaking any message "
        "containing math. Currency ($5, US$300) is left untouched."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "text": {"type": "string", "description": "Text possibly containing LaTeX math."}
        },
        "required": ["text"],
    },
}

DEFAULT_EDGE_VOICE = "en-US-AriaNeural"


def handle_math_speak_text(args: Dict[str, Any], **_kw) -> str:
    try:
        return json.dumps({"success": True, "spoken_text": speak_math(args.get("text") or "")})
    except Exception as exc:  # never break the turn on a text rewrite
        logger.debug("math_speak_text failed: %s", exc)
        return json.dumps({"success": False, "error": str(exc)})


class MathSpeakProvider:
    """TTS provider ``mathspeak``: math-aware synthesis via Edge TTS."""

    name = "mathspeak"

    @property
    def voice_compatible(self) -> bool:
        return False

    def _edge_voice(self, voice: Optional[str]) -> str:
        return voice or os.getenv("MATHSPEAK_VOICE", DEFAULT_EDGE_VOICE)

    def synthesize(self, text: str, output_path: str, *, voice: Optional[str] = None,
                   model: Optional[str] = None, speed: Optional[float] = None,
                   format: str = "mp3", **_extra: Any) -> str:
        try:
            import edge_tts
        except ImportError as exc:
            raise RuntimeError(
                "The 'mathspeak' TTS provider needs the 'edge-tts' package: "
                "pip install edge-tts (or: uv pip install edge-tts)."
            ) from exc
        spoken = speak_math(text)
        if speed and speed != 1.0:
            logger.debug("mathspeak: speed %s ignored (Edge rate not adjusted)", speed)
        if not output_path.lower().endswith(".mp3"):
            base = os.path.splitext(output_path)[0]
            output_path = base + ".mp3" if base else output_path + ".mp3"
        parent = os.path.dirname(output_path)
        if parent:
            os.makedirs(parent, exist_ok=True)

        async def _go() -> None:
            await edge_tts.Communicate(spoken, self._edge_voice(voice)).save(output_path)

        try:
            asyncio.run(_go())
        except RuntimeError:
            # Called from inside a running event loop: isolate a fresh loop.
            failure: list = []

            def _target() -> None:
                try:
                    asyncio.run(_go())
                except Exception as exc:  # propagate to the caller
                    failure.append(exc)

            worker = threading.Thread(target=_target, daemon=True)
            worker.start()
            worker.join(timeout=300)
            if failure:
                raise failure[0]
            if worker.is_alive():
                raise TimeoutError("mathspeak synthesis timed out")
        return output_path

    def list_voices(self):
        return [{"id": DEFAULT_EDGE_VOICE, "display": "Aria (Edge, US English)", "language": "en-US"}]

    def default_voice(self) -> Optional[str]:
        return DEFAULT_EDGE_VOICE


def register(ctx) -> None:
    """Called once by the Hermes plugin loader."""
    ctx.register_tool(name="math_speak_text", toolset="tts", schema=MATH_SPEAK_TOOL_SCHEMA,
                      handler=handle_math_speak_text)
    ctx.register_tts_provider(MathSpeakProvider())
    logger.info("math-speak plugin registered (tool + 'mathspeak' TTS provider)")
