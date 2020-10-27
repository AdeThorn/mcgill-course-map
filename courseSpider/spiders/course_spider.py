import scrapy
from . import subject_data
from ..items import CoursespiderItem, CourseItemLoader
from scrapy.linkextractors import LinkExtractor


"""
Spider that crawls through the courses on McGill's webpage.

...

Attributes
----------
name: str
    Identifies the Spider. It must be unique within a project, 
    that is, you can't set the same name for different Spiders.

Methods
----------
start_requests()
    must return an iterable of Requests 
    (you can return a list of requests or write a generator function) 
    which the Spider will begin to crawl from. 
    Subsequent requests will be generated successively from these initial requests.

parse()
    a method that will be called to handle the response downloaded for each of the requests made. 
    The response parameter is an instance of TextResponse that holds the page content and 
    has further helpful methods to handle it.

    The parse() method usually parses the response, 
    extracting the scraped data as dicts 
    and also finding new URLs to follow and creating new requests (Request) from them.
"""
class CourseSpider(scrapy.Spider):
    name = 'courses'
    # pipeline setting
    custom_settings = {
        'ITEM_PIPELINES': {
            'courseSpider.pipelines.CoursespiderPipeline': 300,
        }
    }

    """
    Schedules scrapy.Request objects returned by the start_requests method of the Spider. Upon receiving
    a response for each one, it instantiates Response objects and calls the callback method associated with the request
    (in this case, the self.parse means the parse method below) passing the response as an argument.
    """
    def start_requests(self):
        # I tried to take a shortcut by using the start_requests() and declaring start_urls variable
        # But this did not work as the logic currently uses a dictionary within its meta-data within the parsing func.
        # See http://scrapingauthority.com/scrapy-meta for information on that tag.
        # TODO: This may change in the future, revisit meta data and the parsing function
        for url in subject_data.LINKS:
            yield scrapy.Request(url=url, meta={'start_url': url}, callback=self.parse)

    """
    Method will be called to handle each of the requests sent in from start_requests. 
    
    parse() method will still be called even if we haven't explicitly told Scrapy to do so (we defined it in this 
    project). This happens because parse() is Scrapy's default callback method, 
    which is called for requests without an explicitly assigned callback.
    
    Best way to learn how to extract data with Scrapy is trying selectors using the Scrapy shell.
    Docs [Scrapy Shell]: https://docs.scrapy.org/en/latest/topics/shell.html#topics-shell
    """
    def parse(self, response):
        """ Get all links on a course page by link selector css + LinkExtractor"""
        all_links = LinkExtractor(restrict_css='.field-content a').extract_links(response)

        # Seems to send every link found to parse_course for further processing using XPaths
        # We pass this off to the parse_course method (as indicated in callback)
        # TODO: Figure out what this does exactly for documenting purposes
        for link in all_links:
            yield response.follow(link.url, meta={'start_url': response.meta['start_url']}, callback=self.parse_course)

        # Retrieves the next page if there is any, and follows it
        next_page = response.css('li.pager-next a::attr(href)').get()
        if next_page is not None:
            # As a shortcut for creating Request objects you can use response.follow
            # Unlike scrapy.Request, response.follow supports relative URLs directly - no need to call urljoin.
            # Note that response.follow just returns a Request instance; you still have to yield this Request.
            yield response.follow(next_page, meta={'start_url': response.meta['start_url']}, callback=self.parse)

    def parse_course(self, response):

        """
            At first, I used the dictionary to assign value to each field, for example:

                course = CoursespiderItem()
                name = response.css('#page-title::text').get()
                course['name'] = name

            ItemLoader is exactly designed to populate fields, so it makes the whole process a lot cleaner.
            All the dirty work is in CourseItemLoader class.
        """

        l = CourseItemLoader(item=CoursespiderItem(), response=response)
        l.add_css('name', '#page-title::text')
        l.add_xpath('prereq', "//li[contains(p, 'Prerequisite')]//a/@href")
        l.add_css('term', '.catalog-terms::text')
        l.add_value('link', response.url)
        l.add_value('subject', response.meta['start_url'])
        return l.load_item()
