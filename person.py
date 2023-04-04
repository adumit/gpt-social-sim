from __future__ import annotations
import typing as ta
import random
import json

import openai

# Below are verbose descriptions of a person's identity in a few sentences
IDENTITIES = [
    "A dragonborn paladin who was once a soldier in a war but left to pursue a more righteous path. They are fiercely loyal to their friends and have a strong sense of justice, always seeking to protect the innocent and punish the guilty.",
    "A tiefling rogue who grew up on the streets and learned to survive by pickpocketing and hustling. They have a talent for deception and often use their charm to get out of sticky situations.",
    "A half-elf bard who was raised by a troupe of traveling performers and has a deep appreciation for music and storytelling. They use their charisma and magical abilities to entertain crowds and sway people to their side.",
    "A human sorcerer who comes from a long line of powerful magic users. They are arrogant and often look down on those who do not have magical abilities, but they are fiercely protective of their family and friends.",
    "A dwarf cleric who worships a god of craftsmanship and takes great pride in their work. They are gruff and no-nonsense but have a heart of gold and will go to great lengths to help those in need.",
    "An elf ranger who has spent their life in the wilderness, hunting game and tracking their prey. They have a deep connection to nature and often speak with animals to gain information or assistance.",
    "A halfling monk who was raised in a monastery and has devoted their life to the pursuit of physical and spiritual perfection. They are disciplined and reserved, but their martial arts skills are unparalleled.",
    "A goblin wizard who was cast out from their tribe for being too intelligent and curious. They have since dedicated their life to the study of arcane magic and seek to uncover the secrets of the universe.",
    "A half-orc barbarian who was once a feared warrior in their tribe but has since left to explore the wider world. They have a quick temper and a love of battle, but they also have a strong sense of honor and loyalty.",
    "A gnome artificer who specializes in creating mechanical devices and gadgets. They have a childlike curiosity and a boundless imagination, but they are also highly skilled and innovative in their craft.",
]

NAMES = [
    "Aaliyah",
    "Aaron",
    "Abigail",
    "Adam",
    "Adrian",
    "Adriana",
    "Adrianna",
    "Adrienne",
    "Agnes",
    "Aidan",
    "Aiden",
    "Aileen",
    "Aimee",
    "Aisha",
    "Aiyana",
    "Akeem",
    "Alaina",
    "Alan",
    "Albert",
    "Alberto",
    "Alden",
    "Alec",
    "Alex",
    "Alexander",
    "Alexandra",
    "Alexandria",
    "Brenda",
    "Brendan",
    "Brennan",
]

GOALS = [
    "we should loot the jewelry from the dead person even if it's dangerous",
    "we should bury the person without removing any of their personal objects",
    "we should flee as fast as possible, there may be enemies about"
]

# TODO: Add in affect and what you think the other person's identity is.
# TODO: Add in goal
SYSTEM_PROMPT = """
You are a person who is talking to another person.
Do not write in second person. Act as though you are the person. Do not write a story.
You are {name}, {identity}.
You are talking to {other_name}.
You currently think that {other_name} is {other_identity}. And you feel {affect} about them.
Your goal is {goal}. You are trying to convince the others in the group to go along with your goal.
"""

INTERPRET_CONVERSATION_PROMPT = """
You just finished the conversation with {other_name}.
The conversation went like this:
{conversation}
You previously thought that {other_name} was {other_identity}. And you felt {affect} about them.
What do you think now?
Respond in JSON format with the following two keys:
<identity>: <NEW IDENTITY>,
<affect>: <NEW AFFECT>
"""


def get_chat_response(messages):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
        temperature=0.7,
        max_tokens=200
    )
    return response.choices[0].message["content"]


class Conversation:
    def __init__(self, person_a: "Person", person_b: "Person") -> None:
        self.person_a = person_a
        self.person_b = person_b
        self.person_a_messages = []
        self.person_b_messages = []

    def append_message(self, message: str, from_person: "Person"):
        if not message:
            return
        if from_person == self.person_a:
            self.person_a_messages.append(message)
        elif from_person == self.person_b:
            self.person_b_messages.append(message)
        else:
            raise ValueError("Invalid person")

    def as_string_messages(self):
        messages = []
        for i in range(max(len(self.person_a_messages), len(self.person_b_messages))):
            if i < len(self.person_a_messages):
                messages.append(f"{self.person_a.name}: {self.person_a_messages[i]}")
            if i < len(self.person_b_messages):
                messages.append(f"{self.person_b.name}: {self.person_b_messages[i]}")
        return "\n".join(messages)

    def to_chat_messages(self):
        messages = []
        for i in range(max(len(self.person_a_messages), len(self.person_b_messages))):
            if i < len(self.person_a_messages):
                messages.append({"role": "assistant", "content": self.person_a_messages[i]})
            if i < len(self.person_b_messages):
                messages.append({"role": "user", "content": self.person_b_messages[i]})
        if not messages:
            messages.append({"role": "user", "content": "What do you say to them?"})
        return messages


class Person:
    def __init__(self, goal: str = None) -> None:
        # TODO: Add in goals
        self.name = random.choice(NAMES)
        self.identity = random.choice(IDENTITIES)
        self.relationships: ta.Dict["Person", "Relationship"]  = {}
        self.current_conversation: ta.Optional[Conversation] = None
        self.goal = goal if goal else random.choice(GOALS)

    def get_conversation(self, other: Person) -> Conversation:
        if other not in self.relationships:
            self.relationships[other] = Relationship(other)
        if self.current_conversation is None:
            self.current_conversation = Conversation(self, other)
        return self.current_conversation

    def get_message(self, other_said: str, other: Person) -> str:
        conversation = self.get_conversation(other)
        conversation.append_message(other_said, other)

        current_relationship = self.relationships.get(other, Relationship(other))
        system_message = {"role": "system", "content": SYSTEM_PROMPT.format(
            name=self.name,
            identity=self.identity,
            other_name=other.name,
            other_identity=current_relationship.target_identity,
            affect=current_relationship.affect,
            goal=self.goal
        )}
        chat_messages = conversation.to_chat_messages()
        messages_to_send = [system_message] + chat_messages
        return get_chat_response(messages_to_send)
    
    def end_conversation(self):
        other = self.current_conversation.person_b
        self.relationships[other].conversation_history.append(self.current_conversation)
        self.interpret_conversation(self.current_conversation, self.relationships[other])
        self.current_conversation = None

    def interpret_conversation(self, conversation: Conversation, relationship: Relationship):
        system_message = {"role": "system", "content": SYSTEM_PROMPT.format(
            name=self.name,
            identity=self.identity,
            other_name=conversation.person_b.name,
            other_identity=relationship.target_identity,
            affect=relationship.affect,
            goal=self.goal
        )}
        
        user_prompt = INTERPRET_CONVERSATION_PROMPT.format(
            other_name=conversation.person_b.name,
            other_identity=relationship.target_identity,
            affect=relationship.affect,
            conversation=conversation.as_string_messages()
        )
        messages_to_send = [system_message] + [{
            "role": "user",
            "content": user_prompt
        }]
        response = get_chat_response(messages_to_send)
        json_response = json.loads(response)
        new_identity = json_response["identity"]
        new_affect = json_response["affect"]
        relationship.target_identity = new_identity
        relationship.affect = new_affect
        print(f"Person {self.name} think {relationship.target.name} is {new_identity} and feels {new_affect} about them.")
        return


class Relationship:
    def __init__(self, target: Person) -> None:
        self.target = target
        self.target_identity = "Currently unknown"  # What I think about you
        self.affect = "Neutral"                     # How I feel about you

        self.conversation_history: ta.List[Conversation] = []

        # Maybe for later.. this persons model of the other person's relationships
        # self.target_relationships: ta.Dict["Person", "Relationship"] = {}
    