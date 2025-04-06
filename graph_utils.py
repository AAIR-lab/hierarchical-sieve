import IPython
import networkx as nx
import pdb
import random

def draw(fname="test.png"):
    pos = nx.spring_layout(self.G)
    nx.draw(input_graph, pos=pos, with_labels=True, font_weight='bold')
    elabels = dict([((x, y), l["label"]) for x, y, l in input_graph.edges(keys=True, data=True)])
    print(elabels)

    nx.draw_networkx_edge_labels(input_graph, pos=pos, edge_labels=elabels, rotate=True, font_size=8)
    plt.savefig(fname)

def get_gv_node_name(node):
    node_tuple = node.split(",")
    v = node_tuple[0].strip("()' ")
    g = node_tuple[1].strip("()' ")
    new_node = "(" + g + ", " + v + ")"
    return new_node

def get_DET_graph_for_drawing(graph):
    B = nx.nx_agraph.to_agraph(graph)
    A = B.copy() #modify B itself because A does not get the name of B
    edges = B.edges()
    nodes = B.nodes()
    B.remove_edges_from(edges)
    B.remove_nodes_from(nodes)
    for node in nodes:
        B.add_node(get_gv_node_name(node))

    for edge in A.edges():
        x = edge[0]
        y = edge[1]
        B.add_edge(get_gv_node_name(x), get_gv_node_name(y))
    return B

def draw_viz(fname="test.png", output_dir="output/", graph=None):
    #return
    print("drawing graph " + fname)
    if graph is None:
        print("Nothing to draw!")
        return
    A = nx.nx_agraph.to_agraph(graph)
    if A.get_name() == "DEF":
        A = get_DET_graph_for_drawing(graph)
    A.edge_attr["fontsize"] = "22"
    A.node_attr["fontsize"] = "22"
    A.edge_attr["penwidth"] = "2"

    for edge in A.edges():
        edge.attr["style"] = "bold"
        edge.attr["minlen"] = "1"

    ofname = fname.split(".")[0]

    A.write(output_dir + "/" + ofname + ".dot")
    #A.layout(prog="dot", args=" -Gratio=0.5")
    A.draw(output_dir + "/" + ofname + ".pdf", format="pdf", prog="dot", \
           args="-Gratio=1, -Goverlap=false, -Gsplines=true, -Gmindist=1")

def get_through_paths(graph, entry_points, exit_points):
    paths = []
    # print("graph.nodes",)
    # print(graph.nodes)
    # print("entry_points" + repr(entry_points))
    # print("exit_points" + repr(exit_points))
    for entry in entry_points:
        for exit in exit_points:
            for path_gen in nx.all_simple_edge_paths(graph, entry, exit):
                simple_path = []
                for edge in path_gen:
                    simple_path.append(edge)
                paths.append(simple_path)
    return paths

def get_per_path_changes(graph, paths):
    edge_dict = {}
    for edge in graph.edges(keys=True, data=True):
        edge_dict[(edge[0], edge[1], edge[2])] = edge[3]
    changes = []
    for path in paths:
        delta_dict = {}
        for e in path:
            label = edge_dict[e]['label']
            # print("label is: " + label)
            var, delta = parse_edge_delta(label)
            delta_dict[var] = delta_dict.setdefault(var, 0) + delta
        changes.append(delta_dict)
        #print("changes due to path: " + repr(tuple(path)) +":" + repr(delta_dict))
    return changes


def parse_edge_delta(label):
    if '+' in label:
        var, delta = label.split("+")
        #print(label + "increases " + var + "  by " + delta )
        delta = int(delta)
    elif '-' in label:
        var, delta = label.split("-")
        #print(label + "decreases " + var + "  by " + delta )
        delta = -1 * int(delta)
    else:
        #print(label + "doesn't change any variable")
        delta = 0
    return var, delta


def generate_input_graph(fname="input/autogen_edge_list.txt", n = 5, v=3):
    nodes = ["q" + repr(i) for i in range(n)]
    edge_list =""

    #create edges with probability 0.5
    for node1 in nodes:
        for node2 in nodes:
            if node2 == node1:
                delta_ub=0
                #positive self-loops are non-terminating
                # not interesting as test cases
            else:
                delta_ub=2
            if random.random()>=0.5:
                var = "x" + repr(random.choice(range(v)))
                delta = random.choice([x for x in range(-2, delta_ub) if x != 0])
                if delta >= 0:
                    label = var + "+" + repr(delta)
                else:
                    label = var + repr(delta)
                #add node1, node2, x_i + delta
                edge_list += node1 + " " + node2 + " {\"label\": \"" + label + "\"}\n"
                #A B {"label": "x1-1"}
    f = open(fname, "w")
    f.writelines(edge_list)
    print("edge list: " + edge_list)
    f.close()


def get_non_trivial_sccs(G):
    child_sccs = list(nx.kosaraju_strongly_connected_components(G))
    dud_sccs = []
    child_scc_lists = [list(x) for x in child_sccs]
    for set_scc in [x for x in child_scc_lists if len(x) == 1]:
        list_scc = list(set_scc)
        if not (list_scc[0], list_scc[0]) in G.edges:
            dud_sccs.append(list_scc)
    return [scc for scc in child_scc_lists if scc not in dud_sccs]


def global_sieve(G):
    scc_list = get_non_trivial_sccs(G)
    if len(scc_list) == 0:
        return True
    status = True
    for list_scc in scc_list:
        var_edges = {}
        iz_vars = []
        scc_graph = G.subgraph(list_scc).copy()
        for edge in scc_graph.edges(keys=True, data=True):
            var, delta = parse_edge_delta(edge[3]["label"])
            var_edges.setdefault(var, []).append(edge)
            if delta >= 0:
                iz_vars.append(var)
        global_dec_vars = var_edges.keys() - iz_vars
        if len(global_dec_vars) > 0:
            for var in global_dec_vars:
                scc_graph.remove_edges_from(var_edges[var])
            status = status and global_sieve(scc_graph)
        else:
            return False

    return status
