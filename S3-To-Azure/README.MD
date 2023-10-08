# AWS S3 to Azure Blob Storage Transfer Lambda

This AWS Lambda function transfers files from an AWS S3 bucket to Azure Blob Storage. It supports both SAS tokens and Azure Blob Storage access keys for authentication.

## Prerequisites

1. AWS Lambda execution role with permissions to read from the source S3 bucket and CloudWatch Logs permissions for logging.
2. Azure Blob Storage account and container.
3. Either a SAS token or an access key for the Azure Blob Storage account.
4. Azure SDK for Python included in the Lambda deployment package.

## Setup

1. Create an AWS Lambda function.
2. Upload the Lambda deployment package which includes the function code and the Azure SDK for Python.
3. Set the Lambda function's handler to `lambda_function.lambda_handler` (assuming the filename is `lambda_function.py`).
4. Increase the Lambda function timeout if your files are large. A good starting point might be 5 minutes.

## Configuration

In the Lambda function code, you need to set the following:

- `account_name`: The name of your Azure Blob Storage account.
- `container_name`: The name of your Azure Blob Storage container.
- `sas_token`: Your SAS token (leave empty if using an access key).
- `access_key`: Your Azure Blob Storage access key (leave empty if using a SAS token).
- `format`: The format of your file. Options are `json.gz`, `ndjson`, and `json`.
- `delete_original`: Set to `True` if you want to delete the original file from the S3 bucket after transferring. Set to `False` to keep the original file.

## Execution

When a new file is uploaded to the S3 bucket, the Lambda function will be triggered. It will then:

1. Fetch the file from the S3 bucket.
2. Convert the file format if necessary (e.g., from `json.gz` to `ndjson` or `json`).
3. Upload the file to Azure Blob Storage.
4. If `delete_original` is set to `True`, it will delete the original file from the S3 bucket.

## Monitoring

You can monitor the Lambda function's execution in the AWS Lambda console and view logs in CloudWatch Logs.

## Troubleshooting

If the file transfer fails:

1. Check the CloudWatch Logs for any error messages.
2. Ensure that the SAS token or access key is correctly set and has the necessary permissions.
3. Ensure that the Lambda function has permissions to read from the S3 bucket.
4. Check the file format and ensure it matches the `format` configuration.

## Conclusion

This Lambda function provides an automated way to transfer files from AWS S3 to Azure Blob Storage. Ensure all configurations are set correctly and monitor the function to ensure smooth transfers.
