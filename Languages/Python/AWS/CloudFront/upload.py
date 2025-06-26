import boto3
import os

s3 = boto3.client('s3',
                  aws_access_key_id='YOUR_AWS_ACCESS_KEY_ID',
                  aws_secret_access_key='YOUR_AWS_SECRET_ACCESS_KEY')

bucket_name = 'your-bucket-name'
react_build_path = 'path/to/your/react/build'

for root, dirs, files in os.walk(react_build_path):
    for file in files:
        local_path = os.path.join(root, file)
        s3_path = os.path.relpath(local_path, react_build_path)
        s3.upload_file(local_path, bucket_name, s3_path, ExtraArgs={'ContentType': 'text/html' if file.endswith('.html') else 'application/javascript' if file.endswith('.js') else 'text/css' if file.endswith('.css') else 'image/png' if file.endswith('.png') else 'application/octet-stream'})
        print(f"Uploaded {local_path} to s3://{bucket_name}/{s3_path}")
