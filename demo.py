from locust import HttpLocust, TaskSet, task
import conf
from lxml import etree
import random


class WebsiteTasks(TaskSet):

    def on_start(self):
        self.depth_url = {1: []}
        self.global_url = []
        self.cur_depth = 1
        # self.root_urls = []
        # self.cur_urls = []
        self.index()
        # self.cur_urls = self.root_urls

    # @task(conf.index_percent)
    def index(self):
        html = self.client.get("/").content
        dom_tree = etree.HTML(html)

        # Handle url without http protocol
        for url in dom_tree.xpath('//a/@href'):
            # self.handle_url(conf.host, url, self.root_urls)
            self.handle_url(conf.host, url, 1)

            # if url.startswith("//"):
            #     url = "http:" + url
            #     # print(url)
            #
            # # Add host with url
            # if not url.startswith("http"):
            #     url = conf.host + url
            #
            # if url not in self.root_urls and url != "javascript:void(0);":
            #     # print(url)
            #     self.root_urls.append(url)

        # print("===========")
        self.client.close()

    @task(conf.random_click_percent)
    def random_click(self):

        if self.check_empty(1):
            c_url = random.choice(self.depth_url[1])
            with self.client.get(c_url, catch_response=True) as response:
                # print("Random : " + c_url)
                # print(str(response.status_code) + "==========")
                if response.status_code in conf.error_code:
                    response.failure("Error " + str(response.status_code) + " for " + c_url)
                else:
                    response.success()

                    # html = self.client.get(c_url).content.decode('utf-8')
                    html = response.content
                    dom_tree = etree.HTML(html)

                    if conf.host in c_url:
                        c_url = conf.host

                    if self.cur_depth == 1:
                        self.cur_depth += 1
                        self.depth_url[self.cur_depth] = []

                    for url in dom_tree.xpath('//a/@href'):
                        # Handle url without http protocol
                        self.handle_url(c_url, url, 2)

            self.client.close()

        # print("===========")

    @task(conf.deep_click_percent)
    def deep_click(self):
        if self.cur_depth == 1:
            self.cur_depth += 1
            self.depth_url[self.cur_depth] = []
            depth = self.cur_depth
        else:
            depth = random.randint(2, self.cur_depth)

        if self.check_empty(depth):
            c_url = random.choice(self.depth_url[depth])
            # response = self.client.get(url)
            with self.client.get(c_url, catch_response=True) as response:
                # print("Deep : " + c_url)
                # print(str(response.status_code) + "==========")
                if response.status_code in conf.error_code:
                    response.failure("Error " + str(response.status_code) + " for " + c_url)
                else:
                    response.success()

                    if depth < conf.depth:
                        html = response.content
                        dom_tree = etree.HTML(html)

                        if conf.host in c_url:
                            c_url = conf.host

                        depth += 1
                        self.cur_depth = max(depth, self.cur_depth)
                        if depth not in self.depth_url.keys():
                            self.depth_url[depth] = []

                        # Handle url without http protocol
                        for url in dom_tree.xpath('//a/@href'):
                            self.handle_url(c_url, url, depth)

            self.client.close()

    def handle_url(self, host, url, depth):

        if url.startswith("//"):
            url = "http:" + url

        if url.startswith("#"):
            if host.endswith("/"):
                url = host + url
            else:
                url = host + "/" + url

        # Add host with url
        if not url.startswith("http"):
            url = host.rstrip("/") + "/" + url.lstrip("/")

        if url not in self.depth_url[depth] and url not in self.global_url and "javascript:" not in url:
            # print(url)
            self.depth_url[depth].append(url)
            self.global_url.append(url)

    def check_empty(self, depth):
        if self.depth_url[depth] is not None and len(self.depth_url[depth]) != 0:
            return True
        else:
            return False


class WebsiteUser(HttpLocust):
    task_set = WebsiteTasks
    host = conf.host
    min_wait = conf.min_wait
    max_wait = conf.max_wait
