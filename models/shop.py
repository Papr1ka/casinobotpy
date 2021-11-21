from collections import namedtuple
from typing import NamedTuple, List, Dict

Item = NamedTuple("Item", [('name', str), ('cost', int), ('description', str), ('roles', list)])
item: Item = namedtuple('Item', ['name', 'cost', 'description', 'roles'])

def get_shop(id) -> Dict[str, List[Item]]:
    return {
        '_id': id,
        'items': [],
    }
