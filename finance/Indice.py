from finance.MoexAPI import MoexAPI


class Indice:

    BRANCH_INDICES = ('MOEXOG', 'MOEXEU', 'MOEXTL', 'MOEXMM', 'MOEXFN', 'MOEXCN', 'MOEXCH', 'MOEXIT', 'MOEXRE', 'MOEXTN')

    def __init__(self, name):
        if name[0] == '.':
            name = name[1:]
        self.name = name

    def current_compound(self):
        request_url = f"statistics/engines/stock/markets/index/analytics/{self.name}.json"
        response = MoexAPI.query(request_url)
        compound = response['analytics']
        return compound

    def tickers(self):
        compound = self.current_compound()
        tickers = [el['ticker'] for el in compound]
        return tickers

    def tickers_weights(self):
        compound = self.current_compound()
        tickers_weights = {}
        for el in compound:
            ticker = el['ticker']
            weight = el['weight']
            tickers_weights[ticker] = weight
        return tickers_weights

    @classmethod
    def ticker_indices(cls, ticker, only_branches=False, return_ids=True):
        request_url = f"securities/{ticker}/indices.json"
        arguments = {"only_actual": 1}
        response = MoexAPI.query(request_url, arguments)
        indices = response['indices']
        if only_branches:
            indices = [indice for indice in indices if indice['SECID'] in cls.BRANCH_INDICES]
        if return_ids:
            ids = [indice['SECID'] for indice in indices]
            return ids
        else:
            return indices

    # @staticmethod
    # def branch_indice(ticker):
    #     indices = Indice.ticker_indices(ticker)
    #     for indice in indices:
    #         if indice in Indice.BRANCH_INDICES:
    #             return indice
    #     return None
