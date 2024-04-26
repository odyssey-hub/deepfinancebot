import os



class Tickers:

    @staticmethod
    def get_tickers(size_version='big'):
        if size_version == 'big':
            filename = 'tickers_big.txt'
        elif size_version == 'medium':
            filename = 'tickers_med.txt'
        elif size_version == 'small':
            filename = 'tickers_sm.txt'
        else:
            filename = 'tickers_tiny.txt'

        path = os.path.join(os.path.dirname(__file__), 'tickers', filename)

        with open(path, 'r') as file:
            tickers = file.read().splitlines()

        return tickers


