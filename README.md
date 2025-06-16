# Podcast Creator

This repository provides a basic tool for generating a simple podcast from text or audio files. It uses [Whisper](https://github.com/openai/whisper) for transcription and XTTS v2 from the [TTS](https://github.com/coqui-ai/TTS) library for text-to-speech voice cloning.

## Requirements

- Python 3.8+
- Optional dependencies:
  - `docx2txt` and `PyPDF2` for reading Word and PDF files
  - `whisper` for audio transcription
  - `TTS` for speech synthesis
  - `streamlit` if you want to run the example web UI

Install the packages with:

```bash
pip install docx2txt PyPDF2 openai-whisper TTS streamlit
```

> **Note**: Installing `TTS` and `whisper` will also download PyTorch and other heavy dependencies.

## Usage

Generate a podcast from a text or audio file:

```bash
python podcast_generator.py INPUT_FILE \
  --audio-refs speakerA.wav speakerB.wav \
  --speaker-names Alice Bob \
  --sentences-per-turn 2 \
  --tts-model tts_models/multilingual/multi-dataset/xtts_v2 \
  --output podcast.wav
```

- `INPUT_FILE` can be a `.txt`, `.docx`, `.pdf`, or an audio file.
- `--audio-refs` supplies reference audio files for cloning each speaker's voice.
- `--speaker-names` sets names for the dialog speakers.
- `--sentences-per-turn` controls how many sentences each turn contains.
- `--tts-model` chooses a specific XTTS model (default is `xtts_v2`).
- `--sample-rate` sets the sampling rate of the output file.
- `--output` sets the path for the generated WAV file.

Run the Streamlit interface:

```bash
streamlit run podcast_app.py
```
