import hashlib, json, datetime, subprocess, platform, importlib.metadata
from pathlib import Path
def checksum(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1024*1024), b""): h.update(b)
    return h.hexdigest()
def save(path, value):
    p = Path(path); p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(value, indent=2, allow_nan=False) + "\n")
def manifest(config_path, config, metrics):
    from .features import FEATURES
    p = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True)
    return dict(run_id=datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%S%fZ"), timestamp=datetime.datetime.now(datetime.timezone.utc).isoformat(), evidence_state="REPRODUCED", git_commit=p.stdout.strip() if p.returncode==0 else None, data_hash=checksum(config["data"]), config_hash=checksum(config_path), config_path=Path(config_path).name, data_path=config.get("data_reference","authorized-input"), seed=config["seed"], feature_list=FEATURES, split_method="sorted scenario IDs, two-stage Spark randomSplit 70/30 then 50/50; stable local partitioning; differs from historical unspecified partition layout", metrics=metrics, environment=dict(python=platform.python_version(), platform=platform.platform(), pyspark=importlib.metadata.version("pyspark")))

def directory_checksum(path):
    h=hashlib.sha256();root=Path(path)
    for p in sorted(root.rglob('*')):
        if p.is_file(): h.update(str(p.relative_to(root)).encode());h.update(checksum(p).encode())
    return h.hexdigest()
