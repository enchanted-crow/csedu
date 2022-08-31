class BST:
    root = None
    size = 0

    def insert(self, value, func):
        parent = self.search(value, func)

        # Insert node into BST
        if(parent == None):
            # No parent. So add as root.
            self._add_root(value)
        else:
            # Parent found
            if(value <= parent.data):
                parent.add_left_child(value)
            else:
                parent.add_right_child(value)
        self.size += 1

    def _add_root(self, value):
        self.root = BST._BSTNode(value)

    def search(self, value, func):
        func()

        if(self.size == 0):
            # Tree empty, return None
            return None
        if(self.size == 1):
            # Only node is root
            return self.root
        else:
            curr = self.root

            while True:
                # Custom function. Here, it will call the hop-counter to increment
                func()

                if(value < curr.data):
                    if(curr.left == None):
                        return curr
                    curr = curr.left
                elif(curr.data < value):
                    if(curr.right == None):
                        return curr
                    curr = curr.right
                else:
                    return curr

    class _BSTNode:
        data = -1
        left = None
        right = None

        def __init__(self, _data):
            self.data = _data

        def __init__(self, _data, _left=None, _right=None):
            self.data = _data
            self.left = _left
            self.right = _right

        def add_left_child(self, value):
            child = BST._BSTNode(value)
            self.left = child

        def add_right_child(self, value):
            child = BST._BSTNode(value)
            self.right = child
