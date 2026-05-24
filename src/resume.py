from pathlib import Path


SUPPORTED_RESUME_EXTENSIONS = {".txt", ".md", ".markdown"}


def read_resume_file(path: str) -> str:
    """Read a local resume file as plain text."""
    resume_path = Path(path).expanduser().resolve()

    if not resume_path.exists():
        raise FileNotFoundError(f"Resume file not found: {resume_path}")

    if resume_path.suffix.lower() not in SUPPORTED_RESUME_EXTENSIONS:
        supported = ", ".join(sorted(SUPPORTED_RESUME_EXTENSIONS))
        raise ValueError(f"Unsupported resume file type. Supported types: {supported}")

    return resume_path.read_text(encoding="utf-8").strip()
