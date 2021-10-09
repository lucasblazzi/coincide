import re
from datetime import date
from re import sub


class Product:
    def __init__(self, product):
        self.product = product

    @property
    def compose_product(self):
        builder = self.product["category_builder"]
        base = {
            "name": str(self.product.get("Nome", "")),
            "link": str(self.product.get("Informações", "")),
            "publication_date": date.today().strftime("%Y-%m-%d"),
            "category": str(self.product.get("category")),
            "source": str(self.product.get("source"))
        }
        return getattr(self, builder)(base)

    def coe_builder(self, base):
        coe = {
            "strategy": str(self.product.get("Estratégia")),
            "deadline": int(re.findall(r'\d+', self.product.get("Reserve até", "0"))[0]),
            "classification": str(self.product.get("Classificação", "")),
            "description": str(self.product.get("Rentabilidade", "")),
        }
        return base | coe

    def stock_rt_builder(self, base):
        stock = {
            "ticker": str(self.product.get("ticker", "")),
            "target_price": float(sub(r'[^\d.]', '', self.product.get("Preço Alvo", "0").replace(",", "."))),
            "segment": str(self.product.get("segmento", "")),
            "recommendation": str(self.product.get("Recomendação", "").upper()),
            "description": str(self.product.get("analise", "")),
        }
        return base | stock

    def fixed_income_builder(self, base):
        fixed_income = self.product
        return base | fixed_income

    def investment_fund_builder(self, base):
        investment_fund = {
            "min_application": float(sub(r'[^\d.]', '', self.product.get("Aplic. Mín.").replace(".", "").replace(",", "."))),
            "adm_tax": float(sub(r'[^\d.]', '', self.product.get("Taxa Adm. (a.a.)").replace(",", "."))),
            "redemption": self.product.get("Cotização de Resgate"),
            "classification": str(self.product.get("Classificação XP")),
            "month_return": float(sub(r'[^\d.]', '', self.product.get("Rent. Mês").replace(",", "."))),
        }
        return base | investment_fund

    def pension_fund_builder(self, base):
        pension_fund = {
            "min_application": float(sub(r'[^\d.]', '', self.product.get("Aplic. Mín.").replace(".", "").replace(",", "."))),
            "adm_tax": float(sub(r'[^\d.]', '', self.product.get("Taxa Adm.").replace(",", "."))),
            "month_return": float(sub(r'[^\d.]', '', self.product.get("Rent. Mês").replace(",", "."))),
        }
        return base | pension_fund

