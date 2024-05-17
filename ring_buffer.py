from settings import * 

class Ring_Buffer():
    def __init__(self) -> None:
        self.values = []
        self.head: int 
        self.tail: int 
        self.num_entries: int 
        self.max_size: int 

    def ring_buffer_init(self, max_size: int):
        self.max_size = max_size
        self.num_entries = 0
        self.head = 0
        self.tail = 0
        self.values = [-1] * max_size

    def ring_buffer_empty(self) -> bool: return self.num_entries == 0
    def ring_buffer_full(self) -> bool: return self.num_entries == self.max_size

    def ring_buffer_put(self, val: int) -> None: # add to the back of the queue
        if self.ring_buffer_full(): return 
        self.values[self.tail] = val
        self.num_entries += 1
        self.tail += 1
        if self.tail >= self.max_size: self.tail = 0

    def ring_buffer_get(self):
        if self.ring_buffer_empty(): return -1
        result = self.values[self.head]
        self.head += 1
        if self.head >= self.max_size: self.head = 0
        self.num_entries -= 1
        return result
    
    def ring_buffer_peek(self):
        if self.ring_buffer_empty(): return -1
        result = self.values[self.head]
        return result

