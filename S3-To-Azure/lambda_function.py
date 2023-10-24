import boto3
import gzip
import json
import urllib.parse 
import urllib3
import certifi

s3_client = boto3.client('s3')

def lambda_handler(event, context):
    # AWS S3 Configuration
    try:
        bucket_name = event['Records'][0]['s3']['bucket']['name']
        object_key = event['Records'][0]['s3']['object']['key']
        object_key = urllib.parse.unquote_plus(object_key)
    except KeyError:
        raise Exception("Unexpected event structure.")
    
    print(f"Bucket: {bucket_name}")
    print(f"Key: {object_key}")

    # Azure Blob Storage Configuration
    account_name = '' # enter the name of the azure storage account
    container_name = '' # enter the name of the storage account container
    sas_token = ''  # SAS token details

    # Lambda Configurations
    format = "json.gz" # Options are json.gz, ndjson and json
    delete_original = True # Option that allows to delete or keep original file

    # Get the file from S3
    try:
        # Get the file from S3
        s3_response = s3_client.get_object(Bucket=bucket_name, Key=object_key)
        file_content = s3_response['Body'].read()
    except Exception as e:
        raise Exception(f"Failed to download file from S3. Reason: {str(e)}")


    base_blob_name = object_key.rsplit('.json.gz', 1)[0]  # Remove .json.gz extension

    try:
        if format == "ndjson":
            # Transform JSON.gz to NDJSON
            data = json.loads(gzip.decompress(file_content).decode('utf-8'))
            ndjson_content = '\n'.join(json.dumps(item) for item in data)
            file_content = ndjson_content.encode('utf-8')  # Convert back to bytes for upload
            blob_name = f"{base_blob_name}.ndjson"

        elif format == "json":
            # Decompress the JSON.gz to JSON
            file_content = gzip.decompress(file_content)
            blob_name = f"{base_blob_name}.json"

        else:
            blob_name = object_key  # Though this should never be the case given the original is always .json.gz

    except (gzip.BadGzipFile, json.JSONDecodeError):
        raise Exception("Error during file transformation.")

    # Use urllib3 with SAS token
    url = f"https://{account_name}.blob.core.windows.net/{container_name}/{blob_name}{sas_token}"

    # Headers for the request
    headers = {
        'x-ms-blob-type': 'BlockBlob',
        'Content-Type': 'application/json; charset=utf-8',
        'Content-Encoding': 'gzip'
    }
    if format == "ndjson":
        headers['Content-Type'] = 'application/x-ndjson'
        headers.pop('Content-Encoding', None)  # Remove gzip encoding for ndjson
    elif format == "json":
        headers.pop('Content-Encoding', None)  # Remove gzip encoding for plain json

    # Initialize the HTTP client
    http = urllib3.PoolManager(cert_reqs='CERT_REQUIRED', ca_certs=certifi.where())

    # Upload to Azure Blob Storage using urllib3
    try:
        # Upload to Azure Blob Storage using urllib3
        response = http.request('PUT', url, body=file_content, headers=headers)
        if response.status != 201:  # 201 is the expected status code for a successful blob creation
            raise Exception(f"Failed to upload blob. Status: {response.status}, Reason: {response.data.decode('utf-8')}")
    except Exception as e:
        raise Exception(f"Failed to upload to Azure Blob Storage. Reason: {str(e)}")


    # Delete the original file from S3 bucket
    if delete_original:
        try:
            s3_client.delete_object(Bucket=bucket_name, Key=object_key)
        except Exception as e:
            raise Exception(f"Failed to delete file from S3. Reason: {str(e)}")

    return {
        'statusCode': 200,
        'body': 'File transferred successfully!'
    }
