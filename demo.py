from locust import HttpLocust, TaskSet, task
import conf
from lxml import etree
import random


class WebsiteTasks(TaskSet):

    def on_start(self):
        self.root_urls = []
        self.cur_urls = []
        self.index()
        self.cur_urls = self.root_urls

    @task(conf.index_percent)
    def index(self):
        html = self.client.get("/").content
        dom_tree = etree.HTML(html)

        for url in dom_tree.xpath('//a/@href'):

            # Handle url without http protocol
            self.handle_url(conf.host, url, self.root_urls)

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

        if self.root_urls is not None and len(self.root_urls) != 0:
            c_url = random.choice(self.root_urls)
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

                self.cur_urls = []
                if conf.host in c_url:
                    c_url = conf.host

                for url in dom_tree.xpath('//a/@href'):
                    # Handle url without http protocol
                    self.handle_url(c_url, url, self.cur_urls)

            self.client.close()

        # print("===========")

    @task(conf.deep_click_percent)
    def deep_click(self):

        if self.cur_urls is not None and len(self.cur_urls) != 0:
            url = random.choice(self.cur_urls)
            # response = self.client.get(url)
            with self.client.get(url, catch_response=True) as response:
                # print("Deep : " + url)
                # print(str(response.status_code) + "==========")
                if response.status_code in conf.error_code:
                    response.failure("Error " + str(response.status_code) + " for " + url)
                else:
                    response.success()
            self.client.close()

    def handle_url(self, host, url, url_set):
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

            # if host.endswith("/") and url.startswith("/"):
            #     url = host + url.lstrip("/")
            # elif not host.endswith("/") and not url.startswith("/"):
            #     url = host + "/" + url
            # else:
            #     url = host + url

        if url not in url_set and "javascript:void(0)" not in url:
            # print(url)
            url_set.append(url)


class WebsiteUser(HttpLocust):
    task_set = WebsiteTasks
    host = conf.host
    min_wait = 100
    max_wait = 500
