import os
import shutil
from contextlib import contextmanager
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Dict
from typing import Generator
from typing import List
from typing import Optional
from unittest.mock import Mock
from unittest.mock import patch

import pytest
from botocore.exceptions import ClientError

from quant_dev.dependencies.create_deps_layer import FileMaker
from quant_dev.dependencies.create_deps_layer import FORMAT
from quant_dev.dependencies.create_deps_layer import generate_and_upload_new_zip_file
from quant_dev.dependencies.create_deps_layer import get_new_aws_credentials
from quant_dev.builder import Builder


class TestGenerateAndUpload:
    def setup_method(self) -> None:
        self.bucket_name = "mybucket"
        self.s3_resource = Mock()
        self.context = Builder.build_random_string()
        self.requirements_file_path = Builder.build_random_string()
        self.file_maker = Mock()
        self.deps_file_name = Path(Builder.build_random_string())
        self.file_maker.get_dependencies_file_name.return_value = self.deps_file_name

    def test_generate_and_upload_new_zip_file_already_exists(self) -> None:
        generate_and_upload_new_zip_file(
            s3_resource=self.s3_resource,
            requirements_file_path_name=self.requirements_file_path,
            bucket_name=self.bucket_name,
            zip_file=None,
            file_maker=self.file_maker,
            docker_build=False,
        )
        self.file_maker.make_file.assert_not_called()
        self.s3_resource.Bucket().upload_file.assert_not_called()

    @pytest.mark.parametrize("docker_build", [False, True])
    def test_generate_and_upload_new_zip_file_file_not_exists(self, docker_build: bool) -> None:
        load_mocked = Mock()
        load_mocked.load.side_effect = ClientError({"Error": {"Code": "404"}}, "Mock")
        self.s3_resource.Object.return_value = load_mocked
        full_file_path = Path("/tmp", self.deps_file_name)
        self.file_maker.make_file.return_value = full_file_path
        zip_file = Builder.build_random_string()
        generate_and_upload_new_zip_file(
            s3_resource=self.s3_resource,
            requirements_file_path_name=self.requirements_file_path,
            bucket_name=self.bucket_name,
            zip_file=zip_file,
            file_maker=self.file_maker,
            docker_build=docker_build,
        )

        self.file_maker.make_file.assert_called_once()
        assert self.file_maker.make_file.call_args.kwargs["requirements_file_path_name"] == self.requirements_file_path
        assert self.file_maker.make_file.call_args.kwargs["zip_file"] == zip_file
        self.s3_resource.Bucket().upload_file.assert_called_once_with(
            Filename=str(full_file_path), Key=self.deps_file_name.name
        )


class TestGetNewAwsCredentials:
    def create_script(self, tmp_dir: str, content: str) -> Path:
        file_path = Path(tmp_dir, "fetch_credentials")
        with open(file_path, "w", encoding="utf-8") as script:
            script.writelines(
                [
                    "#!/usr/bin/env python3.11\n",
                    "\n",
                    "import json\n",
                    "import sys\n",
                    'if __name__ == "__main__":\n' f"    {content}",
                ]
            )
        os.chmod(file_path, 0o775)
        return file_path

    def test_success(self) -> None:
        with TemporaryDirectory() as tmp_dir:
            file_path = self.create_script(tmp_dir, 'print(json.dumps({"foo": "bar", "region": sys.argv[2]}))')
            credentials = get_new_aws_credentials(script=file_path, region_name="my_region")
            assert credentials == {"foo": "bar", "region": "my_region"}

    def test_fail(self) -> None:
        with TemporaryDirectory() as tmp_dir:
            file_path = self.create_script(tmp_dir, 'raise Exception("Unable to fetch credentials")')
            with pytest.raises(RuntimeError):
                get_new_aws_credentials(script=file_path, region_name="my_region")

    def test_invalid_output(self) -> None:
        with TemporaryDirectory() as tmp_dir:
            file_path = self.create_script(tmp_dir, 'print("Some other output")')
            with pytest.raises(RuntimeError):
                get_new_aws_credentials(script=file_path, region_name="my_region")

    def test_file_not_found(self) -> None:
        with TemporaryDirectory() as tmp_dir:
            file_path = Path(tmp_dir, "foo")
            with pytest.raises(FileNotFoundError):
                get_new_aws_credentials(script=file_path, region_name="my_region")


class TestFileMaker:
    @pytest.mark.parametrize("include_zip", [False, True])
    @pytest.mark.parametrize("docker_build", [False, True])
    def test_make_file_success(self, tmp_path: Path, include_zip: bool, docker_build: bool) -> None:
        file_maker = FileMaker(Builder.build_random_string())
        file_name = Builder.build_random_string() + FORMAT
        requirements = [Builder.build_random_string() for _ in range(3)]
        extra_content = {
            Builder.build_random_string(): [Builder.build_random_string() for _ in range(3)] for _ in range(3)
        }
        requirements_file_path_name = os.path.join(tmp_path, Builder.build_random_string())
        _create_requirements_file(requirements_file_path_name, requirements)
        zip_file = str(self.create_dummy_zip(tmp_path=tmp_path, contents=extra_content)) if include_zip else None
        install_dir = os.path.join(tmp_path, "install_dir")
        os.mkdir(install_dir)
        with self.mock_docker():
            with self.mock_pip():
                output_file = file_maker.make_file(
                    install_dir,
                    requirements_file_path_name=requirements_file_path_name,
                    file_name=Path(file_name),
                    zip_file=zip_file,
                    docker_build=docker_build,
                )

                assert os.path.exists(output_file)
                assert output_file.name == file_name
                extract_dir = os.path.join(install_dir, "unpackaged")
                shutil.unpack_archive(output_file, extract_dir)
                assert os.listdir(extract_dir) == ["python"]
                for requirement in requirements:
                    assert requirement in os.listdir(os.path.join(extract_dir, "python"))
                if include_zip:
                    for folder, files in extra_content.items():
                        assert folder in os.listdir(os.path.join(extract_dir, "python"))
                        assert all(file in os.listdir(os.path.join(extract_dir, "python", folder)) for file in files)

    def create_dummy_zip(self, tmp_path: Path, contents: Dict[str, List[str]]) -> Path:
        subdir = "python"
        (Path(tmp_path) / subdir).mkdir()
        for folder, files in contents.items():
            (Path(tmp_path) / subdir / folder).mkdir(parents=True)
            for file in files:
                (Path(tmp_path) / subdir / folder / file).touch()
        file_name = Builder.build_random_string()
        file = shutil.make_archive(
            base_name=os.path.join(tmp_path, file_name),
            format=FORMAT[1:],
            root_dir=tmp_path,
            base_dir=subdir,
        )
        return Path(file)

    @contextmanager
    def mock_docker(self) -> Generator[None, None, None]:
        def _mock_fetch_requirements_docker(
            tmp_dir: str,
            file_name: Path,
            requirements_file_path_name: str,
        ) -> str:
            base_dir = "python"
            os.mkdir(os.path.join(tmp_dir, base_dir))
            with open(requirements_file_path_name, "r", encoding="utf-8") as requirements:
                for requirement in requirements.readlines():
                    os.mkdir(os.path.join(tmp_dir, base_dir, requirement.strip()))
            return shutil.make_archive(
                base_name=os.path.join(tmp_dir, file_name.stem), format=FORMAT[1:], root_dir=tmp_dir, base_dir=base_dir
            )

        with patch.object(FileMaker, "_fetch_requirements_docker") as _fetch_requirements_docker:
            _fetch_requirements_docker.side_effect = _mock_fetch_requirements_docker
            yield

    @contextmanager
    def mock_pip(self) -> Generator[None, None, None]:
        def mock_pip_install(command: List[str]) -> int:
            assert command[0] == "install"
            target_index = command.index("--target")
            target = command[target_index + 1]
            os.mkdir(target)
            for index in range(1, target_index):
                os.mkdir(os.path.join(target, command[index]))
            return 0

        with patch("pip.main") as mock_pip:
            mock_pip.side_effect = mock_pip_install
            yield

    def test_make_file_version_conflict(self, tmp_path: Path) -> None:
        file_maker = FileMaker(Builder.build_random_string())
        requirements = ["asserts==0.11.0", "asserts==0.11.1"]
        requirements_file_path_name = os.path.join(tmp_path, Builder.build_random_string())
        _create_requirements_file(requirements_file_path_name, requirements)
        with pytest.raises(RuntimeError):
            # this test uses the "real" pip, which detects the version conflict before doing any work
            file_maker.make_file(
                tmp_path.as_posix(),
                requirements_file_path_name=requirements_file_path_name,
                file_name=Path(Builder.build_random_string()),
                zip_file=None,
                docker_build=False,
            )


class TestFileMakerFilename:
    @pytest.fixture(autouse=True, scope="function")
    def setup_method(self, tmp_path: Path) -> None:
        self.context = Builder.build_random_string()
        self.requirements = [Builder.build_random_string() for _ in range(3)]
        self.requirements_file_path_name = os.path.join(tmp_path, Builder.build_random_string())
        self.zip_file = Builder.build_random_string()
        _create_requirements_file(self.requirements_file_path_name, self.requirements)

    def test_get_file_name_starts_with_maker_name(self) -> None:
        assert (
            FileMaker(self.context)
            .get_dependencies_file_name(self.requirements_file_path_name, True, self.zip_file)
            .name.startswith(self.context + "-")
        )

    def test_get_file_name_reproducible(self) -> None:
        assert FileMaker(self.context).get_dependencies_file_name(
            self.requirements_file_path_name, True, self.zip_file
        ) == FileMaker(self.context).get_dependencies_file_name(self.requirements_file_path_name, True, self.zip_file)

    def test_get_file_name_other_requirements_different(self, tmp_path: Path) -> None:
        requirements = [Builder.build_random_string() for _ in range(3)]
        requirements_file_path_name = os.path.join(tmp_path, Builder.build_random_string())
        _create_requirements_file(requirements_file_path_name, requirements)

        file_maker = FileMaker(self.context)
        assert file_maker.get_dependencies_file_name(
            requirements_file_path_name=self.requirements_file_path_name,
            docker_build=True,
            zip_file=self.zip_file,
        ) != file_maker.get_dependencies_file_name(
            requirements_file_path_name=requirements_file_path_name, docker_build=True, zip_file=self.zip_file
        )

    @pytest.mark.parametrize("other_zip", [None, "foo"])
    def test_get_file_name_other_zip_file_different(self, tmp_path: Path, other_zip: Optional[str]) -> None:
        requirements = [Builder.build_random_string() for _ in range(3)]
        requirements_file_path_name = os.path.join(tmp_path, Builder.build_random_string())
        _create_requirements_file(requirements_file_path_name, requirements)

        file_maker = FileMaker(self.context)
        assert file_maker.get_dependencies_file_name(
            requirements_file_path_name=requirements_file_path_name,
            docker_build=True,
            zip_file=self.zip_file,
        ) != file_maker.get_dependencies_file_name(
            requirements_file_path_name=self.requirements_file_path_name, docker_build=True, zip_file=other_zip
        )

    def test_get_file_name_reordered_requirements_same(self, tmp_path: Path) -> None:
        requirements = self.requirements[::-1]
        requirements_file_path_name = os.path.join(tmp_path, Builder.build_random_string())
        _create_requirements_file(requirements_file_path_name, requirements)

        assert FileMaker(self.context).get_dependencies_file_name(
            requirements_file_path_name=self.requirements_file_path_name, docker_build=True, zip_file=self.zip_file
        ) == FileMaker(self.context).get_dependencies_file_name(
            requirements_file_path_name=requirements_file_path_name, docker_build=True, zip_file=self.zip_file
        )

    def test_get_file_name_suffix(self) -> None:
        assert (
            FileMaker(Builder.build_random_string())
            .get_dependencies_file_name(
                requirements_file_path_name=self.requirements_file_path_name, docker_build=True, zip_file=self.zip_file
            )
            .suffix
            == FORMAT
        )

    def test_get_file_name_works_with_empty_requirements(self, tmp_path: Path) -> None:
        requirements: List[str] = []
        requirements_file_path_name = os.path.join(tmp_path, Builder.build_random_string())
        _create_requirements_file(requirements_file_path_name, requirements)
        FileMaker(Builder.build_random_string()).get_dependencies_file_name(
            requirements_file_path_name=requirements_file_path_name, docker_build=True, zip_file=None
        )

    @pytest.mark.parametrize("build_docker", [False, True])
    def test_get_file_name_sensitive_to_build_docker(self, build_docker: bool) -> None:
        file_maker = FileMaker(self.context)
        assert (
            "-docker-"
            in file_maker.get_dependencies_file_name(
                requirements_file_path_name=self.requirements_file_path_name,
                docker_build=build_docker,
                zip_file=self.zip_file,
            ).name
        ) == build_docker


def _create_requirements_file(requirements_file_path_name: str, requirements: List[str]) -> None:
    with open(requirements_file_path_name, "w", encoding="utf-8") as file:
        for requirement in requirements:
            file.write(f"{requirement}\n")
