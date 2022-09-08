import aiohttp
import json
from typing import Dict, List, Tuple, Union, Any

class SteamApi:

    URL = 'http://api.steampowered.com'
    STATUS = {
        0: "根本不在线",
        1: "在线挂机，啥都没玩",
        2: "正在忙碌",
        3: "正在AFK",
        4: "正在打盹",
        5: "寻找交易",
        6: "请求互动",
    }

    def __init__(self, key: Union[None, str], config_path: str):
        """
        https://developer.valvesoftware.com/wiki/Steam_Web_API

        :param key: steam api key
        :param config_path: user config file path
        """
        self.api_key = key
        self.config_path = config_path
        with open(self.config_path, 'r') as file:
            self.users = json.load(file)
        self.session = aiohttp.ClientSession()

    async def _request_json(self, api) -> Dict[Any, Any]:
        async with self.session.get(api) as response:
            json = await response.json()
            return json

    async def _get_info(self, id: str) -> Union[Dict[Any, Any], Any]:
        """
        Get user summary

        :param id: 64bit SteamID
        :return: user data dict
        """
        api = f"{self.URL}/ISteamUser/GetPlayerSummaries/v0002/?key={self.api_key}&steamids={id}"
        data = await self._request_json(api)
        if data:
            return data["response"]["players"][0]
        else:
            return data

    async def add_user(self, nickname: str, id: str) -> str:
        """
        Add a steam user to config

        :param nickname: custom nickname
        :param id: 64bit SteamID
        :return: avatar url, display name
        """
        data = await self._get_info(id)
        if data:
            self.users[nickname.lower()] = id
            with open(self.config_path, 'w') as file:
                json.dump(self.users, file, indent=2)
            return f"添加{nickname}成功"
        else:
            return f"添加{nickname}失败"

    async def remove_user(self, nickname: str) -> str:
        """
        Remvoe an user from config

        :param nickname: nickname in config
        :return: message
        """
        if nickname in self.users:
            del self.users[nickname.lower()]
            with open(self.config_path, 'w') as file:
                json.dump(self.users, file, indent=2)
            return f"移除{nickname}成功"
        else:
            return f"移除{nickname}失败"

    async def get_status(self, nickname: str) -> Tuple[str, str, str]:
        """
        Get user status

        :param nickname: nickname stored in config
        :return: tuple containing avatar url, display name, status message
        """
        if nickname not in self.users:
            return ("", "", "")

        data = await self._get_info(self.users[nickname.lower()])
        if data:
            status = data["personastate"]
            if "gameextrainfo" in data:
                game = data["gameextrainfo"]
                message = f"正在玩{game}"
            else:
                message = f"{self.STATUS[status]}"
            return (data["avatar"], data["personaname"], message)
        else:
            return ("", "", "")

    async def list_all(self) -> List[Tuple[str, str, str]]:
        """
        Get status of all users in config

        :return: list of status tuple
        """
        status_list = []
        for nickname in self.users:
            status = await self.get_status(nickname)
            status_list.append(status)
        return status_list
