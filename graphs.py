import pdb

import networkx as nx
import matplotlib
import matplotlib.pyplot as plt
# import pygraphviz as pgv
import IPython
import DET
import graph_utils as gu

class FMP:
    def __init__(self):
        self.G = nx.MultiDiGraph()
        self.G_pristine = nx.MultiDiGraph()
        self.DEF = DET.DEF()

    def initialize(self, fname):
        self.G = nx.read_edgelist(fname, create_using=nx.MultiDiGraph)
        self.G_pristine = self.G.copy()
        #gu.draw_viz(graph=self.G)

    def get_cleaved_in_out_graph(self, node, G=None):
        if G == None:
            G = self.G
        G2 = G.copy()
        out_node = node + '_out'
        G2.add_node(out_node)
        for edge in G.edges(node, data=True, keys=True):
            G2.remove_edge(edge[0], edge[1], edge[2])
            for x in edge:
                new_edge = list(edge)
                new_edge[0] = out_node
            G2.add_edges_from([new_edge])
        return G2

    def generate_DEF(self, G=None):
        print("generating DET")
        self.DEF = DET.DEF()
        if G == None:
            G = self.G
        G_DEF = G.copy()
        self.DEF.grow_with(G_DEF)
        #self.grow_DET_with(G_DET)
        #print(self.DEF.forest.nodes)





    def get_v_to_v_changes(self, mod_graph, v, DEF_node):
        cleaved_mod_graph = self.get_cleaved_in_out_graph(v, mod_graph)
        #gu.draw_viz("cleaved_mod.png", cleaved_mod_graph)

        cycle_paths = nx.all_simple_edge_paths(cleaved_mod_graph, v+"_out", v)
        cycle_changes = gu.get_per_path_changes(cleaved_mod_graph, cycle_paths)

        mod_vertices = DEF_node[1].split("_")
        expanded_mod_graph = self.G.subgraph(mod_vertices).copy()
        through_paths = gu.get_through_paths(expanded_mod_graph, self.DEF.mod_graph_interfaces[DEF_node]["entry"],\
                                                        self.DEF.mod_graph_interfaces[DEF_node]["exit"])
        through_changes = gu.get_per_path_changes(expanded_mod_graph, through_paths)
        # print("\n\nThrough changes in " + repr(DEF_node) + ":" + repr(through_changes))
        # print("cycle changes in " + repr(DEF_node) + ":" + repr(cycle_changes))
        # print("\n")
        all_changes = cycle_changes + through_changes

        return all_changes
        #return changes

    def get_pot_inc_or_zero_change_vars_for_mod(self, mod_graph, v, DET_node):
        path_deltas = self.get_v_to_v_changes(mod_graph, v, DET_node)
        pi_vars = set()
        pz_vars = set()
        for deltas in path_deltas:
            #print(deltas)
            new_pi_vars = set(filter(lambda x: deltas[x]>0, deltas.keys()))
            new_pz_vars = set(filter(lambda x: deltas[x]==0, deltas.keys()))

            pi_vars.update(new_pi_vars)
            pz_vars.update(new_pz_vars)
        # print("PI Vars of " + mod_graph.graph_attr_dict_factory['name']+":"+repr(pi_vars))
        # print(pi_vars)
        # print("PZ Vars of " + mod_graph.graph_attr_dict_factory['name']+":"+repr(pi_vars))
        # print(pz_vars)

        return pi_vars,pz_vars

    def get_all_pot_inc_or_zero_change_vars(self, DET_node):
        pi_vars, pz_vars = self.get_pot_inc_or_zero_change_vars_for_mod(self.DEF.get_mod_graph(DET_node, self.G), DET_node[0], DET_node)

        for child_node in self.DEF.get_children(DET_node):
            new_pi, new_pz = self.get_all_pot_inc_or_zero_change_vars(child_node)
            pi_vars.update(new_pi)
            pz_vars.update(new_pz)
        print("PI Vars of " + repr(DET_node)+":"+repr(pi_vars))
        print("PZ Vars of " + repr(DET_node)+":"+repr(pz_vars))

        return pi_vars, pz_vars

    def get_pot_inc_or_zero_change_vars_for_G(self):
        pi_vars = set()
        pz_vars = set()
        for DET_node in self.DEF.forest_roots:
            pi, pz = self.get_all_pot_inc_or_zero_change_vars(DET_node)
            pi_vars.update(pi)
            pz_vars.update(pz)
        return pi_vars, pz_vars

    def get_dec_vars_for_mod(self, mod_graph, v, DEF_node):
        path_deltas = self.get_v_to_v_changes(mod_graph, v, DEF_node)
        d_vars = []
        for deltas in path_deltas:
            #print(deltas)
            net_dec_vars = list(filter(lambda x: deltas[x]<0, deltas.keys()))
            if len(net_dec_vars) == 0:
                #print("Mod Graph " + mod_graph.graph_attr_dict_factory['name']+ " has a cycle with no net-decrease vars")
                d_vars.append([])
                #return d_vars
            d_vars.append(net_dec_vars)

        if len(path_deltas) != 0:
            #print("Decreased Vars of " + mod_graph.graph_attr_dict_factory['name'])
            #print(d_vars)
            print("")
        else:
            print("No cycles in " + mod_graph.graph_attr_dict_factory['name'])
        return d_vars

    def boxminus(self, list_of_lists, lremove):
        if len(lremove) == 0 or len(list_of_lists)==0:
            return list_of_lists
        boxminus = list(map(lambda x: [e for e in x if not e in lremove], list_of_lists))
        return boxminus

    def get_all_dec_vars(self, DET_node, pi_vars):
        d_vars = set()
        pd_vars = self.get_dec_vars_for_mod(self.DEF.get_mod_graph(DET_node, self.G), DET_node[0], DET_node)
        d_vars = self.boxminus(pd_vars, pi_vars)
        if [] in d_vars:
            #print("Found a cyclic path without a net-decrease variable in " + repr(pd_vars))
            print("because PI Vars are " + repr(pi_vars))
        for child_node in self.DEF.get_children(DET_node):
            d_vars.extend(self.get_all_dec_vars(child_node, pi_vars))
        return d_vars

    def get_dec_var_edges(self, pure_dec_vars):
        print("\n\n pruning edges that decrease " + repr(pure_dec_vars))
        rm_list = []
        for e in self.G.edges(keys=True, data=True):
            print(e)
            if '-' in e[3]['label']:
                if e[3]['label'].split("-")[0] in pure_dec_vars:
                   rm_list.append(e)
                   print("will remove edge  "+ repr(e))
        return rm_list

    def get_dec_vars_for_G(self):
        progress = True
        iteration = 0
        while progress:
            iteration += 1
            gu.draw_viz("o_G" + repr(iteration)+".pdf", self.G)

            self.generate_DEF()
            gu.draw_viz("o_DET" + repr(iteration)+ ".pdf", self.DEF.forest)

            pi_vars, pz_vars = self.get_pot_inc_or_zero_change_vars_for_G()

            print("\n\n\nBuilding List of DecVars\n")
            d_vars = []
            for DET_node in self.DEF.forest_roots:
                d_vars.extend(self.get_all_dec_vars(DET_node, pi_vars))
                if [] in d_vars:
                    #print("List of dec vars in Iteration " + repr(iteration) \
                     #     +": " + repr(d_vars))
                    print("can't guarantee termination yet")
                    # remove variables that can have a net-zero change
                    d_vars = self.boxminus(d_vars, pz_vars)
                    #break

            #print("\n\nGlobal Net Decrease variables " + repr(d_vars))
            print("Global PIVars: " + repr(pi_vars))
            print("Global PZVars: " + repr(pz_vars))
            #print("Global Net Decrease vars for pruning: " + repr(d_vars))

            if [] in d_vars:
            # prepare for the next pass:
            # delete edges with net-dec vars because they can be executed only finitely many times
                d_var_set = set()
                for var_list in d_vars:
                    d_var_set.update(var_list)

                dud_edges = []
                if len(d_var_set)>0:
                    dud_edges = self.get_dec_var_edges(d_var_set)
                if len(dud_edges) == 0:
                    progress = False
                    print("FMP may not terminate")
                    print("Stopping at iteration " + repr(iteration))
                    return False
                print("\n\n====\nStarting iteration " + repr(iteration+1) + "\n====")
                self.G.remove_edges_from(dud_edges)
            else:
                print("Termination established")
                #IPython.embed()
                progress = False
                return True
            #limit to one iteration, no reduction
            #progress = False



if __name__ == "__main__":
    #
    f = FMP()
