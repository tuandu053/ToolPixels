import json
import requests

class GPMLoginApiV3:
    posBrowser = [(0, 0), (751, 0), (1502, 0),                                  
                  (0, 601), (751, 601), (1502, 601),    
                  (0, 1202), (751, 1202), (1502, 1202)]

    START_ENDPOINT = "/api/v3/profiles/start/{id}?win_size=750,600&win_scale=0.8&win_pos={x},{y}"
    CLOSE_ENDPOINT = "/api/v3/profiles/close/{id}"

    def __init__(self, apiUrl):
        self._apiUrl = apiUrl

    async def start_profile_async(self, profileId, index):
        id = profileId
        index = index%8
        x = self.posBrowser[index][0]
        y = self.posBrowser[index][1]
        apiUrl = f"{self._apiUrl}{self.START_ENDPOINT}".replace("{id}", id).replace("{x}", str(x)).replace("{y}", str(y))
        resp = await self.http_get_async(apiUrl)

        if resp is None:
            return None

        try:
            return json.loads(resp)
        except json.JSONDecodeError:
            return None

    async def close_profile_async(self, profileId):
        apiUrl = f"{self._apiUrl}{self.CLOSE_ENDPOINT}".replace("{id}", profileId)
        resp = await self.http_get_async(apiUrl)

        if resp is None:
            return False

        try:
            data = json.loads(resp)
            return data.get("success", False)
        except json.JSONDecodeError:
            return False

    async def http_get_async(self, apiUrl):
        try:
            response = requests.get(apiUrl)
            response.raise_for_status()  # Raise error for non-2xx responses

            return response.text
        except requests.exceptions.RequestException as e:
            print(f"An error occurred: {e}")
            return None
