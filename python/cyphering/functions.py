import os
import datetime
import pathlib
import re

import yaml
import jinja2

from typing import List, Dict, Any, Set

from dotwiz import DotWiz

from . import typedefs

DEFAULT_SEARCH_PATH = pathlib.Path(__file__).parent.absolute().as_posix()

# utilities

def read_yaml(filename: str, dotted: bool=True) -> Dict[str, Any]:
    filename = pathlib.Path(filename).resolve().absolute()
    with open(filename.as_posix()) as file:
        data = yaml.safe_load(file)
        return DotWiz(data) if dotted else data

# render utils

def render_clean(text: str) -> str:
    # duplicate empty lines
    lines = text.split('\n')
    cleaned_lines = []
    for line in lines:
        if line.strip():
            cleaned_lines.append(line)
        elif cleaned_lines and cleaned_lines[-1].strip():
            cleaned_lines.append(line)
    cleaned_text = '\n'.join(cleaned_lines)
    return cleaned_text

# utils

def lower_first(strval: str):
    return strval[0].lower() + result[1:]

# read nodes

def parse_nodes(elements: List[DotWiz]) -> List[typedefs.NodeT]:
    return [ parse_node(e) for e in elements ]

def parse_node(element: DotWiz):
    res = parse_node_base(element)
    res.__element_type = typedefs.ElementType.ELEMENT_TYPE_NODE
    return res

# read rels

def parse_rels(elements: List[DotWiz]) -> List[typedefs.NodeT]:
    return [ parse_rel(e) for e in elements ]

def parse_rel(element: DotWiz) -> typedefs.NodeT:
    res = parse_node_base(element)
    res.__element_type = typedefs.ElementType.ELEMENT_TYPE_NODE
    res.reltype = element.reltype
    return res

# read node base

def parse_node_base(element: DotWiz) -> typedefs.NodeT:
    # TODO: validation

    node = typedefs.NodeT()

    node.label = element.label.strip()

    node.alias = element.alias \
        if 'alias' in element \
        else lower_first(node.label)
    node.alias = node.alias.strip()

    # TODO: use enum
    node.mode = element.get('mode', '').strip()

    if 'attr' in element:

        if 'key' in element.attr:
            node.attr.key = {
                k: v.strip() for k,v in element.attr.key.items()
            }

        if 'on_create' in element.attr:
            node.attr.on_create = {
                k: v.strip() for k,v in element.attr.on_create.items()
            }

        if 'on_update' in element.attr:
            node.attr.on_update = {
                k: v.strip() for k,v in element.attr.on_update.items()
            }

    if 'index' in element:
        node.index = [ e.strip() for e in element.index ]

    if 'constraint' in element:
        node.constraint = [ e.strip() for e in element.constraint ]

    if 'custom' in element:
        node.custom = element.custom

    return node

# expand

def expand_attr_str(text: str, replacement: str, pattern: Any):
    return re.sub(pattern, replacement, text)

def expand_map_attr(
    map: Dict[str, str],
    map_expanded: Dict[str, str],
    depends_on: Set[str],
    self_reference_value: str
) -> None:
    pattern_search = r'(\${\w*})'
    pattern_variable = r'\${(\w*)}'

    self_reference_keyword = 'this'
    entry_reference_keyword = 'entry'

    for k,v in map.items():
        map_expanded[k] = v

        for alias_var in re.findall(pattern_search, v):
            line = map_expanded[k]

            for variable_val in re.findall(pattern_variable, alias_var):
                if variable_val == self_reference_keyword:
                    map_expanded[k] = line.replace(alias_var, self_reference_value)
                elif variable_val == entry_reference_keyword:
                    map_expanded[k] = line.replace(alias_var, entry_reference_keyword)
                else:
                    map_expanded[k] = line.replace(alias_var, variable_val)
                    depends_on.add(variable_val)

def expand_map(nodes: List[typedefs.NodeT]) -> None:
    for node in nodes:

        # on create
        expand_map_attr(
            node.attr.on_create,
            node.attr.expanded_on_create,
            node.depends_on,
            node.alias
        )

        # on update
        expand_map_attr(
            node.attr.on_update,
            node.attr.expanded_on_update,
            node.depends_on,
            node.alias
        )

def expand_index(nodes: List[typedefs.NodeT]) -> None:
    for node in nodes:
        map = { e:e for e in node.index }
        map_expanded = {}
        expand_map_attr(
            map,
            map_expanded,
            node.depends_on,
            node.alias
        )
        node.expanded_index = [ v for v in map_expanded.values()]

def expand_constraint(nodes: List[typedefs.NodeT]) -> None:
    for node in nodes:
        map = { e:e for e in node.constraint }
        map_expanded = {}
        expand_map_attr(
            map,
            map_expanded,
            node.depends_on,
            node.alias
        )
        node.expanded_constraint = [ v for v in map_expanded.values()]

def expand_key(nodes: List[typedefs.NodeT]) -> None:
    for node in nodes:
        expand_map_attr(
            node.attr.key,
            node.attr.expanded_key,
            node.depends_on,
            node.alias
        )

def expand_rels(nodes: List[typedefs.NodeT]) -> None:
    pattern = r'^(\w*)\s*(->|-|<-)\s*(\w*)$'

    for node in nodes:
        map = { '_': node.reltype }
        map_expanded = {}
        expand_map_attr(
            map,
            map_expanded,
            node.depends_on,
            node.alias
        )
        expanded = map_expanded['_']
        expanded = expanded.strip()

        res = re.findall(pattern, expanded)

        if not res or len(res[0]) < 3:
            raise typedefs.CypheringModelException(
                f'"{node.reltype}" doesn\'t match "A -> B, or A - B, or A <- B"'
            )

        # re order the relationship
        # a -> b = same
        # b <- a = a -> b
        # b - a  = same

        node0 = res[0][0]
        reltype_dir = res[0][1]
        node1 = res[0][2]

        reltype_nodes = [ node0, node1 ]
        if reltype_dir == '<-':
            reltype_nodes = reltype_nodes[::-1]

        node.expanded_reltype_nodes = reltype_nodes

        node.expanded_reltype_dir = '->' if reltype_dir == '<-' else reltype_dir


# helpers

def cyphering_get_match(nodes: List[typedefs.NodeT]) -> List[typedefs.NodeT]:
    return list(filter(lambda n: n.mode.lower() == 'match', nodes))

def cyphering_get_create(nodes: List[typedefs.NodeT]) -> List[typedefs.NodeT]:
    return list(filter(lambda n: n.mode.lower() == 'create', nodes))

def cyphering_get_merge(nodes: List[typedefs.NodeT]) -> List[typedefs.NodeT]:
    return list(filter(lambda n: n.mode.lower() == 'merge', nodes))

def cyphering_fmt_list(prefix: str, strlist: List[str], separator: str='.', joiner: str=',') -> List[str]:
    return joiner.join([f'{prefix}{separator}{i}' for i in strlist])

def cyphering_get_deps(nodes: List[typedefs.NodeT], model: typedefs.ModelT) -> typedefs.NodeT:
    dependencies = set()
    for node in nodes:
        dependencies.update(node.depends_on)
    return [ cyphering_get_node(e, model) for e in sorted(dependencies) ]

def cyphering_get_node(alias: str, model: typedefs.ModelT) -> typedefs.NodeT:
    return model.alias_map.get(alias)

def cyphering_join_dicts(dict1: Dict[Any, Any], dict2: Dict[Any, Any]) -> Dict[Any, Any]:
    return {**dict1, **dict2}

helpers = {
    'cyphering_get_match': cyphering_get_match,
    'cyphering_get_create': cyphering_get_create,
    'cyphering_get_merge': cyphering_get_merge,
    'cyphering_fmt_list': cyphering_fmt_list,
    'cyphering_get_deps': cyphering_get_deps,
    'cyphering_get_node': cyphering_get_node,
    'cyphering_join_dicts': cyphering_join_dicts,
}

# render

def render_model(template: str, searchpath: str=DEFAULT_SEARCH_PATH, **kwargs) -> None:
    searchpath = pathlib.Path(searchpath).resolve().absolute()
    loader = jinja2.FileSystemLoader(searchpath=searchpath.as_posix())
    env = jinja2.Environment(loader=loader)
    tplobj = env.get_template(template)
    render = tplobj.render(**helpers, **kwargs)
    render = render_clean(render)
    return render