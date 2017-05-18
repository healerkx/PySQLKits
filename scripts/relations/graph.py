
# http://igraph.org/python/doc/tutorial/tutorial.html
import igraph

class Graph(igraph.Graph):

    def __init__(self):
        super().__init__()
        self.vertex_maps = dict()
    
    def add_vertex(self, name, vertex=None):
        self.vertex_maps[name] = vertex
        self.add_vertices(name)

    def add_edge(self, name1, name2):
        self.add_edges([(name1, name2)])
    
    def get_vertex(self, name):
        return self.vertex_maps[name]


if __name__ == '__main__':
    g = Graph()
    g.add_vertex(0)
    g.add_vertex(1)
    g.add_vertex(2)
    g.add_vertex(3)
    g.add_vertex(4)

    g.add_edge(0, 1)
    g.add_edge(1, 2)
    g.add_edge(2, 4)

    print(g.get_all_shortest_paths(0, 4))

    