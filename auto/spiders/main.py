import scrapy
from ..items import AutoItem
import re


class Main(scrapy.Spider):
    name = 'main'
    allowed_domains = ['salvageautosauction.com']

    def __init__(self, date_from, date_to, make, **kwargs):
        """
        :param date_from: field year_from
        :param date_to: field year_to
        :param make: field Make
        """
        super().__init__(**kwargs)
        self.date_from = date_from
        self.date_to = date_to
        self.make = make
        # self.params - parameters that are transmitted when you click on the Search button.
        # The keys of this dictionary are set by the site itself. (cboFrYear, cboToYear etc.)
        self.params = {
                'cboFrYear': self.date_from,
                'cboToYear': self.date_to,
                'cboMake': self.make,
                'hdnFrYear': self.date_from,
                'hdnToYear': self.date_to,
                'hdnMake': self.make,
                'btnSubmit.x': '0',
                'btnSubmit.y': '0',
            }

    def start_requests(self):
        """
        :return: The script makes a post request to the site. Sends data from the params dictionary
        """
        yield scrapy.FormRequest(
            url='https://www.salvageautosauction.com/price_history',  # Where are we transferring
            formdata=self.params,  # What We Transfer
            callback=self.parse  # What we do next
        )

    def parse(self, response):
        """
        :param response: At the input we receive a response from the post request
        :return: At the intermediate output, we collect data from a page with the necessary data (photo, description,
        etc.), looking for the Next Page button.
        If it is available, perform this operation again and again until we reach the last page.
        """

        item = AutoItem()
        for each in response.xpath('//div[@class="price_history"]').xpath('div[@class=" row"]'):
            def get_item(number):
                """
                :param number: Number of the column. Begins with 0
                :return: Net data without html tags and carriage or indentation characters.(without whitespaces)
                """
                try:
                    return ' '.join(re.sub(r'<[^>]*>', '', each.xpath('div').extract()[number]).split())
                    # re.sub - remove all html tags
                    # each.xpath('div').extract()[number] - Finds a column with a given number
                    # split() - It divides a string into an list by the space between words. Delete all whitespaces
                    # ' '.join(...) - Integrates the blank elements of the list into a string.
                except (AttributeError, TypeError, IndexError):
                    # If the element is not found in the table, return ''
                    return ''
            # Find url image
            try:
                item['image'] = each.xpath('div[1]/img/@src').extract_first().strip()
            except AttributeError:
                item['image'] = ''
            item['description'] = get_item(1)
            item['auction_date'] = get_item(2)
            item['actual_cash_value'] = get_item(3)
            item['repair_cost'] = get_item(4)
            item['odometer'] = get_item(5)
            item['prim_damage'] = get_item(6)
            item['sec_damage'] = get_item(7)
            item['price_sold_or_highest_bid'] = get_item(8)
            yield item

        # Looking for the Next Page button.
        try:
            # Available. Extract href tag and from this tag retrieve the link to which the post request will be sent.
            # href_fom_page = javascript:gotoPage(this, 'https://www.salvageautosauction.com/price_history/2')
            # href_from_page = href_from_page.strip() - delete whitespaces
            # href_from_page = href_from_page.split("'") -> return:
            # ["javascript:gotoPage(this, ", "https://www.salvageautosauction.com/price_history/2", ")"]
            # href_from_page = href_from_page[1] - take the second element of list.
            next_page = response.xpath('//div[@class="item next"]/a/@href').extract_first().strip().split("'")[1]
        except (AttributeError, IndexError):
            # Not Available
            next_page = None

        # if next_page exist, then send a post request to open the next page and do everything again,
        # while the next_page is available
        if next_page:
            yield scrapy.FormRequest(
                url=next_page,
                formdata=self.params,
                callback=self.parse
            )
