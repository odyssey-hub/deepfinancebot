class ForecastException(Exception):
    def __init__(self, type):
        self.message = self.__create_error_msg(type)
        super().__init__(self.message)

    def __create_error_msg(self, type):
        match type:
            case "horizon":
                return "Некорректный горизонт прогнозирования"
            case "model":
                return "Указана некорректная модель прогнозирования"
            case "learning":
                return "При обучении модели произошла ошибка"
            case _:
                return "Возникла ошибка с параметрами прогнозирования"
