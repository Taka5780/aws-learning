from unittest.mock import patch

import pytest

from ec2_app.ec2ctl import determine_action, main


@pytest.mark.parametrize(
    "state, expected",
    [
        ("running", "stop"),
        ("stopped", "start"),
        ("terminated", None),
        ("pending", None),
    ],
)
def test_determine_action(state, expected):
    assert determine_action(state) == expected


def test_main_no_instances(caplog):
    with patch("ec2_app.ec2ctl.Ec2Service") as MockService:
        mock_svc = MockService.return_value
        mock_svc.status = "ok"
        mock_svc.get_instance.return_value = []  # 空のリストを返す

        main()

        assert "No EC2 instances found." in caplog.text


def test_main_user_cancel(caplog):
    with patch("ec2_app.ec2ctl.Ec2Service") as MockService:
        mock_svc = MockService.return_value
        mock_svc.status = "ok"
        mock_svc.get_instance.return_value = [
            {"name": "TestSrv", "instance_id": "i-123", "state": "running"}
        ]

        with patch("builtins.input", return_value=""):
            main()
            assert "No EC2 instances found." not in caplog.text


def test_main_execute_success(caplog):
    with patch("ec2_app.ec2ctl.Ec2Service") as MockService:
        mock_svc = MockService.return_value
        mock_svc.status = "ok"
        mock_svc.get_instance.return_value = [
            {"name": "TestSrv", "instance_id": "i-123", "state": "running"}
        ]
        mock_svc.instance_stop.return_value = (True, None)

        with patch("builtins.input", side_effect=["1", "y"]):
            main()

            assert "Successfully sent stop command." in caplog.text
            mock_svc.instance_stop.assert_called_once_with("i-123")
