#!/usr/bin/env python3
import argparse
import hashlib
import json
import logging
import os
import pathlib
import shutil
import subprocess
import sys
import zipfile
from contextlib import suppress
from json import JSONDecodeError
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any, Dict, List, Optional

import boto3
import pip
import pkg_resources
from botocore.exceptions import ClientError

logging.basicConfig(stream=sys.stderr, level=os.environ.get("LOG_LEVEL", "INFO").upper())
LOG = logging.getLogger("create_deps_layer")
NOTSET = "notset"
FORMAT = ".zip"
MAX_RUN_TIME = 1200


def get_new_aws_credentials(script: Path, region_name: str) -> Dict[str, Any]:
    """Execute a script file to set new AWS Credentials."""
    if not os.path.exists(script):
        LOG.error("File to set new credentials does not exist!")
        raise FileNotFoundError(f"File not found at path {script}")
    with subprocess.Popen(["/bin/sh", "-c", f"{script} --region $0", region_name], stdout=subprocess.PIPE) as process:
        std_output = process.communicate()[0]
        if process.returncode != 0:
            raise RuntimeError(std_output)
        with suppress(JSONDecodeError):
            std_json = json.loads(std_output)
            if isinstance(std_json, dict):
                return std_json

        raise RuntimeError("Please write only the new credentials to the stdout.")


def file_exists_on_aws_s3_client(s3_resource: Any, bucket_name: str, key: str) -> bool:
    """Check for a file already existing in the s3 bucket."""
    try:  # pylint: disable=W0101
        s3_resource.Object(bucket_name, key).load()
        return True
    except ClientError as client_error_exception:
        if client_error_exception.response["Error"]["Code"] != "404":
            raise
    return False


class FileMaker:
    """Builds the dependencies file."""

    def __init__(self, context: str) -> None:
        self._context = context

    def _install_locally(self, installation_path: str, args: List[str]) -> None:
        """Run a local python installation using pip."""
        command = ["install"] + args + ["--target", installation_path, "--quiet"]
        status_code = pip.main(command)
        if status_code != 0:
            raise RuntimeError(
                f"Failed to install the required dependencies. Check for version conflicts! "
                f"The issued command was 'pip {' '.join(command)}'"
            )

    def get_dependencies_file_name(
        self, requirements_file_path_name: str, docker_build: bool, zip_file: Optional[str]
    ) -> Path:
        """Construct the name of the dependencies file to be created."""
        requirements = gather_requirements(requirements_file_path_name)
        requirements_bytes = ("\n".join(sorted(requirements)) + str(zip_file)).encode("utf-8")
        requirements_hash_sum = hashlib.sha256(requirements_bytes).hexdigest()
        is_dockerized = "docker-" if docker_build else ""
        return Path(f"{self._context}-deps-layer-{is_dockerized}{requirements_hash_sum}").with_suffix(FORMAT)

    @classmethod
    def _merge_zip_files(cls, zip_file_base: str, zip_file_add: str) -> None:
        with zipfile.ZipFile(zip_file_base, "a") as base:
            with zipfile.ZipFile(zip_file_add, "r") as add:
                for item in add.namelist():
                    if item not in base.namelist():
                        with add.open(item) as item_object:
                            base.writestr(item, item_object.read())

    @classmethod
    def _fetch_requirements_docker(cls, tmp_dir: str, file_name: Path, requirements_file_path_name: str) -> str:
        lib_path = str(pathlib.Path(__file__).parent.resolve())
        requirements_path = str(pathlib.Path(requirements_file_path_name).parent.resolve())
        # requirements_filter not yet required but must be used when dependencies are tagged
        requirements_filter = ""
        additional_params = "--ssh default" if os.getenv("SSH_AUTH_SOCK") else ""
        try:
            # use proxy definitions defined in ~/docker/config.json
            docker_build_command = (
                f"docker build --progress=plain --pull {requirements_path} "
                f'-f "{lib_path}/Dockerfile" --build-arg "requirements_filter={requirements_filter}" '
                f'-t {file_name.name} --memory "512m" --platform "linux/x86_64" {additional_params}'
            )
            subprocess.check_output(
                docker_build_command, shell=True, stderr=subprocess.STDOUT, text=True, timeout=MAX_RUN_TIME
            )
            docker_run_command = (
                f'docker run --network="none" --rm -v "{tmp_dir}:/mnt" "{file_name.name}"'  # noqa: B028
            )
            subprocess.check_output(
                docker_run_command, shell=True, stderr=subprocess.STDOUT, text=True, timeout=MAX_RUN_TIME
            )
        except subprocess.CalledProcessError as error:
            LOG.exception(error.output)
            LOG.exception(error.stderr)
            raise
        output_file = os.path.join(tmp_dir, file_name.name)
        shutil.move(os.path.join(tmp_dir, "dependencies.zip"), output_file)
        return output_file

    def _fetch_requirements_locally(self, tmp_dir: str, file_name: Path, requirements_file_path_name: str) -> str:
        base_dir = "python"
        installation_python_path = os.path.join(tmp_dir, base_dir)
        requirements = gather_requirements(requirements_file_path_name)
        orjson_dependency = [line for line in requirements if line.startswith("orjson==")]
        # orjson dependency requires special flags
        if orjson_dependency:
            self._install_locally(  # noqa: FKA01
                installation_python_path,
                [
                    "--platform",
                    "manylinux_2_24_x86_64",
                    "--only-binary=:all:",
                    orjson_dependency[0],
                ],
            )
        self._install_locally(installation_python_path, requirements)
        return shutil.make_archive(
            base_name=os.path.join(tmp_dir, file_name.stem), format=FORMAT[1:], root_dir=tmp_dir, base_dir=base_dir
        )

    def make_file(
        self,
        tmp_dir: str,
        requirements_file_path_name: str,
        zip_file: Optional[str],
        file_name: Path,
        docker_build: bool,
    ) -> Path:
        """Create a zip package with the specified name with all required dependencies."""
        if docker_build:
            output_file = self._fetch_requirements_docker(tmp_dir, file_name, requirements_file_path_name)
        else:
            output_file = self._fetch_requirements_locally(tmp_dir, file_name, requirements_file_path_name)
        if zip_file:
            self._merge_zip_files(output_file, zip_file)
        return Path(output_file)


def gather_requirements(
    requirements_file_path_name: str,
) -> List[str]:
    """Read and parse requirements from the requirements file."""
    with open(requirements_file_path_name, "r", encoding="utf-8") as requirements_file:
        return [str(req) for req in pkg_resources.parse_requirements(requirements_file)]


def generate_and_upload_new_zip_file(
    s3_resource: Any,
    requirements_file_path_name: str,
    bucket_name: str,
    zip_file: Optional[str],
    file_maker: FileMaker,
    docker_build: bool,
) -> str:
    """Check if zip has to be built and if required trigger build process and upload it to a S3 bucket."""
    file_name = file_maker.get_dependencies_file_name(
        requirements_file_path_name=requirements_file_path_name, docker_build=docker_build, zip_file=zip_file
    )
    if file_exists_on_aws_s3_client(s3_resource=s3_resource, bucket_name=bucket_name, key=file_name.name):
        LOG.info("File already exists on s3_client")
    else:
        with TemporaryDirectory() as tmp_dir:
            file_path = file_maker.make_file(
                tmp_dir=tmp_dir,
                requirements_file_path_name=requirements_file_path_name,
                file_name=file_name,
                zip_file=zip_file,
                docker_build=docker_build,
            )

            s3_resource.Bucket(bucket_name).upload_file(Filename=str(file_path), Key=file_name.name)

    return json.dumps({"bucket": bucket_name, "key": file_name.name})


def main() -> None:
    """Create and upload deps-layer package."""
    parser = argparse.ArgumentParser(description="Takes care of parsing the arguments for creating the depth layers")
    parser.add_argument("--context", type=str, required=True, help="Context argument")
    parser.add_argument("--requirements-file-path", type=str, required=True, help="Path to the requirements file")
    parser.add_argument("--region", type=str, required=True, help="Region for which the deps layers should be created")
    parser.add_argument(
        "--bucket-name",
        type=str,
        required=True,
        help="bucket-name in which the deps-layer zip shall be saved",
    )
    parser.add_argument(
        "--fetch-custom-credentials",
        type=str,
        required=False,
        help="Optional script file with full path. Only required if you want to overwrite the AWS Credentials from "
        "the environment",
    )
    parser.add_argument(
        "--include-zip",
        type=str,
        required=False,
        help="Path to local zip file containing code that should be included in the layer. "
        "It is assumed that files with the same name have the same contents.",
    )
    parser.add_argument(
        "--docker-build",
        required=False,
        action="store_true",
        help="If true, this will use Docker to build the dependencies layer. Set to true when having binary "
        "dependencies.",
    )

    args = parser.parse_args()
    region = args.region
    fetch_custom_credentials = (
        Path(args.fetch_custom_credentials) if args.fetch_custom_credentials not in {None, "", NOTSET} else None
    )
    credentials = {}
    if fetch_custom_credentials:
        credentials = get_new_aws_credentials(script=fetch_custom_credentials, region_name=region)

    include_zip = args.include_zip if args.include_zip not in {None, "", NOTSET} else None

    print(  # noqa: T201
        generate_and_upload_new_zip_file(
            s3_resource=boto3.resource("s3", region_name=region, **credentials),
            requirements_file_path_name=args.requirements_file_path,
            bucket_name=args.bucket_name,
            zip_file=include_zip,
            file_maker=FileMaker(args.context),
            docker_build=args.docker_build,
        )
    )


if __name__ == "__main__":
    main()
