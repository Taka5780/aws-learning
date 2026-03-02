import boto3
from moto import mock_aws

from ec2_app.ec2_service import Ec2Service


@mock_aws
class TestEc2Service:
    def setup_method(self, method):
        self.ec2_resource = boto3.resource("ec2", region_name="us-east-1")
        self.instance = self.ec2_resource.create_instances(
            ImageId="ami-12345678",
            MinCount=1,
            MaxCount=1,
            TagSpecifications=[
                {
                    "ResourceType": "instance",
                    "Tags": [{"Key": "Name", "Value": "TestInstance"}],
                }
            ],
        )[0]
        self.service = Ec2Service(region_name="us-east-1")

    def test_get_instance_returns_correct_data(self):
        instances = self.service.get_instance()

        assert len(instances) == 1
        assert instances[0]["name"] == "TestInstance"
        assert instances[0]["instance_id"] == self.instance.id

    def test_instance_stop_success(self):
        success, error = self.service.instance_stop(self.instance.id)

        assert success is True
        self.instance.reload()
        state_name = self.instance.state.get("Name")
        assert state_name in ["stopping", "stopped"]
