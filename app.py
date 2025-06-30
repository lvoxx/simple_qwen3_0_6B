import os
from dotenv import load_dotenv

import chainlit as cl
from chainlit.input_widget import Select

from qwen3_0_6B import QwenChatbot
from e_chat_mode import ChatMode
from cache import PromptCache

def load_envs():
    model_name = os.getenv("MODEL_NAME")
    multi_gpus = os.getenv("MULTI_GPUS", "false").lower() == "true"
    return model_name, multi_gpus


@cl.on_app_startup
def on_app_startup():
    load_dotenv()
    global chatbot, cache, model_name, multi_gpus
    model_name, multi_gpus = load_envs()
    
    chatbot = QwenChatbot(model_name=model_name, multi_gpus=multi_gpus)
    cache = PromptCache()

@cl.on_chat_start
async def on_chat_start():
    # Provide a toggle UI to user
    await cl.ChatSettings(
        [
            Select(
                id="active_mode",
                label="Select a working mode:",
                initial_value="None",
                values=[mode.value for mode in ChatMode],
            )
        ]
    ).send()


@cl.set_starters
async def set_starters():
    return [
        cl.Starter(
            label="Morning routine ideation",
            message="Can you help me create a personalized morning routine that would help increase my productivity throughout the day? Start by asking me about my current habits and what activities energize me in the morning.",
            icon="/public/idea.svg",
            ),

        cl.Starter(
            label="Explain superconductors",
            message="Explain superconductors like I'm five years old.",
            icon="/public/learn.svg",
            ),
        cl.Starter(
            label="Python script for daily email reports",
            message="Write a script to automate sending daily email reports in Python, and walk me through how I would set it up.",
            icon="/public/terminal.svg",
            ),
        cl.Starter(
            label="Text inviting friend to wedding",
            message="Write a text asking a friend to be my plus-one at a wedding next month. I want to keep it super short and casual, and offer an out.",
            icon="/public/write.svg",
            )
        ]

@cl.on_message
async def on_message(message: cl.Message):
    prompt = message.content

    settings = cl.user_session.get("chat_settings") or {}
    selected_value = settings.get("active_mode")

    msg = cl.Message(content="")  # Placeholder for streaming    
    await msg.send()

    response = cache.get(prompt)
    if response:
        await chatbot.give_cached_response(response, msg)
    else:
        try:
            selected_mode = ChatMode(selected_value)
        except ValueError:
            selected_mode = ChatMode.THINKING  # fallback default

        if selected_mode == ChatMode.THINKING:
            response = await chatbot.generate_response(prompt, msg, True)
        else:
            response = await chatbot.generate_response(prompt, msg, False)

    print(response)

    await msg.update()  # Finalize the message
