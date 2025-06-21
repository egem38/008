import os
import sys
import argparse
import anthropic
from TTS.api import TTS


def run_chat() -> None:
    """Interactive Turkish chat using Anthropic Claude."""
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise SystemExit(
            "ANTHROPIC_API_KEY ortam değişkeni ayarlanmalı.\n"
            "API anahtarınızı https://console.anthropic.com/ adresinden alabilirsiniz."
        )

    client = anthropic.Anthropic(api_key=api_key)
    history = []

    print('NotebookLM - Türkçe sohbet. Çıkmak için "quit" yazın.')
    while True:
        user_input = input('Siz: ')
        if user_input.lower() in {'quit', 'exit'}:
            break
        history.append({'role': 'user', 'content': user_input})

        try:
            response = client.messages.create(
                model='claude-3-sonnet-20240229',
                messages=history,
                max_tokens=1024,
                temperature=0.7,
            )
        except Exception as exc:
            print(f'Hata: {exc}')
            continue

        assistant_message = ''.join(
            block.text for block in response.content if hasattr(block, 'text')
        )
        history.append({'role': 'assistant', 'content': assistant_message})
        print('Asistan:', assistant_message)


def run_podcast(
    text: str,
    reference: str,
    output: str,
    model: str,
) -> None:
    """Create a podcast-style audio file using Coqui TTS."""
    text = text or "Merhaba, bu podcast ornegidir."

    try:
        tts = TTS(model_name=model).to("cpu")
    except Exception as exc:  # pragma: no cover - runtime check only
        raise SystemExit(f"TTS modeli baslatilamadi: {exc}")

    try:
        tts.tts_to_file(text=text, speaker_wav=reference, file_path=output)
    except Exception as exc:  # pragma: no cover - runtime check only
        raise SystemExit(f"Ses dosyasi olusturulamadi: {exc}")

    print(f"Olusturulan dosya: {output}")


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Sohbet ve podcast aracı")
    sub = parser.add_subparsers(dest="command")

    sub.add_parser("chat", help="Türkçe sohbet başlat")
    pod_parser = sub.add_parser("podcast", help="Metni sese dönüştür")
    pod_parser.add_argument("text", nargs=argparse.REMAINDER, help="Seslendirilecek metin")
    pod_parser.add_argument(
        "--reference",
        default="reference.wav",
        help="Ses klonlamasi için referans dosya",
    )
    pod_parser.add_argument(
        "--output",
        default="output.wav",
        help="Oluşacak ses dosyasi",
    )
    pod_parser.add_argument(
        "--model",
        default="tts_models/multilingual/multi-dataset/your_tts",
        help="Kullanilacak TTS modeli",
    )

    args = parser.parse_args(argv)

    if args.command == "chat":
        run_chat()
    elif args.command == "podcast":
        run_podcast(
            " ".join(args.text),
            reference=args.reference,
            output=args.output,
            model=args.model,
        )
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
