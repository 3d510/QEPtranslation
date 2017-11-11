import json
import queue
import os


def translate_node_to_text(node_dict):
    return str(node_dict)  # To do


def translate_qep_to_dict(qep_path):
    with open(qep_path, 'r') as f:
        plan = json.load(f)[0]['Plan']
    return plan


def translate_qepdict_to_nodes(qepdict):
    node_children = {}  # map a node index to a list of children node's indices
    node_data = {}
    node_counter = 0
    node_queue = queue.Queue()

    node_queue.put(qepdict)
    while not node_queue.empty():
        node = node_queue.get()

        parent_id = node.pop('Parent Node Id', None)
        if parent_id is not None:
            if parent_id not in node_children:
                node_children[parent_id] = [node_counter]
            else:
                node_children[parent_id].append(node_counter)

        plans = node.pop('Plans', None)
        if plans is not None:
            for subplan in plans:
                subplan['Parent Node Id'] = node_counter
                node_queue.put(subplan)

        node_data[node_counter] = translate_node_to_text(node)
        node_counter += 1

    return node_data, node_children


def translate_qep(qep_json_path, qep_text_path):
    qep_dict = translate_qep_to_dict(qep_json_path)
    node_data, node_children = translate_qepdict_to_nodes(qep_dict)

    # traverse the qep tree
    node_visit_order = []

    def qep_tree_dfs(node_id):
        nonlocal node_visit_order
        if node_id in node_children:
            for child_id in node_children[node_id]:
                qep_tree_dfs(child_id)
        node_visit_order.append(node_id)

    qep_tree_dfs(0)
    node_visit_step = {}  # for each node, save the visit step
    for idx, val in enumerate(node_visit_order):
        node_visit_step[val] = idx+1

    # write qep text presentation to text file
    with open(qep_text_path, 'w') as f:
        f.write('hello, suggested query execution plan for your query is as following\n')
        for idx, node_id in enumerate(node_visit_order):
            children_results = ""
            if node_id in node_children:
                children_steps = [str(node_visit_step[child]) for child in node_children[node_id]]
                children_results = "from result of step %s, " % (",".join(children_steps))
            f.write("step %d: %s%s\n" % (idx + 1, children_results, node_data[node_id]))


translate_qep(os.path.join('..', 'data', 'json', 'sample.json'), os.path.join('..', 'data', 'text', 'sample.txt'))


