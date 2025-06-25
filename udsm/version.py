try:
    from .paths import VERSION_PATH
except ImportError:
    # Import fallback should stay here because the bump_version.py scripts
    # Can't handle the relative import
    from paths import VERSION_PATH  # type: ignore[no-redef]

version_string = VERSION_PATH.read_text(encoding="utf-8").strip()
__version__: tuple[int, ...] = tuple(map(int, version_string.split(".")))
