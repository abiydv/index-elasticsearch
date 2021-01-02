# provides helper functions

import boto3
import botocore
import requests


def s3_get_object(bucket, key):
    try:
        s3client = boto3.client("s3")
        data = s3client.get_object(Bucket=bucket, Key=key)
    except botocore.exceptions.ClientError as cerr:
        print("error_message: {}".format(cerr.response["Error"]["Message"]))
        return None
    else:
        s3file = data["Body"].read().decode("utf-8")
        print(repr(s3file))
        return s3file


def bad_request():
    return {
        "statusCode": 400,
        "headers": {"content-type": "application/json"},
        "body": "Bad Request",
    }


def accepted_request(body):
    return {
        "statusCode": 200,
        "headers": {"content-type": "application/json"},
        "body": body,
    }


def post_request(url, **kwargs):
    try:
        r = requests.post(url, **kwargs, timeout=10)
        r.raise_for_status()
    except requests.exceptions.HTTPError as h:
        print("post_http_error: {}".format(h))
    except requests.exceptions.ConnectionError as c:
        print("post_connection_error: {}".format(c))
    except requests.exceptions.Timeout as t:
        print("post_timeout_error: {}".format(t))
    except Exception as err:
        print("post_unknown_error: {}".format(err))
    else:
        return r
    return None


def head_request(url, headers):
    try:
        r = requests.head(url, headers=headers, timeout=10)
        r.raise_for_status()
    except requests.exceptions.HTTPError as h:
        print("head_http_error: {}".format(h))
    except requests.exceptions.ConnectionError as c:
        print("head_connection_error: {}".format(c))
    except requests.exceptions.Timeout as t:
        print("head_timeout_error: {}".format(t))
    except Exception as err:
        print("head_unknown_error: {}".format(err))
    else:
        return r
    return None


def put_request(url, headers):
    try:
        r = requests.put(url, headers=headers, timeout=10)
        r.raise_for_status()
    except requests.exceptions.HTTPError as h:
        print("put_http_error: {}".format(h))
    except requests.exceptions.ConnectionError as c:
        print("put_connection_error: {}".format(c))
    except requests.exceptions.Timeout as t:
        print("put_timeout_error: {}".format(t))
    except Exception as err:
        print("put_unknown_error: {}".format(err))
    else:
        return r
    return None
