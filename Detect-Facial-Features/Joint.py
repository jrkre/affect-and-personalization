import uuid

'''
Mostly stolen from https://stackoverflow.com/questions/2482602/a-general-tree-implementation
'''
(_ADD, _DELETE, _INSERT) = range(3)
(_ROOT, _DEPTH, _WIDTH) = range(3)


def sanitize_id(id):
    return id.strip().replace(" ", "")

class Joint:

    def __init__(self, name, identifier=None, offset=None, channels=None, expanded=True):
        self.offset = offset #transform from parent
        self.name = sanitize_id(name)
        self.__identifier = (str(uuid.uuid1()) if identifier is None else
                sanitize_id(str(identifier)))
        self.children = []
        self.channels = channels
        self.__bpointer = None
        self.__fpointer = []
        self.expanded = expanded

    @property
    def identifier(self):
        return self.__identifier

    @property
    def bpointer(self):
        return self.__bpointer

    @bpointer.setter
    def bpointer(self, value):
        if value is not None:
            self.__bpointer = sanitize_id(value)

    @property
    def fpointer(self):
        return self.__fpointer

    def update_fpointer(self, identifier, mode=_ADD):
        if mode is _ADD:
            self.__fpointer.append(sanitize_id(identifier))
        elif mode is _DELETE:
            self.__fpointer.remove(sanitize_id(identifier))
        elif mode is _INSERT:
            self.__fpointer = [sanitize_id(identifier)]

    
    # def add_child(self, node, parent):
    #     #print(f'adding node {node.name} to {self.name}')
        
    #     if parent == self.name:
    #         self.children.append(node)
    #         return
    #     else:
    #         for x in range(0, len(self.children)):
    #             self.children[x].add_child(node,parent)
    
    # def get_node(self, name):

    #     print (f'get_node checking: {self.name}')

    #     if self.name == name:
    #         return self
        
    #     for x in range(0, len(self.children)):
    #         return self.children[x].get_node(name)
        
        
    # def count(self):
    #     return 1 + sum(children.count() for children in self.children)
    
    # def print(self):
    #     print(f'NODE: {self.name} , {self.channels}, {self.offset}')
        
    #     for child in self.children:
    #         child.print()
    
    # def get_names_of_subtree(self, list):
    #     list.append(self.name)
    #     for x in range(0, len(self.children)):
    #         self.children[x].get_names_of_subtree(list)
    #     return list
    
    # def make_yaml(self):
    #     skeleton = dict()
    #     children = []
    #     if len(self.children) == 0:
    #         return dict(
    #             offset=self.offset,
    #             channels=self.channels,
    #             children=None
    #         )
        
    #     for x in range(0, len(self.children)):
    #         children.append(self.children[x].make_yaml())
        
    #     skeleton[self.name] = dict(
    #         offset=self.offset,
    #         channels=self.channels,
    #         children=children
    #     )
    #     return skeleton

class JointTree:
    def __init__(self):
        self.nodes = []

    def get_index(self, position):
        for index, node in enumerate(self.nodes):
            if node.identifier == position:
                break
        return index

    def create_joint(self, name, identifier=None, parent=None, offset=None, channels=None):

        node = Joint(name, identifier,offset,channels)
        self.nodes.append(node)
        self.__update_fpointer(parent, node.identifier, _ADD)
        node.bpointer = parent
        return node
    
    def create_joint_from_joint(self, node, parent_id=None):
        self.nodes.append(node)
        self.__update_fpointer(parent_id, node.identifier, _ADD)
        node.bpointer = parent_id
        return node


    def show(self, position, level=_ROOT):
        queue = self[position].fpointer
        if level == _ROOT:
            print("{0} [{1}]".format(self[position].name, self[position].identifier))
        else:
            print("\t"*level, "{0} [{1}]".format(self[position].name, self[position].identifier))
        if self[position].expanded:
            level += 1
            for element in queue:
                self.show(element, level)  # recursive call

    def get_subtree(self,position,level=_ROOT):
        nodes = []
        queue = self[position].fpointer
        if level == _ROOT:
            nodes.append(self[0])
            #print("{0} [{1}]".format(self[position].name, self[position].identifier))
        else:
            nodes.append(self[0])
            #print("\t"*level, "{0} [{1}]".format(self[position].name, self[position].identifier))
        if self[position].expanded:
            level += 1
            for element in queue:
                self.get_subtree(element, level)  # recursive call
        return nodes

    # def get_names_of_subtree(self,position,level=_ROOT):
    #     nodes = []
    #     queue = self[position].fpointer
        
    #     nodes.append(self[position].name)

    #     if self[position].expanded:
    #         level += 1
    #         for element in queue:
    #             nodes.append(self.get_names_of_subtree(element, level)[position].name)  # recursive call
    #     return nodes
        
    def __get_names_of_subtree_rec(self, nodes, cur_node):

        if cur_node.expanded:
            for element in cur_node.fpointer:
                print (element)
                nodes.append(element.name)

                self.get_names_of_subtree(nodes, element)

            return nodes

        return None

    def get_names_of_subtree(self, position):
        return self.__get_names_of_subtree_rec([self[position]], self[position])

    def expand_tree(self, position, mode=_DEPTH):
        # Python generator. Loosly based on an algorithm from 'Essential LISP' by
        # John R. Anderson, Albert T. Corbett, and Brian J. Reiser, page 239-241
        yield position
        queue = self[position].fpointer
        while queue:
            yield queue[0]
            expansion = self[queue[0]].fpointer
            if mode is _DEPTH:
                queue = expansion + queue[1:]  # depth-first
            elif mode is _WIDTH:
                queue = queue[1:] + expansion  # width-first

    def is_branch(self, position):
        return self[position].fpointer
    
    def get_current_root(self):
        return self[0]

    def __update_fpointer(self, position, identifier, mode):
        if position is None:
            return
        else:
            self[position].update_fpointer(identifier, mode)

    def __update_bpointer(self, position, identifier):
        self[position].bpointer = identifier

    def __getitem__(self, key):
        return self.nodes[self.get_index(key)]

    def __setitem__(self, key, item):
        self.nodes[self.get_index(key)] = item

    def __len__(self):
        return len(self.nodes)

    def __contains__(self, identifier):
        return [node.identifier for node in self.nodes if node.identifier is identifier]
    
    def __contains__(self, name):
        return [node.name for node in self.nodes if node.name is name]