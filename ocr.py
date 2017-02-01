import requirements

from PIL import Image
import sys
import pyocr
import pyocr.builders

import urllib
import os
import subprocess
import base64
import json
import boto3

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
LIB_DIR = os.path.join(SCRIPT_DIR, 'lib')
LANG_DIR = os.path.join(SCRIPT_DIR, 'tessdata')

def response(code, body):
    return {
        'statusCode': code,
        'headers': {
            'Access-Control-Allow-Origin': '*',
        },
        'body': json.dumps(body),
    }

def handler(event, context):
    # Get the bucket and object from the event
    try:
        tools = pyocr.get_available_tools()
        if len(tools) == 0:
            print("No OCR tool found")
            sys.exit(1)
        tool = tools[0]
        print("Will use tool '%s'" % (tool.get_name()))

        request = event['body']

        result_filepath = '/tmp/result'
        img_filepath = '/tmp/image.png'
        with open(img_filepath, 'wb') as fh:
            fh.write(base64.decodestring(request['template']))

        command = 'LD_LIBRARY={} TESSDATA_PREFIX={} {}/tesseract {} {} -l eng --oem 0  tsv'.format(
            LIB_DIR,
            SCRIPT_DIR,
            SCRIPT_DIR,
            img_filepath,
            result_filepath
        )
        print command

        try:
            output = subprocess.check_output(
                command,
                shell=True,
                stderr=subprocess.STDOUT
            )
            print(output)

            with open(result_filepath + '.tsv', 'rb') as fh:
                print(fh.read())
        except subprocess.CalledProcessError as e:
            return "except:: " + e.output

    except Exception as e:
        print(e)
        raise e

