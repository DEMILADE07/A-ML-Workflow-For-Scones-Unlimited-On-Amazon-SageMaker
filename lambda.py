# The is the first lambda function for serializing image data

import json
import boto3
import base64

s3 = boto3.client('s3')

def lambda_handler(event, context):
    """A function to serialize target data from S3"""

    # Get the s3 address from the Step Function event input
    key = event['prefix'] ## TODO: fill in
    bucket = 'scones-unlimited-projectv3' ## TODO: fill in

    # Download the data from s3 to /tmp/image.png
    ## TODO: fill in
    s3.download_file(bucket, key, "/tmp/image.png")

    # We read the data from a file
    with open("/tmp/image.png", "rb") as f:
        image_data = base64.b64encode(f.read())

    # Pass the data back to the Step Function
    print("Event:", event.keys())
    return {
        'statusCode': 200,
        'body': {
            "image_data": image_data,
            "s3_bucket": bucket,
            "s3_key": key,
            "inferences": []
        }
    }




# This is the second lambda function for classyfying image data

import json
import boto3
import base64

# Fill this in with the name of your deployed model
ENDPOINT = 'image-classification-2023-10-25-14-58-02-667'## TODO: fill in
# session = session.Session()
runtime = boto3.Session().client('sagemaker-runtime')

def lambda_handler(event, context):

    # Decode the image data
    image = base64.b64decode(event['body']['image_data'])
    
    # invoke endpoint with boto3
    response = runtime.invoke_endpoint(EndpointName = ENDPOINT, ContentType = 'image/png', Body = image)
    predictions = json.loads(response['Body'].read().decode())
    # return data back to StepFunctions
    event['body']['inferences'] = predictions
    
   
    return {
        'statusCode': 200,
        'body': event
    }






# This is the third Lambda function for filtering low-confidence-inferences

import json

THRESHOLD = .93

def lambda_handler(event, context):
    print('Received event:', json.dumps(event))

    # Grab the inferences from the event
    inferences = event['body']['body']['inferences']

    # Check if any values in our inferences are above THRESHOLD
    meets_threshold = [True if x>=THRESHOLD else False for x in inferences]

    # If our threshold is met, pass our data back out of the
    # Step Function, else, end the Step Function with an error
    if any(meets_threshold):
        print('Threshold is met')
        pass
    else:
        raise ValueError ("THRESHOLD_CONFIDENCE_NOT_MET")

    return {
        'statusCode': 200,
        'body': json.dumps(event)
    }
    


