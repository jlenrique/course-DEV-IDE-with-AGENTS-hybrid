# Local Binary Paths

This file records local executable locations that are easy to miss during production runs.

## ffmpeg

- Canonical project-local path (repo-root-relative):
  `.venv\Lib\site-packages\imageio_ffmpeg\binaries\ffmpeg-win-x86_64-v7.1.exe`
- Recommended PowerShell pattern (from the repo root):
  `& '.\.venv\Lib\site-packages\imageio_ffmpeg\binaries\ffmpeg-win-x86_64-v7.1.exe' -version`
- Repo helper:
  `scripts/utilities/ffmpeg.py` resolves this binary automatically before falling back to `PATH`.
- Reason:
  `ffmpeg` is bundled through `imageio_ffmpeg` inside the project virtual environment, so `where.exe ffmpeg` will not find it unless that directory is added to `PATH`.
