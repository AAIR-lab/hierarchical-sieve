import pdb

import networkx as nx
import graph_utils as gu
import random

class DEF:
    def __init__(self):
        self.forest = nx.DiGraph(name="DEF")
        self.forest_roots = []
        self.mod_graphs = {}
        self.mod_graph_interfaces = {}

    def grow_with(self, current_subgraph, parent_node=None, interactive=False):
        child_scc_list = nx.kosaraju_strongly_connected_components(current_subgraph)
        for set_scc in child_scc_list:
            list_scc = list(set_scc)
            list_scc.sort()
            if len(list_scc) == 1:
                if not (list_scc[0], list_scc[0]) in current_subgraph.edges:
                    continue

            chosen_v = random.choice(list_scc)
            if interactive:
                chosen_v = input("Nodes in SCC = " + repr(list_scc) + ". which should be used next?" )

            # #---------- for use with NT_edge_list3.txt
            # if 'I' in list_scc:
            #     chosen_v = 'I'
            # else:
            #     chosen_v = 'B'
            # #------- shows that not considering through-path changes
            # leads to incorrect assertion of termination
            # use with return changes (not all_changes) in graphs.py:
            # get_v_to_v_changes

            scc_name = "_".join(list_scc)
            new_DET_node = tuple([chosen_v, scc_name])
            self.forest.add_node(new_DET_node)
            if parent_node is not None:
                #print("adding edge: " + repr(parent_node) + " -> " +repr(new_DET_node))
                self.forest.add_edge(parent_node, new_DET_node)
            else:
                self.forest_roots.append(new_DET_node)

            child_subgraph = current_subgraph.subgraph(list_scc).copy()
            child_subgraph.remove_nodes_from([chosen_v])

            self.grow_with(child_subgraph, new_DET_node)

    def get_children(self, DEF_node):
        if self.forest.edges(DEF_node) is None:
            return None
        return [edge[1] for edge in self.forest.edges(DEF_node)]

    def get_mod_graph(self, DEF_node, input_graph):
        if DEF_node in self.mod_graphs.keys():
            #print("Found a stored mod-graph! Returning stored mod-graph")
            return self.mod_graphs[DEF_node]

        mod_vertices = DEF_node[1].split("_")
        mod_graph = input_graph.subgraph(mod_vertices).copy()

        child_DEF_nodes = [edge[1] for edge in self.forest.edges(DEF_node)]
        gname = "Gr[" + DEF_node[0] + "]" + DEF_node[1] + "|" + ",".join([node[1] for node in child_DEF_nodes])
        mod_graph.graph_attr_dict_factory = {'name': gname}

        print("creating mod graph for " + gname)

        # entry vertices are those that come into mod_graph from the input_graph
        entry_vertices = [edge[1] for edge in input_graph.edges(data=True, keys=True) if
                          edge[1] in mod_vertices and edge[0] not in mod_vertices]
        # exit vertices lead out of the mod_graph in to the input_graph
        exit_vertices = [edge[0] for edge in input_graph.edges(data=True, keys=True) if
                         edge[0] in mod_vertices and edge[1] not in mod_vertices]
        self.mod_graph_interfaces[DEF_node] = {"entry": entry_vertices, "exit": exit_vertices}

        for (vertex, subgraph_catlist) in child_DEF_nodes:
            subgraph_vertex_list = subgraph_catlist.split("_")
            subgraph_vertex_list.sort()
            # print("child's vertex set " + repr(subgraph_vertex_list))
            #in_edges are edges that go into subgraphs. edge[1] is in the child subgraph.
            in_edges = [edge for edge in mod_graph.edges(data=True, keys=True) if
                        edge[1] in subgraph_vertex_list and edge[0] not in subgraph_vertex_list]
            #out_edges come out of subgraphs. edge[0] is in the subgraph
            out_edges = [edge for edge in mod_graph.edges(data=True, keys=True) if
                         edge[0] in subgraph_vertex_list and edge[1] not in subgraph_vertex_list]
            # print("edges going into subgraph: " + repr(in_edges))
            # print("edges coming out of subgraph: " + repr(out_edges))

            mod_graph.remove_nodes_from(subgraph_vertex_list)
            subgraph_node = "c:" + "_".join(subgraph_vertex_list)
            mod_graph.add_node(subgraph_node)
            in_edge_count = 0
            for e in in_edges:
                le = list(e)
                le[1] = subgraph_node
                in_edge_count += 1
                le[2] = in_edge_count
                mod_graph.add_edges_from([tuple(le)])
            out_edge_count = 0
            for e in out_edges:
                le = list(e)
                le[0] = subgraph_node
                out_edge_count += 1
                le[2] = out_edge_count
                mod_graph.add_edges_from([tuple(le)])


        #gu.draw_viz("o_mod_graph" + gname + ".png", mod_graph)
        self.mod_graphs[DEF_node] = mod_graph

        return mod_graph

