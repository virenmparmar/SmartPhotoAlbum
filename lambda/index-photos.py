import json
import logging
import boto3
import datetime
import requests

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

def getImageData(eventData):
    logger.error('Retrieving data from eventdata')
    return eventData[0].get('s3').get('bucket').get('name'),eventData[0].get('s3').get('object').get('key')

def detectLabels(bucket, photo):
    logger.error('Inside detecting labels function of index-photos')
    labels =[]
    try:
        client=boto3.client('rekognition')

        response = client.detect_labels(Image={'S3Object':{'Bucket':bucket,'Name':photo}},
        MaxLabels=10)

        logger.debug('Detected labels for ' + photo) 
        logger.debug(response['Labels'])
        for label in response['Labels']:
            labels.append(label.get('Name'))
    except Exception as e:
        logger.error('Exception occured while detecting labels')
        logger.error(e)
        return labels
    
    return labels
    
def s3MetaData(bucket, photo):
    logger.error('Inside s3MetaData')
    client = boto3.client('s3')
    customLabel = []
    #need to retrive data from user metadata x-amz-meta-customLabels​
    try:
        response = client.head_object(Bucket=bucket, Key=photo);
        logger.debug(response)
        try:
            customLabel = response.get('Metadata').get('customLabels').split(',')
        #5 to 26
        except Exception:
            return customLabel
        return customLabel
    except Exception as e:
        logger.error(e)
        logger.debug('s3MetaData failed')
        return customLabel

def addIndex(bucket, objectKey, labels):
    body = {'objectKey':objectKey,'bucket':bucket,'createdTimestamp':str(datetime.datetime.now()),'labels':labels}
    url = 'https://search-search-photo-rwgymlf6d427ufgi4wfi55rrma.us-east-1.es.amazonaws.com/photo/_doc'
    headers = {"Content-Type":"application/json"}
    logger.debug('Inside addIndex')
    logger.debug(body)
    
    try:    
        response = requests.post(url,data=json.dumps(body).encode("utf-8"),headers=headers,auth=('viren', 'Zaq1@wsx'))
        logger.debug(response.text)
    except Exception as e:
        logger.error(e)

def lambda_handler(event, context):
    # TODO implement
    logger.error("lambda function index-photos is triggered on photo upload")
    logger.debug(event)
    
    eventData = event.get('Records')
    print(eventData[0])
    bucket, fileName = getImageData(event.get('Records'))
    customLabels = []
    logger.debug('Bucket is ' + str(bucket))
    logger.debug('File name is ' + str(fileName))
    labels = detectLabels(bucket, fileName)
    customLabels = s3MetaData(bucket,fileName)
    
    labels = labels + customLabels
    
    addIndex(bucket, fileName, labels)
    
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }
