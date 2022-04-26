
class SubscribersHandler:
    def __init__(self, subscribers=[]) -> None:
        self.subscribers = set(subscribers)

    def add(self, id):
        self.subscribers.add(id)

    def remove(self, id):
        self.subscribers.remove(id)

    def get(self):
        return self.subscribers