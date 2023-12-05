import boto3
import gzip
import json
import urllib.parse

# Control where the file will be uploaded: 'internal S3' or 'external S3'
DESTINATION = 'internal'  # Defaulting to 'internal'

# Variables to control script behavior
DELETE_ORIGINAL = True  # Set to False if you don't want to delete the original file
SUFFIX_MODE = "remove"  # Modes: "add" or "remove"
ORIGINAL_SUFFIX = "unprocessed"  # The suffix in the original folder name
NEW_SUFFIX = ""  # The suffix to add in the new folder name
OUTPUT_FORMAT = "ndjson"  # Options: "ndjson" or "json"
INTERNAL_DESTINATION_BUCKET = None  # If None, it'll default to the source bucket

# Variables for external S3 destination
EXTERNAL_AWS_ACCESS_KEY_ID = ''
EXTERNAL_AWS_SECRET_ACCESS_KEY = ''
EXTERNAL_BUCKET_REGION = ''  # Optional but recommended
EXTERNAL_DESTINATION_BUCKET = ''
EXTERNAL_PREFIX = ''  # End with a slash if specified, otherwise, keep it empty

if DESTINATION == "external":
    external_s3_client = boto3.client(
        's3',
        aws_access_key_id=EXTERNAL_AWS_ACCESS_KEY_ID,
        aws_secret_access_key=EXTERNAL_AWS_SECRET_ACCESS_KEY,
        region_name=EXTERNAL_BUCKET_REGION
    )

def lambda_handler(event, context):
    # Internal S3 client
    s3_client = boto3.client('s3')

    print("Lambda invoked.")

    # Extract bucket and file key from the event
    try:
        source_bucket = event['Records'][0]['s3']['bucket']['name']
        key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'])
    except KeyError:
        print("Unexpected event structure.")
        return {
            'statusCode': 400,
            'body': json.dumps('Unexpected event structure.')
        }
    print (f"source_bucket: {source_bucket}")
    print (f"key: {key}")
    # Download the file and read its content
    download_path = '/tmp/{}'.format(key.split('/')[-1])

    # Downloading the file
    try:
        s3_client.download_file(source_bucket, key, download_path)
    except Exception as e:
        print(f"Error downloading file from S3: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps('Failed to download file from S3.')
        }

    try:
        with gzip.open(download_path, 'rt') as f:
            data = json.load(f)

        # Transform JSON based on OUTPUT_FORMAT
        if OUTPUT_FORMAT == "ndjson":
            transformed_content = '\n'.join(json.dumps(item) for item in data)
            output_extension = '.ndjson'
        else:  # Assuming "json"
            transformed_content = json.dumps(data)
            output_extension = '.json'
        print(f"Transformation to {OUTPUT_FORMAT} done.")

    except (gzip.BadGzipFile, json.JSONDecodeError) as e:
        print(f"Error during file transformation: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps('Failed during file transformation.')
        }

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

    if DESTINATION == "internal":
        if INTERNAL_DESTINATION_BUCKET:
            destination_bucket = INTERNAL_DESTINATION_BUCKET
        else:
            destination_bucket = source_bucket

        try:
            s3_client.upload_file(output_path, destination_bucket, output_key)
        except Exception as e:
            print(f"Error uploading to internal S3: {e}")
            return {
                'statusCode': 500,
                'body': json.dumps('Failed to process file!')
            }

    elif DESTINATION == "external":
        if not 'external_s3_client' in globals():
            print("Error: External S3 client not initialized.")
            return {
                'statusCode': 500,
                'body': json.dumps('Failed to process file!')
            }
        
        destination_bucket = EXTERNAL_DESTINATION_BUCKET
        destination_key = f"{EXTERNAL_PREFIX}{output_key}"
        
        try:
            external_s3_client.upload_file(output_path, destination_bucket, destination_key)
            print("upload complete")
        except Exception as e:
            print(f"Error uploading to external S3: {e}")
            return {
                'statusCode': 500,
                'body': json.dumps('Failed to process file!')
            }

    # Optionally delete the original file
    if DELETE_ORIGINAL:
        try:
            s3_client.delete_object(Bucket=source_bucket, Key=key)
        except Exception as e:
            print(f"Error deleting original file from S3: {e}")
            return {
                'statusCode': 500,
                'body': json.dumps('Failed to delete original file from S3.')
            }

    # Delete the downloaded file
    try:
        os.remove(download_path)
        print(f"Downloaded file {download_path} deleted.")
    except Exception as e:
        print(f"Warning: Could not delete the downloaded file: {e}")

    # Delete the output file
    try:
        os.remove(output_path)
        print(f"Output file {output_path} deleted.")
    except Exception as e:
        print(f"Warning: Could not delete the output file: {e}")

    print("Lambda execution completed.")

    return {
        'statusCode': 200,
        'body': json.dumps('File processed successfully!')
    }
