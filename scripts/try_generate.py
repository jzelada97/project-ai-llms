"""Prueba rápida desde terminal (sin interfaz web).

Uso:  python scripts/try_generate.py "Beneficios de dormir 8 horas" LinkedIn General
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from content_generator.config import ConfigError  # noqa: E402
from content_generator.generator import ContentRequest, GenerationError, generate_content  # noqa: E402


def main() -> None:
    topic = sys.argv[1] if len(sys.argv) > 1 else "Beneficios de dormir 8 horas"
    platform = sys.argv[2] if len(sys.argv) > 2 else "LinkedIn"
    audience = sys.argv[3] if len(sys.argv) > 3 else "General"
    try:
        print(generate_content(ContentRequest(topic, platform, audience)))
    except (ConfigError, GenerationError) as exc:
        sys.exit(f"Error: {exc}")


if __name__ == "__main__":
    main()
