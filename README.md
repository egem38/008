# Ses Klonlama Aracı

Bu proje, metinleri Türkçe olarak sizin sesinizle okuyabilen basit bir Python aracıdır. Word (`.docx`) veya PDF dosyalarından metin alabilir, ya da doğrudan metin girişi yapabilirsiniz. Model olarak Hugging Face üzerinde bulunan ve çoklu dil desteği sunan **XTTS v2** kullanılır.

## Gereksinimler

- Python 3.10
- [Coqui TTS](https://github.com/coqui-ai/TTS) kütüphanesi
- `PyPDF2` ve `python-docx` paketleri

Örnek kurulum:

```bash
python3.10 -m venv venv
source venv/bin/activate
pip install TTS PyPDF2 python-docx
```

## Kullanım

```bash
python voice_cloner.py INPUT REF_VOICE.wav --output cikis.wav
```

Parametreler:

- **INPUT**: Metin dosyası, `.docx`, `.pdf` ya da doğrudan metin.
- **REF_VOICE.wav**: Klonlamak istediğiniz referans ses kaydı.
- **--model_name**: (Opsiyonel) Kullanmak istediğiniz model adı. Varsayılan: `tts_models/multilingual/multi-dataset/xtts_v2`.
- **--output**: (Opsiyonel) Çıktı ses dosyasının adı. Varsayılan: `output.wav`.

Örnek:

```bash
python voice_cloner.py ornek.pdf sesim.wav --output sonuc.wav
```

Bu komut `ornek.pdf` içindeki metni okur ve `sesim.wav` dosyasındaki ses tonunu taklit ederek `sonuc.wav` dosyasını üretir.

## Notlar

- PDF dosyalarının metin yapısı karmaşık olabilir; mümkünse `.docx` veya düz metin kullanın.
- İlk çalıştırmada model Hugging Face üzerinden indirileceği için internet bağlantısı gereklidir.
- Uzun metinler belleği zorlayabilir. Gerekirse metni parçalara bölerek işleyin.
