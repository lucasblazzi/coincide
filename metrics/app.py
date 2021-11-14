import os
import grpc
import pandas as pd
from concurrent import futures
from datetime import datetime
from dateutil.relativedelta import relativedelta

from google.protobuf.json_format import MessageToDict
import coincide_pb2_grpc as grpc_service
from coincide_pb2_grpc import InfoStub
from coincide_pb2 import InfoRequest, MetricsResponse

from utils.product_metrics import Metrics


prices_host = os.environ.get("PRICES_HOST", "localhost")
prices_port = os.environ.get("PRICES_PORT", "8888")

metrics_host = os.environ.get("METRICS_HOST", "localhost")
metrics_port = os.environ.get("METRICS_PORT", "9999")


def get_12m(base_date):
    return (datetime.strptime(base_date, "%Y-%m-%d") -
                          relativedelta(months=12)).strftime("%Y-%m-%d")


def get_prices(request):
    try:
        with grpc.insecure_channel(f"{prices_host}:{prices_port}") as channel:
            stub = InfoStub(channel)
            start_date = get_12m(request.base_date)
            request = InfoRequest(ticker=f"{request.ticker}.SA", start_date=start_date, end_date=request.base_date)
            prices = stub.GetInfo(request)
            return prices
    except Exception as e:
        raise e

def response_builder(metrics, name):
    _metrics = MetricsResponse()
    _metrics.name = name
    for k, v in metrics.items():
        metric_value = _metrics.metrics.add()
        metric_value.name = k
        if v:
            metric_value.value = float(v)
        else:
            metric_value.value = 0.0
    return _metrics


def prepare_info(info, index, field, name):
    if info.get(field):
        dividends = pd.DataFrame(info[field]).rename(columns={"value": name})
    else:
        dividends = pd.DataFrame()
        dividends["date"] = index
        dividends[name] = 0.0
    return dividends


def compose_df(data):
    info = MessageToDict(data)
    if not info.get("prices"):
        return pd.DataFrame()
    close = pd.DataFrame(info["prices"]).rename(columns={"value": "close"})
    volumes = prepare_info(info, close["date"], "volumes", "volume")
    dividends = prepare_info(info, close["date"], "dividends", "dividend")
    final_df = close.merge(dividends, "left", on="date").merge(volumes, "left", on="date").set_index("date").fillna(0)
    cols = final_df.columns
    final_df[cols] = final_df[cols].apply(pd.to_numeric, errors='coerce')
    return final_df


def server_setup():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    grpc_service.add_MetricsServicer_to_server(MetricsServicer(), server)
    server.add_insecure_port(f"{metrics_host}:{metrics_port}")
    try:
        server.start()
        print(f"Server is running on {metrics_host}:{metrics_port}")
        server.wait_for_termination()
    except KeyboardInterrupt:
        print("Stopping metrics service")
        server.stop(0)


class MetricsServicer(grpc_service.MetricsServicer):
    def GetMetrics(self, request, context):
        data = get_prices(request)
        if data.ByteSize():
            df = compose_df(data)
            if df.empty:
                return MetricsResponse()
            metrics = Metrics(request).get_metrics(df)
            return response_builder(metrics, data.name)
        else:
            return MetricsResponse()


if __name__ == "__main__":
    print(f"Starting metrics server on port {metrics_port}")
    server_setup()