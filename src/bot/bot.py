import asyncio

import aiohttp
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message
from aiogram_dialog import Dialog, DialogManager, Window
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Back, Button, Cancel, Column, Row, Select
from aiogram_dialog.widgets.text import Const, Format
from config import BOT_TOKEN, DJANGO_API_URL


# States for the dialog
class TaskStates(StatesGroup):
    choosing_action = State()
    adding_title = State()
    adding_description = State()
    adding_categories = State()
    viewing_tasks = State()


# API Client to communicate with Django
class APIClient:
    def __init__(self):
        self.base_url = DJANGO_API_URL

    async def get_user_tasks(self, user_id: int):
        async with aiohttp.ClientSession() as session:
            # In a real system, we'd have a way to authenticate users
            # For now, we simulate getting tasks for a user
            url = f"{self.base_url}/tasks/"
            try:
                async with session.get(url) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        # Filter for user's tasks (in real implementation would use token)
                        return data
                    else:
                        return []
            except Exception as e:
                print(f"Error fetching tasks: {e}")
                return []

    async def create_task(self, title: str, description: str, user_id: int):
        async with aiohttp.ClientSession() as session:
            url = f"{self.base_url}/tasks/"
            payload = {
                "title": title,
                "user": user_id,  # In real implementation, this would be handled differently
            }
            try:
                async with session.post(url, json=payload) as resp:
                    if resp.status == 201:
                        return await resp.json()
                    else:
                        return None
            except Exception as e:
                print(f"Error creating task: {e}")
                return None


# Main menu window
async def main_menu_handler(
    callback: CallbackQuery, button: Button, manager: DialogManager
):
    await manager.start(TaskStates.choosing_action)


# Choosing action window
main_window = Window(
    Const("/todo - View your tasks\n/add_task - Add a new task"),
    state=TaskStates.choosing_action,
    getter=lambda **kwargs: {},
)


# Adding title window
add_title_window = Window(
    Const("Please enter a title for your task:"),
    MessageInput(lambda message, dialog_manager: dialog_manager.next()),
    state=TaskStates.adding_title,
    getter=lambda **kwargs: {},
)


# Adding description window
add_description_window = Window(
    Const("Please enter a description for your task (optional, send /skip to skip):"),
    MessageInput(lambda message, dialog_manager: dialog_manager.next()),
    state=TaskStates.adding_description,
    getter=lambda **kwargs: {},
)


# Adding categories window
add_categories_window = Window(
    Const(
        "Please enter categories for your task (comma separated, send /skip to skip):"
    ),
    MessageInput(lambda message, dialog_manager: dialog_manager.done()),
    state=TaskStates.adding_categories,
    getter=lambda **kwargs: {},
)


# Viewing tasks window
view_tasks_window = Window(
    Format("Your tasks:\n{tasks_text}"),
    Button(Const("Back"), id="back_to_main", on_click=main_menu_handler),
    state=TaskStates.viewing_tasks,
    getter=lambda **kwargs: {"tasks_text": kwargs.get("tasks", "No tasks found")},
)


# Create dialog
dialog = Dialog(
    main_window,
    add_title_window,
    add_description_window,
    add_categories_window,
    view_tasks_window,
)


# Handler for /start command
async def start_handler(message: Message, dialog_manager: DialogManager):
    await dialog_manager.start(TaskStates.choosing_action)


# Handler for /add_task command
async def add_task_handler(message: Message, dialog_manager: DialogManager):
    await dialog_manager.start(TaskStates.adding_title)


# Handler for /todo command
async def view_tasks_handler(message: Message, dialog_manager: DialogManager):
    api_client = APIClient()
    tasks = await api_client.get_user_tasks(message.from_user.id)

    tasks_text = ""
    if tasks:
        for task in tasks:
            tasks_text += f"• {task['title']} (Created: {task['created_at']})\n"
            if task.get("due_date"):
                tasks_text += f"  Due: {task['due_date']}\n"
            if task.get("categories"):
                cats = [cat["name"] for cat in task["categories"]]
                tasks_text += f"  Categories: {', '.join(cats)}\n"
            tasks_text += "\n"
    else:
        tasks_text = "No tasks found."

    # Update the dialog data with tasks
    dialog_manager.dialog_data["tasks"] = tasks_text
    dialog_manager.dialog_data['tasks'] = tasks_text
    await dialog_manager.start(TaskStates.viewing_tasks)


# Handler for skipping description/categories
async def skip_handler(message: Message, dialog_manager: DialogManager):
    if dialog_manager.current_context().state == TaskStates.adding_description:
        await dialog_manager.next()
    elif dialog_manager.current_context().state == TaskStates.adding_categories:
        await dialog_manager.done()


def setup_handlers(dp: Dispatcher):
    dp.message.register(start_handler, CommandStart())
    dp.message.register(add_task_handler, Command(commands=["add_task"]))
    dp.message.register(view_tasks_handler, Command(commands=["todo"]))
    dp.message.register(skip_handler, F.text.lower() == "/skip")


async def main():
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()

    # Register dialog
    dp.include_router(dialog)

    # Setup handlers
    setup_handlers(dp)

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
