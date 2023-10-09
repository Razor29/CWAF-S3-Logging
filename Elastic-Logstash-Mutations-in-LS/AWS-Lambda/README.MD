# S3 JSON.gz Transformer Lambda Function

This AWS Lambda function is designed to process compressed `.json.gz` files stored in an S3 bucket, decompress them, transform the JSON content based on the specified format, and save the transformed content to a different folder in the same S3 bucket. Optionally, the original file can be deleted after processing.

## Features

- **Decompression**: Decompress `.json.gz` files to extract the JSON content.
- **File Transformation**: Convert the extracted JSON content to either NDJSON (newline-delimited JSON) or plain JSON format.
- **Flexible Suffix Handling**: Add or remove suffixes from the folder name where the transformed file will be saved.
- **Optional Deletion**: Choose to delete the original file after processing.

## Configuration

The behavior of the script can be controlled using the following variables:

- `DELETE_ORIGINAL`: Set to `True` if you want to delete the original file after processing. Default is `True`.
- `SUFFIX_MODE`: Determines how the folder name suffix is handled. Options are:
  - `"add"`: Add a new suffix to the folder name.
  - `"remove"`: Remove the existing suffix from the folder name.
- `ORIGINAL_SUFFIX`: The suffix in the original folder name that you might want to remove. Default is `"unprocessed"`.
- `NEW_SUFFIX`: The new suffix to add to the folder name if `SUFFIX_MODE` is set to `"add"`. Default is an empty string.
- `OUTPUT_FORMAT`: The format of the transformed file. Options are:
  - `"ndjson"`: Newline-delimited JSON format.
  - `"json"`: Plain JSON format.

## Deployment

1. Ensure you are using **Python 3.11** for the Lambda runtime.
2. It's recommended to increase the Lambda function timeout, especially if processing large files. A starting point might be setting the timeout to 5 minutes, but adjust based on your specific needs.
3. Deploy this Lambda function.
4. Set up an S3 event trigger to invoke this Lambda function whenever a new `.json.gz` file is uploaded to the specified S3 bucket.

## Usage

1. Upload a `.json.gz` file to the S3 bucket.
2. The Lambda function will process the file, decompress it, transform the JSON content based on the specified format, and save the transformed content to a different folder in the same S3 bucket.

## Dependencies

- `boto3`: The AWS SDK for Python. It allows Python developers to write software that makes use of services like Amazon S3 and Amazon EC2.
- `gzip`: Module to work with Gzipped files.
- `json`: Module to work with JSON data.
- `urllib.parse`: Module to parse URLs.

## Lambda IAM Permissions

Ensure that the Lambda function's execution role has the following permissions:

- `s3:GetObject`: To read the original file from the S3 bucket.
- `s3:PutObject`: To upload the transformed file to the S3 bucket.
- `s3:DeleteObject`: To delete the original file from the S3 bucket (if `DELETE_ORIGINAL` is set to `True`).
- `logs:CreateLogGroup`: To create a new log group in Amazon CloudWatch Logs.
- `logs:CreateLogStream`: To create a log stream within the log group.
- `logs:PutLogEvents`: To write log events to the log stream in Amazon CloudWatch Logs.

Additionally, ensure that the trust policy of the execution role allows the Lambda service to assume the role.

## Conclusion

This Lambda function provides a flexible way to process, decompress, and transform `.json.gz` files in an S3 bucket. Adjust the configuration variables as needed to fit your use case.
