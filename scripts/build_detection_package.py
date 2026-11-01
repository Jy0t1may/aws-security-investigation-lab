from pathlib import Path
from zipfile import ZipFile, ZipInfo, ZIP_DEFLATED

root = Path(__file__).resolve().parents[1]
source = root / "cloud/detection_runner"
files = {path.name: path for path in source.glob("*.py")}
files["detection.sql"] = (
    root / "queries/detections/AWSLAB-DET-001-windowed.sql"
)

required = {"handler.py", "publication.py", "detection.sql"}
if not required.issubset(files):
    raise SystemExit("STOP: required package files are missing.")

destination = root / "infrastructure/build/detection-runner.zip"
destination.parent.mkdir(parents=True, exist_ok=True)

with ZipFile(destination, "w") as archive:
    for name, path in sorted(files.items()):
        info = ZipInfo(name, date_time=(2020, 1, 1, 0, 0, 0))
        info.compress_type = ZIP_DEFLATED
        info.external_attr = 0o644 << 16
        archive.writestr(info, path.read_bytes())

print(f"Built {destination.name}: {destination.stat().st_size} bytes")
