import argparse
import hashlib
import json
import shutil
import tempfile
from pathlib import Path
from zipfile import ZipFile


def compute_sha256(file_paths):
    """Compute a deterministic SHA-256 hash from the contents of multiple files."""
    hashes = []
    for file_path in sorted(file_paths):
        with open(file_path, "rb") as f:
            file_hash = hashlib.sha256(f.read()).hexdigest()
            hashes.append(file_hash)

    combined_hash = hashlib.sha256("".join(hashes).encode()).hexdigest()
    return combined_hash


def ignore_patterns(_, names):
    """Ignore Terraform state files, hidden files, and temporary files."""
    ignored = {
        name for name in names if name.endswith(".tfstate") or name.endswith(".tfstate.backup") or name.startswith(".")
    }
    return ignored


def bundle_lambda(task, filename, code_path, config_path=None):
    """Bundle Python code for a Lambda deployment package or layer."""
    artifacts_dir = Path("/tmp/artifacts")
    artifacts_dir.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory() as build_dir:
        build_path = Path(build_dir)

        if task == "layer":
            lambda_layer_path = build_path / "python"
            shutil.copytree(code_path, lambda_layer_path, dirs_exist_ok=True, ignore=ignore_patterns)
        elif task == "package":
            shutil.copytree(code_path, build_path, dirs_exist_ok=True, ignore=ignore_patterns)
            if config_path:
                shutil.copy(config_path, build_path / Path(config_path).name)

        # Remove test files and Python cache
        for pattern in ["*_test.py", "*.pyc"]:
            for file in build_path.rglob(pattern):
                file.unlink()

        # Create ZIP file
        zip_path = build_path / "output.zip"
        with ZipFile(zip_path, "w") as zipf:
            for file in build_path.rglob("*"):
                zipf.write(file, file.relative_to(build_path))

        # Compute hash for deterministic naming
        file_hash = compute_sha256([f for f in build_path.rglob("*") if f.is_file()])
        final_filename = f"{filename}-{file_hash}.zip"
        final_zip_path = artifacts_dir / final_filename
        shutil.move(zip_path, final_zip_path)

        # Return JSON output (compatible with Terraform `external` test_data source)
        print(json.dumps({"file": str(final_zip_path)}))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Bundle Python code for AWS Lambda")
    parser.add_argument("--task", choices=["layer", "package"], help="Specify either --layer or --package")
    parser.add_argument("--filename", help="Base filename for output ZIP")
    parser.add_argument("--code_path", help="Path to the source code")
    parser.add_argument("--config_path", nargs="?", default=None, help="Optional config file for --package")

    args = parser.parse_args()

    # Resolve absolute paths
    args.code_path = str(Path(args.code_path).resolve())
    if args.config_path:
        args.config_path = str(Path(args.config_path).resolve())

    bundle_lambda(args.task, args.filename, args.code_path, args.config_path)
