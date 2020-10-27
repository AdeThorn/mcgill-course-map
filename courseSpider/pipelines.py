# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

from pathlib import Path
from scrapy.exporters import JsonLinesItemExporter

# $(pwd)/../../course_data equivalent where pwd is full path of pipelines.py:
OUTPUT_PATH = Path(__file__).parent.parent.joinpath('course_data')


class CoursespiderPipeline(object):

    # Method called when spider is opened
    def __init__(self):
        self.subject_exporters = {}

    # This method is called for every item pipline component
    # Item is an item object: https://doc.scrapy.org/en/latest/topics/items.html#item-types
    # process_item() must either: return an item object, return a Deferred or raise a DropItem exception
    # More info here:
    # Deferred: https://twistedmatrix.com/documents/current/api/twisted.internet.defer.Deferred.html
    # DropItem: https://doc.scrapy.org/en/latest/topics/exceptions.html#scrapy.exceptions.DropItem
    def process_item(self, item, spider):
        # _exporter_for_item(item) retrieves the subject from item and returns an exporter to be used for this item
        exporter = self._exporter_for_item(item)
        exporter.export_item(item)
        return item

    # Method called when spider is closed
    def close_spider(self, spider):
        # Loop over all exporters to stop them
        for exporter in self.subject_exporters.values():
            exporter.finish_exporting()
            exporter.file.close()

    def _exporter_for_item(self, item):
        # Get the subject of the current item
        subject = item['subject']
        # If this is a new subject, create a new file with subject.jl as its name
        # object.jl as name to store all courses of the same subject
        if subject not in self.subject_exporters:
            f = open(Path(OUTPUT_PATH).joinpath(f'{subject}.jl'), mode='wb')
            exporter = JsonLinesItemExporter(f)
            exporter.start_exporting()
            self.subject_exporters[subject] = exporter  # add a new entry in the exporter dictionary
        return self.subject_exporters[subject]
