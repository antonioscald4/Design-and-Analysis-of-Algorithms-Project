from graphs.graph import Graph
from graphs.bfs import BFS

def can_be_derived(other_profile, profile,k):
    "a profile can be derived from another one only if the difference between them is some S in place of a P or an F"
    count_of_s = 0
    for i in range(len(other_profile)):
        if other_profile[i] != profile[i]:
            if other_profile[i] == 'S':
                count_of_s += 1
            else: return False
    if count_of_s <= k: 
        return True
    else: return False 

def is_a_cheat(other_profile, profile):
    "supposing that other profile can be derived from profile"
    for i in range(len(other_profile)):
        if other_profile[i] != profile[i]:
            if other_profile[i] == 'S' and profile[i] == 'F':
                return True
            else: return False

def factorial(n):
    fact = 1
    for i in range(1, n+1):
        fact = fact * i
    return fact

def get_node_from_graph(graph, element):
    for node in graph.vertices():
        if node.element() == element:
            return node

def edge_is_in_path(edge, s_t_path):
    u, v = edge.endpoints()
    for i in range(len(s_t_path)-1):
        if u.element() == s_t_path[i].element() and v.element() == s_t_path[i+1].element():
            return True
    return False
        
def copy_original_graph(graph): 
    residual_graph = Graph(directed=True)
    for node in graph.vertices():
        residual_graph.insert_vertex(node.element())
    for edge in graph.edges():
        u,v = edge.endpoints()
        u_in_residual_graph = get_node_from_graph(residual_graph, u.element())
        v_in_residual_graph = get_node_from_graph(residual_graph, v.element())
        capacity = edge.element()
        #print("edge " + str(edge))
        residual_graph.insert_edge(u_in_residual_graph, v_in_residual_graph, capacity)   
        print("forward edge inserted: " + str(residual_graph.get_edge(u_in_residual_graph, v_in_residual_graph)))    
        
    return residual_graph

def compute_residual_graph(original_graph, graph, flow, s_t_path): 
    residual_graph = Graph(directed=True) 
    for node in graph.vertices():
        residual_graph.insert_vertex(node.element())
    for edge in graph.edges(): # creates the edges in the new residual graph according to the flow passed as parameter
        u,v = edge.endpoints()
        u_in_residual_graph = get_node_from_graph(residual_graph, u.element())
        v_in_residual_graph = get_node_from_graph(residual_graph, v.element())
        u_in_original_graph = get_node_from_graph(original_graph, u.element())
        v_in_original_graph = get_node_from_graph(original_graph, v.element())
        if original_graph.get_edge(u_in_original_graph, v_in_original_graph) is not None: # check if the current edge corresponds to an edge in the original graph (in the original graph there is an edge with the same source and the same destination)
            capacity = original_graph.get_edge(u_in_original_graph, v_in_original_graph).element()
        else: capacity = edge.element()
        #print("edge " + str(edge))
        if flow is not None and flow[edge] < capacity:
            residual_graph.insert_edge(u_in_residual_graph, v_in_residual_graph, capacity-flow[edge])
            print("forward edge inserted: " + str(residual_graph.get_edge(u_in_residual_graph, v_in_residual_graph)))    
        if flow is not None and flow[edge] > 0:
            residual_graph.insert_edge(v_in_residual_graph, u_in_residual_graph, flow[edge])
            flow[residual_graph.get_edge(v_in_residual_graph, u_in_residual_graph)] = flow[graph.get_edge(v, u)] if graph.get_edge(v, u) is not None else 0 ###################################
            print("back edge inserted: " + str(residual_graph.get_edge(v_in_residual_graph, u_in_residual_graph)))
        
    return residual_graph

def source_target_path(graph, source, target):
    forest = {}
    forest[source] = None         
    BFS(graph, source, forest)
    path = [target]
    previous_node = target
    if target not in forest.keys():
        return None
    while previous_node != source:
        path.append(forest[previous_node].opposite(previous_node))
        previous_node = forest[previous_node].opposite(previous_node)
    path.reverse()
    return path


def augment_flow(original_graph, residual_graph, s_t_path, flow):
    new_flow = dict()
    if flow is not None:         
        for edge in flow.keys(): # copy the previous flow in a new flow for the new residual graph
            if edge is not None:   
                u,v = edge.endpoints()
                node_u_in_residual_graph = get_node_from_graph(residual_graph, u.element())
                node_v_in_residual_graph = get_node_from_graph(residual_graph, v.element())
                new_flow[residual_graph.get_edge(node_u_in_residual_graph,node_v_in_residual_graph)] = flow[edge]
            else: print("edge None: "+ str(edge))
    bottleneck_capacity = 100                                   
    for i in range(len(s_t_path)-1):   # find the bottleneck capacity
        edge_origin = get_node_from_graph(residual_graph, s_t_path[i].element()) # nodes in s_t_path are not from the current residual graph, take the corresponding node in the current residual graph
        edge_destination = get_node_from_graph(residual_graph, s_t_path[i+1].element())
        current_edge = residual_graph.get_edge(edge_origin,edge_destination)
        if current_edge is not None and current_edge.element() < bottleneck_capacity:
            bottleneck_capacity = current_edge.element()
    print("bottleneck " + str(bottleneck_capacity))
    for i in range(len(s_t_path)-1):   # augment the flow
        edge_origin = get_node_from_graph(residual_graph, s_t_path[i].element())
        edge_destination = get_node_from_graph(residual_graph, s_t_path[i+1].element())
        current_edge = residual_graph.get_edge(edge_origin,edge_destination)
        if current_edge is not None:
            u_in_original_graph = get_node_from_graph(original_graph, s_t_path[i].element())
            v_in_original_graph = get_node_from_graph(original_graph, s_t_path[i+1].element())
            edge_in_original_graph = original_graph.get_edge(u_in_original_graph,v_in_original_graph)
            if edge_in_original_graph is not None: # if current_edge was in the original graph, then it is a forward edge
                new_flow[current_edge] += bottleneck_capacity
            else:
                new_flow[current_edge] -= bottleneck_capacity

    return new_flow


def get_max_flow(original_graph, source, target):
    flow = dict()
    for edge in original_graph.edges():
        flow[edge] = 0
    residual_graph = copy_original_graph(original_graph)
    s_t_path = source_target_path(original_graph, source, target)
    while s_t_path is not None:
        print("path: ")
        for i in range(len(s_t_path)):
            print(s_t_path[i].element())
        new_flow = augment_flow(original_graph, residual_graph, s_t_path, flow) 
        flow = new_flow
        residual_graph = compute_residual_graph(original_graph, residual_graph, flow, s_t_path) 
        s_t_path = source_target_path(residual_graph, get_node_from_graph(residual_graph, source.element()), get_node_from_graph(residual_graph, target.element()))
    
    return flow, residual_graph


def admitted(k,distro):
    if len(distro) != 3**k:
        raise ValueError("Distro must contain 3^k entries")
    
    graph = Graph(directed=True)
    for result_profile in distro.keys():
        graph.insert_vertex(result_profile)
    for node in graph.vertices():
        for other_node in graph.vertices():
            if node!=other_node and can_be_derived(other_node.element(),node.element(),k):
                if is_a_cheat(other_node.element(),node.element()):
                    graph.insert_edge(node,other_node, 1)
                    graph.insert_edge(other_node,node, 100-2*distro[node.element()]+factorial(k)+1) # since there is the constraint to pick always the profile related to a cheat and the corresponding profile without the cheat, an edge going from the node of the cheat to the true-profile node is necessary to keep these nodes always connected
                else: graph.insert_edge(node,other_node, 1)
    adm_node = graph.insert_vertex("ADM")
    not_node = graph.insert_vertex("NOT")
    for node in graph.vertices():
        if node.element() != "ADM" and node.element() != "NOT":
            graph.insert_edge(adm_node,node,distro[node.element()])
            graph.insert_edge(node,not_node,100-distro[node.element()])

    max_flow, residual_graph = get_max_flow(graph, adm_node, not_node) # get the minimum cut in the graph: the source node is the adm_node, the target is the not_node 
    for key in max_flow.keys():
        print("edge: "+ str(key) + " flow: " + str(max_flow[key]))
    forest = {}
    BFS(residual_graph, get_node_from_graph(residual_graph,adm_node.element()), forest) # get the nodes reachable from the source
    reachable_nodes = []
    for key in forest.keys():
        print("node: " + str(key) + " reachable via: " + str(forest[key]))
        if str(key) != "ADM":
            reachable_nodes.append(key)
    
    return tuple(reachable_nodes)

    
# 100-2*distro[node.element()]+3 is the capacity of the edges that start from a "cheat-node" and end to a "node" representing the profile the "cheat-node" can be derived from, by substituting an "F" with an "S".   
# With this capacity it is possible to respect the constraint given: in fact, in this situation the set of edges representing the minimum cut will not contain the edges with this capacity.
# The constraint is valid because the weight of all the other edges not adjacent to ADM and NOT is <= 1






# Testing
k = 2
distro = {
    ('F', 'F'): 10,
    ('F', 'P'): 40,
    ('F', 'S'): 20,
    ('P', 'F'): 40,
    ('P', 'P'): 90,
    ('P', 'S'): 65,
    ('S', 'F'): 10,
    ('S', 'P'): 50,
    ('S', 'S'): 1
}
admitted_profiles = (admitted(k, distro))
for profile in admitted_profiles:
    print(str(profile))
