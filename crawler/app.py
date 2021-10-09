import os
import grpc
from coincide_pb2 import MetricsRequest
from coincide_pb2_grpc import MetricsStub

from utils.product import Product
from sources.btg import full_btg
from sources.xp import full_xp


metrics_host = os.environ.get("METRICS_HOST", "[::]")


def get_metrics(ticker):
    try:
        with grpc.insecure_channel(f"{metrics_host}:9999") as channel:
            stub = MetricsStub(channel)
            request = MetricsRequest(base_date=date.today().strftime("%Y-%m-%d"), ticker=ticker)
            metrics = stub.GetMetrics(request)
    except Exception as e:
        raise e
    return metrics


def compose_products(products: list) -> list:
    _products = list()
    calculate = ("Ações", "Fundos Imobiliários")
    for product in products:
        _product = Product(product).compose_product
        if _product["category"] in calculate:
            metrics = {x.name: x.value for x in get_metrics(_product["ticker"])}
            _product = _product | metrics
        _products.append(_product)
    return _products


def get_products():
    _products = list()
    _products.extend(full_btg())
    _products.extend(full_xp())
    return compose_products(_products)
