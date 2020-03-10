import boto3
import uuid
import pandas as pd

s3_client = boto3.client('s3')
s3_resource = boto3.resource('s3')

def create_bucket_name(bucket_prefix):
    # The generated bucket name must be between 3 and 63 chars long
    return ''.join([bucket_prefix, str(uuid.uuid4())])


def create_bucket(bucket_prefix, s3_connection):
    session = boto3.session.Session()
    current_region = session.region_name
    bucket_name = create_bucket_name(bucket_prefix)
    bucket_response = s3_connection.create_bucket(
        Bucket=bucket_name,
        CreateBucketConfiguration={
        'LocationConstraint': current_region})
    print(bucket_name, current_region)
    return bucket_name, bucket_response


from io import StringIO # python3; python2: BytesIO
#first_bucket_name, first_response = create_bucket(
  # bucket_prefix='firstpythonbucket',
  # s3_connection=s3_resource.meta.client)

def read_file(bucket,file_name):
    obj = s3_client.get_object(Bucket= bucket, Key= file_name)
    return pd.read_csv(obj['Body'])

def insert_df_to_s3(bucket,df,file_name):
    csv_buffer = StringIO()
    df.to_csv(csv_buffer,encoding='utf-8',index=False)
    s3_resource = boto3.resource('s3')
    s3_resource.Object(bucket, file_name).put(Body=csv_buffer.getvalue())

