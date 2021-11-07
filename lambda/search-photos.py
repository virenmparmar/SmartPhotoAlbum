import json
import logging
import requests
import boto3

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

def findNamesOfImages(labels):
    logger.debug('Inside findNamesOfImages function1')
    
    url = []
    for label in labels:
        if label is not None:
            url = 'https://search-search-photo-rwgymlf6d427ufgi4wfi55rrma.us-east-1.es.amazonaws.com/photo/_doc'
            headers = {"Content-Type":"application/json"}
            logger.debug('Inside addIndex')
            
            query = {
            'size': 50,
            'query': {
                'multi_match': {
                'query': label,
                'fields': ['labels']
                }
                }
            }
            
            try:    
                response = requests.get(url,data=json.dumps(query).encode("utf-8"),headers=headers,auth=('viren', 'Zaq1@wsx'))
                logger.debug(response.text)
            except Exception as e:
                logger.error(e)
            hits = response.get('hits').get('hits')
            for hit in hits:
                bucket = hit.get('_source').get('bucket')
                image =  hit.get('_source').get('objectKey')
                imglink = 'https://s3.amazonaws.com/' + str(bucket) + '/' + str(image)
                logger.debug(imglink)
                url.append(imglink)
    return url
        
def getKeywordsFromString(query):
    client = boto3.client('lex-runtime')
    response = client.post_text(botName='SearchPhotos',
                                botAlias='beta',
                                userId='viren',
                                inputText=query)
    logger.debug(response)
    logger.debug(type(response))
    slot1 = response.get('slots').get('firstSlot')
    slot2 = response.get('slots').get('secondSlot')
    logger.debug(slot1)
    logger.debug(slot2)
    return [slot1, slot2]

def lambda_handler(event, context):
    # TODO implement
    logger.debug(event)
    queryString = event.get('q')
    
    labels = getKeywordsFromString(queryString)
    logger.debug(labels)
    photos = findNamesOfImages(labels)
    logger.debug(photos)
    --results
    return {
        'statusCode': 200,
        'body': {
            'results': photos,
            'userQuery': queryString,
            'labels': labels,
        },
        'headers': {
            'Access-Control-Allow-Origin': '*'
        }
    }
