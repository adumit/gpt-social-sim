from __future__ import annotations
import typing as ta
import random

import openai

# Below are verbose descriptions of a person's identity in a few sentences
IDENTITIES = [
    "a hardworking single mother who dedicates most of her time to her two children. In her spare time, she enjoys painting landscapes and taking nature walks. You are is passionate about environmental conservation and dreams of one day opening her own art gallery.",
    "a young software engineer who loves to explore new technologies and programming languages. He is a talented musician, playing the guitar and piano in a local band. You are volunteers at a local animal shelter, where he helps care for abandoned pets.",
    "a talented chef who runs her own restaurant, specializing in fusion cuisine. She loves to travel the world, sampling various cultures and incorporating their flavors into her cooking. You are also an advocate for sustainable agriculture and sources her ingredients from local organic farms.",
    "a professional athlete, playing soccer for a renowned team. He is passionate about fitness and spends hours in the gym, perfecting his skills. You are a role model for young athletes and actively participates in charity events to raise funds for underprivileged children.",
    "a compassionate nurse who works long hours to provide care and comfort to her patients. She is an avid reader and loves to unwind with a good book after a long day. You are also a talented baker, often bringing her homemade treats to share with her colleagues.",
    "a successful entrepreneur who has built a tech startup from the ground up. He is deeply interested in artificial intelligence and its potential to revolutionize various industries. You enjoys mentoring young entrepreneurs and sharing his experiences with others.",
    "a dedicated high school teacher who is passionate about helping her students reach their full potential. She spends her free time volunteering at a local community center, teaching adult literacy courses. You love exploring the outdoors and going on long hikes with her dog.",
    "an accomplished architect, designing sustainable and innovative buildings around the world. He is a history enthusiast and enjoys visiting historical sites and museums during his travels. You are an amateur photographer and often captures stunning images of the places he visits.",
    "a talented dancer who performs with a prestigious ballet company. She is dedicated to her craft and spends hours perfecting her technique. You are passionate about animal welfare and supports various organizations that work towards the protection and conservation of wildlife.",
    "a gifted scientist, working on cutting-edge research in the field of renewable energy. He enjoys sharing his knowledge and frequently gives lectures at universities and conferences. You are a nature lover and spends his weekends birdwatching and participating in local conservation efforts.",
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

# TODO: Add in affect and what you think the other person's identity is.
# TODO: Add in goal
SYSTEM_PROMPT = """
You are a person who is talking to another person.
You are {name}, {identity}.
You are talking to {other_name}.
"""


class Conversation:
    def __init__(self, person_a: "Person", person_b: "Person") -> None:
        self.person_a = person_a
        self.person_b = person_b
        self.person_a_messages = []
        self.person_b_messages = []

    def append_message(self, message: str, from_person: "Person"):
        if message == "":
            return
        if from_person == self.person_a:
            self.person_a_messages.append(message)
        elif from_person == self.person_b:
            self.person_b_messages.append(message)
        else:
            raise ValueError("Invalid person")
        
    def to_chat_messages(self):
        messages = []
        for i in range(max(len(self.person_a_messages), len(self.person_b_messages))):
            if i < len(self.person_a_messages):
                messages.append({"role": "assistant", "content": self.person_a_messages[i]})
            if i < len(self.person_b_messages):
                messages.append({"role": "user", "content": self.person_b_messages[i]})
        return messages


class Person:
    def __init__(self) -> None:
        # TODO: Add in goals
        self.name = random.choice(NAMES)
        self.identity = random.choice(IDENTITIES)
        self.relationships: ta.Dict["Person", "Relationship"]  = {}
        self.current_conversation: ta.Optional[Conversation] = None

    def get_conversation(self, other: Person) -> Conversation:
        if other not in self.relationships:
            self.relationships[other] = Relationship(other)
        if self.current_conversation is None:
            self.current_conversation = Conversation(self, other)
        return self.current_conversation

    def get_message(self, other_said: str, other: Person) -> str:
        conversation = self.get_conversation(other)
        conversation.append_message(other_said, other)
        system_message = {"role": "system", "content": SYSTEM_PROMPT.format(
            name=self.name,
            identity=self.identity,
            other_name=other.name,
        )}
        chat_messages = conversation.to_chat_messages()
        messages_to_send = [system_message] + chat_messages
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages_to_send,
            temperature=0.7,
            max_tokens=200
        )
        return response.choices[0].message["content"]
    
    def end_conversation(self):
        other = self.current_conversation.person_b
        self.relationships[other].conversation_history.append(self.current_conversation)
        self.interpret_conversation(self.current_conversation)
        self.current_conversation = None

    def interpret_conversation(self, conversation: Conversation):
        pass


class Relationship:
    def __init__(self, target: Person) -> None:
        self.target = target
        self.target_identity = ""  # What I think about you
        self.affect = ""           # How I feel about you

        self.conversation_history: ta.List[Conversation] = []

        # Maybe for later.. this persons model of the other person's relationships
        # self.target_relationships: ta.Dict["Person", "Relationship"] = {}
    