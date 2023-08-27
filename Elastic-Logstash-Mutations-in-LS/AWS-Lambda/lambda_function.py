import boto3
import gzip
import json
import urllib.parse  

s3_client = boto3.client('s3')

# Variables to control script behavior
DELETE_ORIGINAL = True  # Set to False if you don't want to delete the original file
SUFFIX_MODE = "remove"  # Modes: "add" or "remove"
ORIGINAL_SUFFIX = "unprocessed"  # The suffix in the original folder name
NEW_SUFFIX = ""  # The suffix to add in the new folder name

def lambda_handler(event, context):
    print("Lambda invoked.")
    
    # Extract bucket and file key from the event
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'])
    
    print(f"Bucket: {bucket}")
    print(f"Key: {key}")

    # Download the file and read its content
    download_path = '/tmp/{}'.format(key.split('/')[-1])
    s3_client.download_file(bucket, key, download_path)
    
    with gzip.open(download_path, 'rt') as f:
        data = json.load(f)
    
    # Transform JSON to NDJSON
    ndjson_content = '\n'.join(json.dumps(item) for item in data)
    
    # Determine the output path
    first_folder = key.split('/')[0]
    if SUFFIX_MODE == 'remove':
        first_folder = first_folder.replace(f'-{ORIGINAL_SUFFIX}', '')
    elif SUFFIX_MODE == 'add':
        first_folder = f'{first_folder}-{NEW_SUFFIX}'
        
    output_key = key.replace(key.split('/')[0], first_folder).replace('.json.gz', '.ndjson')
    output_path = f'/tmp/{output_key.split("/")[-1]}'
    
    # Save the transformed content
    with open(output_path, 'w') as f:
        f.write(ndjson_content)
    
    # Upload the transformed content to S3
    s3_client.upload_file(output_path, bucket, output_key)
    
    # Optionally delete the original file
    if DELETE_ORIGINAL:
        s3_client.delete_object(Bucket=bucket, Key=key)

    return {
        'statusCode': 200,
        'body': json.dumps('File processed successfully!')
    }
