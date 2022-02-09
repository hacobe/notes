"""Web crawler

Notes:
* Don't forget the self prefix
* Don't forget to mark the task done
* If I don't use the lock context, then make sure to release the lock before continuing to the next neighbor_url

Sources:
* https://leetcode.com/problems/web-crawler-multithreaded/discuss/434058/ThreadPoolExecutor-%2B-Queue-python-2
"""
import threading
import Queue


def get_host_name(url):
    start = len("http://")
    i = start
    while i < len(url) and url[i] != "/":
        i += 1
    return url[start:i]


class Crawler:
    
    def __init__(self, htmlParser):
        self.htmlParser = htmlParser
        self.queue = Queue.Queue()
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
