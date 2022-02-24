"""Concurrent web crawler with thread-safe queue

Notes:
* Don't forget the self prefix
* Don't forget to mark the task done
* If I don't use the lock context,
  then make sure to release the lock before continuing to the next neighbor_url.
* Using an Event doesn't work,
  because you'll end up blocking on get forever when the queue is empty.
* Note that the queue uses a different lock than self.lock

Sources:
* https://leetcode.com/problems/web-crawler-multithreaded/discuss/434058/ThreadPoolExecutor-%2B-Queue-python-2
"""
import threading
from queue import Queue


def get_host_name(url):
    start = len("http://")
    i = start
    while i < len(url) and url[i] != "/":
        i += 1
    return url[start:i]


class Crawler:
    
    def __init__(self, htmlParser):
        self.htmlParser = htmlParser
        self.queue = Queue()
        self.lock = threading.Lock()
        self.visited = set()
        
    def _worker(self):
        while True:
            # Also, works if timeout=0.1 and then you don't need to send None
            # In that case, it will raise an Empty error eventually and that
            # will stop the submitted future.
            url = self.queue.get(block=True)

            if url is None:
                break

            neighbor_urls = self.htmlParser.getUrls(url)
            for neighbor_url in neighbor_urls:
                # This releases the lock if it reaches the end of the code
                # in the context, if there's an error or if continue is
                # called.
                with self.lock:
                    if neighbor_url in self.visited:
                        continue
                    if get_host_name(url) != get_host_name(neighbor_url):
                        continue
                    self.visited.add(neighbor_url)
                    self.queue.put(neighbor_url)
            self.queue.task_done()
                
    def crawl(self, startUrl):
        self.visited.clear()
        while self.queue.qsize() > 0:
            self.queue.get()

        self.visited.add(startUrl)
        self.queue.put(startUrl)
        
        # Using ThreadPoolExecutor would make a difference
        # if the worker function didn't just run continuously
        # until we tell it to stop.
        num_threads = 8
        threads = []
        for _ in range(num_threads):
            threads.append(threading.Thread(target=self._worker))
            threads[-1].start()

        self.queue.join()

        for _ in range(num_threads):
            self.queue.put(None)

        for i in range(num_threads):
            threads[i].join()
        
        return list(self.visited)


class Solution(object):
    def crawl(self, startUrl, htmlParser):
        """
        :type startUrl: str
        :type htmlParser: HtmlParser
        :rtype: List[str]
        """
        return Crawler(htmlParser).crawl(startUrl)


if __name__ == "__main__":
    class HtmlParser:

        def __init__(self):
            urls = [
                "http://news.yahoo.com",
                "http://news.yahoo.com/news",
                "http://news.yahoo.com/news/topics/",
                "http://news.google.com",
                "http://news.yahoo.com/us"
            ]
            edges = [[2,0],[2,1],[3,2],[3,1],[0,4]]
            self.adj = {}
            for u, v in edges:
                if urls[u] not in self.adj:
                    self.adj[urls[u]] = []
                self.adj[urls[u]].append(urls[v])

        def getUrls(self, url):
            return self.adj.get(url, [])

    expected = [
        "http://news.yahoo.com",
        "http://news.yahoo.com/news",
        "http://news.yahoo.com/news/topics/",
        "http://news.yahoo.com/us"
    ]
    expected.sort()
    htmlParser = HtmlParser()
    startUrl = "http://news.yahoo.com/news/topics/"
    solution = Solution()
    actual = solution.crawl(startUrl, htmlParser)
    actual.sort()
    print(actual)
    assert actual == expected
