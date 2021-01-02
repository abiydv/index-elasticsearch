import mock
import moto
import boto3
import requests

from .context import src
from src.config import REGION

"""
reusable mock_response method

"""


def mock_response(
    status=200, content="CONTENT", text="TEXT", json_data=None, raise_for_status=None
):
    mock_resp = mock.Mock()
    mock_resp.raise_for_status = mock.Mock()

    if raise_for_status:
        mock_resp.raise_for_status.side_effect = raise_for_status

    mock_resp.status_code = status
    mock_resp.content = content
    mock_resp.text = text

    if json_data:
        mock_resp.json = mock.Mock(return_value=json_data)

    return mock_resp


def test_bad_request():
    mock_resp = {
        "statusCode": 400,
        "headers": {"content-type": "application/json"},
        "body": "Bad Request",
    }
    assert src.helper.bad_request() == mock_resp


def test_accepted_request():
    mock_body = "valid_request"
    mock_resp = {
        "statusCode": 200,
        "headers": {"content-type": "application/json"},
        "body": mock_body,
    }
    assert src.helper.accepted_request(mock_body) == mock_resp


"""
s3_get_object tests

"""


# test if no bucket exists
@moto.mock_s3
def test_s3_client_get_object_none_no_bucket():
    bucket = "bucket"
    key = "path/key"
    s3_data = src.helper.s3_get_object(bucket, key)
    assert s3_data is None


# test if bucket exists but no key exists
@moto.mock_s3
def test_s3_client_get_object_none_no_key():
    bucket = "bucket"
    key = "path/key"
    conn = boto3.client("s3", region_name=REGION)
    conn.create_bucket(Bucket=bucket)

    s3_data = src.helper.s3_get_object(bucket, key)
    assert s3_data is None


# test if bucket and key exists
@moto.mock_s3
def test_s3_client_get_object_success():
    bucket = "bucket"
    key = "path/key"
    body = "random_value"
    conn = boto3.client("s3", region_name=REGION)
    conn.create_bucket(Bucket=bucket)
    conn.put_object(Bucket=bucket, Key=key, Body=body)

    s3_data = src.helper.s3_get_object(bucket, key)
    assert s3_data == body


"""
post_request tests

"""


@mock.patch("src.helper.requests.post")
def test_post_request_fail_connection(mock_request):

    mock_request.return_value = mock_response(
        status=0, raise_for_status=requests.exceptions.ConnectionError("connection")
    )
    assert src.helper.post_request(url="someurl", body="", headers="") is None


@mock.patch("src.helper.requests.post")
def test_post_request_fail_timeout(mock_request):
    mock_request.return_value = mock_response(
        status=0, raise_for_status=requests.exceptions.Timeout("timeout")
    )
    assert src.helper.post_request(url="someurl", body="", headers="") is None


@mock.patch("src.helper.requests.post")
def test_post_request_fail_random(mock_request):
    mock_request.return_value = mock_response(
        status=0, raise_for_status=Exception("random")
    )
    assert src.helper.post_request(url="someurl", body="", headers="") is None


@mock.patch("src.helper.requests.post")
def test_post_request_fail_404(mock_request):
    mock_request.return_value = mock_response(
        status=404, raise_for_status=requests.exceptions.HTTPError("404")
    )
    assert src.helper.post_request(url="someurl", body="", headers="") is None


@mock.patch("src.helper.requests.post")
def test_post_request_fail_500(mock_request):
    mock_request.return_value = mock_response(
        status=500, raise_for_status=requests.exceptions.HTTPError("500")
    )
    assert src.helper.post_request(url="someurl", body="", headers="") is None


@mock.patch("src.helper.requests.post")
def test_post_request_success_201(mock_request):
    mock_request.return_value = mock_response(status=201, content="updated")
    r = src.helper.post_request(url="someurl", body="", headers="")
    assert r.status_code == 201
    assert r.content == "updated"


"""
head_request tests

"""


@mock.patch("src.helper.requests.head")
def test_head_request_fail_connection(mock_request):

    mock_request.return_value = mock_response(
        status=0, raise_for_status=requests.exceptions.ConnectionError("connection")
    )
    assert src.helper.head_request(url="someurl", headers="") is None


@mock.patch("src.helper.requests.head")
def test_head_request_fail_timeout(mock_request):
    mock_request.return_value = mock_response(
        status=0, raise_for_status=requests.exceptions.Timeout("timeout")
    )
    assert src.helper.head_request(url="someurl", headers="") is None


@mock.patch("src.helper.requests.head")
def test_head_request_fail_random(mock_request):
    mock_request.return_value = mock_response(
        status=0, raise_for_status=Exception("random")
    )
    assert src.helper.head_request(url="someurl", headers="") is None


@mock.patch("src.helper.requests.head")
def test_head_request_fail_404(mock_request):
    mock_request.return_value = mock_response(
        status=404, raise_for_status=requests.exceptions.HTTPError("404")
    )
    assert src.helper.head_request(url="someurl", headers="") is None


@mock.patch("src.helper.requests.head")
def test_head_request_fail_500(mock_request):
    mock_request.return_value = mock_response(
        status=500, raise_for_status=requests.exceptions.HTTPError("500")
    )
    assert src.helper.head_request(url="someurl", headers="") is None


@mock.patch("src.helper.requests.head")
def test_head_request_success_200(mock_request):
    mock_request.return_value = mock_response(status=200, content="exists!")
    r = src.helper.head_request(url="someurl", headers="")
    assert r.status_code == 200
    assert r.content == "exists!"


"""
put_request tests

"""


@mock.patch("src.helper.requests.put")
def test_put_request_fail_connection(mock_request):

    mock_request.return_value = mock_response(
        status=0, raise_for_status=requests.exceptions.ConnectionError("connection")
    )
    assert src.helper.put_request(url="someurl", headers="") is None


@mock.patch("src.helper.requests.put")
def test_put_request_fail_timeout(mock_request):
    mock_request.return_value = mock_response(
        status=0, raise_for_status=requests.exceptions.Timeout("timeout")
    )
    assert src.helper.put_request(url="someurl", headers="") is None


@mock.patch("src.helper.requests.put")
def test_put_request_fail_random(mock_request):
    mock_request.return_value = mock_response(
        status=0, raise_for_status=Exception("random")
    )
    assert src.helper.put_request(url="someurl", headers="") is None


@mock.patch("src.helper.requests.put")
def test_put_request_fail_404(mock_request):
    mock_request.return_value = mock_response(
        status=404, raise_for_status=requests.exceptions.HTTPError("404")
    )
    assert src.helper.put_request(url="someurl", headers="") is None


@mock.patch("src.helper.requests.put")
def test_put_request_fail_500(mock_request):
    mock_request.return_value = mock_response(
        status=500, raise_for_status=requests.exceptions.HTTPError("500")
    )
    assert src.helper.put_request(url="someurl", headers="") is None


@mock.patch("src.helper.requests.put")
def test_put_request_success_200(mock_request):
    mock_request.return_value = mock_response(status=201, content="updated")
    r = src.helper.put_request(url="someurl", headers="")
    assert r.status_code == 201
    assert r.content == "updated"


@mock.patch("src.helper.requests.put")
def test_put_request_success_200_json(mock_request):
    mock_request.return_value = mock_response(status=200, text='{"json":"updated"}')
    r = src.helper.put_request(url="someurl", headers="")
    assert r.status_code == 200
    assert r.text == '{"json":"updated"}'
