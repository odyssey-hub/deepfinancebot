class RequestException(Exception):
    def __init__(self, type):
        self.message = self.__create_error_msg(type)
        super().__init__(self.message)


    def __create_error_msg(self, type):
        match type:
            case "ticker":
                return "Ошибка. Не удалось получить данные по тикеру(ам)"
            case "indice":
                return "Ошибка. Не удалось получить данные по индексу"
            case "moex":
                return "Возникла ошибка при скачивании данных."
            case _:
                return "Возникла ошибка с MoexAPI"