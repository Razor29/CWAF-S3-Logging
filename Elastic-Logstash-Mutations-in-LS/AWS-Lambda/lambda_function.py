import boto3
import gzip
import json
import urllib.parse  # <-- Import this

s3_client = boto3.client('s3')

# Variables to control script behavior
DELETE_ORIGINAL = True  # Set to False if you don't want to delete the original file
SUFFIX_MODE = "remove"  # Modes: "add" or "remove"
ORIGINAL_SUFFIX = "unprocessed"  # The suffix in the original folder name
NEW_SUFFIX = ""  # The suffix to add in the new folder name
OUTPUT_FORMAT = "ndjson"  # Options: "ndjson" or "json"

def lambda_handler(event, context):
    print("Lambda invoked.")
    
    # Extract bucket and file key from the event
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'])
    
    print(f"Bucket: {bucket}")
    print(f"Key: {key}")

    # Download the file and read its content
    download_path = '/tmp/{}'.format(key.split('/')[-1])
    print(f"Downloading file to: {download_path}")
    s3_client.download_file(bucket, key, download_path)
    
    with gzip.open(download_path, 'rt') as f:
        data = json.load(f)
    
    print("File contents read successfully.")
    
    # Transform JSON based on OUTPUT_FORMAT
    if OUTPUT_FORMAT == "ndjson":
        transformed_content = '\n'.join(json.dumps(item) for item in data)
        output_extension = '.ndjson'
    else:  # Assuming "json"
        transformed_content = json.dumps(data)
        output_extension = '.json'
    print(f"Transformation to {OUTPUT_FORMAT} done.")

    # Determine the output path
    first_folder = key.split('/')[0]
    if SUFFIX_MODE == 'remove':
        first_folder = first_folder.replace(f'-{ORIGINAL_SUFFIX}', '')
    elif SUFFIX_MODE == 'add':
        first_folder = f'{first_folder}-{NEW_SUFFIX}'

    # Modify the output path logic
    output_key = key.replace(key.split('/')[0], first_folder).replace('.json.gz', output_extension)
    output_path = f'/tmp/{output_key.split("/")[-1]}'
    print(f"Writing transformed content to: {output_path}")

    with open(output_path, 'w') as f:
        f.write(transformed_content)
    
    # Upload the transformed content to the different folder in the same S3 bucket
    print(f"Uploading transformed content to S3 bucket: {bucket} and key: {output_key}")
    s3_client.upload_file(output_path, bucket, output_key)
    
    # Optionally delete the original file
    if DELETE_ORIGINAL:
        s3_client.delete_object(Bucket=bucket, Key=key)

    print("Lambda execution completed.")
    
    return {
        'statusCode': 200,
        'body': json.dumps('File processed successfully!')
    }
