class HashTable:
    table_size = 0
    secondary_hash_function_m = 0
    hash_table = []
    n_keys = 0

    def __init__(self, _size):
        self.table_size = HashTable._nextprime(_size)
        self.secondary_hash_function_m = HashTable._nextprime(
            self.table_size + 1)
        self.hash_table = [self._HashTableItem(occupied=False)
                           for i in range(0, self.table_size)]

    def insert(self, key, func):
        try:
            idx = self.search(key, func)
            self.hash_table[idx].put(key)
        except:
            print("Stuck in loop!")

    def search(self, key, func):
        func()
        idx = HashTable.H_primary(self, key=key)
        if(self.hash_table[idx].occupied == False):
            # Spot found
            return idx
        else:
            # Hash collision
            probe_number = 1
            while(True):  # TODO: Figure out the stop condition
                func()

                if(probe_number == 1000):
                    print("Probe " + str(probe_number))
                    return None

                new_idx = HashTable.probing_function(self, key, probe_number)
                if(self.hash_table[new_idx].occupied == False):
                    # Found a free spot
                    return new_idx
                probe_number += 1

    @staticmethod
    def _nextprime(n):
        p = n + 1
        for i in range(2, int(p)):
            if(p % i == 0):
                p = p + 1
        return p

    @staticmethod
    def H_primary(self, key):
        return key % self.table_size

    @staticmethod
    def H_secondary(self, key):
        return 1 + key % self.secondary_hash_function_m

    @staticmethod
    def probing_function(self, key, i):
        return (HashTable.H_primary(self, key) + i * HashTable.H_secondary(self, key)) % self.table_size

    class _HashTableItem:
        key = 0
        occupied = False

        def __init__(self, _key=-1, occupied=True):
            self.key = _key
            self.occupied = occupied

        def put(self, _key):
            self.key = _key
            self.occupied = True
            pass
