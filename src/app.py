"""main module for the orchastrator chatbot, seperate from the ollama container"""

from typing import List
from collections import deque
import json

import dotenv
from websockets.asyncio.client import connect
from ollama import Client

from aes import AESGCM
from classes import Transaction, Privilege, User
import asyncio


model = "smollm2"
system = deque(
    [
        {
            "role": "system",
            "content": "you are an assitant in a group chat, you are called whenever a message contains the sequence @ai, this means you should NEVER write it in your messages",
        },
        {
            "role": "system",
            "content": "you can see up to 50 previous messages or until and excluding the last message that you have sent",
        },
        {
            "role": "system",
            "content": "the messages after these system messages are everyone's messages without sender name. you should send your own messag as just the content",
        },
        {
            "role": "system",
            "content": "you should generally focus on answering the last messags and only use the previous messages for context",
        },
        {
            "role": "system",
            "content": "if are asked somethink you aren't sure about answer but prefix the answer with 'i may be wron here, but'",
        },
    ]
)


class ChatBot:
    """a class managing the bridge between orchastrator and ollama"""

    creds: dict
    messages: deque[dict[str, str]]
    users: List[User]
    system_prmpt: str
    encryption: AESGCM

    def __init__(self) -> None:
        self.creds = dotenv.dotenv_values()
        if not all(
            cred in self.creds
            for cred in ["URL", "gid", "username", "password", "AES_KEY"]
        ):
            raise ValueError("Missing required credentials in .env file")
        self.messages = deque(maxlen=50)
        self.users = [User(username="SYSTEM", privilege=Privilege.ADMIN)]
        self.encryption = AESGCM(self.creds["AES_KEY"])
        self.client = Client(host="ollama")

    async def start(self) -> None:
        """
        function that connects both to the server and the ollama model,
        and starts the message loop

        :param creds: dictionary for connection credentials for the orchastrator instance
        :type creds: dict
        """
        async with connect(f"{self.creds['URL']}/{self.creds['gid']}") as websocket:
            await websocket.send(
                json.dumps(
                    {
                        "username": self.creds["username"],
                        "password": self.creds["password"],
                    }
                )
            )
            assert "goahead" == await websocket.recv()
            await websocket.send("999999")
            async for data in websocket:
                message = Transaction.from_dict(json.loads(data))
                if message.mtype == 0:
                    plaintext = json.loads(self.encryption.decrypt(message.content))
                    if plaintext["oid"] != 1:
                        continue
                    content = plaintext["content"]
                    self.messages.append({"role": "user", "content": content})
                    if "@ai" in content:
                        response = (
                            self.client.chat(
                                model=model, messages=(system + self.messages)
                            )
                        ).message.content or "no response"
                        await websocket.send(
                            json.dumps(
                                {
                                    "content": self.encryption.encrypt(
                                        json.dumps({"content": response, "oid": 1})
                                    ),
                                    "mtype": 0,
                                }
                            )
                        )


def main() -> None:
    """main function to start the chatbot"""
    bot = ChatBot()

    asyncio.run(bot.start())


if __name__ == "__main__":
    main()
