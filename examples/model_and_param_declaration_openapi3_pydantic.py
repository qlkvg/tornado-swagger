from typing import List, Optional

import tornado.ioloop
import tornado.options
import tornado.web

from tornado_swagger.const import API_OPENAPI_3_PYDANTIC
from tornado_swagger.setup import setup_swagger, swagger_decorator

from pydantic import BaseModel, Field


class SumResponse(BaseModel):
    sum: int = Field(..., example=42, description="This is sum")
    you_are_cool: Optional[bool] = Field(None, description="You're cool if sum is 69")


class StatusItem(BaseModel):
    item_name: str = Field(..., example="item_name")
    item_health: str = Field(..., example="item_health")


class StatusResponse(BaseModel):
    status: str = Field(..., example="ok")
    items: List[StatusItem] = Field(...)


class StatusHandler(tornado.web.RequestHandler):
    @swagger_decorator(response=StatusResponse, tags=["Status"])
    def get(self):
        self.write({"status": "ok"})


class SumHandler(tornado.web.RequestHandler):
    @swagger_decorator(response=SumResponse, tags=["Calculus"])
    def post(self, term_one: int, term_two: int):
        term_one = int(term_one)
        term_two = int(term_two)
        result = term_one + term_two
        you_are_cool = result == 69
        response = SumResponse(sum=result, you_are_cool=you_are_cool)
        self.write(response.json())


class Application(tornado.web.Application):
    _routes = [
        tornado.web.url(r"/term-one/(?P<term_one>[0-9]+)/term-two/(?P<term_two>[0-9]+)/sum", SumHandler),
        tornado.web.url(r"/status", StatusHandler),
        tornado.web.url(r"/static/(.*)", tornado.web.StaticFileHandler, {"path": "/var/www"}),
    ]

    def __init__(self):
        settings = {"debug": True}

        setup_swagger(
            self._routes,
            swagger_url="/doc",
            api_base_url="/",
            description="",
            api_version="1.0.0",
            title="test API",
            contact="name@domain",
            schemes=["https"],
            api_definition_version=API_OPENAPI_3_PYDANTIC,
        )
        super(Application, self).__init__(self._routes, **settings)


if __name__ == "__main__":
    tornado.options.define("port", default="8080", help="Port to listen on")
    tornado.options.parse_command_line()

    app = Application()
    app.listen(port=8080)

    tornado.ioloop.IOLoop.current().start()
