
class SubscribersHandler:
    def __init__(self) -> None:
        self.subscribers = set([648038516])

    def add(self, id):
        self.subscribers.add(id)

    def remove(self, id):
        self.subscribers.remove(id)

    def get(self):
        return self.subscribers