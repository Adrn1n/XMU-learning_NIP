<!--
网络编程IV

任务
实现一个简易的Web爬虫，从指定的一个初始页面的URL出发，执行操作：获取页面分析页面提取链接获取新页面……
为简单起见
仅考虑获取普通http页面，相关简要说明参见课本6.4.3
链接获取最多3层
-->
# Report 8
## 1. Experiment Name
Network Programming IV.

## 2. Experiment Tasks
- Implement a simple Web crawler that starts from a specified initial page URL and performs the following operations: fetch the page -> analyze the page -> extract links -> fetch new pages...
- For simplicity
    - only consider fetching ordinary http pages, as briefly described in section 6.4.3 of the textbook
    - the link extraction should be limited to a maximum depth of 3 layers

## 3. Experiment Environment and Tools
- M4 MacBook Air
- Python 3.12.12

## 4. Experiment Records and Result Analysis
### 4.1 Records
- `main.py`
    ```python
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

    ```

### 4.2 Analysis
```text
(base) b@bogon Lab %  cd /Users/Shared/Files/XMU/Learning/NIP/Lab ; /usr/bin/env /opt/anaconda3/bin/python /User
s/b/.vscode/extensions/ms-python.debugpy-2026.6.0-darwin-arm64/bundled/libs/debugpy/adapter/../../debugpy/launch
er 53521 -- /Users/Shared/Files/XMU/Learning/NIP/Lab/l08/main.py 
URL = http://mt.xmu.edu.cn/xmuslt/
[CRAWLING] http://mt.xmu.edu.cn/xmuslt/ (depth=0)
[SAVED] http://mt.xmu.edu.cn/xmuslt/: downs/mt.xmu.edu.cn/xmuslt/f9d6ca28769acbf76f8c3411731dc106.no_ext
[CRAWLING] javascript:OnSampleClick(101) (depth=1)
[ERROR] Fail to crawl javascript:OnSampleClick(101): <urlopen error unknown url type: javascript>
[CRAWLING] javascript:OnSampleClick(102) (depth=1)
[CRAWLING] javascript:OnSampleClick(301) (depth=1)
[ERROR] Fail to crawl javascript:OnSampleClick(301): <urlopen error unknown url type: javascript>
[CRAWLING] javascript:OnSampleClick(302) (depth=1)
[ERROR] Fail to crawl javascript:OnSampleClick(102): <urlopen error unknown url type: javascript>[CRAWLING] mailto:ydchen@xmu.edu.cn (depth=1)[CRAWLING] http://nlp.xmu.edu.cn/ (depth=1)
[ERROR] Fail to crawl javascript:OnSampleClick(302): <urlopen error unknown url type: javascript>


[ERROR] Fail to crawl mailto:ydchen@xmu.edu.cn: <urlopen error unknown url type: mailto>
[SAVED] http://nlp.xmu.edu.cn/: downs/nlp.xmu.edu.cn/ff1f08d2871eff3c5328b6edf75cf4b2.no_ext
[CRAWLING] javascript:void(0) (depth=2)[CRAWLING] http://nlp.xmu.edu.cn/index.html (depth=2)
[CRAWLING] http://nlp.xmu.edu.cn/research.html (depth=2)[CRAWLING] http://nlp.xmu.edu.cn/group.html (depth=2)[CRAWLING] http://nlp.xmu.edu.cn/newslist.html (depth=2)
[CRAWLING] http://nlp.xmu.edu.cn/links.html (depth=2)
[CRAWLING] http://jf.xmu.edu.cn:9080/static/index.html (depth=2)[CRAWLING] http://cloudtranslation.xmu.edu.cn (depth=2)[CRAWLING] http://nmt.xmu.edu.cn (depth=2)
[CRAWLING] http://jf.xmu.edu.cn (depth=2)
[CRAWLING] http://cloudtranslation.xmu.edu.cn/search (depth=2)
[CRAWLING] http://jf.xmu.edu.cn/variants.html (depth=2)

[CRAWLING] http://nlp.xmu.edu.cn/news/2026/0409.html (depth=2)[CRAWLING] http://nlp.xmu.edu.cn/news/2025/1110.html (depth=2)


[CRAWLING] http://nlp.xmu.edu.cn/news/2023/1214.html (depth=2)[CRAWLING] http://nlp.xmu.edu.cn/news/2023/1209.html (depth=2)
[CRAWLING] http://nlp.xmu.edu.cn/news/2023/1103.html (depth=2)


[CRAWLING] http://nlp.xmu.edu.cn/news/2023/0717.html (depth=2)
[CRAWLING] http://nlp.xmu.edu.cn/news/2023/0714.html (depth=2)
[CRAWLING] http://nlp.xmu.edu.cn:8085/2021/01/09/%e5%8c%97%e4%ba%ac%e8%88%aa%e7%a9%ba%e8%88%aa%e5%a4%a9%e5%a4%a7%e5%ad%a6%e9%83%91%e5%bf%97%e6%98%8e%e9%99%a2%e5%a3%ab%e5%8f%97%e9%82%80%e6%9d%a5%e5%8e%a6%e9%97%a8%e5%a4%a7%e5%ad%a6%e4%bd%9c/ (depth=2)
[ERROR] Fail to crawl javascript:void(0): <urlopen error unknown url type: javascript>

[CRAWLING] http://nlp.xmu.edu.cn:8085/2020/12/14/%e7%83%ad%e7%83%88%e7%a5%9d%e8%b4%ba%e6%88%91%e7%b3%bb%e9%99%88%e6%af%85%e4%b8%9c%e8%80%81%e5%b8%88%e6%8c%87%e5%af%bc%e7%9a%84%e4%bd%9c%e5%93%81%e6%96%a9%e8%8e%b7%e5%8d%8e%e4%b8%ba%e6%9d%af/ (depth=2)

[CRAWLING] mailto: (depth=2)
[ERROR] Fail to crawl mailto:: <urlopen error unknown url type: mailto>
[SAVED] http://nlp.xmu.edu.cn/news/2023/0717.html: downs/nlp.xmu.edu.cn/news/2023/0717.html
[CRAWLING] https://aclanthology.org/2023.acl-long.409/ (depth=3)
[SAVED] http://nlp.xmu.edu.cn/news/2023/1103.html: downs/nlp.xmu.edu.cn/news/2023/1103.html
[SAVED] http://nlp.xmu.edu.cn/news/2023/0714.html: downs/nlp.xmu.edu.cn/news/2023/0714.html[CRAWLING] https://doi.org/10.1016/j.neunet.2023.10.053 (depth=3)

[CRAWLING] https://doi.org/10.1016/j.inffus.2023.101830 (depth=3)
[SAVED] http://nlp.xmu.edu.cn/news/2025/1110.html: downs/nlp.xmu.edu.cn/news/2025/1110.html
[SAVED] http://nlp.xmu.edu.cn/news/2023/1214.html: downs/nlp.xmu.edu.cn/news/2023/1214.html
[SAVED] http://nlp.xmu.edu.cn/news/2026/0409.html: downs/nlp.xmu.edu.cn/news/2026/0409.html
[SAVED] http://nlp.xmu.edu.cn/index.html: downs/nlp.xmu.edu.cn/index.html
[SAVED] http://nlp.xmu.edu.cn/news/2023/1209.html: downs/nlp.xmu.edu.cn/news/2023/1209.html
[SAVED] http://nlp.xmu.edu.cn/links.html: downs/nlp.xmu.edu.cn/links.html
[CRAWLING] https://github.com/XMUNLP (depth=3)[CRAWLING] https://github.com/thumt/THUMT (depth=3)[CRAWLING] https://github.com/facebookresearch (depth=3)[CRAWLING] https://github.com/tensorflow/models/tree/master/research (depth=3)[CRAWLING] http://nlp.xmu.edu.cn:8085/ (depth=3)
[CRAWLING] http://www.52nlp.cn (depth=3)
[CRAWLING] https://nlpers.blogspot.com/ (depth=3)



[CRAWLING] https://ai.googleblog.com/ (depth=3)
[CRAWLING] https://deepmind.com/blog/ (depth=3)
[CRAWLING] https://www.microsoft.com/en-us/research/blog/ (depth=3)[CRAWLING] https://research.fb.com/blog/ (depth=3)


[SAVED] http://nlp.xmu.edu.cn/newslist.html: downs/nlp.xmu.edu.cn/newslist.html
[CRAWLING] http://www.google.com/ (depth=3)
[SAVED] http://nlp.xmu.edu.cn/research.html: downs/nlp.xmu.edu.cn/research.html
[CRAWLING] http://www.bing.com/ (depth=3)
[SAVED] http://nlp.xmu.edu.cn/group.html: downs/nlp.xmu.edu.cn/group.html
[CRAWLING] http://www.wolframalpha.com/ (depth=3)
[ERROR] Fail to crawl https://research.fb.com/blog/: <urlopen error [Errno 8] nodename nor servname provided, or not known>
[CRAWLING] http://scholar.google.com/ (depth=3)
[ERROR] Fail to crawl http://jf.xmu.edu.cn: HTTP Error 400: Bad Request
[ERROR] Fail to crawl http://jf.xmu.edu.cn/variants.html: HTTP Error 400: Bad Request
[CRAWLING] http://academic.research.microsoft.com/ (depth=3)
[CRAWLING] https://arxiv.org/ (depth=3)
[ERROR] Fail to crawl http://academic.research.microsoft.com/: <urlopen error [Errno 8] nodename nor servname provided, or not known>
[CRAWLING] http://www.arxiv-sanity.com/ (depth=3)
[ERROR] Fail to crawl https://nlpers.blogspot.com/: <urlopen error [Errno 61] Connection refused>
[CRAWLING] http://www.aclweb.org (depth=3)
[SAVED] http://cloudtranslation.xmu.edu.cn: downs/cloudtranslation.xmu.edu.cn/bb986e2d7d842c5c9996dc3562ba35ae.no_ext
[CRAWLING] http://www.aclweb.org/anthology/ (depth=3)
[SAVED] http://www.bing.com/: downs/www.bing.com/54e2c4bdcfd12a9bb8f7c38ddbcc0c06.no_ext
[CRAWLING] http://www.nist.gov/tac/ (depth=3)
[SAVED] http://cloudtranslation.xmu.edu.cn/search: downs/cloudtranslation.xmu.edu.cn/search.no_ext
[CRAWLING] http://www.statmt.org/moses/?n=Moses.Marathons (depth=3)
[SAVED] https://arxiv.org/: downs/arxiv.org/ab95abe6c062a6a1f0e920ec1e52959f.no_ext
[CRAWLING] http://sigir.org (depth=3)
[ERROR] Fail to crawl http://nlp.xmu.edu.cn:8085/2021/01/09/%e5%8c%97%e4%ba%ac%e8%88%aa%e7%a9%ba%e8%88%aa%e5%a4%a9%e5%a4%a7%e5%ad%a6%e9%83%91%e5%bf%97%e6%98%8e%e9%99%a2%e5%a3%ab%e5%8f%97%e9%82%80%e6%9d%a5%e5%8e%a6%e9%97%a8%e5%a4%a7%e5%ad%a6%e4%bd%9c/: <urlopen error timed out>
[CRAWLING] http://cjc.ict.ac.cn/ (depth=3)
[ERROR] Fail to crawl http://nlp.xmu.edu.cn:8085/2020/12/14/%e7%83%ad%e7%83%88%e7%a5%9d%e8%b4%ba%e6%88%91%e7%b3%bb%e9%99%88%e6%af%85%e4%b8%9c%e8%80%81%e5%b8%88%e6%8c%87%e5%af%bc%e7%9a%84%e4%bd%9c%e5%93%81%e6%96%a9%e8%8e%b7%e5%8d%8e%e4%b8%ba%e6%9d%af/: <urlopen error timed out>
[CRAWLING] http://www.jos.org.cn/ch/index.aspx (depth=3)
[ERROR] Fail to crawl http://nlp.xmu.edu.cn:8085/: <urlopen error timed out>
[CRAWLING] http://crad.ict.ac.cn/ (depth=3)
[ERROR] Fail to crawl https://github.com/facebookresearch: <urlopen error timed out>
[CRAWLING] http://talip.acm.org/ (depth=3)
[ERROR] Fail to crawl http://scholar.google.com/: <urlopen error timed out>
[CRAWLING] http://www.kluweronline.com/issn/0922-6567 (depth=3)
[SAVED] http://cjc.ict.ac.cn/: downs/cjc.ict.ac.cn/94c938e3220fd92a59f4211498b4c340.no_ext
[CRAWLING] http://www.jsjkx.com/jsjkx/ch/index.aspx (depth=3)
[ERROR] Fail to crawl http://nmt.xmu.edu.cn: The read operation timed out
[CRAWLING] http://www.msra.cn/ (depth=3)
[ERROR] Fail to crawl https://github.com/tensorflow/models/tree/master/research: The read operation timed out
[CRAWLING] http://www-2.cs.cmu.edu/~ralf/nlp.html (depth=3)
[ERROR] Fail to crawl https://github.com/XMUNLP: The read operation timed out
[CRAWLING] http://www.cs.cornell.edu/Info/Projects/NLP/ (depth=3)
[ERROR] Fail to crawl http://crad.ict.ac.cn/: HTTP Error 403: Forbidden
[CRAWLING] http://www1.cs.columbia.edu/nlp/index.cgi (depth=3)
[ERROR] Fail to crawl http://www.jsjkx.com/jsjkx/ch/index.aspx: HTTP Error 403: Forbidden
[CRAWLING] http://nlp.stanford.edu/ (depth=3)
[ERROR] Fail to crawl http://talip.acm.org/: HTTP Error 403: Forbidden
[CRAWLING] http://nlp.cs.berkeley.edu/Main.html (depth=3)
[ERROR] Fail to crawl https://www.microsoft.com/en-us/research/blog/: <urlopen error _ssl.c:993: The handshake operation timed out>
[CRAWLING] http://www.ldc.upenn.edu/ (depth=3)
[ERROR] Fail to crawl http://jf.xmu.edu.cn:9080/static/index.html: <urlopen error timed out>
[CRAWLING] http://www.cs.ust.hk/~hltc/ (depth=3)
[ERROR] Fail to crawl http://www.google.com/: <urlopen error timed out>
[CRAWLING] http://www-nlp.stanford.edu/links/statnlp.html (depth=3)
[ERROR] Fail to crawl https://ai.googleblog.com/: <urlopen error timed out>
[CRAWLING] http://acs.lbl.gov/software/colt/ (depth=3)
[ERROR] Fail to crawl http://www.arxiv-sanity.com/: <urlopen error timed out>
[CRAWLING] http://www.csie.ntu.edu.tw/~cjlin/liblinear/ (depth=3)
[ERROR] Fail to crawl https://github.com/thumt/THUMT: <urlopen error timed out>
[CRAWLING] http://dragon.ischool.drexel.edu/default.asp (depth=3)
[SAVED] https://aclanthology.org/2023.acl-long.409/: downs/aclanthology.org/2023.acl-long.409/6b687d017141a426f937be6fee305fc4.no_ext
[CRAWLING] http://www.statmt.org/moses/ (depth=3)
[ERROR] Fail to crawl http://www.msra.cn/: <urlopen error timed out>
[CRAWLING] http://www.speech.sri.com/projects/srilm/ (depth=3)
[ERROR] Fail to crawl http://www.wolframalpha.com/: <urlopen error _ssl.c:993: The handshake operation timed out>
[CRAWLING] https://cwiki.apache.org/confluence/display/JOSHUA/ (depth=3)
[ERROR] Fail to crawl http://www.ldc.upenn.edu/: HTTP Error 403: Forbidden
[CRAWLING] https://github.com/tmikolov/word2vec (depth=3)
[ERROR] Fail to crawl https://doi.org/10.1016/j.neunet.2023.10.053: <urlopen error _ssl.c:993: The handshake operation timed out>
[CRAWLING] https://www.tensorflow.org/?hl=zh-cn (depth=3)
[ERROR] Fail to crawl http://www.kluweronline.com/issn/0922-6567: HTTP Error 404: Not Found
[CRAWLING] http://deeplearning.net/software/theano/ (depth=3)
[ERROR] Fail to crawl http://www.52nlp.cn: The read operation timed out
[CRAWLING] https://pytorch.org/ (depth=3)
[ERROR] Fail to crawl http://www.jos.org.cn/ch/index.aspx: The read operation timed out
[CRAWLING] http://torch.ch/ (depth=3)
[SAVED] http://sigir.org: downs/sigir.org/c89b00ce1b63c365624c3ac3f2f547aa.no_ext
[CRAWLING] https://deeplearning4j.org/ (depth=3)
[ERROR] Fail to crawl http://dragon.ischool.drexel.edu/default.asp: <urlopen error timed out>
[CRAWLING] http://homepages.inf.ed.ac.uk/pkoehn/ (depth=3)
[ERROR] Fail to crawl http://www.nist.gov/tac/: HTTP Error 403: Forbidden
[CRAWLING] http://web.science.mq.edu.au/~mjohnson/ (depth=3)
[SAVED] http://www.cs.ust.hk/~hltc/: downs/www.cs.ust.hk/~hltc/4bf0186c45529ce495697f18b25c1ee7.no_ext
[CRAWLING] http://nlp.xmu.edu.cn:8085/2020/09/29/%e7%a5%9d%e8%b4%ba%e6%88%91%e5%ae%9e%e9%aa%8c%e5%ae%a4%e7%a5%9e%e7%bb%8f%e6%89%8b%e8%af%ad%e7%bf%bb%e8%af%91%e9%a1%b9%e7%9b%ae%e5%9b%a2%e9%98%9f%e5%85%a5%e5%9b%b4%e7%ac%ac%e4%ba%8c/ (depth=3)
[ERROR] Fail to crawl http://www.speech.sri.com/projects/srilm/: <urlopen error timed out>
[CRAWLING] http://nlp.xmu.edu.cn:8085/2019/11/11/%e5%8d%8e%e4%b8%ba%e8%af%ba%e4%ba%9a%e6%96%b9%e8%88%9f%e5%ae%9e%e9%aa%8c%e5%ae%a4%e8%af%ad%e9%9f%b3%e8%af%ad%e4%b9%89%e9%a6%96%e5%b8%ad%e7%a7%91%e5%ad%a6%e5%ae%b6%e5%88%98%e7%be%a4-%e5%ba%94%e9%82%80/ (depth=3)
[SAVED] http://nlp.cs.berkeley.edu/Main.html: downs/nlp.cs.berkeley.edu/Main.html
[CRAWLING] http://nlp.xmu.edu.cn:8085/2019/11/10/%e5%a4%a9%e6%b4%a5%e5%a4%a7%e5%ad%a6%e7%86%8a%e5%be%b7%e6%84%8f%e6%95%99%e6%8e%88%e5%8f%8a%e5%8d%97%e4%ba%ac%e5%a4%a7%e5%ad%a6%e9%bb%84%e4%b9%a6%e5%89%91%e5%89%af%e6%95%99%e6%8e%88-%e5%ba%94%e9%82%80/ (depth=3)
[ERROR] Fail to crawl https://github.com/tmikolov/word2vec: <urlopen error timed out>
[CRAWLING] http://nlp.xmu.edu.cn:8085/2019/09/27/%e5%ae%9e%e9%aa%8c%e5%ae%a4%e5%9b%9b%e5%90%8d%e5%b8%88%e7%94%9f%e5%8f%82%e4%b8%8e%e7%ac%ac%e5%8d%81%e4%ba%94%e5%b1%8a%e5%85%a8%e5%9b%bd%e6%9c%ba%e5%99%a8%e7%bf%bb%e8%af%91%e5%a4%a7%e4%bc%9a/ (depth=3)
[SAVED] http://www-2.cs.cmu.edu/~ralf/nlp.html: downs/www-2.cs.cmu.edu/~ralf/nlp.html
[CRAWLING] http://nlp.xmu.edu.cn:8085/2019/07/15/祝贺实验室不能说的秘密-神经手语翻译项目团 (depth=3)
[ERROR] Fail to crawl http://nlp.xmu.edu.cn:8085/2019/07/15/祝贺实验室不能说的秘密-神经手语翻译项目团: 'ascii' codec can't encode characters in position 16-26: ordinal not in range(128)
[CRAWLING] http://nlp.xmu.edu.cn:8085/2019/04/02/yuqing/ (depth=3)
[ERROR] Fail to crawl https://doi.org/10.1016/j.inffus.2023.101830: <urlopen error _ssl.c:993: The handshake operation timed out>
[CRAWLING] http://nlp.xmu.edu.cn:8085/2018/11/25/oracle/ (depth=3)
[ERROR] Fail to crawl http://deeplearning.net/software/theano/: <urlopen error timed out>
[CRAWLING] http://nlp.xmu.edu.cn:8085/2018/11/21/%e5%8c%97%e4%ba%ac%e5%a4%a7%e5%ad%a6%e8%ae%a1%e7%ae%97%e6%9c%ba%e7%a7%91%e5%ad%a6%e6%8a%80%e6%9c%af%e7%a0%94%e7%a9%b6%e6%89%80%e4%b8%87%e5%b0%8f%e5%86%9b%e5%8d%9a%e5%a3%ab%e5%8f%8a%e8%85%be%e8%ae%afai/ (depth=3)
[ERROR] Fail to crawl http://www.aclweb.org/anthology/: <urlopen error _ssl.c:993: The handshake operation timed out>
[CRAWLING] http://www.cipsc.org.cn/annual2018/ (depth=3)
[SAVED] http://torch.ch/: downs/torch.ch/9c677d39c4ec4035936ae6a73a46f8b8.no_ext
[CRAWLING] http://nlp.xmu.edu.cn:8085/2018/11/05/%E5%AE%9E%E9%AA%8C%E5%AE%A4%E7%A0%94%E5%8F%91%E7%9A%84%E6%9C%BA%E5%99%A8%E5%90%8C%E4%BC%A0%E7%B3%BB%E7%BB%9F%E4%BA%AE%E7%9B%B8%E7%A6%8F%E5%BB%BA%E7%9C%81%E4%BA%BA%E5%B7%A5%E6%99%BA%E8%83%BD%E5%AD%A6/ (depth=3)
[ERROR] Fail to crawl https://deeplearning4j.org/: HTTP Error 403: Forbidden
[CRAWLING] http://nlp.xmu.edu.cn:8085/2018/10/27/%E5%AE%9E%E9%AA%8C%E5%AE%A4%E4%B8%BB%E4%BB%BB%E5%8F%B2%E6%99%93%E4%B8%9C%E6%95%99%E6%8E%88%E7%8E%87%E9%A2%86%E5%8D%81%E4%B8%80%E5%90%8D%E5%B8%88%E7%94%9F%E5%8F%82%E5%8A%A0%E7%AC%AC%E5%8D%81%E5%9B%9B/ (depth=3)
[ERROR] Fail to crawl http://www.cs.cornell.edu/Info/Projects/NLP/: <urlopen error _ssl.c:993: The handshake operation timed out>
[CRAWLING] http://nlp.xmu.edu.cn:8085/2018/08/01/%E5%AE%9E%E9%AA%8C%E5%AE%A4%E4%B8%83%E5%90%8D%E7%A1%95%E5%A3%AB%E7%94%9F%E5%8F%82%E5%8A%A0%E7%AC%AC%E5%8D%81%E4%B8%89%E5%B1%8A%E4%B8%AD%E5%9B%BD%E4%B8%AD%E6%96%87%E4%BF%A1%E6%81%AF%E5%AD%A6%E4%BC%9A/ (depth=3)
[SAVED] http://www.cipsc.org.cn/annual2018/: downs/www.cipsc.org.cn/annual2018/fcc8d3ae55a69ebe6bec1f5531304b7e.no_ext
[CRAWLING] http://nlp.xmu.edu.cn:8085/2018/07/26/%E8%97%8F%E6%B1%89%E7%A5%9E%E7%BB%8F%E6%9C%BA%E5%99%A8%E7%BF%BB%E8%AF%91%E6%A8%A1%E5%9E%8B%E5%8F%8A%E7%B3%BB%E7%BB%9F%E5%AE%9E%E7%8E%B0%E9%A1%B9%E7%9B%AE%E9%89%B4%E5%AE%9A%E4%BC%9A/ (depth=3)
[ERROR] Fail to crawl http://nlp.xmu.edu.cn:8085/2020/09/29/%e7%a5%9d%e8%b4%ba%e6%88%91%e5%ae%9e%e9%aa%8c%e5%ae%a4%e7%a5%9e%e7%bb%8f%e6%89%8b%e8%af%ad%e7%bf%bb%e8%af%91%e9%a1%b9%e7%9b%ae%e5%9b%a2%e9%98%9f%e5%85%a5%e5%9b%b4%e7%ac%ac%e4%ba%8c/: <urlopen error timed out>
[CRAWLING] http://nlp.xmu.edu.cn:8085/2018/07/17/%E4%B8%8A%E6%B5%B7%E4%BA%A4%E9%80%9A%E5%A4%A7%E5%AD%A6%E5%A4%96%E5%9B%BD%E8%AF%AD%E5%AD%A6%E9%99%A2%E8%83%A1%E5%BC%80%E5%AE%9D%E9%99%A2%E9%95%BF%E8%AE%BF%E9%97%AE%E5%AE%9E%E9%AA%8C%E5%AE%A4/ (depth=3)
[ERROR] Fail to crawl http://www.aclweb.org: HTTP Error 418: Unknown
[CRAWLING] http://nlp.xmu.edu.cn:8085/2018/07/12/jgw/ (depth=3)
[ERROR] Fail to crawl http://nlp.xmu.edu.cn:8085/2019/11/11/%e5%8d%8e%e4%b8%ba%e8%af%ba%e4%ba%9a%e6%96%b9%e8%88%9f%e5%ae%9e%e9%aa%8c%e5%ae%a4%e8%af%ad%e9%9f%b3%e8%af%ad%e4%b9%89%e9%a6%96%e5%b8%ad%e7%a7%91%e5%ad%a6%e5%ae%b6%e5%88%98%e7%be%a4-%e5%ba%94%e9%82%80/: <urlopen error timed out>
[CRAWLING] http://nlp.xmu.edu.cn:8085/2018/06/28/%E3%80%90%E5%AD%A6%E6%9C%AF%E8%AE%B2%E5%BA%A7%E3%80%91%E5%8F%B2%E6%99%93%E4%B8%9C%E6%95%99%E6%8E%88%E4%BD%9C%E6%9C%BA%E5%99%A8%E5%90%8C%E4%BC%A0%E6%8A%80%E6%9C%AF%E6%8E%A2%E8%AE%A8/ (depth=3)
[ERROR] Fail to crawl http://nlp.xmu.edu.cn:8085/2019/11/10/%e5%a4%a9%e6%b4%a5%e5%a4%a7%e5%ad%a6%e7%86%8a%e5%be%b7%e6%84%8f%e6%95%99%e6%8e%88%e5%8f%8a%e5%8d%97%e4%ba%ac%e5%a4%a7%e5%ad%a6%e9%bb%84%e4%b9%a6%e5%89%91%e5%89%af%e6%95%99%e6%8e%88-%e5%ba%94%e9%82%80/: <urlopen error timed out>
[CRAWLING] http://nlp.xmu.edu.cn:8085/2018/06/25/xmucwmt2018/ (depth=3)
[SAVED] http://nlp.stanford.edu/: downs/nlp.stanford.edu/15a6bc92c9f86680f26ccd4d5e430ede.no_ext
[CRAWLING] http://nlp.xmu.edu.cn:8085/2018/02/01/%E3%80%8A%E5%8E%A6%E9%97%A8%E5%A4%A7%E5%AD%A6%E5%AD%A6%E6%8A%A5%EF%BC%88%E8%87%AA%E7%84%B6%E7%A7%91%E5%AD%A6%E7%89%88%EF%BC%89%E3%80%8B%E5%BE%81%E7%A8%BF/ (depth=3)
[ERROR] Fail to crawl http://nlp.xmu.edu.cn:8085/2019/09/27/%e5%ae%9e%e9%aa%8c%e5%ae%a4%e5%9b%9b%e5%90%8d%e5%b8%88%e7%94%9f%e5%8f%82%e4%b8%8e%e7%ac%ac%e5%8d%81%e4%ba%94%e5%b1%8a%e5%85%a8%e5%9b%bd%e6%9c%ba%e5%99%a8%e7%bf%bb%e8%af%91%e5%a4%a7%e4%bc%9a/: <urlopen error timed out>
[CRAWLING] http://nlp.xmu.edu.cn:8085/2017/03/19/%E5%BE%B7%E5%9B%BD%E4%BA%BA%E5%B7%A5%E6%99%BA%E8%83%BD%E7%A0%94%E7%A9%B6%E4%B8%AD%E5%BF%83%E7%A7%91%E5%AD%A6%E4%B8%BB%E4%BB%BB%EF%BC%8C%E6%AC%A7%E6%B4%B2%E7%A7%91%E5%AD%A6%E9%99%A2%E9%99%A2%E5%A3%AB/ (depth=3)
[ERROR] Fail to crawl http://nlp.xmu.edu.cn:8085/2019/04/02/yuqing/: <urlopen error timed out>
[CRAWLING] http://nlp.xmu.edu.cn:8085/2017/03/18/%E5%8F%B2%E6%99%93%E4%B8%9C%E6%95%99%E6%8E%88%E4%B8%BB%E6%8C%81%E4%B8%A4%E5%B2%B8%E4%B9%A6%E5%8D%B7%E5%AD%97%E4%BB%8A%E9%9F%B3%E5%BC%82%E5%90%8C%E4%B8%93%E9%A2%98%E7%A0%94%E7%A9%B6%E7%A0%94%E8%AE%A8/ (depth=3)
[ERROR] Fail to crawl http://nlp.xmu.edu.cn:8085/2018/11/25/oracle/: <urlopen error timed out>
[CRAWLING] http://nlp.xmu.edu.cn:8085/2016/12/24/%E5%AE%9E%E9%AA%8C%E5%AE%A4%E5%8F%B2%E6%99%93%E4%B8%9C%E6%95%99%E6%8E%88%E8%8E%B7%E9%92%B1%E4%BC%9F%E9%95%BF%E4%B8%AD%E6%96%87%E4%BF%A1%E6%81%AF%E5%A4%84%E7%90%86%E7%A7%91%E5%AD%A6%E6%8A%80%E6%9C%AF/ (depth=3)
[SAVED] http://www.statmt.org/moses/?n=Moses.Marathons: downs/www.statmt.org/moses/faec7e3726d7faba78243c9945636d81.no_ext
[CRAWLING] http://nlp.xmu.edu.cn:8085/2016/11/18/%E9%9D%A2%E5%90%91%E8%97%8F%E8%AF%AD%E7%9A%84%E8%B7%A8%E8%AF%AD%E8%A8%80%E8%88%86%E6%83%85%E5%88%86%E6%9E%90%E4%B8%8E%E6%A3%80%E6%B5%8B%E5%85%B3%E9%94%AE%E6%8A%80%E6%9C%AF%E7%A0%94%E7%A9%B6/ (depth=3)
[SAVED] http://web.science.mq.edu.au/~mjohnson/: downs/web.science.mq.edu.au/~mjohnson/30d4a97ef1402a125cf6ce0d6130b3e9.no_ext
[CRAWLING] http://nlp.xmu.edu.cn:8085/2016/08/15/%E4%B8%AD%E5%A4%AE%E6%95%99%E8%82%B2%E4%B8%80%E5%8F%B0%E7%9A%84%E4%B8%93%E9%A2%98%E7%89%87%E3%80%8A%E6%BD%AE%E5%B9%B3%E4%B8%A4%E5%B2%B8%E9%98%94%E3%80%8B%E6%8F%90%E5%88%B0%E6%88%91%E7%BB%84%E7%9A%84/ (depth=3)
[ERROR] Fail to crawl http://www1.cs.columbia.edu/nlp/index.cgi: timed out
[CRAWLING] http://nlp.xmu.edu.cn:8085/2016/03/30/jfhanzizhuanhuan/ (depth=3)
[ERROR] Fail to crawl http://nlp.xmu.edu.cn:8085/2018/11/21/%e5%8c%97%e4%ba%ac%e5%a4%a7%e5%ad%a6%e8%ae%a1%e7%ae%97%e6%9c%ba%e7%a7%91%e5%ad%a6%e6%8a%80%e6%9c%af%e7%a0%94%e7%a9%b6%e6%89%80%e4%b8%87%e5%b0%8f%e5%86%9b%e5%8d%9a%e5%a3%ab%e5%8f%8a%e8%85%be%e8%ae%afai/: <urlopen error timed out>
[CRAWLING] http://nlp.xmu.edu.cn:8085/2015/09/24/cwmt2015conference/ (depth=3)
[ERROR] Fail to crawl http://nlp.xmu.edu.cn:8085/2018/11/05/%E5%AE%9E%E9%AA%8C%E5%AE%A4%E7%A0%94%E5%8F%91%E7%9A%84%E6%9C%BA%E5%99%A8%E5%90%8C%E4%BC%A0%E7%B3%BB%E7%BB%9F%E4%BA%AE%E7%9B%B8%E7%A6%8F%E5%BB%BA%E7%9C%81%E4%BA%BA%E5%B7%A5%E6%99%BA%E8%83%BD%E5%AD%A6/: <urlopen error timed out>
[CRAWLING] http://nlp.xmu.edu.cn:8085/2015/08/19/%E7%AC%AC%E4%BA%8C%E5%B1%8A%E8%97%8F%E6%96%87%E4%BF%A1%E6%81%AF%E5%A4%84%E7%90%86%E5%AD%A6%E6%9C%AF%E7%A0%94%E8%AE%A8%E4%BC%9A%E5%9C%A8%E8%A5%BF%E5%8C%97%E6%B0%91%E6%97%8F%E5%A4%A7%E5%AD%A6%E4%B8%BE/ (depth=3)
[ERROR] Fail to crawl https://cwiki.apache.org/confluence/display/JOSHUA/: The read operation timed out
[CRAWLING] http://nlp.xmu.edu.cn:8085/2015/08/04/%E6%88%91%E7%BB%84%E5%8F%82%E5%8A%A0cwmt2015%E7%9A%84%E8%AF%84%E6%B5%8B%E7%BB%93%E6%9E%9C%E5%85%AC%E5%B8%83/ (depth=3)
[ERROR] Fail to crawl http://nlp.xmu.edu.cn:8085/2018/10/27/%E5%AE%9E%E9%AA%8C%E5%AE%A4%E4%B8%BB%E4%BB%BB%E5%8F%B2%E6%99%93%E4%B8%9C%E6%95%99%E6%8E%88%E7%8E%87%E9%A2%86%E5%8D%81%E4%B8%80%E5%90%8D%E5%B8%88%E7%94%9F%E5%8F%82%E5%8A%A0%E7%AC%AC%E5%8D%81%E5%9B%9B/: <urlopen error timed out>
[CRAWLING] http://nlp.xmu.edu.cn:8085/2014/11/19/simplify2tradition/ (depth=3)
[ERROR] Fail to crawl http://nlp.xmu.edu.cn:8085/2018/08/01/%E5%AE%9E%E9%AA%8C%E5%AE%A4%E4%B8%83%E5%90%8D%E7%A1%95%E5%A3%AB%E7%94%9F%E5%8F%82%E5%8A%A0%E7%AC%AC%E5%8D%81%E4%B8%89%E5%B1%8A%E4%B8%AD%E5%9B%BD%E4%B8%AD%E6%96%87%E4%BF%A1%E6%81%AF%E5%AD%A6%E4%BC%9A/: <urlopen error timed out>
[CRAWLING] http://nlp.xmu.edu.cn:8085/2014/08/ (depth=3)
[ERROR] Fail to crawl http://nlp.xmu.edu.cn:8085/2018/07/26/%E8%97%8F%E6%B1%89%E7%A5%9E%E7%BB%8F%E6%9C%BA%E5%99%A8%E7%BF%BB%E8%AF%91%E6%A8%A1%E5%9E%8B%E5%8F%8A%E7%B3%BB%E7%BB%9F%E5%AE%9E%E7%8E%B0%E9%A1%B9%E7%9B%AE%E9%89%B4%E5%AE%9A%E4%BC%9A/: <urlopen error timed out>
[CRAWLING] http://nlp.xmu.edu.cn:8085/2013/05/13/checks2fchinesesystemdevelopment/ (depth=3)
[SAVED] https://deepmind.com/blog/: downs/deepmind.com/blog/0c55371214ba9f1157d33cbf5b01bef2.no_ext
[CRAWLING] http://121.192.180.171:8080/tr.html (depth=3)
[ERROR] Fail to crawl http://nlp.xmu.edu.cn:8085/2018/07/17/%E4%B8%8A%E6%B5%B7%E4%BA%A4%E9%80%9A%E5%A4%A7%E5%AD%A6%E5%A4%96%E5%9B%BD%E8%AF%AD%E5%AD%A6%E9%99%A2%E8%83%A1%E5%BC%80%E5%AE%9D%E9%99%A2%E9%95%BF%E8%AE%BF%E9%97%AE%E5%AE%9E%E9%AA%8C%E5%AE%A4/: <urlopen error timed out>
[CRAWLING] http://121.192.180.171:8080/segtag.html (depth=3)
[ERROR] Fail to crawl http://nlp.xmu.edu.cn:8085/2018/07/12/jgw/: <urlopen error timed out>
[CRAWLING] http://121.192.180.172 (depth=3)
[ERROR] Fail to crawl http://nlp.xmu.edu.cn:8085/2018/06/28/%E3%80%90%E5%AD%A6%E6%9C%AF%E8%AE%B2%E5%BA%A7%E3%80%91%E5%8F%B2%E6%99%93%E4%B8%9C%E6%95%99%E6%8E%88%E4%BD%9C%E6%9C%BA%E5%99%A8%E5%90%8C%E4%BC%A0%E6%8A%80%E6%9C%AF%E6%8E%A2%E8%AE%A8/: <urlopen error timed out>
[CRAWLING] http://121.192.180.171:8080/webkwic.html (depth=3)
[ERROR] Fail to crawl http://nlp.xmu.edu.cn:8085/2018/06/25/xmucwmt2018/: <urlopen error timed out>
[CRAWLING] http://121.192.180.171:8080/corpus_cn.html (depth=3)
[ERROR] Fail to crawl http://nlp.xmu.edu.cn:8085/2018/02/01/%E3%80%8A%E5%8E%A6%E9%97%A8%E5%A4%A7%E5%AD%A6%E5%AD%A6%E6%8A%A5%EF%BC%88%E8%87%AA%E7%84%B6%E7%A7%91%E5%AD%A6%E7%89%88%EF%BC%89%E3%80%8B%E5%BE%81%E7%A8%BF/: <urlopen error timed out>
[CRAWLING] http://121.192.180.171:8080/e.html (depth=3)
[SAVED] http://acs.lbl.gov/software/colt/: downs/acs.lbl.gov/software/colt/1e9422008e56b765e3f12ec15ab4a78b.no_ext
[CRAWLING] http://121.192.180.171:8080/dic.html (depth=3)
[ERROR] Fail to crawl http://nlp.xmu.edu.cn:8085/2017/03/19/%E5%BE%B7%E5%9B%BD%E4%BA%BA%E5%B7%A5%E6%99%BA%E8%83%BD%E7%A0%94%E7%A9%B6%E4%B8%AD%E5%BF%83%E7%A7%91%E5%AD%A6%E4%B8%BB%E4%BB%BB%EF%BC%8C%E6%AC%A7%E6%B4%B2%E7%A7%91%E5%AD%A6%E9%99%A2%E9%99%A2%E5%A3%AB/: <urlopen error timed out>
[CRAWLING] http://121.192.180.171:8080/clir.html (depth=3)
[ERROR] Fail to crawl http://homepages.inf.ed.ac.uk/pkoehn/: HTTP Error 404: Not Found
[CRAWLING] http://121.192.180.172/sccl/ (depth=3)
[ERROR] Fail to crawl http://nlp.xmu.edu.cn:8085/2017/03/18/%E5%8F%B2%E6%99%93%E4%B8%9C%E6%95%99%E6%8E%88%E4%B8%BB%E6%8C%81%E4%B8%A4%E5%B2%B8%E4%B9%A6%E5%8D%B7%E5%AD%97%E4%BB%8A%E9%9F%B3%E5%BC%82%E5%90%8C%E4%B8%93%E9%A2%98%E7%A0%94%E7%A9%B6%E7%A0%94%E8%AE%A8/: <urlopen error timed out>
[CRAWLING] http://121.192.180.171:8080/ (depth=3)
[ERROR] Fail to crawl http://nlp.xmu.edu.cn:8085/2016/12/24/%E5%AE%9E%E9%AA%8C%E5%AE%A4%E5%8F%B2%E6%99%93%E4%B8%9C%E6%95%99%E6%8E%88%E8%8E%B7%E9%92%B1%E4%BC%9F%E9%95%BF%E4%B8%AD%E6%96%87%E4%BF%A1%E6%81%AF%E5%A4%84%E7%90%86%E7%A7%91%E5%AD%A6%E6%8A%80%E6%9C%AF/: <urlopen error timed out>
[ERROR] Fail to crawl http://nlp.xmu.edu.cn:8085/2016/11/18/%E9%9D%A2%E5%90%91%E8%97%8F%E8%AF%AD%E7%9A%84%E8%B7%A8%E8%AF%AD%E8%A8%80%E8%88%86%E6%83%85%E5%88%86%E6%9E%90%E4%B8%8E%E6%A3%80%E6%B5%8B%E5%85%B3%E9%94%AE%E6%8A%80%E6%9C%AF%E7%A0%94%E7%A9%B6/: <urlopen error timed out>[CRAWLING] http://nlp.xmu.edu.cn/teachers/ydchen/index.html (depth=3)

[CRAWLING] https://informatics.xmu.edu.cn/info/1395/25159.htm (depth=3)
[SAVED] http://nlp.xmu.edu.cn/teachers/ydchen/index.html: downs/nlp.xmu.edu.cn/teachers/ydchen/index.html
[CRAWLING] https://informatics.xmu.edu.cn/info/1395/25199.htm (depth=3)
[ERROR] Fail to crawl http://nlp.xmu.edu.cn:8085/2016/08/15/%E4%B8%AD%E5%A4%AE%E6%95%99%E8%82%B2%E4%B8%80%E5%8F%B0%E7%9A%84%E4%B8%93%E9%A2%98%E7%89%87%E3%80%8A%E6%BD%AE%E5%B9%B3%E4%B8%A4%E5%B2%B8%E9%98%94%E3%80%8B%E6%8F%90%E5%88%B0%E6%88%91%E7%BB%84%E7%9A%84/: <urlopen error timed out>
[CRAWLING] http://home.ibookman.net/ (depth=3)
[ERROR] Fail to crawl http://home.ibookman.net/: <urlopen error [Errno 8] nodename nor servname provided, or not known>
[CRAWLING] https://informatics.xmu.edu.cn/info/1231/23549.htm (depth=3)
[ERROR] Fail to crawl http://nlp.xmu.edu.cn:8085/2016/03/30/jfhanzizhuanhuan/: <urlopen error timed out>
[CRAWLING] https://informatics.xmu.edu.cn/info/1231/23539.htm (depth=3)
[SAVED] http://www-nlp.stanford.edu/links/statnlp.html: downs/www-nlp.stanford.edu/links/statnlp.html
[CRAWLING] https://lingluodlut.github.io/ (depth=3)
[ERROR] Fail to crawl http://nlp.xmu.edu.cn:8085/2015/09/24/cwmt2015conference/: <urlopen error timed out>
[CRAWLING] https://wanyu2018umac.github.io/ (depth=3)
[ERROR] Fail to crawl https://informatics.xmu.edu.cn/info/1395/25159.htm: HTTP Error 404: Not Found
[ERROR] Fail to crawl https://informatics.xmu.edu.cn/info/1395/25199.htm: HTTP Error 404: Not Found[CRAWLING] http://cloudtranslation.xmu.edu.cn/aboutus/ (depth=3)

[CRAWLING] http://cloudtranslation.xmu.edu.cn/handbook/ (depth=3)
[ERROR] Fail to crawl https://informatics.xmu.edu.cn/info/1231/23549.htm: HTTP Error 404: Not Found
[CRAWLING] http://cloudtranslation.xmu.edu.cn/yunshi.html (depth=3)
[ERROR] Fail to crawl http://nlp.xmu.edu.cn:8085/2015/08/19/%E7%AC%AC%E4%BA%8C%E5%B1%8A%E8%97%8F%E6%96%87%E4%BF%A1%E6%81%AF%E5%A4%84%E7%90%86%E5%AD%A6%E6%9C%AF%E7%A0%94%E8%AE%A8%E4%BC%9A%E5%9C%A8%E8%A5%BF%E5%8C%97%E6%B0%91%E6%97%8F%E5%A4%A7%E5%AD%A6%E4%B8%BE/: <urlopen error timed out>
[ERROR] Fail to crawl http://nlp.xmu.edu.cn:8085/2015/08/04/%E6%88%91%E7%BB%84%E5%8F%82%E5%8A%A0cwmt2015%E7%9A%84%E8%AF%84%E6%B5%8B%E7%BB%93%E6%9E%9C%E5%85%AC%E5%B8%83/: <urlopen error timed out>
[ERROR] Fail to crawl https://informatics.xmu.edu.cn/info/1231/23539.htm: HTTP Error 404: Not Found
[ERROR] Fail to crawl http://nlp.xmu.edu.cn:8085/2014/11/19/simplify2tradition/: <urlopen error timed out>
[ERROR] Fail to crawl http://nlp.xmu.edu.cn:8085/2014/08/: <urlopen error timed out>
[ERROR] Fail to crawl http://nlp.xmu.edu.cn:8085/2013/05/13/checks2fchinesesystemdevelopment/: <urlopen error timed out>
[SAVED] http://www.statmt.org/moses/: downs/www.statmt.org/moses/003408a86af9ef4dddf50a9717415045.no_ext
[ERROR] Fail to crawl http://121.192.180.171:8080/tr.html: <urlopen error timed out>
[ERROR] Fail to crawl http://121.192.180.171:8080/segtag.html: <urlopen error timed out>
[ERROR] Fail to crawl https://pytorch.org/: The read operation timed out
[ERROR] Fail to crawl http://121.192.180.172: <urlopen error timed out>
[SAVED] http://cloudtranslation.xmu.edu.cn/aboutus/: downs/cloudtranslation.xmu.edu.cn/aboutus/64303ccfe6a798406dec67b5e6e4b9fd.no_ext
[SAVED] http://cloudtranslation.xmu.edu.cn/handbook/: downs/cloudtranslation.xmu.edu.cn/handbook/64303ccfe6a798406dec67b5e6e4b9fd.no_ext
[ERROR] Fail to crawl http://121.192.180.171:8080/webkwic.html: <urlopen error timed out>
[ERROR] Fail to crawl http://121.192.180.171:8080/corpus_cn.html: <urlopen error timed out>
[ERROR] Fail to crawl http://cloudtranslation.xmu.edu.cn/yunshi.html: HTTP Error 404: Not Found
[ERROR] Fail to crawl http://121.192.180.171:8080/e.html: <urlopen error timed out>
[ERROR] Fail to crawl http://121.192.180.171:8080/dic.html: <urlopen error timed out>
[ERROR] Fail to crawl http://121.192.180.171:8080/clir.html: <urlopen error timed out>
[SAVED] http://www.csie.ntu.edu.tw/~cjlin/liblinear/: downs/www.csie.ntu.edu.tw/~cjlin/liblinear/30af58ca35d38083c863f79cdc63916b.no_ext
[ERROR] Fail to crawl http://121.192.180.171:8080/: <urlopen error timed out>
[ERROR] Fail to crawl http://121.192.180.172/sccl/: <urlopen error timed out>
[SAVED] https://wanyu2018umac.github.io/: downs/wanyu2018umac.github.io/068ae9160071b5846bdae08db683d80a.no_ext
[SAVED] https://lingluodlut.github.io/: downs/lingluodlut.github.io/fb33edf1ecd4ac78ab82447a014fa90c.no_ext
[ERROR] Fail to crawl https://www.tensorflow.org/?hl=zh-cn: <urlopen error timed out>
(base) b@bogon Lab % 
```

The execution log demonstrates that the multi-threaded web crawler successfully executed according to the design specifications. The key observations from the run are as follows:
1. Breadth-First Crawling & Depth Control:
    - The crawler started at Depth 0, extracted links, and recursively crawled up to Depth 3.
    - The recursion strictly terminated at Depth 3, verifying the depth-limit logic.
2. Multi-threaded Concurrency:
    - The interleaved output of `[CRAWLING]` and `[SAVED]` logs confirms that the 25 worker threads successfully fetched pages concurrently from the shared `queue.Queue`.
3. Page Storage & URL Normalization:
    - Pages were successfully mapped to the local directory structure (`downs/`).
    - URLs lacking a distinct filename were correctly saved using their MD5 hashes as filenames with a `.no_ext` suffix, preventing name collisions.
4. Error Handling and Robustness:
    - Protocol Filtering: Non-HTTP links were gracefully caught by the try-except block, preventing program crashes.
    - Timeouts and Network Blocks: Setting timeout=0.5 caused numerous urlopen error timed out errors, particularly at Depth 3 on slower external sites. Some servers also rejected requests with 403 Forbidden (likely due to the lack of a realistic User-Agent header) or 404 Not Found.
    - Encoding Issues: An ASCII encoding exception occurred when encountering unquoted Chinese characters in a URL, suggesting a need for proper URL encoding (`urllib.parse.quote`) before fetching.


## 5. Problems Encountered and Solutions
### 5.1 Problems
- No suitable website for crawling
- Depth 3 will crawl a large number of web pages

### 5.2 Solutions
- Use a project website of the teacher, which is relatively simple and safe
- Shorten the timeout time
