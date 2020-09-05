import requests
urlFrom = 'https://cloud.domainfrom.tld'
authFrom = ('username', 'password')

urlTo = 'https://nextcloud.domainto.tld'
authTo = ('username', 'password')

headers={'OCS-APIRequest': 'true', 'Content-Type': 'application/json'}


def getBoards():
    response = requests.get(
            f'{urlFrom}/index.php/apps/deck/api/v1.0/boards',
            auth=authFrom,
            headers=headers)
    response.raise_for_status()
    return response.json()

def getBoardDetails(boardId):
    response = requests.get(
            f'{urlFrom}/index.php/apps/deck/api/v1.0/boards/{boardId}',
            auth=authFrom,
            headers=headers)
    response.raise_for_status()
    return response.json()

def getStacks(boardId):
    response = requests.get(
            f'{urlFrom}/index.php/apps/deck/api/v1.0/boards/{boardId}/stacks',
            auth=authFrom,
            headers=headers)
    response.raise_for_status()
    return response.json()

def getStacksArchived(boardId):
    response = requests.get(
            f'{urlFrom}/index.php/apps/deck/api/v1.0/boards/{boardId}/stacks/archived',
            auth=authFrom,
            headers=headers)
    response.raise_for_status()
    return response.json()

def createBoard(title, color):
    response = requests.post(
            f'{urlTo}/index.php/apps/deck/api/v1.0/boards',
            auth=authTo,
            json={
                'title': title,
                'color': color
            },
            headers=headers)
    response.raise_for_status()
    board = response.json()
    boardId = board['id']
    # remove all default labels
    for label in board['labels']:
        labelId = label['id']
        response = requests.delete(
            f'{urlTo}/index.php/apps/deck/api/v1.0/boards/{boardId}/labels/{labelId}',
            auth=authTo,
            headers=headers)
        response.raise_for_status()
    return board

def createLabel(title, color, boardId):
    response = requests.post(
            f'{urlTo}/index.php/apps/deck/api/v1.0/boards/{boardId}/labels',
            auth=authTo,
            json={
                'title': title,
                'color': color
            },
            headers=headers)
    response.raise_for_status()
    return response.json()

def createStack(title, order, boardId):
    response = requests.post(
            f'{urlTo}/index.php/apps/deck/api/v1.0/boards/{boardId}/stacks',
            auth=authTo,
            json={
                'title': title,
                'order': order
            },
            headers=headers)
    response.raise_for_status()
    return response.json()

def createCard(title, ctype, order, description, duedate, boardId, stackId):
    response = requests.post(
            f'{urlTo}/index.php/apps/deck/api/v1.0/boards/{boardId}/stacks/{stackId}/cards',
            auth=authTo,
            json={
                'title': title,
                'type': ctype,
                'order': order,
                'description': description,
                'duedate': duedate
            },
            headers=headers)
    response.raise_for_status()
    return response.json()

def assignLabel(labelId, cardId, boardId, stackId):
    response = requests.put(
            f'{urlTo}/index.php/apps/deck/api/v1.0/boards/{boardId}/stacks/{stackId}/cards/{cardId}/assignLabel',
            auth=authTo,
            json={
                'labelId': labelId
            },
            headers=headers)
    response.raise_for_status()

def archiveCard(card, boardId, stackId):
    cardId = card['id']
    card['archived'] = True
    response = requests.put(
            f'{urlTo}/index.php/apps/deck/api/v1.0/boards/{boardId}/stacks/{stackId}/cards/{cardId}',
            auth=authTo,
            json=card,
            headers=headers)
    response.raise_for_status()

def copyCard(card, boardIdTo, stackIdTo, labelsMap):
    createdCard = createCard(
        card['title'],
        card['type'],
        card['order'],
        card['description'],
        card['duedate'],
        boardIdTo,
        stackIdTo
    )

    # copy card labels
    if card['labels']:
        for label in card['labels']:
            assignLabel(labelsMap[label['id']], createdCard['id'], boardIdTo, stackIdTo)

    if card['archived']:
        archiveCard(createdCard, boardIdTo, stackIdTo)


# get boards list
boards = getBoards()

# create boards
for board in boards:
    boardIdFrom = board['id']
    # create board
    createdBoard = createBoard(board['title'], board['color'])
    boardIdTo = createdBoard['id']
    print('Created board', board['title'])

    # create labels
    boardDetails = getBoardDetails(board['id'])
    labelsMap = {}
    for label in boardDetails['labels']:
        createdLabel = createLabel(label['title'], label['color'], boardIdTo)
        labelsMap[label['id']] = createdLabel['id']

    # copy stacks
    stacks = getStacks(boardIdFrom)
    stacksMap = {}
    for stack in stacks:
        createdStack = createStack(stack['title'], stack['order'], boardIdTo)
        stackIdTo = createdStack['id']
        stacksMap[stack['id']] = stackIdTo
        print('  Created stack', stack['title'])
        # copy cards
        if not 'cards' in stack:
            continue
        for card in stack['cards']:
            copyCard(card, boardIdTo, stackIdTo, labelsMap)
        print('    Created', len(stack['cards']), 'cards')

    # copy archived stacks
    stacks = getStacksArchived(boardIdFrom)
    for stack in stacks:
        # copy cards
        if not 'cards' in stack:
            continue
        print('  Stack', stack['title'])
        for card in stack['cards']:
            copyCard(card, boardIdTo, stacksMap[stack['id']], labelsMap)
        print('    Created', len(stack['cards']), 'archived cards')