import requests
import re
from bs4 import BeautifulSoup


#TODO: Consider having something to get the current year + current_year+1 automatically so that we don't have to
#   Update this ourselves
url = 'https://mcgill.ca/study/2020-2021/courses/search'
# url = 'https://www.mcgill.ca/study/2020-2021/courses/comp-251'
page = requests.get(url)
soup = BeautifulSoup(page.text, 'html.parser')

result = soup.select("#facetapi-facet-search-apicourses-block-field-subject-code .facetapi-inactive")

NAMES = [ re.sub(' \(([0-9])*\)', '', n.contents[0]) for n in result ]
LINKS = ['https://mcgill.ca' + l['href'] for l in result ]
CODES = [ n[:4] for n in NAMES  ]

# If you want to store the data:
# for (lst, filename) in [([NAMES], 'names'), ([LINKS], 'links'), ([CODES], 'codes')]:
#     with open(f'{filename}.csv', 'w') as resultFile:
#         wr = csv.writer(resultFile)
#         wr.writerows(lst)
