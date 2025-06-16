import os
import re
from typing import List, Optional

# Optional third-party imports; these modules may need to be installed
try:
    import docx2txt
except ImportError:
    docx2txt = None

try:
    import PyPDF2
except ImportError:
    PyPDF2 = None

try:
    import whisper
except ImportError:
    whisper = None

try:
    from TTS.api import TTS
except ImportError:
    TTS = None


def load_text(file_path: str) -> str:
    """Load text from txt, docx, or pdf."""
    ext = os.path.splitext(file_path)[1].lower()
    if ext == ".txt":
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    elif ext == ".docx" and docx2txt:
        return docx2txt.process(file_path)
    elif ext == ".pdf" and PyPDF2:
        text = []
        with open(file_path, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                text.append(page.extract_text() or "")
        return "\n".join(text)
    else:
        raise ValueError(f"Unsupported file type or missing dependency: {file_path}")


def transcribe_audio(audio_path: str, model: str = "base") -> str:
    """Transcribe audio to text using Whisper."""
    if not whisper:
        raise RuntimeError("whisper package is not installed")
    model = whisper.load_model(model)
    result = model.transcribe(audio_path)
    return result.get("text", "")


def split_sentences(text: str) -> List[str]:
    """Split text into sentences."""
    # Simple sentence splitter using regex.
    sentences = re.split(r"(?<=[.!?]) +", text.strip())
    return [s.strip() for s in sentences if s.strip()]


def generate_podcast_dialog(
    sentences: List[str],
    speaker_names: Optional[List[str]] = None,
    sentences_per_turn: int = 1,
) -> List[str]:
    """Create a dialog script.

    Parameters
    ----------
    sentences : List[str]
        Sentences to arrange in dialog form.
    speaker_names : Optional[List[str]]
        Names for the speakers. Defaults to ["A", "B"].
    sentences_per_turn : int
        Number of sentences each speaker says per turn.
    """

    if not speaker_names:
        speaker_names = ["A", "B"]

    dialog = []
    i = 0
    speaker_idx = 0
    while i < len(sentences):
        chunk = " ".join(sentences[i : i + sentences_per_turn])
        speaker = speaker_names[speaker_idx % len(speaker_names)]
        dialog.append(f"{speaker}: {chunk}")
        i += sentences_per_turn
        speaker_idx += 1

    return dialog


def synthesize_dialog(
    dialog: List[str],
    speaker_audio: Optional[List[str]],
    output_path: str,
    tts_model: str = "tts_models/multilingual/multi-dataset/xtts_v2",
    speaker_names: Optional[List[str]] = None,
    sample_rate: int = 24000,
) -> None:
    """Synthesize dialog using XTTS v2.

    Parameters
    ----------
    dialog : List[str]
        Dialog lines in the format ``"Speaker: text"``.
    speaker_audio : Optional[List[str]]
        Reference audio files corresponding to ``speaker_names``.
    output_path : str
        Where to save the resulting WAV file.
    tts_model : str
        Name or path of the XTTS model.
    speaker_names : Optional[List[str]]
        Names used in ``dialog``. Defaults to ["A", "B"].
    sample_rate : int
        Sampling rate of the output WAV file.
    """
    if not TTS:
        raise RuntimeError("TTS package is not installed")

    if not speaker_names:
        speaker_names = ["A", "B"]

    tts = TTS(tts_model)

    if speaker_audio and len(speaker_audio) >= len(speaker_names):
        tts.tts_with_preset = getattr(tts, "tts", None)  # for compatibility
        speaker_refs = [tts.get_speaker_vector(p) for p in speaker_audio[: len(speaker_names)]]
    else:
        speaker_refs = [None] * len(speaker_names)

    wavs = []
    for line in dialog:
        speaker, text = line.split(":", 1)
        speaker = speaker.strip()
        text = text.strip()
        try:
            idx = speaker_names.index(speaker)
        except ValueError:
            idx = 0
        ref = speaker_refs[idx] if idx < len(speaker_refs) else None
        wav = tts.tts(text=text, speaker_wav=ref)
        wavs.append(wav)

    # Concatenate WAVs
    import numpy as np
    from scipy.io.wavfile import write

    if wavs:
        audio = np.concatenate(wavs)
        write(output_path, sample_rate, audio)


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Generate a podcast from text or audio using XTTS v2 and Whisper")
    parser.add_argument("input", help="Path to input txt/docx/pdf or audio file")
    parser.add_argument("--audio-refs", nargs="*", metavar="WAV", help="Reference audio files for each speaker")
    parser.add_argument("--speaker-names", nargs="*", metavar="NAME", help="Names of the speakers")
    parser.add_argument("--sentences-per-turn", type=int, default=1, help="Number of sentences per dialog turn")
    parser.add_argument("--tts-model", default="tts_models/multilingual/multi-dataset/xtts_v2", help="XTTS model name or path")
    parser.add_argument("--sample-rate", type=int, default=24000, help="Sample rate for output audio")
    parser.add_argument("--output", default="podcast.wav", help="Output WAV file")
    args = parser.parse_args()

    ext = os.path.splitext(args.input)[1].lower()
    if ext in [".txt", ".docx", ".pdf"]:
        text = load_text(args.input)
    else:
        text = transcribe_audio(args.input)

    sentences = split_sentences(text)
    dialog = generate_podcast_dialog(
        sentences,
        speaker_names=args.speaker_names,
        sentences_per_turn=args.sentences_per_turn,
    )
    synthesize_dialog(
        dialog,
        speaker_audio=args.audio_refs,
        output_path=args.output,
        tts_model=args.tts_model,
        speaker_names=args.speaker_names,
        sample_rate=args.sample_rate,
    )

    for line in dialog:
        print(line)
    print(f"Saved podcast to {args.output}")


if __name__ == "__main__":
    main()
