import requests
from utils import get_abs, safeget, to_csv


class FinnhubClient:

    API_VERSION = "v1"
    URL = f"https://finnhub.io/api/{API_VERSION}/quote"  # symbol={symbol}&token={token}

    def __init__(self, symbols, token):
        self.token = token
        self.symbols = symbols
        self.stocks = {}
        self.most_volatile_stock = None

    def _request(self, method, endpoint, params=None, headers=None, data=None):
        """Make rest api request.
        Args:
            method: str. rest api method
            endpoint: str. rest api endpoint
            params(optional): dict. query params
            headers(optional): dict. additional headers
            data(optional): dict. form data content
        Returns
            response_data: dict or list. json response data
        """

        response = requests.request(method, endpoint, params=params)
        response_data = response.json()

        if "error" in response_data:
            raise Exception(response_data["error"])

        return response_data

    def get_data(self, symbol):
        """
        This function returns a dict response attributes
        Args:
            symbol: str. symbol of the stock for which we are fetching data

        Return:
            data: dict. current stock data. For example:
            {
                "c": 113.67,
                "d": -0.89,
                "dp": -0.7769,
                "h": 116.25,
                "l": 112.43,
                "o": 115.1,
                "pc": 114.56,
                "t": 1665432004,
            }
        """
        
        params = {"symbol": symbol, "token": self.token}
        data = self._request("GET", FinnhubClient.URL, params=params)

        if data.get("dp"):
            return data

    def get_stocks(self):
        """
        This function returns a dict of dict where stock symbol is key and dict of response attributes is value

        Return:
            stocks: dict. all stocks data. For example:

            {
                "AAPL": {
                    "c": 113.67,
                    "d": -0.89,
                    "dp": -0.7769,
                    "h": 116.25,
                    "l": 112.43,
                    "o": 115.1,
                    "pc": 114.56,
                    "t": 1665432004,
                }
            }
        """

        for symbol in self.symbols.values():
            data = self.get_data(symbol)
            if data:
                self.stocks[symbol] = data
            else:
                print("Skipping... Invalid Stock Symbol:", symbol)

        return self.stocks

    def get_most_volatile_stock(self):
        """
        This function returns the symbol of most_volatile_stock

        Return:
             str. symbol of most_volatile_stock. For example : 'AAPL'

        """
        if not self.stocks:
            self.get_stocks()
        for stock in self.stocks:
            if not self.most_volatile_stock:
                self.most_volatile_stock = stock

            if get_abs(safeget(self.stocks, stock, "dp")) > get_abs(
                safeget(self.stocks, self.most_volatile_stock, "dp")
            ):
                self.most_volatile_stock = stock
        return self.most_volatile_stock

    def generate_csv(self):
        """
        This function generates the csv file with required data

        """
        if not self.most_volatile_stock:
            self.get_most_volatile_stock()
        header = [
            "stock_symbol",
            "percentage_change",
            "current_price",
            "last_close_price",
        ]
        data = [
            safeget(self.most_volatile_stock),
            get_abs(safeget(self.stocks, self.most_volatile_stock, "dp")),
            safeget(self.stocks, self.most_volatile_stock, "c"),
            safeget(self.stocks, self.most_volatile_stock, "pc"),
        ]
        to_csv(header, data)


if __name__ == "__main__":

    symbols = {
        "apple": "AAPL",
        "amazon": "AMZN",
        "netflix": "NFLX",
        "facebook": "META",
        "google": "GOOGL",
    }
    TOKEN = "cd013pqad3i1q4rcs8egcd013pqad3i1q4rcs8f0"
    try:
        stock_obj = FinnhubClient(symbols, TOKEN)
        stock_obj.generate_csv()

    except Exception as error:
        print(error)
