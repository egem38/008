# -*- coding: utf-8 -*-
"""xtts synthesizer driver for NVDA

This driver uses the xtts v2 model from the `TTS` library to provide
Turkish speech output for NVDA. The implementation is intentionally
minimal and focuses on demonstrating how a synthesizer driver can
integrate an external TTS engine. It does not include the full
configuration or error handling you would expect in a production
NVDA add-on.

You need to install the `TTS` library and download an xtts v2
model that supports Turkish in order to use this driver.
"""

from __future__ import annotations

import os
from typing import Iterable, Optional

try:
    from TTS.api import TTS  # type: ignore
except ImportError:
    TTS = None  # The driver will not function without the library

import speech
import synthDriverHandler
from logHandler import log
import queueHandler


class SynthDriver(synthDriverHandler.SynthDriver):
    name = "xtts"
    description = "XTTS v2 Turkish synthesizer"

    supportedSettings = (
        synthDriverHandler.VoiceSetting(),
        synthDriverHandler.RateSetting(),
        synthDriverHandler.PitchSetting(),
        synthDriverHandler.VolumeSetting(),
    )

    supportedCommands = {
        speech.IndexCommand,
        speech.CharacterModeCommand,
        speech.BeepCommand,
    }

    hasAudioOutput = True
    hasAudioEffects = False
    _tts: Optional[TTS] = None

    def __init__(self):
        super().__init__()
        if TTS is None:
            raise RuntimeError("TTS library not available; install with `pip install TTS`." )
        try:
            # Replace "tts_models/multilingual/xtts_v2" with the actual
            # path or model identifier you wish to use.
            self._tts = TTS(model_name="tts_models/multilingual/xtts_v2")
        except Exception as e:
            log.error(f"Failed to initialize XTTS engine: {e}")
            raise

    def speak(self, speechSequence: Iterable[speech.SpeechCommand]):
        # Combine text from the speech sequence into a single utterance.
        parts = []
        for item in speechSequence:
            if isinstance(item, speech.SpeechCommand):
                continue
            parts.append(str(item))
        text = "".join(parts)
        if not text:
            return
        try:
            assert self._tts is not None
            # xtts returns audio as a NumPy array. We write it to a temp
            # WAV file and queue it for playback.
            wav_path = "/tmp/xtts_output.wav"
            self._tts.tts_to_file(text=text, file_path=wav_path, speaker_wav=None, language="tr")
            queueHandler.queueFunction(queueHandler.eventQueue, synthDriverHandler.playWaveFile, wav_path)
        except Exception as e:
            log.error(f"XTTS synthesis error: {e}")

    def cancel(self):
        synthDriverHandler.stop()
