import os
import requests
from functools import cached_property

# logging.basicConfig(level=logging.DEBUG)

from dotenv import load_dotenv
load_dotenv() 

class KitchenOwlAPI:
    def __init__(self, household_id):
        self.base_url = self._env_or_raise("KITCHENOWL_API_URL")
        self.household_id = household_id
        token = self._env_or_raise("KITCHENOWL_API_KEY")
        self.DEFAULT_HEADERS = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
        }

    def _env_or_raise(self, name) -> str:
        result = os.getenv(name)
        if not result:
            raise Exception(f"Please set the {name} environment variable.")
        return result

    def shopping_lists(self):
        url = f"{self.base_url}/household/{self.household_id}/shoppinglist"
        response = requests.get(url, headers=self.DEFAULT_HEADERS)
        response.raise_for_status()
        return response.json()

    @cached_property
    def list_id(self) -> str:
        if selected_id := os.getenv("KITCHENOWL_SHOPPING_LIST_ID"):
            return selected_id
        else:
            return self.shopping_lists()[0]["id"]

    def list_items(self) -> list[str]:
        slist = self.shopping_lists()[0]
        return [i["name"] for i in slist["items"]]

    def add_item(self, item_name):
        url = f"{self.base_url}/shoppinglist/{self.list_id}/add-item-by-name"
        data = {"name": item_name}
        response = requests.post(url, json=data, headers=self.DEFAULT_HEADERS)
        response.raise_for_status()
        return response

    def remove_item(self, item_name):
        item_ids = [
            item["id"]
            for item in self.shopping_lists()[0]["items"]
            if item["name"].lower() == item_name.lower()
        ]

        responses = []
        for item_id in item_ids:
            url = f"{self.base_url}/shoppinglist/{self.list_id}/item"
            response = requests.delete(
                url, json={"item_id": item_id}, headers=self.DEFAULT_HEADERS
            )
            responses.append(response)
        return responses

    def check_item(self, item_name):
        item_ids = [
            item["id"]
            for item in self.shopping_lists()[0]["items"]
            if item["name"].lower() == item_name.lower()
        ]

        responses = []
        for item_id in item_ids:
            responses.append(item_id)
        return responses
