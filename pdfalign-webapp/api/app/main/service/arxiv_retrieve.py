from lxml import etree
from ..util.utils import remove_bad_chars

import sys

if sys.version_info[0] == 3:
    from urllib.request import urlopen
else:
    # Not Python 3 - today, it is most likely to be Python 2
    # But note that this might need an update when Python 4
    # might be around one day
    from urllib import urlopen

def retrieve_id_pdf(id):
    url = 'http://export.arxiv.org/api/query?id_list=' + id
    data = urlopen(url).read()
    tree = etree.fromstring(data)

    link_nodes = tree.findall(".//{http://www.w3.org/2005/Atom}link")
    pdf = list(filter(lambda x: x.attrib['type'] == 'application/pdf', link_nodes))

    if len(pdf) > 0:
        return retrieve_pdf_url(pdf[0].attrib['href'])
    else:
        return { 'success' : False,
            'message' : 'Unable to retrieve arxiv record with id ' + id }

def retrieve_pdf_url(url):
    data = urlopen(url).read()
    print(data)
    return data

print(retrieve_id_pdf('cond-mat/0207270v1'))
