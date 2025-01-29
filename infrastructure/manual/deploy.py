import argparse
import os
import sys

_BUCKET_NAME = "tf-state-bucket-658616507787"
_REGION = "eu-west-1"


def parse_arguments() -> argparse.Namespace:
    argument_parser = argparse.ArgumentParser()

    argument_parser.add_argument(
        "--environment",
        type=str,
        required=True,
        help="Name of the deployment (dev, prod)",
    )
    argument_parser.add_argument(
        "--command",
        type=str,
        required=True,
        help="Command to execute (plan, apply, destroy)",
    )

    return argument_parser.parse_args()


def main() -> None:
    arguments = parse_arguments()

    assert arguments.environment in ["dev", "prod"], "Invalid environment"
    assert arguments.command in ["plan", "apply", "destroy"], "Invalid command"

    # Build the commands
    commands = [
        f"cd {os.path.join(os.path.dirname(__file__))}",
        # Terraform init with a remote S3 backend:
        " ".join(
            [
                "terraform init",
                "-reconfigure",
                f'-backend-config="bucket={_BUCKET_NAME}"',
                f'-backend-config="key=terraform_{arguments.environment}.tfstate"',
                f'-backend-config="region={_REGION}"',
            ]
        ),
        # Use environment-specific tfvars and state file
        (
            f"terraform {arguments.command}"
            f" -var-file=tf_{arguments.environment}.tfvars"
            f" -state=terraform_{arguments.environment}.tfstate"
        ),
    ]

    # Chain commands with &&
    full_command = " && ".join(commands)
    exit_code = os.system(full_command)

    # Pass Terraform's exit code through
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
