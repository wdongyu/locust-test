## Locust Test

配置：

`pip install locustio`

`pip install lxml`
 
自定义相关参数：
> edit conf.py

运行

1. 单进程no_web：
	
	`locust -f demo.py --no-web -c 1`
2. 单进程web：

	`locust -f demo.py`
	
	访问 localhost:8089
3. 多进程：

	`locust -f demo.py --master`
	
	`locust -f demo.py --slave`

 