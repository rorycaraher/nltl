import boto3
import os
from jinja2 import Environment, FileSystemLoader
from dateutil import parser

class ArchiveGenerator:
    def __init__(self, boto3_client):
        self.client = boto3_client
        self.archive_path = "content/archive"

    def get_archive_objects(self):
        return self.client.list_objects_v2(
            Bucket='nltl-archive',
            Prefix='archive')

    def empty_existing_archive(self):
        for f in os.listdir(self.archive_path):
            os.remove(os.path.join(self.archive_path, f))

    def create_archive_entries(self, archive_objects):
        environment = Environment(loader=FileSystemLoader("archive-generator/templates/"))
        template = environment.get_template("archive-item.txt")
        for content in archive_objects.get('Contents', []):
            if "mp3" in content['Key']:
                key_split = content['Key'].split("/")
                filename = "{}.md".format(key_split[1].replace(".mp3",""))
                content = template.render(
                    title = parser.parse(key_split[1].split(".")[0]),
                    date = content['LastModified'],
                    size = content['Size'],
                    file_link = "https://www.nothinglefttolearn.com/archive/{}".format(key_split[1])
                )
                with open("content/archive/{}".format(filename), mode="w", encoding="utf-8") as file:
                    file.write(content)

if __name__ == "__main__":
    archive_generator = ArchiveGenerator(boto3.client('s3'))
    archive_objects = archive_generator.get_archive_objects()
    if archive_objects:
        archive_generator.empty_existing_archive()
        archive_generator.create_archive_entries(archive_objects)
