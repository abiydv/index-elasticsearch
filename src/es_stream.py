import json
from urllib.parse import unquote
from src.helper import s3_get_object, post_request, head_request, put_request
from src.config import ES_BASE_URL


def index_exists(index):
    index_url = ES_BASE_URL + "/" + index
    headers = {"Content-Type": "application/json"}
    r = head_request(url=index_url, headers=headers)
    if r is None:
        print("could not connect, cannot continue")
        return False
    elif r.status_code == 200:
        return True
    else:
        print("error reading index")
        return False


def create_index(index):
    index_url = ES_BASE_URL + "/" + index
    headers = {"Content-Type": "application/json"}
    r = put_request(url=index_url, headers=headers)
    if r is None:
        print("could not connect, cannot continue")
        return False
    elif r.status_code == 200:
        return True
    else:
        print("error creating index")
        return False


def bulk_index(index, bulk_doc):
    url = ES_BASE_URL + "/" + index + "/_doc/_bulk"
    headers = {"Content-Type": "application/json"}
    r = post_request(url=url, data=bulk_doc, headers=headers)
    if r is None:
        print("could not connect, cannot continue")
        return False
    elif r.status_code != 200:
        print("docs not indexed " + r.text)
        return False
    else:
        print(r.text)
        return True


def identify_index(key):
    index_pattern = key.split("/")[0]
    if index_pattern == "serviceA":
        index = "{}-{}".format(
            index_pattern, key.split("/")[1].split("T")[0].replace("-", ".")
        )
        return index
    else:
        return False


def prepare_bulk_doc(docs):
    bulk_doc = """"""
    meta = """{"index":{}}"""
    for doc in docs:
        try:
            jdoc = json.loads(doc)
        except json.JSONDecodeError as jerr:
            print("{} : json_decode_error {}".format(doc, jerr))
            continue
        bulk_doc = bulk_doc + """{}\n{}\n""".format(meta, json.dumps(jdoc))

    if bulk_doc == """""":
        print("no valid json record to index")
        return False
    else:
        return bulk_doc


def get_docs(bucket, key):
    obj = s3_get_object(bucket, key)
    if obj is None:
        print("unable to read s3 file, cannot continue")
        return False
    else:
        docs = obj.splitlines()
        print("docs_to_index: " + str(len(docs)))
        return docs


def es_init(records):
    for record in records:
        try:
            bucket = record["s3"]["bucket"]["name"]
            key = unquote(record["s3"]["object"]["key"])
        except KeyError as kerr:
            print("key error ", kerr)
            return False

        docs = get_docs(bucket, key)
        index = identify_index(key)

        if not index or not docs:
            return False

        bulk_docs = prepare_bulk_doc(docs)
        if not bulk_docs:
            return False

        if not index_exists(index):
            if not create_index(index):
                print("cannot continue")
                return False

        if not bulk_index(index, bulk_docs):
            print("bulk index error")
            return False

    return True


def main(event, context):
    try:
        records = event["Records"]
    except TypeError as terr:
        print("type error:", terr)
        return False
    else:
        if es_init(records):
            return True
        else:
            return False
