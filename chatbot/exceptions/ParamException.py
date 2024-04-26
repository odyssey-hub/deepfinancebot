class ParamException(Exception):
    def __init__(self, param):
        self.message = self.__create_error_msg(param)
        super().__init__(self.message)


    def __create_error_msg(self, param):
        match param:
            case "argparse":
                return "Ошибка. Указаны неверные параметры или их значения"
            case "no_param":
                return "Ошибка. Не указано значение одного из параметров"
            case "no_ticker":
                return "Ошибка. Укажите тикер"
            case "no_tickers":
                return "Ошибка. Укажите тикеры"
            case "no_period":
                return "Ошибка. Укажите период"
            case "period":
                return "Ошибка. Указан неверный период"
            case "timeframe":
                return "Ошибка. Указан неверный таймфрейм"
            case "columns":
                return "Ошибка. Указан некорректный столбец(цы)"
            case _:
                return f"Ошибка. Указано неверное значение {param}"
