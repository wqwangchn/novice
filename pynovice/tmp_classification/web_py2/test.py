# -*- coding: utf-8 -*-
# /usr/bin/env python

'''
Author: wenqiangw
Email: wqwangchn@163.com
Date: 2023/12/7 15:24
Desc:
'''
import web

urls = (
    '/upload', 'Upload',
)


class Upload:
    def GET(self):
        return """<html><head></head><body>
            <form method="POST" enctype="multipart/form-data" action="">
            <input type="file" name="myfile" />
            <br/>
            <input type="submit" />
            </form>
            </body></html>"""

    def POST(self):
        x = web.input(myfile={})
        web.debug(x['myfile'].filename)  # 这里是文件名
        web.debug(x['myfile'].value)  # 这里是文件内容
        web.debug(x['myfile'].file.read())  # 或者使用一个文件对象
        print(x)
        raise web.seeother('/upload')

if __name__ == "__main__":
   app = web.application(urls, globals())
   app.run()
