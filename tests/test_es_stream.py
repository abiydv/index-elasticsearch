import json
import mock
from pathlib import Path

from .context import src

RESOURCES = Path("tests/resources/")

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


"""
index_exists tests

"""


@mock.patch("src.es_stream.head_request")
def test_index_exists_true(mock_head_request):
    # this should not fail
    mock_head_request.return_value.status_code = 200
    assert src.es_stream.index_exists("index")


@mock.patch("src.es_stream.head_request")
def test_index_exists_false(mock_head_request):
    # this should fail as index does not exist
    mock_head_request.return_value.status_code = 404
    assert not src.es_stream.index_exists("index")


@mock.patch("src.es_stream.head_request")
def test_index_exists_request_get_none_false(mock_head_request):
    # this should fail as index does not exist
    mock_head_request.return_value = None
    assert not src.es_stream.index_exists("index")


"""
create_index tests

"""


@mock.patch("src.es_stream.put_request")
def test_create_index_true(mock_put_request):
    # this should not fail
    mock_put_request.return_value.status_code = 200
    assert src.es_stream.create_index("index")


@mock.patch("src.es_stream.put_request")
def test_create_index_false(mock_put_request):
    # this should fail as index does not exist
    mock_put_request.return_value.status_code = 404
    assert not src.es_stream.create_index("index")


@mock.patch("src.es_stream.put_request")
def test_create_index_request_get_none_false(mock_put_request):
    # this should fail as index does not exist
    mock_put_request.return_value = None
    assert not src.es_stream.create_index("index")


"""
get_docs tests

"""


@mock.patch("src.es_stream.s3_get_object")
def test_get_docs_s3_req_none_fail(mock_s3_get_object):
    # this should fail as no files returned from s3
    mock_s3_get_object.return_value = None
    assert not src.es_stream.get_docs("bucket", "key")


@mock.patch("src.es_stream.s3_get_object")
def test_get_docs_success(mock_s3_get_object):
    # this should fail as no files returned from s3
    mock_s3_get_object.return_value = """line1
line2
line3"""
    assert src.es_stream.get_docs("bucket", "key") == ["line1", "line2", "line3"]


"""
identify_index tests

"""


def test_identify_index_success():
    assert (
        src.es_stream.identify_index("serviceA/2020-01-01/log001")
        == "serviceA-2020.01.01"
    )


def test_identify_index_fail():
    assert not src.es_stream.identify_index("something/random")


"""
bulk_index tests

"""


@mock.patch("src.es_stream.post_request")
def test_bulk_index_success(mock_post_request):
    mock_post_request.return_value = mock_response(status=200, text="updated")
    assert src.es_stream.bulk_index("index", "doc1")


@mock.patch("src.es_stream.post_request")
def test_bulk_index_fail(mock_post_request):
    mock_post_request.return_value = mock_response(
        status=404, text="error indexing document"
    )
    assert not src.es_stream.bulk_index("index", "doc1")


@mock.patch("src.es_stream.post_request")
def test_bulk_index_none_fail(mock_post_request):
    mock_post_request.return_value = None
    assert not src.es_stream.bulk_index("index", "doc1")


"""
prepare_bulk_doc tests

"""


def test_prepare_bulk_doc_fail():
    assert not src.es_stream.prepare_bulk_doc(["invalid_json"])


def test_prepare_bulk_doc_success():
    docs = [
        json.dumps({"timestamp": "2020-01-01T00:01:01", "url": "/path/page1.html"}),
        json.dumps({"timestamp": "2020-01-01T00:02:01", "url": "/path/page2.html"}),
    ]
    bulk_doc = """{"index":{}}
{"timestamp": "2020-01-01T00:01:01", "url": "/path/page1.html"}
{"index":{}}
{"timestamp": "2020-01-01T00:02:01", "url": "/path/page2.html"}
"""
    assert src.es_stream.prepare_bulk_doc(docs) == bulk_doc


"""
es_init tests

"""


def test_es_init_invalid_event_fail():
    invalid_records = json.loads((RESOURCES / "invalid_event.json").read_text())
    assert not src.es_stream.es_init(invalid_records["Records"])


# tests function is successful - no index exists, new index is created, doc is indexed
@mock.patch("src.es_stream.prepare_bulk_doc")
@mock.patch("src.es_stream.identify_index")
@mock.patch("src.es_stream.get_docs")
def test_es_init_not_index_fail(
    mock_get_docs, mock_identify_index, mock_prepare_bulk_doc
):
    mock_get_docs.return_value is True
    mock_identify_index.return_value is False
    mock_prepare_bulk_doc.return_value = True
    valid_records = json.loads((RESOURCES / "valid_event.json").read_text())
    assert not src.es_stream.es_init(valid_records["Records"])


@mock.patch("src.es_stream.prepare_bulk_doc")
@mock.patch("src.es_stream.identify_index")
@mock.patch("src.es_stream.get_docs")
def test_es_init_not_docs_fail(
    mock_get_docs, mock_identify_index, mock_prepare_bulk_doc
):
    mock_get_docs.return_value = False
    mock_identify_index.return_value = True
    mock_prepare_bulk_doc.return_value = True
    valid_records = json.loads((RESOURCES / "valid_event.json").read_text())
    assert not src.es_stream.es_init(valid_records["Records"])


@mock.patch("src.es_stream.prepare_bulk_doc")
@mock.patch("src.es_stream.identify_index")
@mock.patch("src.es_stream.get_docs")
def test_es_init_not_bulk_doc_fail(
    mock_get_docs, mock_identify_index, mock_prepare_bulk_doc
):
    mock_get_docs.return_value = True
    mock_identify_index.return_value = True
    mock_prepare_bulk_doc.return_value = False
    valid_records = json.loads((RESOURCES / "valid_event.json").read_text())
    assert not src.es_stream.es_init(valid_records["Records"])


@mock.patch("src.es_stream.create_index")
@mock.patch("src.es_stream.index_exists")
@mock.patch("src.es_stream.prepare_bulk_doc")
@mock.patch("src.es_stream.identify_index")
@mock.patch("src.es_stream.get_docs")
def test_es_init_not_index_exist_create_fail(
    mock_get_docs,
    mock_identify_index,
    mock_prepare_bulk_doc,
    mock_index_exists,
    mock_create_index,
):
    mock_get_docs.return_value = True
    mock_identify_index.return_value = True
    mock_prepare_bulk_doc.return_value = True
    mock_index_exists.return_value = False
    mock_create_index.return_value = False
    valid_records = json.loads((RESOURCES / "valid_event.json").read_text())
    assert not src.es_stream.es_init(valid_records["Records"])


@mock.patch("src.es_stream.bulk_index")
@mock.patch("src.es_stream.create_index")
@mock.patch("src.es_stream.index_exists")
@mock.patch("src.es_stream.prepare_bulk_doc")
@mock.patch("src.es_stream.identify_index")
@mock.patch("src.es_stream.get_docs")
def test_es_init_bulk_index_error_fail(
    mock_get_docs,
    mock_identify_index,
    mock_prepare_bulk_doc,
    mock_index_exists,
    mock_create_index,
    mock_bulk_index,
):
    mock_get_docs.return_value = True
    mock_identify_index.return_value = True
    mock_prepare_bulk_doc.return_value = True
    mock_index_exists.return_value = False
    mock_create_index.return_value = True
    mock_bulk_index.return_value = False
    valid_records = json.loads((RESOURCES / "valid_event.json").read_text())
    assert not src.es_stream.es_init(valid_records["Records"])


@mock.patch("src.es_stream.bulk_index")
@mock.patch("src.es_stream.index_exists")
@mock.patch("src.es_stream.prepare_bulk_doc")
@mock.patch("src.es_stream.identify_index")
@mock.patch("src.es_stream.get_docs")
def test_es_init_index_exist_true_success(
    mock_get_docs,
    mock_identify_index,
    mock_prepare_bulk_doc,
    mock_index_exists,
    mock_bulk_index,
):
    mock_get_docs.return_value = True
    mock_identify_index.return_value = True
    mock_prepare_bulk_doc.return_value = True
    mock_index_exists.return_value = True
    mock_bulk_index.return_value = True
    valid_records = json.loads((RESOURCES / "valid_event.json").read_text())
    assert src.es_stream.es_init(valid_records["Records"])


@mock.patch("src.es_stream.bulk_index")
@mock.patch("src.es_stream.create_index")
@mock.patch("src.es_stream.index_exists")
@mock.patch("src.es_stream.prepare_bulk_doc")
@mock.patch("src.es_stream.identify_index")
@mock.patch("src.es_stream.get_docs")
def test_es_init_create_index_true_success(
    mock_get_docs,
    mock_identify_index,
    mock_prepare_bulk_doc,
    mock_index_exists,
    mock_create_index,
    mock_bulk_index,
):
    mock_get_docs.return_value = True
    mock_identify_index.return_value = True
    mock_prepare_bulk_doc.return_value = True
    mock_index_exists.return_value = False
    mock_create_index.return_value = True
    mock_bulk_index.return_value = True
    valid_records = json.loads((RESOURCES / "valid_event.json").read_text())
    assert src.es_stream.es_init(valid_records["Records"])


"""
main tests

"""


@mock.patch("src.es_stream.es_init")
def test_main_true(mock_es_init):
    mock_es_init.return_value = True
    mock_event = {"Records": [{"one": 1}]}
    assert src.es_stream.main(mock_event, "context")


@mock.patch("src.es_stream.es_init")
def test_main_false(mock_es_init):
    mock_es_init.return_value = False
    mock_event = {"Records": [{"one": 1}]}
    assert not src.es_stream.main(mock_event, "context")


# this tests if an invalid event is passed to the function it exits gracefully
@mock.patch("src.es_stream.es_init")
def test_main_invalid_event_false(mock_es_init):
    mock_es_init.return_value = False
    mock_event = "invalid_records"
    assert not src.es_stream.main(mock_event, "context")
