import os
import threading

from fastapi import Request, Response

from .. import APIFastAPI, APIExceptions, APIConstants, APIPaths, APIGlobals
from ...core import NyanController, NyanLogging as logging, NyanThreading, NyanGlobals


class Test_Service(APIFastAPI.Nyan_Router):
    def __init__(self, controller: NyanController.Nyan_Controller):

        APIFastAPI.Nyan_Router.__init__(self, "Test Service", controller)

        self.add_api_route("/tst/single_job/{name}", self.route_single_job_test, methods=["GET"])
        self.add_api_route("/tst/repeating_job/{name}", self.route_repeating_job_test, methods=["GET"])
        self.add_api_route("/tst/cancel_all/", self.route_cancel_all_test, methods=["GET"])
        self.add_api_route("/tst/set_api_shutdown_flag/", self.route_set_debug_flag, methods=["GET"])

        self.single_jobs: list[NyanThreading.Single_Job] = []
        self.repeating_jobs: list[NyanThreading.Repeating_Job] = []

    def job_callback(self, name: str = None):

        logging.debug(f"{threading.current_thread().name} {threading.current_thread().ident} {name}")

    @APIFastAPI.Nyan_Router.die_if_shutdown_endpoint_wrapper_async
    async def route_set_debug_flag(self, request: Request):

        NyanGlobals.debug_value = True
        APIGlobals.shutdown_api = True

    @APIFastAPI.Nyan_Router.die_if_shutdown_endpoint_wrapper_async
    async def route_single_job_test(self, request: Request, name: str):

        logging.debug("putting single job")

        self.single_jobs.append(self.controller.call_later(30, self.job_callback, name))

    @APIFastAPI.Nyan_Router.die_if_shutdown_endpoint_wrapper_async
    async def route_repeating_job_test(self, request: Request, name: str):

        logging.debug("putting repeating job")

        self.repeating_jobs.append(self.controller.call_repeating(0, 5, self.job_callback, name))

    @APIFastAPI.Nyan_Router.die_if_shutdown_endpoint_wrapper_async
    async def route_cancel_all_test(self, request: Request):

        for i in self.single_jobs:

            i.cancel()
            logging.debug(f"Canceling: {i.get_pretty_job()}")

        for i in self.repeating_jobs:

            i.cancel()
            logging.debug(f"Canceling: {i.get_pretty_job()}")
