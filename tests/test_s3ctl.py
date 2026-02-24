from botocore.exceptions import ClientError

from s3_app.s3ctl import (
    check_bucket_exists,
    error_message,
    get_bucket_name_list,
    get_buckets,
    print_bucket_names,
)


# Simple S3 dummy class for mocking
class DummyS3:
    def __init__(self, list_buckets_result=None, head_results=None):
        self._list_buckets_result = list_buckets_result or {"Buckets": []}
        self._head_results = head_results or {}

    def list_buckets(self):
        if isinstance(self._list_buckets_result, Exception):
            raise self._list_buckets_result
        return self._list_buckets_result

    def head_bucket(self, Bucket):
        code, msg = self._head_results.get(Bucket, ("200", "OK"))

        if code != "200":
            raise ClientError({"Error": {"Code": code, "Message": msg}}, "HeadBucket")
        return {}


# get_bucket_name_list
def test_get_bucket_name_list_normal():
    buckets = {"Buckets": [{"Name": "a"}, {"Name": "b"}]}
    assert get_bucket_name_list(buckets) == ["a", "b"]


def test_get_bucket_name_list_empty():
    buckets = {"Buckets": []}
    assert get_bucket_name_list(buckets) == []


# get_buckets
def test_get_buckets_normal():
    s3 = DummyS3({"Buckets": [{"Name": "x"}]})
    result = get_buckets(s3)
    assert result["Buckets"][0]["Name"] == "x"


def test_get_buckets_empty():
    s3 = DummyS3({"Buckets": []})
    result = get_buckets(s3)
    assert result == {"Buckets": []}


def test_get_buckets_client_error(caplog):
    error = ClientError(
        {"Error": {"Code": "403", "Message": "Forbidden"}}, "ListBuckets"
    )
    s3 = DummyS3(error)
    result = get_buckets(s3)
    assert result == {"Buckets": []}
    assert "[AWS ERROR]" in caplog.text


# check_bucket_exists
def test_check_bucket_exists_full(caplog):
    s3 = DummyS3(
        head_results={
            "ok": ("200", "OK"),
            "forbidden": ("403", "Forbidden"),
            "notfound": ("404", "NotFound"),
        }
    )

    check_bucket_exists(s3, ["ok", "forbidden", "notfound"])

    assert "Bucket ok exists." in caplog.text
    assert "Bucket forbidden exists but cannot be accessed (403)" in caplog.text
    assert "Bucket notfound does not exist." in caplog.text


# print_bucket_names
def test_print_bucket_names(caplog):
    print_bucket_names(["a", "b"])
    assert "a" in caplog.text
    assert "b" in caplog.text


# error_message
def test_error_message(caplog):
    err = ClientError({"Error": {"Code": "403", "Message": "Forbidden"}}, "HeadBucket")
    error_message(err)
    assert "[AWS ERROR] 403 : Forbidden" in caplog.text
