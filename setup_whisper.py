from whisper import _download, _MODELS
import os

DOWNLOAD_DIR = os.path.join(os.path.expanduser("~"), ".cache")
_download(_MODELS["medium.en"], DOWNLOAD_DIR, False)