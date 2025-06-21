import argparse
import os
from typing import List

from docx import Document
from PyPDF2 import PdfReader
from TTS.api import TTS


def extract_text_from_docx(path: str) -> str:
    doc = Document(path)
    return "\n".join([p.text for p in doc.paragraphs])


def extract_text_from_pdf(path: str) -> str:
    text: List[str] = []
    with open(path, "rb") as f:
        reader = PdfReader(f)
        for page in reader.pages:
            txt = page.extract_text()
            if txt:
                text.append(txt)
    return "\n".join(text)


def load_text(input_path: str) -> str:
    if os.path.isfile(input_path):
        if input_path.lower().endswith(".pdf"):
            return extract_text_from_pdf(input_path)
        elif input_path.lower().endswith(".docx"):
            return extract_text_from_docx(input_path)
        else:
            with open(input_path, "r", encoding="utf-8") as f:
                return f.read()
    else:
        return input_path


def main():
    parser = argparse.ArgumentParser(description="Türkçe Ses Klonlama Aracı")
    parser.add_argument("input", help="Metin, DOCX ya da PDF dosyası")
    parser.add_argument("ref_voice", help="Referans ses dosyası (wav)")
    parser.add_argument(
        "--model_name",
        default="tts_models/multilingual/multi-dataset/xtts_v2",
        help="Hugging Face model adı",
    )
    parser.add_argument(
        "--output",
        default="output.wav",
        help="Oluşturulacak ses dosyası",
    )

    args = parser.parse_args()
    text = load_text(args.input)

    tts = TTS(args.model_name)
    tts.tts_to_file(text=text, speaker_wav=args.ref_voice, file_path=args.output)


if __name__ == "__main__":
    main()
