from aiogram.fsm.state import StatesGroup, State


class EditHandledPost(StatesGroup):
    input_post = State()


class AddKey(StatesGroup):
    input_key = State()
