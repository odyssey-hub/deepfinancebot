class Delta2WException(Exception):
    def __init__(self, type):
        self.message = self.__create_error_msg(type)
        super().__init__(self.message)

    def __create_error_msg(self, type):
        match type:
            case "interval":
                return "Ошибка. Некорректный интервал"
            case "corr":
                return "Ошибка. Некорректная корреляция"
            case "params":
                return "Ошибка. Некорректные значения параметров"
            case "and_or_no_params":
                return "Ошибка. Для каждой части между AND или OR должны быть указаны все параметры"
            case "and_or_only":
                return "Ошибка. В одном запросе поддерживается только использование либо AND, либо OR"
            case _:
                return "Возникла ошибка, связанная с моделью Delta2W и ее параметрами"
