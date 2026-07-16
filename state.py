from aiogram.fsm.state import StatesGroup, State

class pogodai(StatesGroup):
    strana = State()
    srok = State()


class fakti(StatesGroup):
    strana = State()
    col = State()

class escursi(StatesGroup):
    strana = State()
    col = State()

class cursi(StatesGroup):
    vala = State()
    valb = State()
    col = State()