from typing import Optional

from ec2_app.ec2_service import Ec2Service
from logger_config import setup_logger

logger = setup_logger()


def main() -> None:
    service = Ec2Service()
    if service.status == "error":
        logger.error("AWS connection issue. Check credentials.")
        return

    instances = service.get_instance()
    if not instances:
        logger.warning("No EC2 instances found.")
        return

    display_instance_table(instances)

    selected_idx = get_user_choice(len(instances))
    if selected_idx is None:
        return

    target = instances[selected_idx]
    action = determine_action(target["state"])

    if not action:
        print(f"No action available for state: {target['state']}")
        return

    confirm = input(f">>> Target: {target['name']} / Action: {action.upper()}? (y/n): ")
    if confirm.lower() == "y":
        execute_func = (
            service.instance_start if action == "start" else service.instance_stop
        )
        success, error_code = execute_func(target["instance_id"])

        if success:
            logger.info(f"Successfully sent {action} command.")
        else:
            logger.error(f"Failed to {action}. Error: {error_code}")


def determine_action(current_state: str) -> Optional[str]:
    logic_map = {"running": "stop", "stopped": "start"}
    return logic_map.get(current_state)


def display_instance_table(instances: list[dict[str, str]]) -> None:
    print(f"\n{'No.':<3} | {'Name':<25} | {'Instance ID':<20} | {'Status':<10}")
    print("-" * 65)
    for i, inst in enumerate(instances, 1):
        print(
            f"{i:<3} | {inst['name']:<25} | {inst['instance_id']:<20} | {inst['state']:<10}"
        )


def get_user_choice(max_val: int) -> Optional[int]:
    try:
        user_input = input("\nEnter the number to operate (Press Enter to cancel): ")
        if not user_input:
            return None

        idx = int(user_input) - 1
        if 0 <= idx < max_val:
            return idx
        print("Invalid number selected.")
    except ValueError:
        print("Please enter a valid number.")
    return None


def handle_result(success: bool, error_code: str | None, action_name: str) -> None:
    if success:
        logger.info(f"The {action_name} command was successfully sent.")
    else:
        logger.error(f"The {action_name} command failed. Error code: {error_code}")


if __name__ == "__main__":
    main()
