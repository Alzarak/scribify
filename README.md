# Whisper API Wrapper - Audio Transcription CLI

A Python CLI that transcribes large audio files using OpenAI's
`gpt-4o-mini-transcribe` model. Files above 25MB are
automatically chunked and merged into a single plain-text output.

## Requirements

- Python 3.9+
- FFmpeg (system dependency)
  - Linux: `apt-get install ffmpeg`
  - macOS: `brew install ffmpeg`

## Install

```bash
pip install -e .
```

## Quick Start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export OPENAI_API_KEY="sk-your-key"
whisper-cli path/to/audio.mp3 -o output.txt
```

## Configuration

Set your API key in the environment:

```bash
export OPENAI_API_KEY="sk-your-key"
```

You can copy `.env.example` to `.env` and set your key there if you prefer.

## Usage

```bash
whisper-cli path/to/audio.mp3 -o output.txt
```

Options:

- `-m, --model` override model
- `--chunk-size` target chunk size in MB
- `-q, --quiet` suppress progress UI
- `-v, --verbose` verbose logging

## Examples

Small file:

```bash
whisper-cli small.mp3 -o transcript.txt
```

Large file:

```bash
whisper-cli large.mp3 --verbose -o transcript.txt
```

## Notes

- Large files are chunked; chunks are exported as mp3 for broad FFmpeg compatibility.
- Costs & data handling: API calls incur OpenAI usage fees; your audio is sent to OpenAI for transcription; keep your `OPENAI_API_KEY` private and out of version control.

## Troubleshooting

- FFmpeg missing: `apt-get install ffmpeg` or `brew install ffmpeg`
- API key missing: ensure `OPENAI_API_KEY` is set in your shell or `.env`

## License

MIT. See `LICENSE`.

## Development

```bash
pip install -r requirements-dev.txt
pytest -v
```
