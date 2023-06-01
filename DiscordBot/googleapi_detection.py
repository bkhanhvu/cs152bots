import os
import openai
import requests
import json
from google.cloud import vision

async def run_quickstart_uri(uri) -> vision.EntityAnnotation:
    """Provides a quick start example for Cloud Vision."""

    # Instantiates a client
    client = vision.ImageAnnotatorClient()
    image = vision.Image()
    image.source.image_uri = uri

    # Performs label detection on the image file
    response = client.label_detection(image=image)
    labels = response.label_annotations

    # print('Labels:')
    # for label in labels:
    #     print(label.description)

    return labels

async def detect_label_safe_search_uri(uri):
    """Detects unsafe features in the file located in Google Cloud Storage or
    on the Web."""

    client = vision.ImageAnnotatorClient()
    image = vision.Image()
    image.source.image_uri = uri

    response = client.annotate_image({
      'image': {'source': {'image_uri': uri}},
      'features': [{'type_': vision.Feature.Type.LABEL_DETECTION, 'max_results': 5},
      {'type_': vision.Feature.Type.SAFE_SEARCH_DETECTION}],
    })

    safe, labels = response.safe_search_annotation, response.label_annotations
    print('response=')
    print(response)
    # Names of likelihood from google.cloud.vision.enums
    likelihood_name = ('UNKNOWN', 'VERY_UNLIKELY', 'UNLIKELY', 'POSSIBLE',
                       'LIKELY', 'VERY_LIKELY')
    # print('Safe search:')

    # print(f'adult: {likelihood_name[safe.adult]}')
    # print(f'medical: {likelihood_name[safe.medical]}')
    # print(f'spoofed: {likelihood_name[safe.spoof]}')
    # print(f'violence: {likelihood_name[safe.violence]}')
    # print(f'racy: {likelihood_name[safe.racy]}')

    if response.error.message:
        raise Exception(
            '{}\nFor more info on error messages, check: '
            'https://cloud.google.com/apis/design/errors'.format(
                response.error.message))
    
    return {'adult': likelihood_name[safe.adult], \
            'medical': likelihood_name[safe.medical], \
            'spoofed': likelihood_name[safe.spoof], \
            'violence': likelihood_name[safe.violence],
            'racy': likelihood_name[safe.racy]
            }, labels