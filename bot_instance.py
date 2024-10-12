from aiogram import Bot
from config_reader import config

bot = Bot(config.bot_token.get_secret_value())
