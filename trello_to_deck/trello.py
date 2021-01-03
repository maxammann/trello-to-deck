from dataclasses import dataclass
from typing import List
import dateutil.parser

color_map = {
    "default": "0082c9",
    "green": "49b675",
    "yellow": "FFFF00",
    "orange": "FFA500",
    "red": "FF0000",
    "purple": "800080",
    "blue": "0000FF",
    "sky": "87ceeb",
    "lime": "9efd38",
    "pink": "c09da4",
    "black": "000000"
}


@dataclass
class ChecklistItem:
    name: str
    completed: bool
    order: int


@dataclass
class Checklist:
    name: str
    items: List[str]
    order: int


@dataclass
class Label:
    trelloId: str
    name: str
    color: str

@dataclass
class Attachment:
    fileName: str
    date: str
    url: str
    mimeType: str

@dataclass
class Card:
    name: str
    archived: bool
    due_date: str
    description: str
    order: int  # Order within a stack
    checklists: List[Checklist]
    labels: List[Label]
    trelloUrl: str
    comments: List[str]
    attachments: List[Attachment]

@dataclass
class Stack:
    name: str
    order: int
    cards: List[Card]


@dataclass
class Board:
    title: str
    color: str
    labels: List[Label]
    stacks: Stack

def get_checklist_by_card(checklists, card_id):
    checklists = filter(lambda checklist: checklist.idCard == card_id, checklists)
    return list(
        sorted(
            map(
                lambda checklist: Checklist(
                    checklist.name,
                    list(
                        sorted(
                            map(
                                lambda item: ChecklistItem(
                                    item.name, item.state == "complete", item.pos
                                ),
                                checklist.checkItems,
                            ),
                            key=lambda item: item.order,
                        )
                    ),
                    checklist.pos,
                ),
                checklists,
            ),
            key=lambda checklist: checklist.order,
        )
    )


def get_comments_by_card(actions, trello_card_id):
    commentCardActions = filter(lambda action: action.type == 'commentCard' and action.data.card.id == trello_card_id, actions)
    comments = list(map(lambda action: action.data.text, commentCardActions))
    return comments

def get_label_ids(labels, label_ids):
    return list(filter(lambda label: label.trelloId in label_ids, labels))


def get_cards_by_stack(cards, checklists, actions, labels, trello_stack_id):
    cards = filter(lambda card: card.idList == trello_stack_id, cards)
    return list(
        sorted(
            map(
                lambda card: Card(
                    card.name,
                    card.closed,
                    dateutil.parser.isoparse(card.badges.due)
                    if card.badges.due is not None
                    else None,
                    card.desc,
                    card.pos,
                    get_checklist_by_card(checklists, card.id),
                    get_label_ids(labels, card.idLabels),
                    card.shortUrl,
                    get_comments_by_card(actions, card.id),
                    list(map(lambda attachment: Attachment(attachment.fileName, attachment.date, attachment.url, attachment.mimeType), filter(lambda attachment: attachment.isUpload, card.attachments)))
                ),
                cards,
            ),
            key=lambda card: card.order,
        )
    )


def to_board(trello_json):
    labels = []
    for i, json_label in enumerate(trello_json.labels):
        label_name = json_label.name if len(json_label.name) > 0 else f"Label {i+1}"

        try:
            label_color = color_map[json_label.color]
        except KeyError:
            label_color = color_map["default"]

        labels.append(Label(json_label.id, label_name, label_color))

    not_closed_stacks = filter(lambda stack: not stack.closed, trello_json.lists)
    lists = list(
        sorted(
            map(
                lambda stack: Stack(
                    stack.name,
                    stack.pos,
                    get_cards_by_stack(
                        trello_json.cards, trello_json.checklists, trello_json.actions, labels, stack.id
                    ),
                ),
                not_closed_stacks,
            ),
            key=lambda stack: stack.order,
        )
    )

    # If background has 24 chars then it is an images
    if len(trello_json.prefs.background) != 24:
        try:
            background_color = color_map[trello_json.prefs.background] 
        except KeyError:
            background_color = color_map["default"] 
    else:
        background_color = color_map["default"] 

    return Board(
        trello_json.name, background_color, labels, lists
    )
