from typing import List, Dict

# Curated, compact universe approximating large-cap US names (S&P 100 style)
SP100: List[str] = [
    "AAPL","MSFT","AMZN","GOOGL","GOOG","META","NVDA","TSLA","BRK-B","JPM",
    "V","JNJ","WMT","PG","MA","UNH","HD","XOM","BAC","PFE","KO","TMO",
    "DIS","VZ","ADBE","CSCO","PEP","CMCSA","NFLX","CRM","ABT","CVX","NKE",
    "ORCL","ACN","AVGO","DHR","MDT","MCD","COST","TXN","LIN","AMD","HON",
    "INTC","PM","UPS","MS","IBM","QCOM","SBUX","LLY","BMY","AMGN","AMAT",
    "CAT","GS","BLK","BKNG","SPGI","RTX","ISRG","GILD","ADP","DE","LOW",
    "GE","C","NOW","SCHW","T","PYPL","UNP","INTU","MMM","MO","BA","PLD",
    "USB","MDLZ","MMC","TGT","CVS","TJX","DUK","SO","BK","PNC","FDX",
]

# NASDAQ-100 styled preset (representative subset; may not be exhaustive)
NASDAQ100: List[str] = [
    "AAPL","MSFT","AMZN","NVDA","GOOGL","GOOG","META","TSLA","PEP","AVGO",
    "COST","ADBE","CSCO","NFLX","AMD","INTC","CMCSA","QCOM","TXN","AMAT",
    "HON","INTU","SBUX","AMGN","ADI","PDD","MRNA","LRCX","BKNG","GILD",
    "PYPL","ABNB","PANW","VRTX","REGN","CRWD","CSX","CHTR","MU","KLAC",
    "MAR","MELI","IDXX","KDP","SNPS","CDNS","KHC","AEP","ODFL","FTNT",
    "CTAS","ADP","ORLY","MNST","ROST","AZN","NXPI","TEAM","PAYX","PCAR",
    "WDAY","DXCM","BIIB","XEL","VRSK","EA","SPLK","CEG","MRVL","MCHP",
    "EXC","LULU","EBAY","ANSS","CPRT","CSGP","VRSN","CTSH","DLTR","FAST",
    "MDLZ","JD","ALGN","ZTS","CDW","VRTX","WBD","BIDU","NTES","PDD","ZM",
    "DDOG","OKTA","DOCU","ZS","ROKU","NVAX","PTON","LCID","RIVN","COIN",
]

PRESETS: Dict[str, List[str]] = {
    "S&P 100": SP100,
    "NASDAQ 100": NASDAQ100,
}


def get_preset(name: str) -> List[str]:
    return PRESETS.get(name, SP100)
