import asyncio
from aiogram import Dispatcher
import logging
from bot_instance import bot 
from middlewares.antiflood import AntiFloodMiddleware
from middlewares.badwordshandler import MultiLangBadWordsMiddleware
from handlers import user_commands, callback_handlers, questionnaire
from new_data import pars







async def main() -> None:
    dp = Dispatcher()

 
    dp.message.middleware(MultiLangBadWordsMiddleware(file_paths=["badwordsru.json"]))
    dp.message.middleware(AntiFloodMiddleware(0.5))
    asyncio.create_task(pars())

    dp.include_routers(
        user_commands.router,
        questionnaire.router,
        callback_handlers.router,
       
    )

  
    await bot.delete_webhook(drop_pending_updates=True)
    
    await dp.start_polling(bot)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Exiting')
