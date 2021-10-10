import os
import grpc
from concurrent import futures
from datetime import datetime

import pandas as pd
import yfinance as yf

from coincide_pb2 import InfoResponse
import coincide_pb2_grpc as grpc_service


prices_host = os.environ.get("PRICES_HOST", "localhost")
prices_port = os.environ.get("PRICES_PORT", "8888")


def get_series(ticker, start_date, end_date):
    historic = ticker.history(start=start_date, end=end_date)
    historic.index = historic.index.strftime("%Y-%m-%d")
    return historic.to_dict()


def get_info(ticker):
    info = pd.DataFrame.from_dict(ticker.info, orient="index").to_dict()[0]
    return info.get("longName")


def multi_builder(name, pbuff_obj, series):
    for k, v in series[name].items():
        if v:
            multi_obj = pbuff_obj.add()
            multi_obj.date = k
            multi_obj.value = v
        else:
            continue
    return pbuff_obj


def response_builder(name, series):
    info_response = InfoResponse()
    info_response.name = name
    multi_builder("Close", info_response.prices, series)
    multi_builder("Volume", info_response.volumes, series)
    multi_builder("Dividends", info_response.dividends, series)
    return info_response


def server_setup():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    grpc_service.add_InfoServicer_to_server(InfoServicer(), server)
    server.add_insecure_port(f"{prices_host}:{prices_port}")
    server.start()
    print(f"Server is running on {prices_host}:{prices_port}")
    server.wait_for_termination()


class InfoServicer(grpc_service.InfoServicer):
    def GetInfo(self, request, context):
        ticker = yf.Ticker(request.ticker)
        series = get_series(ticker, request.start_date, request.end_date)
        name = get_info(ticker)
        result = response_builder(name, series)
        return result


if __name__ == "__main__":
    print(f"Starting prices server on port {prices_port}")
    server_setup()