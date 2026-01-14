import logging
import sys
from typing import Optional

import click
from dotenv import load_dotenv

from .api_client import OpenAITranscriptionClient
from .config import Config
from .exceptions import WhisperCLIError
from .transcriber import Transcriber


def _configure_logging(verbose: bool) -> None:
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(level=level, format="%(message)s")


@click.command()
@click.argument("audio_file", type=click.Path(exists=True))
@click.option("-o", "--output", help="Output file path")
@click.option("-m", "--model", help="Model override")
@click.option("--chunk-size", type=int, help="Chunk size in MB")
@click.option("-q", "--quiet", is_flag=True, help="Suppress progress")
@click.option("-v", "--verbose", is_flag=True, help="Verbose logging")
def main(
    audio_file: str,
    output: Optional[str],
    model: Optional[str],
    chunk_size: Optional[int],
    quiet: bool,
    verbose: bool,
) -> None:
    try:
        load_dotenv()
        config = Config.load(model=model, chunk_size_mb=chunk_size, verbose=verbose, quiet=quiet)
        _configure_logging(config.verbose)
        client = OpenAITranscriptionClient(api_key=config.api_key, model=config.model)
        transcriber = Transcriber(client=client, quiet=config.quiet)
        transcript = transcriber.transcribe(audio_file)

        if output:
            with open(output, "w", encoding="utf-8") as handle:
                handle.write(transcript)
        else:
            click.echo(transcript)
    except WhisperCLIError as exc:
        click.echo(f"Error: {exc}", err=True)
        sys.exit(1)
    except KeyboardInterrupt:
        click.echo("Interrupted by user.", err=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
