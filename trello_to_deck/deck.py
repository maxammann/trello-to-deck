import requests

headers = {"OCS-APIRequest": "true", "Content-Type": "application/json"}

# The API is implemented as documented here: https://deck.readthedocs.io/en/latest/API/
class DeckAPI:
    def __init__(self, url, auth):
        self.url = url
        self.auth = auth

    def getBoards(self):
        response = requests.get(
            f"{self.url}/index.php/apps/deck/api/v1.0/boards",
            auth=self.auth,
            headers=headers,
        )
        response.raise_for_status()
        return response.json()

    def getBoardDetails(self, boardId):
        response = requests.get(
            f"{self.url}/index.php/apps/deck/api/v1.0/boards/{boardId}",
            auth=self.auth,
            headers=headers,
        )
        response.raise_for_status()
        return response.json()

    def getStacks(self, boardId):
        response = requests.get(
            f"{self.url}/index.php/apps/deck/api/v1.0/boards/{boardId}/stacks",
            auth=self.auth,
            headers=headers,
        )
        response.raise_for_status()
        return response.json()

    def getStacksArchived(self, boardId):
        response = requests.get(
            f"{self.url}/index.php/apps/deck/api/v1.0/boards/{boardId}/stacks/archived",
            auth=self.auth,
            headers=headers,
        )
        response.raise_for_status()
        return response.json()

    def createBoard(self, title, color):
        response = requests.post(
            f"{self.url}/index.php/apps/deck/api/v1.0/boards",
            auth=self.auth,
            json={"title": title, "color": color},
            headers=headers,
        )
        response.raise_for_status()
        board = response.json()
        boardId = board["id"]
        # remove all default labels
        for label in board["labels"]:
            labelId = label["id"]
            response = requests.delete(
                f"{self.url}/index.php/apps/deck/api/v1.0/boards/{boardId}/labels/{labelId}",
                auth=self.auth,
                headers=headers,
            )
            response.raise_for_status()
        return board

    def createLabel(self, title, color, boardId):
        response = requests.post(
            f"{self.url}/index.php/apps/deck/api/v1.0/boards/{boardId}/labels",
            auth=self.auth,
            json={"title": title, "color": color},
            headers=headers,
        )
        response.raise_for_status()
        return response.json()

    def createStack(self, title, order, boardId):
        response = requests.post(
            f"{self.url}/index.php/apps/deck/api/v1.0/boards/{boardId}/stacks",
            auth=self.auth,
            json={"title": title, "order": order},
            headers=headers,
        )
        response.raise_for_status()
        return response.json()

    def createCard(self, title, ctype, order, description, duedate, boardId, stackId):
        response = requests.post(
            f"{self.url}/index.php/apps/deck/api/v1.0/boards/{boardId}/stacks/{stackId}/cards",
            auth=self.auth,
            json={
                "title": title,
                "type": ctype,
                "order": order,
                "description": description,
                "duedate": duedate.isoformat() if duedate is not None else None,
            },
            headers=headers,
        )
        response.raise_for_status()
        return response.json()

    def assignLabel(self, labelId, cardId, boardId, stackId):
        response = requests.put(
            f"{self.url}/index.php/apps/deck/api/v1.0/boards/{boardId}/stacks/{stackId}/cards/{cardId}/assignLabel",
            auth=self.auth,
            json={"labelId": labelId},
            headers=headers,
        )
        response.raise_for_status()

    def archiveCard(self, card, boardId, stackId):
        cardId = card["id"]
        response = requests.put(
            f"{self.url}/index.php/apps/deck/api/v1.0/boards/{boardId}/stacks/{stackId}/cards/{cardId}",
            auth=self.auth,
            json=card,
            headers=headers,
        )
        response.raise_for_status()

    def commentOnCard(self, cardId, message, parentId=None):
        response = requests.post(
            f"{self.url}/ocs/v2.php/apps/deck/api/v1.0/cards/{cardId}/comments",
            auth=self.auth,
            json={"message": message, "parentId": parentId},
            headers=headers,
        )
        response.raise_for_status()
