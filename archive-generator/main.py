import boto3
from dateutil import parser
client = boto3.client('s3')

response = client.list_objects_v2(
    Bucket='nltl-archive',
    Prefix='archive')

for content in response.get('Contents', []):
    key_split = content['Key'].split("/")
    if "mp3" in content['Key']:
        with open("output/{}.md".format(key_split[1].replace(".mp3","")), "w") as file:
            file.writelines(
                """---
title: "{title}"
date: {title}+00:00
tags: ["archive"]
draft: false
size: {size}
duration: 0
file_link: "{file_link}"
file_type: "mp3"
---
Archived at {title}
                """.format(
                        title = parser.parse(key_split[1].split(".")[0]),
                        date = content['LastModified'],
                        size = content['Size'],
                        file_link = "https://www.nothinglefttolearn.com/archive/{}".format(key_split[1])
                    )
            )
