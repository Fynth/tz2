import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message
from aiogram_dialog import DialogManager, StartMode, setup_dialogs
from aiogram_dialog.api.exceptions import UnknownIntent

from src.bot.config import BOT_TOKEN
from src.bot.dialogs import TaskDialogSG, task_dialog

# Enable logging
logging.basicConfig(level=logging.INFO)


class TaskBotStates(StatesGroup):
    waiting_for_title = State()
    waiting_for_description = State()


async def start_command(message: Message, dialog_manager: DialogManager):
    """Handle /start command"""
    await message.answer("Welcome to the ToDo List Bot!")
    # Start the main menu dialog
    try:
        await dialog_manager.start(TaskDialogSG.main_menu, mode=StartMode.RESET_STACK)
    except UnknownIntent:
        # If context lost, reset and start new
        await dialog_manager.reset_stack()
        await dialog_manager.start(TaskDialogSG.main_menu, mode=StartMode.RESET_STACK)


async def main():
    """Main function to run the bot"""
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()

    # Register commands first
    dp.message.register(start_command, CommandStart())

    # Include the dialog after
    dp.include_router(task_dialog)

    # Setup dialogs
    setup_dialogs(dp)

    # Run the bot
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
