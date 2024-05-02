from dataclasses import dataclass, field
from enum import Enum
from typing import List, Set, Dict, Any

class ElementType(Enum):
    ELEMENT_TYPE_UNSET = -1
    ELEMENT_TYPE_NODE = 0
    ELEMENT_TYPE_RELATIONSHIP = 1

@dataclass
class AttrT:
    key: Dict[str, str] = field(default_factory=dict)
    expanded_key: Dict[str, str] = field(default_factory=dict)

    on_create: Dict[str, str] = field(default_factory=dict)
    expanded_on_create: Dict[str, str] = field(default_factory=dict)

    on_update: Dict[str, str] = field(default_factory=dict)
    expanded_on_update: Dict[str, str] = field(default_factory=dict)

@dataclass
class NodeT:
    label: str = field(default_factory=str)
    alias: str = field(default_factory=str)
    mode: str = field(default_factory=str)

    reltype: str = field(default_factory=str)
    expanded_reltype_nodes: List[str] = field(default_factory=list)
    expanded_reltype_dir: str = field(default_factory=str)

    attr: AttrT = field(default_factory=AttrT)

    index: List[str] = field(default_factory=list)
    expanded_index: List[str] = field(default_factory=list)

    constraint: List[str] = field(default_factory=list)
    expanded_constraint: List[str] = field(default_factory=list)

    expanded_element_type: ElementType = ElementType.ELEMENT_TYPE_UNSET

    depends_on: Set[str] = field(default_factory=set)

    custom: Any = field(default_factory=list)

@dataclass
class ModelT:
    nodes: List[NodeT] = field(default_factory=list)
    rels: List[NodeT] = field(default_factory=list)
    alias_map: Dict[str, NodeT] = field(default_factory=dict)

class CypheringModelException(Exception):
    def __init__(self, error_message):
        self.error_message = error_message
        super().__init__(error_message)