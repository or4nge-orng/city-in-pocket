from aiogram.fsm.state import StatesGroup, State


class Registration(StatesGroup):
    name = State()
    loc = State()
    time = State()
    
    
class ChangeCity(StatesGroup):
    loc = State()
    
    
class ChangeTime(StatesGroup):
    time = State()