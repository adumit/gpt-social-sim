import openai

from person import Person

class TalkListenPair:
    def __init__(self, talker: Person, listener: Person, message: str):
        self.talker = talker
        self.listener = listener
        self.message = message
    
    def get_response(self):
        response = openai.ChatCompletion.create(
            engine="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": self.listener.personality},
                {"role": "user", "content": self.message},
                {"role": "assistant", "content": self.talker.personality},
                
            ],
            temperature=0.7,
            max_tokens=200,
        )
        return response.choices[0].message["content"]
