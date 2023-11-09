import json
from dataclasses import dataclass, field
from itertools import groupby
from typing import List, ForwardRef, Dict, Set

from src.db.dicom.dicom import DataSetItem
from src.domain.dicom.tag.dicom_tag import DicomTag, DataSet

# All DataSets are lists of tagitems, but not all list of tagitems are datasets!
# Ex: the input to transform is a flat list of data_set items that represent a single tag that may
# contain datasets recursively, but the input to the function is not a dataset!
SqlDataSet = List[DataSetItem]


@dataclass
class DataSetItemTreeNode:
    id: str
    set_id: str = field(default=None)
    children: Set[ForwardRef("DataSetTreeNode")] = field(default_factory=set)

    def __hash__(self):
        return hash(self.id)


def transform(dataset_items: List[DataSetItem]) -> DicomTag:
    """

    :param dataset_items: A flat list of datasetitems representing a dicom tag
    :return: a DicomTag entity from the original flat representation
    """
    root: DataSetItemTreeNode = construct_tree(dataset_items)
    dataset_map: Dict[str, DataSetItem] = construct_map(dataset_items)
    return traverse_tree(root, dataset_map)


def traverse_tree(root: DataSetItemTreeNode, dataset_map: Dict[str, DataSetItem]) -> DicomTag:
    """

    :param root: The root of the datasetitem tree
    :param dataset_map: The map of id to datasetitem to retrieve while traversing the treee
    :return: The DicomTag from the tree representation
    """
    root_id = root.id
    dataset_item = dataset_map.get(root_id)
    if root.children:
        children: List[DataSet] = []
        for child_group in groupby(sorted(root.children, key=lambda x: x.set_id), lambda x: x.set_id):
            dataset: DataSet = []
            for child in child_group[1]:
                dataset.append(traverse_tree(child, dataset_map))
            children.append(dataset)
        return DicomTag[List[DataSet]](group_id=dataset_item.group_id, element_id=dataset_item.element_id,
                                       vr=dataset_item.tag_lookup.vr, name=dataset_item.tag_lookup.name,
                                       value=children
                                       )
    else:
        return DicomTag(group_id=dataset_item.group_id, element_id=dataset_item.element_id,
                        vr=dataset_item.tag_lookup.vr, name=dataset_item.tag_lookup.name,
                        vm=dataset_item.vm,
                        value=dataset_item.value if dataset_item.vm == 1 else json.loads(dataset_item.value)
                        )


def construct_map(dataset_items: List[DataSetItem]) -> Dict[str, DataSetItem]:
    item_map: Dict[str, DataSetItem] = {}

    for item in dataset_items:
        item_map[item.id] = item
    return item_map


def construct_tree(dataset_items: List[DataSetItem]) -> DataSetItemTreeNode:
    """
    Construct a hierarchical tree from the flat list
    """
    root: DataSetItemTreeNode
    tree_map: Dict[str, DataSetItemTreeNode] = {}

    for item in dataset_items:
        item: DataSetItem
        parent_id = item.parent_id
        set_id = item.data_set_id
        if item.id not in tree_map:
            tree_node = DataSetItemTreeNode(id=item.id, set_id=set_id)
            tree_map[item.id] = tree_node
        else:
            tree_node = tree_map[item.id]
            tree_node.set_id = set_id

        if parent_id:
            parent_tree_node = tree_map.get(parent_id)
            if not parent_tree_node:
                parent_tree_node = DataSetItemTreeNode(id=parent_id)
                tree_map[parent_id] = parent_tree_node
            parent_tree_node.children.add(tree_node)
        else:
            root = tree_node

    return root
