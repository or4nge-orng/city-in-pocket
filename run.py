from database.scritps import db_session
import asyncio
import logging
from create_bot import dp, bot
from app.handlers import router


logging.basicConfig(level=logging.INFO)


async def main():
    dp.include_router(router)
    await dp.start_polling(bot, msg_to_del={})

if __name__ == '__main__':
    try:
        db_session.global_init('database/db.db')
        asyncio.run(main())
    except KeyboardInterrupt: 
        print('Exit')
