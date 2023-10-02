import boto3
import urllib.parse 
import urllib3
import certifi

def lambda_handler(event, context):
    # AWS S3 Configuration
    s3_client = boto3.client('s3')
    bucket_name = event['Records'][0]['s3']['bucket']['name']
    object_key = event['Records'][0]['s3']['object']['key']
    object_key = urllib.parse.unquote_plus(object_key)
    
    print(f"Bucket: {bucket_name}")
    print(f"Key: {object_key}")


    # Get the file from S3
    s3_response = s3_client.get_object(Bucket=bucket_name, Key=object_key)
    file_content = s3_response['Body'].read()

    # Azure Blob Storage Configuration
    account_name = 'cwaflogs' # enter the name of the azure storage account
    container_name = 'logs' # enter the name of the storage account container
    blob_name = object_key  # or any other desired name
    sas_token = ''  # It will look something like "?sv=2019-12-12&ss=bfqt&srt=sco&sp=rwdlacupx&se=2023-10-01T00:00:00Z&st=2023-10-01T00:00:00Z&spr=https&sig=..."
    # Create the URL with the SAS token appended
    url = f"https://{account_name}.blob.core.windows.net/{container_name}/{blob_name}{sas_token}"

    # Upload to Azure Blob Storage using REST API
    headers = {
        'x-ms-blob-type': 'BlockBlob',
        'Content-Type': 'application/json; charset=utf-8',
        'Content-Encoding': 'gzip'
    }
    # Initialize the HTTP client
    http = urllib3.PoolManager(cert_reqs='CERT_REQUIRED', ca_certs=certifi.where())

    # Upload to Azure Blob Storage using urllib3
    response = http.request('PUT', url, body=file_content, headers=headers)
    
    if response.status != 201:  # 201 is the expected status code for a successful blob creation
        raise Exception(f"Failed to upload blob. Status: {response.status}, Reason: {response.data.decode('utf-8')}")

    return {
        'statusCode': 200,
        'body': 'File transferred successfully!'
    }

