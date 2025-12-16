import asyncio

import aiohttp
from aiogram import F, Router
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message
from aiogram_dialog import Dialog, DialogManager, StartMode, Window
from aiogram_dialog.api.entities import Data
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Back, Button, Cancel, Column, Row, SwitchTo
from aiogram_dialog.widgets.text import Const, Format

from src.bot.config import DJANGO_API_URL

router = Router()


# States for the dialog
class TaskDialogSG(StatesGroup):
    main_menu = State()
    adding_title = State()
    adding_description = State()
    viewing_tasks = State()


# API Client to communicate with Django
class APIClient:
    def __init__(self):
        self.base_url = DJANGO_API_URL

    async def get_user_tasks(self, telegram_user_id: int):
        async with aiohttp.ClientSession() as session:
            try:
                # Use the new endpoint that accepts telegram ID
                url = f"{self.base_url}/telegram/user/{telegram_user_id}/tasks/"
                async with session.get(url) as resp:
                    if resp.status == 200:
                        return await resp.json()
                    else:
                        return []
            except Exception as e:
                print(f"Error fetching tasks: {e}")
                return []

    async def create_task(self, title: str, description: str, telegram_user_id: int):
        async with aiohttp.ClientSession() as session:
            # In a real implementation, we'd need to authenticate the user
            # For this demo, we'll use a default user (ID=1), but in real app you'd have auth
            url = f"{self.base_url}/tasks/"
            payload = {
                "title": title,
                "description": description,
                "user": 1,  # In real app, this would be authenticated user's ID
            }
            try:
                async with session.post(url, json=payload) as resp:
                    print(f"API Response Status: {resp.status}")
                    response_text = await resp.text()
                    print(f"API Response Text: {response_text}")
                    if resp.status in [200, 201]:
                        return await resp.json()
                    else:
                        print(f"Error creating task: {resp.status}")
                        return None
            except Exception as e:
                print(f"Error creating task: {e}")
                return None


# Data getters
async def main_menu_getter(dialog_manager: DialogManager, **kwargs):
    return {}


async def tasks_getter(dialog_manager: DialogManager, **kwargs):
    # This would be called when viewing tasks
    tasks = dialog_manager.dialog_data.get("tasks", [])
    tasks_str = ""
    if tasks:
        for task in tasks:
            tasks_str += f"• {task.get('title', 'No title')} (Created: {task.get('created_at', 'Unknown date')})\n"
    else:
        tasks_str = "No tasks found."

    return {"tasks_str": tasks_str}


# Handler for description getter
async def description_getter(dialog_manager: DialogManager, **kwargs):
    title = dialog_manager.dialog_data.get("title", "New Task")
    return {"title": title}


# Handlers for navigation
async def show_main_menu(
    callback: CallbackQuery, button: Button, manager: DialogManager
):
    await manager.switch_to(TaskDialogSG.main_menu)


async def show_add_title(
    callback: CallbackQuery, button: Button, manager: DialogManager
):
    # Reset any existing dialog data
    manager.dialog_data["title"] = ""
    manager.dialog_data["description"] = ""
    await manager.switch_to(TaskDialogSG.adding_title)


async def show_view_tasks(
    callback: CallbackQuery, button: Button, manager: DialogManager
):
    # Fetch actual tasks from Django API
    client = APIClient()
    tasks = await client.get_user_tasks(callback.from_user.id)

    manager.dialog_data["tasks"] = tasks
    await manager.switch_to(TaskDialogSG.viewing_tasks)


# Input handlers
async def process_title(
    message: Message,
    message_input,  # This is the MessageInput widget instance
    dialog_manager: DialogManager,
):
    # This handler should only be called when in adding_title state
    title = message.text
    dialog_manager.dialog_data["title"] = title
    await message.answer(f"Title set to: {title}. Now send description or /skip.")
    # Move to next state by switching to the description window
    await dialog_manager.switch_to(TaskDialogSG.adding_description)


async def process_description(
    message: Message, message_input, dialog_manager: DialogManager
):
    # This handler should only be called when in adding_description state
    current_state = dialog_manager.current_context().state

    # Check if this is a /skip command before treating as description
    if message.text.strip().lower() == "/skip":
        title = dialog_manager.dialog_data.get("title", "Untitled")
        dialog_manager.dialog_data["description"] = ""

        # Create the task with empty description (for skip)
        client = APIClient()
        task = await client.create_task(title, "", message.from_user.id)

        if task:
            await message.answer(f"Task created successfully: {task['title']}")
        else:
            await message.answer("Error creating task")

        await dialog_manager.switch_to(TaskDialogSG.main_menu)
        return

    # If not /skip, treat as normal description
    description = message.text
    dialog_manager.dialog_data["description"] = description
    title = dialog_manager.dialog_data.get("title", "Untitled")

    # Create the task with the actual description
    client = APIClient()
    task = await client.create_task(title, description, message.from_user.id)

    if task:
        await message.answer(f"Task created successfully: {task['title']}")
    else:
        await message.answer("Error creating task")

    await dialog_manager.switch_to(TaskDialogSG.main_menu)


async def skip_description_handler(
    callback: CallbackQuery, button: Button, dialog_manager: DialogManager
):
    title = dialog_manager.dialog_data.get("title", "Untitled")
    dialog_manager.dialog_data["description"] = ""

    # Create the task
    client = APIClient()
    task = await client.create_task(title, "", callback.from_user.id)

    if task:
        await callback.message.answer(f"Task created successfully: {task['title']}")
    else:
        await callback.message.answer(f"Error creating task {task}")

    await dialog_manager.switch_to(TaskDialogSG.main_menu)


# Create dialog
task_dialog = Dialog(
    Window(
        Const("Welcome! Choose an option:"),
        Button(Const("View Tasks"), id="view_tasks", on_click=show_view_tasks),
        Button(Const("Add Task"), id="add_task", on_click=show_add_title),
        state=TaskDialogSG.main_menu,
        getter=main_menu_getter,
    ),
    Window(
        Const("Please enter the task title:"),
        MessageInput(process_title),
        Button(Const("Back"), id="back_to_main", on_click=show_main_menu),
        state=TaskDialogSG.adding_title,
    ),
    Window(
        Format("Current task: {title}\n\nEnter description or press 'Skip':"),
        MessageInput(process_description),
        Button(
            Const("Skip Description"), id="skip_desc", on_click=skip_description_handler
        ),
        Button(Const("Back"), id="back_to_main", on_click=show_main_menu),
        state=TaskDialogSG.adding_description,
        getter=description_getter,
    ),
    Window(
        Format("{tasks_str}"),
        Button(Const("Back"), id="back_to_main", on_click=show_main_menu),
        state=TaskDialogSG.viewing_tasks,
        getter=tasks_getter,
    ),
)
