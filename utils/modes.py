from config import logger


class Modes:
    def __init__(self):
        self.mode = 'no_modding'
        logger.info('modding is off')

    def change_mode(self):
        if self.mode == 'no_modding':
            self.mode = 'modding'
            status = 'on'
        else:
            self.mode = 'no_modding'
            status = 'off'
        logger.info(f'modding is {status}')

    def get_mode(self):
        if self.mode == 'no_modding':
            answer = 'Модерация отключена'
        else:
            answer = 'Модерация включена'
        return answer


edit_mode = Modes()