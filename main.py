import csv
import json
import time
from scrapy_app.crawler import MainCrawler

result = MainCrawler().crawl()

print ('- '*20 + str(len(result)) + ' RESULTS ' + ' -'*20)
print ('TOTAL RESULTS: ', len(result))
# for i in result:
#     # print (i)
#     print (type(i))
#
#     print (json.dumps(i, indent=2, ensure_ascii=False))
#     print ('*'*50)



