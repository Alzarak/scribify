# Scribify

A Python application that transcribes large audio files using OpenAI's
`gpt-4o-mini-transcribe` model. Available as both a CLI tool and web interface.
Files above 25MB are automatically chunked and merged into a single plain-text
output, with progress feedback.

## Features

- **Dual Interface**: CLI tool and web application
- Auto-chunking for large files (keeps each chunk under the API limit)
- Plain-text output to stdout or file
- Progress UI with Rich (can be silenced in CLI)
- Retry handling for transient API failures
- Supports common formats (mp3, wav, m4a, aac, flac, ogg, wma)
- Docker support with best practices (multi-stage builds, non-root user, health checks)

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
scribify path/to/audio.mp3 -o output.txt
```

## Configuration

Set your API key in the environment:

```bash
export OPENAI_API_KEY="sk-your-key"
```

You can copy `.env.example` to `.env` and set your key there if you prefer.

## Web Interface

Run the web application for a browser-based transcription interface:

### Local Development

```bash
# Install web dependencies
pip install -r requirements.txt

# Run the web server
python web_app.py
```

Then open http://localhost:8000 in your browser.

### Docker Deployment

The easiest way to run the web interface is with Docker:

```bash
# Copy and configure environment
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY

# Start the service
docker compose up -d

# View logs
docker compose logs -f

# Stop the service
docker compose down
```

Access the web interface at http://localhost:8000

For detailed Docker configuration and production deployment, see [DOCKER.md](DOCKER.md).

## How It Works

1. Validates the file and checks size.
2. If under 25MB, transcribes directly.
3. If over 25MB, splits into chunks, transcribes each, and merges results.
4. Temporary chunks are cleaned up after completion.

## CLI Usage

```bash
scribify path/to/audio.mp3 -o output.txt
```

Options:

- `-m, --model` override model
- `--chunk-size` target chunk size in MB
- `-q, --quiet` suppress progress UI
- `-v, --verbose` verbose logging

## Output

- By default, transcripts are printed to stdout.
- Use `-o/--output` to write a file.
- Chunked transcripts are concatenated with newlines.

## Examples

Small file:

```bash
scribify small.mp3 -o transcript.txt
```

Large file:

```bash
scribify large.mp3 --verbose -o transcript.txt
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
