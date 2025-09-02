from pydantic import BaseModel, Field

class HashRate(BaseModel):
    """Схема валидации данных о хешрейте"""
    hash_rate_5_second: float
    hash_rate_30_minutes: float
    hash_rate_avg: float

class StatsFan(BaseModel):
    """Схема валидации данных о скорости работы вентиляторов"""
    first_fan: int = Field(gt=0)
    second_fan: int = Field(gt=0)
    third_fan: int = Field(gt=0)
    fourth_fan: int = Field(gt=0)

class StatsBoard(BaseModel):
    """Схема валидации данных о температура входящего воздуха, платы и чипов"""
    board_number: int
    incoming_air: list
    temperature_of_the_board: list
    chip_temperature: list
