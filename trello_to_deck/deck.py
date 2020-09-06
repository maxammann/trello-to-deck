import requests

headers = {"OCS-APIRequest": "true", "Content-Type": "application/json"}


class DeckAPI:
    def __init__(self, url, auth, dry_run):
        self.url = url
        self.auth = auth
        self.dry_run = dry_run

    def get(self, route):
        response = requests.get(
            f"{self.url}{route}",
            auth=self.auth,
            headers=headers,
        )
        response.raise_for_status()
        return response.json()

    def post(self, route, json):
        if self.dry_run:
            return ""

        response = requests.post(
            f"{self.url}{route}",
            auth=self.auth,
            json=json,
            headers=headers,
        )
        response.raise_for_status()
        return response.json()

    def put(self, route, json):
        if self.dry_run:
            return ""

        response = requests.put(
            f"{self.url}{route}",
            auth=self.auth,
            json=json,
            headers=headers,
        )
        response.raise_for_status()
        return response.json()

    def delete(self, route):
        if self.dry_run:
            return ""

        response = requests.put(
            f"{self.url}{route}",
            auth=self.auth,
            headers=headers,
        )
        response.raise_for_status()
        return response.json()

    def getBoards(self):
        return self.get(f"/index.php/apps/deck/api/v1.0/boards")

    def getBoardDetails(self, boardId):
        return self.get(f"/index.php/apps/deck/api/v1.0/boards/{boardId}")

    def getStacks(self, boardId):
        return self.get(f"/index.php/apps/deck/api/v1.0/boards/{boardId}/stacks")

    def getStacksArchived(self, boardId):
        return self.get(
            f"/index.php/apps/deck/api/v1.0/boards/{boardId}/stacks/archived"
        )

    def createBoard(self, title, color):
        board = self.post(
            "/index.php/apps/deck/api/v1.0/boards", {"title": title, "color": color}
        )
        boardId = board["id"]
        # remove all default labels
        for label in board["labels"]:
            labelId = label["id"]
            self.delete(
                f"/index.php/apps/deck/api/v1.0/boards/{boardId}/labels/{labelId}"
            )
        return board

    def createLabel(self, title, color, boardId):
        return self.post(
            f"/index.php/apps/deck/api/v1.0/boards/{boardId}/labels",
            {"title": title, "color": color},
        )

    def createStack(self, title, order, boardId):
        return self.post(
            f"/index.php/apps/deck/api/v1.0/boards/{boardId}/stacks",
            {"title": title, "order": order},
        )

    def createCard(self, title, ctype, order, description, duedate, boardId, stackId):
        return self.post(
            f"/index.php/apps/deck/api/v1.0/boards/{boardId}/stacks/{stackId}/cards",
            {
                "title": title,
                "type": ctype,
                "order": order,
                "description": description,
                "duedate": duedate.isoformat() if duedate is not None else None,
            },
        )

    def assignLabel(self, labelId, cardId, boardId, stackId):
        self.put(
            f"/index.php/apps/deck/api/v1.0/boards/{boardId}/stacks/{stackId}/cards/{cardId}/assignLabel",
            {"labelId": labelId},
        )

    def archiveCard(self, card, boardId, stackId):
        self.put(
            f"/index.php/apps/deck/api/v1.0/boards/{boardId}/stacks/{stackId}/cards/{cardId}",
            card,
        )

    def commentOnCard(self, cardId, message, parentId=None):
        self.post(
            f"/ocs/v2.php/apps/deck/api/v1.0/cards/{cardId}/comments",
            {"message": message, "parentId": parentId},
        )
