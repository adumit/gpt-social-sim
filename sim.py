import typing as ta
import random
import time

from person import Person



def two_people_talk(person_a: Person, person_b: Person, max_number_of_messages_per_person: int = 3):
    person_b_message = ""
    for _ in range(max_number_of_messages_per_person):
        person_a_message = person_a.get_message(person_b_message, person_b)
        person_b_message = person_b.get_message(person_a_message, person_a)
        print(f"{person_a.name} says: {person_a_message}")
        time.sleep(0.3)
        print(f"{person_b.name} says: {person_b_message}")
        time.sleep(0.3)

    person_a.end_conversation()
    person_b.end_conversation()
    return


def run_sim(number_of_people: int = 3):
    people: ta.List[Person] = [
        Person()  # TODO: Initialize with goals
        for _ in range(number_of_people)
    ]
    
    for person in people:
        print(f"{person.name} {person.identity}")

    print("Starting conversations...\n\n")

    for _ in range(10):
        p1 = random.choice(people)
        p2 = random.choice([p for p in people if p != p1])
        print(f"Person {p1.name} is talking to person {p2.name}")
        two_people_talk(p1, p2)
        print("")


if __name__ == "__main__":
    run_sim()