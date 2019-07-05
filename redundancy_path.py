import networkx as nx
import matplotlib.pyplot as plt
import sys

#返回目标节点的前置节点，list
# TODO 单向图问题待解决,目前支持双向图
def get_prenodes(G, target):
    dijkstra_predecessor = nx.dijkstra_predecessor_and_distance(G, target, cutoff=1, weight=None)
    return list(dijkstra_predecessor[1])

# 判断路径是否完全冗余 shortest_path 是已确定的最短路径， path_nodes 是搜索的新的路径
def judging_absent_shortestpath(shortest_path, path_nodes):
    for each in path_nodes:
        if each in shortest_path:
            return False
    return True

# 去掉重复的节点
def remove_repeat_node(source_nodes,target_nodes):
    repeat_nodes = list(set(source_nodes) & set(target_nodes))
    for each in repeat_nodes:
        source_nodes.remove(each)
    return source_nodes

# 找备份路径
def seek_redundancy_path(G, source, target, shortest_path, path_stacklist, searchedlist, weight=None):
    print("enter the seek_redundancy_path func")
    path_stacklist.append(target) # 存放倒序的列表 放入终点
    #源和目的一样，说明找到了最后一个节点，返回备份路径
    if source == target:
        path_stacklist.reverse()
        print("seek_redundancy_path:redundancy_path",path_stacklist)
        return path_stacklist

    #获取连接的节点
    target_prenodes = get_prenodes(G, target)
    # 去掉path_stacklist和searchedlist 已有的node
    target_prenodes = remove_repeat_node(target_prenodes,path_stacklist)
    target_prenodes = remove_repeat_node(target_prenodes,searchedlist)

    if (len(target_prenodes) == 1):  # 只有一个前置节点，上一跳只能是该节点，备份路径目的改成上一个节点寻找
        print("just one node", target)
        target = shortest_path[-2]   #目的节点前移一个
        shortest_path = shortest_path[0:-1]
        return seek_redundancy_path(G, source, target, shortest_path, path_stacklist, searchedlist)
    else:   #不只一个连接节点
        has_redundancy_node = False 
        refer_length = sys.maxsize
        redundancy_path = []
        newtarget = target
        pre_short_path = []

        for eachnode in target_prenodes:
            if eachnode not in path_stacklist:
                if eachnode not in shortest_path:  # 找新的可达前置节点 
                    if nx.has_path(G, source, eachnode):
                        has_redundancy_node = True  # 有冗余节点并且可达，置为true
                        pre_short_path = nx.dijkstra_path(G, source, eachnode, weight='weight')
                        #计算此节点的权重和
                        path_length = nx.dijkstra_path_length(G, source, eachnode)
                        #判断是否路径完全不重叠
                        if judging_absent_shortestpath(shortest_path[1:-1], pre_short_path):
                            if path_length < refer_length:
                                refer_length = path_length
                                path_stacklist.reverse()
                                redundancy_path =  pre_short_path + path_stacklist
                                print("totally redundancy path",redundancy_path,path_length)
                            #找到的第一条完全备份路径，不一定是最优的，需要把相同层级的节点遍历完
                            continue
                        else:
                            # 不能完全分离，需要先遍历完看看有没有完全分离的，作为次优选
                            if path_length < refer_length:
                                newtarget = eachnode  
                    else:  # 没有可达路径说明不可用
                        pass
        # 存在完全分离路径，返回最优路径                
        if len(redundancy_path):
            print("best totally redundancy path", redundancy_path)
            return redundancy_path
        else: #不存在完全分离的情况
            return seek_redundancy_path(G, source, newtarget, pre_short_path, path_stacklist, target_prenodes)
        
        #有冗余节点，但起点不可达，TODO 可能不存在这个场景
        if (has_redundancy_node == False):  
            print("has_no_redundancy_node", target)
            target = shortest_path[-2]      # 向前找
            shortest_path = shortest_path[0:-1]
            return seek_redundancy_path(G, source, target, shortest_path, path_stacklist,target_prenodes,weight=None)

#获取备份路径    
def get_redundancy_path(G, source, target, weight='weight'):
    #计算最短路径
    short_path = nx.dijkstra_path(G, source, target, weight='weight')
    print(short_path)

    path_stacklist = []
    redundancy_path = []
    searchedlist = []

    redundancy_path = seek_redundancy_path(G, source, target, short_path, path_stacklist, searchedlist, weight=None)
    
    if short_path == redundancy_path:
        print("have no redundancy_path")
        return None
    else:
        print("get_redundancy_path:redundancy_path", redundancy_path)
        return redundancy_path
    

if __name__ == "__main__":
    # 构造网络图
    G = nx.DiGraph()
    G.add_nodes_from(["A","B","C","D","E","F","G","H","I","J"])
    '''
    G.add_edges_from([("A","B", {'weight': 2}),
                    ("A","F", {'weight': 2}),
                    ("A","I", {'weight': 3}),
                    ("B", "A", {'weight': 2}),
                    ("B", "C", {'weight': 2}),
                    ("B", "F", {'weight': 1}),
                    ("C", "B", {'weight': 2}),
                    ("C", "G", {'weight': 1}),
                    ("C", "D", {'weight': 2}),
                    ("D", "C", {'weight': 2}),
                    ("D", "H", {'weight': 1}),
                    ("D", "E", {'weight': 2}),
                    ("E", "D", {'weight': 2}),
                    ("E", "H", {'weight': 2}),
                    ("E", "J", {'weight': 2}),
                    ("F", "A", {'weight': 2}),
                    ("F", "B", {'weight': 1}),
                    ("F", "G", {'weight': 2}),
                    ("G", "F", {'weight': 2}),
                    ("G", "C", {'weight': 1}),
                    ("G", "H", {'weight': 2}),
                    ("H", "G", {'weight': 2}),
                    ("H", "D", {'weight': 1}),
                    ("H", "E", {'weight': 2}),
                    ("I", "A", {'weight': 3}),
                    ("I", "J", {'weight': 6}),
                    ("J", "I", {'weight': 6}),
                    ("J", "E", {'weight': 3})])

    G.add_edges_from([("A","B"),("B","A"),("B","C"),("C","B"),("C","D"),("D","C"),("D","E"),
    ("E","D"),("C","F"),("F","C"),("F","E"),("E","F"),("B","H"),("H","B"),("H","E"),("E","H"),
    ("I","E"),("E","I"),("A","I"),("I","A")])
    '''

    # 双菱形组网
    '''
    G.add_edges_from([("A","B"),("B","A"),("A","C"),("C","A"),("B","D"),("D","B"),("D","C"),
    ("C","D"),("D","G"),("G","D"),("F","D"),("D","F"),("G","E"),("E","G"),("F","E"),("E","F"),
    ("B","C"),("C","B"),("G","F"),("F","G")])
    '''
    # 单路径
    '''
    G.add_edges_from([("A","B"),("B","A"),("B","C"),("C","B"),("C","D"),("D","C"),("D","E"),
    ("E","D")])
    '''
    #双矩形 
    G.add_edges_from([("A","B"),("B","A"),("B","C"),("C","B"),("C","D"),("D","C"),("D","A"),
    ("A","D"),("C","E"),("E","C"),("B","F"),("F","B"),("E","F"),("F","E")])

    
    nx.draw(G, with_labels=True)
    plt.show()
    
    ret = get_redundancy_path(G, "A", "E", weight='weight')

    if ret == None:
        print("have no redundancy_path")
    else:
        print("the redundancy_path is", ret)



                        


            





