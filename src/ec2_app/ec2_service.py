from typing import Any, Optional

import boto3
from botocore.exceptions import BotoCoreError, ClientError
from mypy_boto3_ec2 import EC2Client


class Ec2Service:
    ec2: EC2Client
    status: str

    def __init__(self, region_name: Optional[str] = None, client: Any = None) -> None:
        if client:
            self.ec2 = client
            self.status = "connected"
        else:
            try:
                self.ec2 = boto3.client("ec2", region_name=region_name)
                self.status = "connected"
            except BotoCoreError:
                self.status = "error"

    def get_instance(self) -> list[dict[str, str]]:
        instance_list: list[dict[str, str]] = []
        try:
            instances_info = self.ec2.describe_instances()
            for reservation in instances_info.get("Reservations", []):
                for instance in reservation.get("Instances", []):
                    instance_id = instance.get("InstanceId", "Unknown")
                    state_dict = instance.get("State", {})
                    state_name = state_dict.get("Name", "unknown")

                    name = next(
                        (
                            tag.get("Value", "")
                            for tag in instance.get("Tags", [])
                            if tag.get("Key") == "Name"
                        ),
                        "No Name",
                    )
                    instance_list.append(
                        {
                            "instance_id": instance_id,
                            "state": state_name,
                            "name": name,
                        }
                    )
            return instance_list
        except ClientError as e:
            self.handle_error(e)
            return []

    def instance_start(self, instance_id: str) -> tuple[bool, Optional[str]]:
        try:
            self.ec2.start_instances(InstanceIds=[instance_id])
            return True, None
        except ClientError as e:
            error_code = self.handle_error(e)
            return False, error_code

    def instance_stop(self, instance_id: str) -> tuple[bool, Optional[str]]:
        try:
            self.ec2.stop_instances(InstanceIds=[instance_id])
            return True, None
        except ClientError as e:
            error_code = self.handle_error(e)
            return False, error_code

    def handle_error(self, error) -> Optional[str]:
        return error.response["Error"]["Code"]
