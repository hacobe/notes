"""Concurrent Web crawler without thread-safe queue.

Notes:
* If the queue is empty, it does not mean everything is done.
* Queue does not have to be bounded
* This is like the implementation that uses the Queue except that
  * No need for not_full condition or capacity
  * Add the following check self.not_empty.wait()
      if self.unfinished_tasks == 0:
        self.not_empty.notify_all()
        return
    (this obviates the need for adding Nones to the queue, join() or all_tasks_done)

Questions:
* When do you know that you're done?
* Is the wait call wrapped in a while loop?
* Will the wait call wait forever?
* Will every sleeping thread eventually get a signal to wake up?
* Are there no returns, continues, or errors in between lock acquire and release?
* Is every url only visited once?
"""
import collections
import threading

def get_host_name(url):
    return url.split("/")[2]

class Crawler:
    
    def __init__(self, htmlParser):
        self.htmlParser = htmlParser
        self.lock = threading.Lock()
        self.not_empty = threading.Condition(self.lock)
        self.queue = collections.deque()
        self.visited = set()
        self.unfinished_tasks = 0
        
    def _worker(self):
        while True:
            # url = queue.get()
            # without the notify for not_full, because the queue
            # does not have a max capacity.
            with self.lock:
                while len(self.queue) == 0:
                    # Check to see that all tasks are finished.
                    if self.unfinished_tasks == 0:
                        # Wake up all the threads.
                        self.not_empty.notify_all()
                        return
                    self.not_empty.wait()
                url = self.queue.popleft()
                
            neighbor_urls = self.htmlParser.getUrls(url)
            for neighbor_url in neighbor_urls:
                with self.lock:
                    if neighbor_url in self.visited:
                        continue
                    if get_host_name(neighbor_url) != get_host_name(url):
                        continue
                    self.visited.add(neighbor_url)

                    # queue.put(neighbor_url)
                    # without having a max capacity.
                    self.queue.append(neighbor_url)
                    self.unfinished_tasks += 1
                    self.not_empty.notify()

            # queue.task_done()
            # without checking that unfinished_tasks is non-negative
            # and without signaling all_tasks_done
            with self.lock:
                self.unfinished_tasks -= 1

    def crawl(self, startUrl):
        self.visited.clear()
        self.queue.clear()
        self.unfinished_tasks = 0

        self.visited.add(startUrl)
        self.queue.append(startUrl)
        self.unfinished_tasks += 1
        
        num_threads = 8
        threads = []
        for _ in range(num_threads):
            threads.append(threading.Thread(target=self._worker))
            threads[-1].start()
        
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
