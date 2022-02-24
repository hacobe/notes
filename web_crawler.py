"""Basic web crawler.

See also: web_crawler_concurrent.py
"""
import collections

def get_host_name(url):
    return url.split('/')[2]

class Solution(object):
    def crawl(self, startUrl, htmlParser):
        """
        :type startUrl: str
        :type htmlParser: HtmlParser
        :rtype: List[str]
        """
        host_name = get_host_name(startUrl)
        queue = collections.deque([startUrl])
        visited = {startUrl}
        while queue:
            url = queue.popleft()
            neighbor_urls = htmlParser.getUrls(url)
            for neighbor_url in neighbor_urls:
                same_host = get_host_name(neighbor_url) == host_name
                if (neighbor_url not in visited) and same_host:
                    visited.add(neighbor_url)
                    queue.append(neighbor_url)
        return list(visited)
