import os
import threading

from fastapi import Request, Response

from .. import APIFastAPI, APIExceptions, APIConstants, APIPaths
from ...core import aNyanController, aNyanThreading, aNyanLogging as logging


class Test_Service(APIFastAPI.Nyan_Router):
    def __init__(self, controller: aNyanController.Nyan_Controller):

        APIFastAPI.Nyan_Router.__init__(self, "Test Service", controller)

        self.add_api_route("/tst/single_job/{name}", self.route_single_job_test, methods=["GET"])
        self.add_api_route("/tst/repeating_job/{name}", self.route_repeating_job_test, methods=["GET"])
        self.add_api_route("/tst/cancel_all/", self.route_cancel_all_test, methods=["GET"])

        self.single_jobs: list[aNyanThreading.Single_Job] = []
        self.repeating_jobs: list[aNyanThreading.Repeating_Job] = []

    def job_callback(self, name: str = None):

        logging.debug(f"{threading.current_thread().name} {threading.current_thread().ident} {name}")

    async def route_single_job_test(self, request: Request, name: str):

        logging.debug("putting single job")

        self.single_jobs.append(self.controller.call_later(30, self.job_callback, name))

    async def route_repeating_job_test(self, request: Request, name: str):

        logging.debug("putting repeating job")

        self.repeating_jobs.append(self.controller.call_repeating(0, 5, self.job_callback, name))

    async def route_cancel_all_test(self, request: Request):

        for i in self.single_jobs:

            i.cancel()
            logging.debug(f"Canceling: {i.get_pretty_job()}")

        for i in self.repeating_jobs:

            i.cancel()
            logging.debug(f"Canceling: {i.get_pretty_job()}")
