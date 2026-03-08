"""main module for the orchastrator chatbot, seperate from the ollama container"""

from typing import List
from collections import deque
import json

import dotenv
from websockets.asyncio.client import connect
from ollama import chat

from aes import AESGCM
from classes import Transaction, Privilege, User


class ChatBot:
    """a class managing the bridge between orchastrator and ollama"""

    creds: dict
    messages: deque[dict[str, str]]
    users: List[User]
    system_prmpt: str
    encryption: AESGCM

    def __init__(self) -> None:
        with open("system.txt", "r", encoding="utf-8") as f:
            self.system_prmpt = f.read()
        self.creds = dotenv.dotenv_values()
        if not all(
            cred in self.creds
            for cred in ["url", "gid", "username", "password", "AES_KEY"]
        ):
            raise ValueError("Missing required credentials in .env file")
        self.messages = deque(maxlen=50)
        self.users = [User(username="SYSTEM", privilege=Privilege.ADMIN)]
        self.encryption = AESGCM(self.creds["AES_KEY"])

    async def start(self) -> None:
        """
        function that connects both to the server and the ollama model,
        and starts the message loop

        :param creds: dictionary for connection credentials for the orchastrator instance
        :type creds: dict
        """
        async with connect(f"{self.creds['url']}/{self.creds['gid']}") as websocket:  # type: ignore
            await websocket.send(
                json.dumps(self.creds.fromkeys(["username", "password"]))
            )
            assert websocket.recv() == "goahead"
            await websocket.send("0")
            async for data in websocket:
                message = Transaction.from_dict(json.loads(data))
                if message.mtype == 0:
                    sender = self.users[message.sender]
                    plaintext = json.loads(self.encryption.decrypt(message.content))
                    if plaintext["oid"] != 1:
                        continue
                    content = plaintext["content"]
                    quote = f"{sender.username} the {sender.privilege.name}: {content}"
                    self.messages.append({"role": "user", "content": quote})
                    if "@ai" in content:
                        response = (
                            chat(
                                model="smollm2",
                                messages=list(self.messages),
                            ).message.content
                            or "no response"
                        )
                        self.messages.append({"role": "assistant", "content": response})
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
                elif message.mtype == 1:
                    action = json.loads(message.content)
                    match action["type"]:
                        case "user addition":
                            user = action["user"]
                            self.users.append(
                                User(
                                    username=user["username"],
                                    privilege=Privilege(user["privilege"]),
                                )
                            )
                        case "perm":
                            self.users[action["uid"]].privilege = Privilege(
                                action["new"]
                            )
