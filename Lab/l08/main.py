from html.parser import HTMLParser
from urllib.parse import urljoin, urlparse
import os
import hashlib
import urllib.request
from contextlib import suppress
import threading
import queue

REQ_PARAMS = {"headers": {}}
OPEN_PARAMS = {"timeout": 0.5}
URL = ""
DEFAULT_CHARSET = "utf-8"
MAX_DEPTH = 3
MAX_CONN = 25
SAVE_DIR = "downs"


class LinkParser(HTMLParser):
    def __init__(self, url):
        super().__init__()
        self.url = url
        self.links = []

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            for attr, value in attrs:
                if attr == "href":
                    self.links.append(urljoin(self.url, value))


def save(url, save_dir, content):
    parsed = urlparse(url)
    idx = parsed.path.rfind("/")
    save_dir = os.path.join(save_dir, parsed.netloc + parsed.path[: idx + 1])
    f_name = parsed.path[idx + 1 :]
    if not f_name:
        f_name = hashlib.md5(content).hexdigest()
    _, ext = os.path.splitext(f_name)
    if not ext:
        f_name += ".no_ext"
    f_name = os.path.join(save_dir, f_name)
    os.makedirs(save_dir, exist_ok=True)
    try:
        with open(f_name, "wb") as f:
            f.write(content)
            print(f"[SAVED] {url}: {f_name}")
    except Exception as e:
        print(f"[ERROR] Fail to save {url}: {e}")


def crawl(url, depth, vis_lock, vis, que, *args, **kwargs):
    try:
        print(f"[CRAWLING] {url} (depth={depth})")
        with urllib.request.urlopen(
            urllib.request.Request(url, **REQ_PARAMS), *args, **kwargs
        ) as resp:
            content = resp.read()
            save(url, SAVE_DIR, content)
            if depth < MAX_DEPTH:
                with suppress(Exception):
                    parser = LinkParser(url)
                    parser.feed(
                        content.decode(
                            resp.headers.get_content_charset() or DEFAULT_CHARSET,
                            "ignore",
                        )
                    )
                    for link in parser.links:
                        link = link.split("#")[0]
                        with vis_lock:
                            if link not in vis:
                                que.put((link, depth + 1))
                                vis.add(link)
    except Exception as e:
        print(f"[ERROR] Fail to crawl {url}: {e}")


def worker(vis_lock, vis, que):
    while True:
        try:
            url, depth = que.get()
            crawl(url, depth, vis_lock, vis, que, **OPEN_PARAMS)
        except Exception as e:
            print(f"[ERROR] {e}")
        finally:
            que.task_done()


if __name__ == "__main__":
    l = URL if URL else input("URL = ")
    vis_lk = threading.Lock()
    v = set()
    v.add(l)
    q = queue.Queue()
    q.put((l, 0))
    for _ in range(MAX_CONN):
        t = threading.Thread(target=worker, args=(vis_lk, v, q), daemon=True)
        t.start()
    q.join()
