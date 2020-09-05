from dataclasses import dataclass
from typing import List
import dateutil.parser

color_map = {
    "green": "49b675",
    "yellow": "FFFF00",
    "orange": "FFA500",
    "red": "FF0000",
    "purple": "800080",
    "blue": "0000FF",
    "sky": "87ceeb",
    "lime": "9efd38",
    "pink": "c09da4",
    "black": "000000",
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
class Card:
    name: str
    archived: bool
    due_date: str
    description: str
    order: int  # Order within a stack
    checklists: List[Checklist]
    labels: List[Label]
    trelloUrl: str


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


# TODO: Assign correct users


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
                                    item.name, item.name == "completed", item.pos
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


def get_label_ids(labels, label_ids):
    return list(filter(lambda label: label.trelloId in label_ids, labels))


def get_cards_by_stack(cards, checklists, labels, trello_stack_id):
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
                ),
                cards,
            ),
            key=lambda card: card.order,
        )
    )


def to_board(trello_json):
    labels = list(
        map(
            lambda label: Label(label.id, label.name, color_map[label.color]),
            trello_json.labels,
        )
    )

    not_closed_stacks = filter(lambda stack: not stack.closed, trello_json.lists)
    lists = list(
        sorted(
            map(
                lambda stack: Stack(
                    stack.name,
                    stack.pos,
                    get_cards_by_stack(
                        trello_json.cards, trello_json.checklists, labels, stack.id
                    ),
                ),
                not_closed_stacks,
            ),
            key=lambda stack: stack.order,
        )
    )

    return Board(
        trello_json.name, color_map[trello_json.prefs.background], labels, lists
    )
