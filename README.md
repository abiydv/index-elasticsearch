# AWS Elasticsearch ingestion Lambda

This lambda function indexes files dumpled periodically on S3 to AWS Elasticsearch (or self hosted). It uses the bulk API to index. See below for the log format.

Deploying this stack will create a new lambda function, triggers and alarm (to alert if the function errors out).

### **PREREQUISITES**
1. [AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-install.html) (preferably v2)
1. [Serverless framework](https://www.serverless.com/framework/docs/providers/aws/guide/installation/) 
1. AWS Account with - 
    * S3 bucket to use for serverless framework's artifacts
    * S3 bucket where the logs (in json format) are dumped periodically. 
1. Log format - 
    * Valid json string on each new line
    * S3 path - `s3://bucket/service/date/logfile-sequence.log`
    * A new index is created daily during ingestion. Index name pattern is `service-date`. Example - `httpd-2020.01.01`

### **SETUP**

1. Create and activate virtual environment
    ```
    $ python3 -m venv env
    $ source env/bin/activate
    ```

1. Install dependencies
    ```
    (env) $ pip3 install -r requirements.txt
    ```

1. Format, lint, run tests, check coverage reports etc.
    ```
    (env) $ black src/*.py
    (env) $ flake8
    (env) $ pytest
    (env) $ coverage run -m pytest
    (env) $ coverage html

1. Modify configs as per your environment - ES base url, account number etc.

### **DEPLOY**

1. Export the AWS credentials as environment variables. Either access/secret keys or the aws cli profile

1. Deploy/Update the service to AWS 
    ```
    sls deploy
    ```

### **CLEANUP**

1. Remove the service
    ```
    sls remove
    ```
