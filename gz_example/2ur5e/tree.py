import copy
import numpy as np
#form, traverse and solve the tree
class Treenode(object):  # Add Node feature
    def __init__(self, index, level, weight, parent=None):
        self.index = index
        self.level = level
        self.weight = weight
        self.parent = parent
        self.weight_till_now=0
        self.children = []
        self.remaining_object=[]

def formD(objects, desired_locations, home):
	D=np.full((len(objects)+len(desired_locations),len(objects)+len(desired_locations)),np.inf)
	for i in range(len(objects)):
		for j in range(len(desired_locations)):
			D[i][j+len(objects)]=np.linalg.norm(objects[i]-desired_locations[j])
			D[j+len(objects)][i]=np.linalg.norm(objects[i]-desired_locations[j])
		D[i][-1]=np.linalg.norm(objects[i]-home)
		D[-1][i]=np.linalg.norm(objects[i]-home)
	for j in range(len(desired_locations)):
		D[-1][j+len(objects)]=np.linalg.norm(home-desired_locations[j])
		D[j+len(objects)][-1]=np.linalg.norm(home-desired_locations[j])

	return D,list(range(len(objects))),list(range(len(objects),len(objects)+len(desired_locations))),-1
# D=np.array([[np.inf,np.inf,np.inf,np.inf,3,2,1,1,1],
# 			[np.inf,np.inf,np.inf,np.inf,4,3,2,2,3],
# 			[np.inf,np.inf,np.inf,np.inf,5,4,3,3,2],
# 			[np.inf,np.inf,np.inf,np.inf,6,5,4,4,4],
# 			[3,4,5,6,np.inf,np.inf,np.inf,np.inf,5],
# 			[2,3,4,5,np.inf,np.inf,np.inf,np.inf,4],
# 			[1,2,3,4,np.inf,np.inf,np.inf,np.inf,3],
# 			[1,2,3,4,np.inf,np.inf,np.inf,np.inf,3],
# 			[1,3,2,4,5,4,3,3,np.inf]
# 	])

# object_idx_list=[0,1,2,3]
# box_idx_list=[4,5,6,7]
# home_idx=-1

def solver(D,object_idx_list,box_idx_list,home_idx):

	root=Treenode(home_idx,0,0)
	root.remaining_object=copy.deepcopy(object_idx_list)
	node_stack=[root]
	leaf_nodes=[]		#list of leaf node


	while node_stack:
		cur_node=node_stack.pop(-1)
		try:
			cur_node.weight_till_now=cur_node.parent.weight_till_now+cur_node.weight
		except AttributeError:
			cur_node.weight_till_now=cur_node.weight
		if cur_node.index==home_idx and cur_node.parent:			# if returns home
			leaf_nodes.append(cur_node)
			continue
		#next node should be box
		if cur_node.index in object_idx_list:
			destination_idx=int(cur_node.level/2)
			cur_node.children.append(Treenode(box_idx_list[destination_idx],cur_node.level+1,D[cur_node.index][box_idx_list[destination_idx]],cur_node))
			cur_node.children[-1].remaining_object=cur_node.remaining_object
			node_stack.append(cur_node.children[-1])
		#next node should be objects
		elif cur_node.index in box_idx_list or cur_node.index==home_idx:
			if not cur_node.remaining_object:
				node_stack.append(Treenode(-1,cur_node.level+1,D[cur_node.index][-1],cur_node))
				continue
			for remaining_object in cur_node.remaining_object:

				cur_node.children.append(Treenode(remaining_object,cur_node.level+1,D[cur_node.index][remaining_object],cur_node))
				cur_node.children[-1].remaining_object=copy.deepcopy(cur_node.remaining_object)
				cur_node.children[-1].remaining_object.remove(remaining_object)
				node_stack.append(cur_node.children[-1])
		
	total_weight_list=[leaf_node.weight_till_now for leaf_node in leaf_nodes]
	# print(total_weight_list)

	####decode matrix index to object/box names:
	# names_dict={0:'1',1:'2',2:'3',3:'4',4:'A',5:'B',6:'C',7:'D',-1:'H'}
	# cur_node=leaf_nodes[total_weight_list.index(min(total_weight_list))]
	# order=[]
	# while cur_node.parent:
	# 	order.insert(0,names_dict[cur_node.index])
	# 	cur_node=cur_node.parent
	# return ['H']+order
	cur_node=leaf_nodes[total_weight_list.index(min(total_weight_list))]
	order=[]
	while cur_node.parent:
		order.insert(0,cur_node.index)
		cur_node=cur_node.parent
	return [-1]+order


def train(D,object_idx_list,box_idx_list,home_idx):
	##initialize Q to np.inf
	Q=np.full((len(box_idx_list),len(object_idx_list)),np.inf)
	for i in range(50000):
		#get random start objects
		visited=[]
		for j in range(len(box_idx_list)):
			cur_obj=int(np.random.random()*len(box_idx_list))
			while cur_obj in visited:
				cur_obj=int(np.random.random()*len(box_idx_list))
			visited.append(cur_obj)
			#from previous location travel to obj, obj to destination
			if j==0:
				weight=D[home_idx][cur_obj]+D[box_idx_list[j]][cur_obj]
			else:
				weight=D[box_idx_list[j]-1][cur_obj]+D[box_idx_list[j]][cur_obj]
			#last step, go home
			if j==len(box_idx_list)-1:
				weight+=D[-1][box_idx_list[j]]
				Q[j][cur_obj]=weight
			else:
				Q_next=np.delete(Q[j+1], visited)
				Q[j][cur_obj]=weight+np.min(Q_next)
	return Q
def execute(Q,object_idx_list,box_idx_list,home_idx):
	visited=[]
	order=[home_idx]
	for j in range(len(box_idx_list)):
		Q_next=np.delete(Q[j],visited)
		min_weight=np.min(Q_next)

		cur_obj=np.where(Q[j]==min_weight)[0][0]
		visited.append(cur_obj)
		order.append(cur_obj)
		order.append(box_idx_list[j])
	order.append(-1)
	return order


#1 for abb, 2 for sawyer
# box1=[-0.6, 0.6]
# box2=[0.6, 0.6]
# des1=[-0.1,0]
# des2=[0.1,0]
# home1=np.array([-0.5,0,1.])
# objects=[]
# desired_locations=[]
# for i in range(4):
# 	objects.append(np.array([box1[0]-0.05,box1[1]-0.15+0.1*i,1.]))
# 	objects.append(np.array([box1[0]+0.05,box1[1]-0.15+0.1*i,1.]))
# 	desired_locations.append(np.array([des1[0]+0.2,des1[1]-0.8+0.3*i,1.]))
# 	desired_locations.append(np.array([des1[0]-0.2,des1[1]-0.8+0.3*i,1.]))

# D,object_idx_list,box_idx_list,home_idx=formD(objects, desired_locations, home1)
# order=solver(D,object_idx_list,box_idx_list,home_idx)
# print(order)

# Q=train(D,object_idx_list,box_idx_list,home_idx)
# order=execute(Q,object_idx_list,box_idx_list,home_idx)

# print(order)
