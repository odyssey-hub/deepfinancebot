class DBException(Exception):
    def __init__(self, type, ticker=None):
        self.message = self.__create_error_msg(type, ticker)
        super().__init__(self.message)

    def __create_error_msg(self, type, ticker):
        match type:
            case "ticker":
                return f"Ошибка. Не получилось считать данные по {ticker} из БД"
            case _:
                return "Возникла ошибка, связанная с базой данных"