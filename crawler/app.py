import requests
from bs4 import BeautifulSoup, Tag


categories = {
    "ativos_coe": "COE",
    "ativos_acoes_fund": "Ações",
    "ativos_fund_imob": "Fundos Imobiliários",
    "renda_fixa_ativos_credito_privado,renda_fixa_ativos_bancarios,renda_fixa_ativos_tesouro_direto": "Renda Fixa",
    "ativos_fund_invest": "Fundos de Investimento",
    "ativos_prev_privada": "Previdência Privada"
}


def xp_crawl(target):
    page = requests.get(f'https://conteudos.xpi.com.br/wp-json/xpinsights/v2/filtrar-conteudo?filter-function=xpinsights_default_destaques_ativos_filter&destaque={target}&box=Produtos&multiauthors=true', headers={'User-Agent': 'Mozilla/5.0'})
    soup = BeautifulSoup(page.json()["html"], 'html.parser')
    products = soup.find_all("div", {"class": "box-produtos"})

    parsed_products = []
    #print(products[0])
    for product in products:
        parsed_product = {}
        for dado in product.ul:
            if isinstance(dado, Tag):
                data = dado.text.replace("  ", "").strip().split("\n")
                parsed_data = list(filter(None, data))
                parsed_product[parsed_data[0]] = parsed_data[1]
            else:
                continue
        parsed_product["Nome"] = product.h4.text
        parsed_product["Informações"] = product.a["href"]
        parsed_products.append(parsed_product)
    print(parsed_products)


xp_crawl("ativos_prev_privada")