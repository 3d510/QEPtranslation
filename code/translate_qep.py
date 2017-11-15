import json
import queue
import os
import re
from collections import OrderedDict


def translate_qeptree_to_text(qep_json_path, qep_text_path=os.path.join('..', 'data', 'txt', 'sample.txt')):
    qep_dict = translate_qepjson_to_dict(qep_json_path)
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

    # write qep txt presentation to txt file
    with open(qep_text_path, 'w') as f:
        f.write('hello, suggested query execution plan for your query is as following\n')
        for idx, node_id in enumerate(node_visit_order):
            children_results = ""
            if node_id in node_children:
                children_steps = [str(node_visit_step[child]) for child in node_children[node_id]]
                children_results = "from result of step %s, " % (",".join(children_steps))
            f.write("step %d:\n %s%s\n" % (idx + 1, children_results, node_data[node_id]))


def translate_qepjson_to_dict(qep_path):
    with open(qep_path, 'r') as f:
        plan = json.load(f, object_pairs_hook=OrderedDict)[0]['Plan']
    return plan


def translate_qepdict_to_nodes(qepdict):
    node_children = {}  # map a node id to a list of children node's indices
    node_data = {}  # map node id to corresponding data in that node
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


def translate_node_to_text(node_dict):
    node_type = node_dict.pop('Node Type')
    node_type = node_type.replace('Seq', 'Sequential')
    plan_rows = node_dict.get('Plan Rows', 'unknown numbers of')

    if node_type == "Result":
        qep_text = "get value of operation where"
    else:
        qep_text = "perform %s operation with" % node_type

    if 'Relation Name' in node_dict:
        qep_text += " relation %s aliased %s, " % (node_dict['Relation Name'], node_dict['Alias'])
    for key, value in node_dict.items():
        if key in ['Plan Width', 'Plan Rows', 'Startup Cost', "Total Cost", "Parallel Aware", "Relation Name", 'Alias']:
            continue
        qep_text += (" %s is %s, " % (key, value))
    qep_text += "\n there are %s rows returned with startup cost %s and total cost %s" \
                % (str(plan_rows), node_dict.get('Startup Cost'), node_dict.get('Total Cost'))

    # post process qep_text
    qep_text = re.sub(r'[()\[\]{}$]', '', qep_text.lower())  # remove brackets and $ sign
    qep_text = qep_text.replace(">=", "greater than or equal")\
        .replace("<=", "smaller than or equal")\
        .replace("=", "equal")\
        .replace(">", "greater than")\
        .replace("<", "smaller than")\
        .replace(" cond ", " condition ")\
        .replace("returns", 'that returns')
    return qep_text
