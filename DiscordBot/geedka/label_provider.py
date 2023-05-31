
class LabelProvider:
        def __init__(self):
                self.counter = 0

        # Python doesn't have post increment?
        def get_label(self) -> int:
                tmp : int = self.counter
                self.counter += 1
                return tmp

