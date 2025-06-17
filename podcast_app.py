import os
import streamlit as st
from podcast_generator import (
    load_text,
    transcribe_audio,
    split_sentences,
    generate_podcast_dialog,
    synthesize_dialog,
)

st.title("Podcast Creator")

uploaded_file = st.file_uploader(
    "Upload text (txt, docx, pdf) or audio", type=["txt", "docx", "pdf", "wav", "mp3", "m4a"]
)

speaker_a = st.file_uploader(
    "Speaker A reference audio", type=["wav", "mp3", "m4a"], key="a"
)
speaker_b = st.file_uploader(
    "Speaker B reference audio", type=["wav", "mp3", "m4a"], key="b"
)

speaker_a_name = st.text_input("Speaker A name", "A")
speaker_b_name = st.text_input("Speaker B name", "B")
sentences_per_turn = st.number_input("Sentences per turn", min_value=1, value=1)
tts_model = st.text_input(
    "XTTS model", value="tts_models/multilingual/multi-dataset/xtts_v2"
)
sample_rate = st.number_input("Sample rate", min_value=8000, value=24000, step=1000)
output_path = st.text_input("Output file", "podcast.wav")

if st.button("Generate Podcast") and uploaded_file is not None:
    tmp_input = os.path.join(st.experimental_user_dir(), uploaded_file.name)
    with open(tmp_input, "wb") as f:
        f.write(uploaded_file.getbuffer())

    ext = os.path.splitext(tmp_input)[1].lower()
    if ext in [".txt", ".docx", ".pdf"]:
        text = load_text(tmp_input)
    else:
        text = transcribe_audio(tmp_input)

    sentences = split_sentences(text)
    dialog = generate_podcast_dialog(
        sentences,
        speaker_names=[speaker_a_name, speaker_b_name],
        sentences_per_turn=int(sentences_per_turn),
    )

    tmp_a = None
    tmp_b = None
    if speaker_a:
        tmp_a = os.path.join(st.experimental_user_dir(), speaker_a.name)
        with open(tmp_a, "wb") as f:
            f.write(speaker_a.getbuffer())
    if speaker_b:
        tmp_b = os.path.join(st.experimental_user_dir(), speaker_b.name)
        with open(tmp_b, "wb") as f:
            f.write(speaker_b.getbuffer())

    synthesize_dialog(
        dialog,
        [tmp_a, tmp_b],
        output_path,
        tts_model=tts_model,
        speaker_names=[speaker_a_name, speaker_b_name],
        sample_rate=int(sample_rate),
    )

    st.success(f"Saved podcast to {output_path}")
    st.audio(output_path)
    st.text("\n".join(dialog))
