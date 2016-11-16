
class Vertex:
    """
    A vertex is a wrapper for a customer object
    """
    def __init__(self, inner):
        self.inner = inner
        self.visit = 0
        self.adjacencies = []

    def add_adjacency(self, *adjacencies):
        for adjacency in adjacencies:
            self.adjacencies.append(adjacency)

    def can_visit_next(self):
        return self.visit + 1 <= len(self.adjacencies)

    def visit_next(self):
        if self.can_visit_next():
            cur = self.adjacencies[self.visit]
            self.visit += 1
            return cur
        else:
            return None
    
    def adjacency_list(self):
        return ','.join(map(lambda x: str(x.inner), self.adjacencies))

    def __str__(self):
        return "%s -> [%s]" % (str(self.inner), self.adjacency_list())


class Graph:
    """
    Hold a dict stores vertexes, provide graph API BFS, DFS related
    """
    def __init__(self):
        self.vertex_map = {}
    
    def add_vertex(self, name, vertex):
        self.vertex_map[name] = vertex
    
    def get_vertex(self, name):
        return self.vertex_map[name]

    @staticmethod
    def prev_vertex_list(graph, end):
        return [each for each in graph if end in each.adjacencies]

    @staticmethod
    def __all_paths(graph, begin, end):
        results = []
        middles = Graph.prev_vertex_list(graph, end)
        for middle in middles:
            if begin != middle:
                paths = Graph.__all_paths(graph, begin, middle)
                for path in paths:
                    results.append(path + [end])
            else:
                results.append([begin, end])

        return results

    def all_paths(self, begin, end):
        """
        Broad first search
        """
        return Graph.__all_paths(self.vertex_map.values(), begin, end)
    
    @staticmethod
    def prints(obj):
        values = obj
        if isinstance(obj, Graph):
            values = obj.vertex_map.values()
        for a in values:
            print(a)

    def find_path(self, begin, end):
        """
        Depth first search
        using stack
        TODO: Adding step show flag
        """
        v = begin
        stack = []
        
        while len(stack) >= 0:
            if v.can_visit_next():
                stack.append(v)
                v = v.visit_next()
                print("Move to", v)
                if v == end:
                    stack.append(v)
                    print("Found")
                    break
            elif len(stack) > 0:
                v = stack.pop()
                print("Back to", v)
            else:
                print('Not Found')
                break

        return stack


if __name__ == '__main__':
    """
    TODO: Finish a demo for Graph and Vertex usage
    """
    print('-' * 5, "One Way from <%s> to <%s>." % (a, j), '-' * 5)
    print(can_walk(a, j))


    