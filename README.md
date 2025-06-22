# NotebookLM Benzeri Türkçe Uygulama

Bu depoda, sohbet ve podcast oluşturma işlevlerini `app` klasöründe topladık.
Anthropic'in Claude modelleriyle sohbet edebilir veya Coqui TTS ile ses
klonlamalı podcast oluşturabilirsiniz.

## Kurulum
1. Python 3.12 veya üzeri bir sürüm kullanın.
2. Gerekli paketleri yükleyin:
   ```bash
   pip install anthropic TTS torch
   ```
3. Anthropic API anahtarınızı edinin ve `ANTHROPIC_API_KEY` ortam değişkeni olarak tanımlayın.

## Kullanım
İki alt komut bulunmaktadır:

### Sohbet
```bash
python -m app chat
```
`quit` yazarak çıkabilirsiniz.

### Podcast Oluşturma
```bash
python -m app podcast "Podcast metni buraya" --reference kendi_ses.wav --output sonuc.wav
```
Varsayılan olarak `reference.wav` dosyası klonlanır ve `output.wav` oluşturulur. `--model` seçeneği ile farklı bir Coqui TTS modeli belirtebilirsiniz.
