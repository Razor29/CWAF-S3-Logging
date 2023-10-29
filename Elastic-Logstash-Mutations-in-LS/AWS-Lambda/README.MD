# S3 JSON.gz Transformer Lambda Function

This AWS Lambda function is designed to process compressed `.json.gz` files stored in an S3 bucket. It can decompress them, transform the JSON content to the desired format, and save the transformed content to a different folder in the same S3 bucket or an external S3 bucket. Optionally, the original file can be deleted after processing.

## Features

- **Decompression**: Decompress `.json.gz` files to extract the JSON content.
- **File Transformation**: Convert the extracted JSON content to either NDJSON (newline-delimited JSON) or plain JSON format.
- **Flexible Suffix Handling**: Add or remove suffixes from the folder name where the transformed file will be saved.
- **Optional Deletion**: Choose to delete the original file after processing.
- **Destination Control**: Ability to decide the destination of the transformed file - either an internal S3 bucket or an external S3 bucket.

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
- `DESTINATION`: Control where the file will be uploaded - 'internal S3' or 'external S3'. Default is 'internal'.
- `INTERNAL_DESTINATION_BUCKET`: If set, the transformed file will be uploaded to this bucket. If left as `None`, it'll default to the source bucket.
- External S3 configurations like `EXTERNAL_AWS_ACCESS_KEY_ID`, `EXTERNAL_AWS_SECRET_ACCESS_KEY`, `EXTERNAL_BUCKET_REGION`, `EXTERNAL_DESTINATION_BUCKET`, and `EXTERNAL_PREFIX` are for when the destination is set to 'external'.

## Deployment

1. Ensure you are using **Python 3.11** for the Lambda runtime.
2. Given the added complexities and potential for longer processing times, it's more important than ever to correctly set the Lambda function's timeout. Start with 5 minutes and adjust as necessary.
3. Deploy this Lambda function.
4. Set up an S3 event trigger to invoke this Lambda function whenever a new `.json.gz` file is uploaded to the specified S3 bucket.

## Usage

1. Upload a `.json.gz` file to the S3 bucket.
2. The Lambda function will process the file, decompress it, transform the JSON content to the desired format, and save the transformed content to the specified destination.

## Dependencies

- `boto3`: The AWS SDK for Python. Allows for interactions with AWS services like S3.
- `gzip`: Module to work with Gzipped files.
- `json`: Module to work with JSON data.
- `urllib.parse`: Module to parse URLs.

## Lambda IAM Permissions

Ensure the Lambda function's execution role has the necessary permissions:

- `s3:GetObject`: To read the original file from the S3 bucket.
- `s3:PutObject`: To upload the transformed file to the S3 bucket.
- `s3:DeleteObject`: To delete the original file from the S3 bucket (if `DELETE_ORIGINAL` is set to `True`).
- `logs:CreateLogGroup`, `logs:CreateLogStream`, `logs:PutLogEvents`: For logging to Amazon CloudWatch Logs.
  
If using the external S3 option, ensure the appropriate permissions are in place to interact with the external bucket.

## Conclusion

With enhanced features and improved flexibility, this Lambda function provides a comprehensive solution for processing, decompressing, and transforming `.json.gz` files in an S3 bucket, and then deciding the destination of the transformed data.
