import boto3
from botocore.exceptions import BotoCoreError, ClientError
from mypy_boto3_s3.client import S3Client
from mypy_boto3_s3.type_defs import ListBucketsOutputTypeDef

from s3_app.logger_config import setup_logger

logger = setup_logger()


def main() -> None:
    try:
        s3 = boto3.client("s3")
    except BotoCoreError:
        logger.error(
            "There is an issue preparing to connect to AWS (please check your credentials or settings)."
        )
        return

    bucket_name_list = get_bucket_name_list(get_buckets(s3))
    check_bucket_exists(s3, bucket_name_list)
    print_bucket_names(bucket_name_list)


def get_buckets(s3: S3Client) -> ListBucketsOutputTypeDef:
    try:
        response = s3.list_buckets()
    except ClientError as e:
        error_message(e)
        return {"Buckets": []}

    return response if response.get("Buckets") else {"Buckets": []}


def get_bucket_name_list(buckets: ListBucketsOutputTypeDef) -> list[str]:
    return [bucket["Name"] for bucket in buckets.get("Buckets", [])]


def check_bucket_exists(s3: S3Client, bucket_names: list[str]) -> None:
    for bucket_name in bucket_names:
        try:
            s3.head_bucket(Bucket=bucket_name)
            logger.info(f"Bucket {bucket_name} exists.")
        except ClientError as e:
            code = e.response["Error"]["Code"]

            if code == "404":
                logger.error(f"Bucket {bucket_name} does not exist.")
            else:
                # Other errors
                logger.info(
                    f"Bucket {bucket_name} exists but cannot be accessed ({code})"
                )
            error_message(e)


def print_bucket_names(bucket_names: list[str]) -> None:
    for name in bucket_names:
        logger.info(name)


def error_message(e: ClientError) -> None:
    logger.error(
        f"[AWS ERROR] {e.response['Error']['Code']} : {e.response['Error']['Message']}"
    )


if __name__ == "__main__":
    main()
