#include <regex>
#include <sstream>

#include "cyphering.h"

// utils

// TODO all to lower instead...?
std::string LowerFirst(const std::string& str) {
    std::string result = str;

    // capitalize the first letter if it's lowercase
    if (std::isupper(result[0])) {
        result[0] = std::tolower(result[0]);
    }

    return std::move(result);
}

bool fileExists(const std::string& filename) {
    std::ifstream file(filename);
    return file.good();
}

std::string readFile(const std::string& filename) {
    std::ifstream file(
        filename,
        std::ios::in | std::ios::out | std::ios::binary | std::ios::ate
    );

    if (!file.is_open()) {
        throw std::runtime_error("Failed to open file: " + filename);
    }

    const size_t len = file.tellg();
    if (len <= 0) {
        throw std::runtime_error("Failed to open file: " + filename);
    }
    file.seekg(0, std::ios::beg);

    std::string content = std::string(len, '\0');
    if (file.is_open())
        file.read(&content[0], len);

    file.close();

    return std::move(content);
}

// read nodes

std::list<cyphering::NodeT> ReadNodes(const ryml::ConstNodeRef& node) {
    std::list<cyphering::NodeT> cnodes;
    for(ryml::ConstNodeRef const& child : node.children()) {
        cyphering::NodeT cnode = ReadNode(child);
        cnodes.push_back(cnode);
    }
    return cnodes;
}

cyphering::NodeT ReadNode(const ryml::ConstNodeRef& node) {
    cyphering::NodeT cnode = ReadNodeBase(node);
    cnode.__type = cyphering::ELEMENT_TYPE_NODE;
    return cnode;
}

std::list<cyphering::NodeT> ReadRels(const ryml::ConstNodeRef& node) {
    std::list<cyphering::NodeT> cnodes;
    for(ryml::ConstNodeRef const& child : node.children()) {
        cyphering::NodeT cnode = ReadNode(child);
        cnodes.push_back(cnode);
    }
    return cnodes;
}

cyphering::NodeT ReadRel(const ryml::ConstNodeRef& node) {
    cyphering::NodeT cnode = ReadNodeBase(node);

    // type
    cnode.label = node["type"].val().str;

    cnode.__type = cyphering::ELEMENT_TYPE_RELATIONSHIP;
    return cnode;
}

cyphering::NodeT ReadNodeBase(const ryml::ConstNodeRef& node) {
    // TODO, structure validations
    // TODO, validate mode type
    // TODO, validate type structure
    // TOOD, validate references
    // TODO, validate types
    // TOOD, validate

    cyphering::NodeT cnode;

    // label
    cnode.label = ReadNodeValStr(node, "label");

    // alias
    if (!node["alias"].empty()) {
        cnode.alias = ReadNodeValStr(node, "alias");
    } else {
        cnode.alias = cnode.label;
    }
    cnode.alias = LowerFirst(cnode.alias);

    // mode
    cnode.mode = ReadNodeValStr(node, "mode");

    // attr

    // attr on_create
    if (!node["attr"]["on_create"].empty()) {
        ryml::ConstNodeRef root = node["attr"]["on_create"];
        for(ryml::ConstNodeRef const& child : root.children()) {
            std::string key = std::string(child.key().str, child.key().len);
            std::string val = std::string(child.val().str, child.val().len);
            cnode.attr.on_create[key] = val;
        }
    }

    // attr on_update
    if (!node["attr"]["on_update"].empty()) {
        ryml::ConstNodeRef root = node["attr"]["on_update"];
        for(ryml::ConstNodeRef const& child : root.children()) {
            std::string key = std::string(child.key().str, child.key().len);
            std::string val = std::string(child.val().str, child.val().len);
            cnode.attr.on_update[key] = val;
        }
    }

    // index
    if (!node["index"].empty()) {
        ryml::ConstNodeRef root = node["index"];
        for(ryml::ConstNodeRef const& child : root.children()) {
            std::string val = std::string(child.val().str, child.val().len);
            cnode.index.push_back(val);
        }
    }

    // constraints
    if (!node["constraints"].empty()) {
        ryml::ConstNodeRef root = node["constraints"];
        for(ryml::ConstNodeRef const& child : root.children()) {
            std::string val = std::string(child.val().str, child.val().len);
            cnode.constraints.push_back(val);
        }
    }

    return cnode;
}

std::string ReadNodeValStr(const ryml::ConstNodeRef& node, const std::string& key) {
    std::string val = std::string(node[key.c_str()].val().str, node[key.c_str()].val().len);
    return val;
}

// expand model

std::string ExpandAttrStr(const std::string& str, const std::string& keyword, const std::string& regex) {
    std::string res = std::regex_replace(str, std::regex(regex), keyword);
    return res;
}

void ExpandAttr(
    cyphering::NodeT& node,
    const std::map<std::string, std::string>& map,
    std::map<std::string, std::string> expandedMap,
    const std::string& keyword
) {
    // \$.*\.
    // .*\$(.*)\..*

    for (auto it = map.begin(); it != map.end(); ++it) {
        std::string key = it->first;
        std::string val = it->second;

        std::smatch match_results;

        if (std::regex_search(val, match_results, std::regex(X_ATTR_REGEX_ENTRY_MATCH))) {
            if (std::regex_search(val, match_results, std::regex(X_ATTR_REGEX_ENTRY_GROUP))) {
                std::string alias = match_results[1];

                if (!alias.empty()) {

                    std::string replacement = alias + std::string(X_ATTR_REGEX_SEPARATOR);
                    std::string regex = X_ATTR_REGEX_ENTRY_MATCH;
                    std::string expanded = ExpandAttrStr(val, replacement, regex);
                    expandedMap[key] = expanded;
                    node.depends_on.insert(alias);

                } else {

                    std::string replacement = X_ATTR_KEYWORD_REPLACE;
                    std::string regex = X_ATTR_REGEX_ENTRY_MATCH;
                    std::string expanded = ExpandAttrStr(val, replacement, regex);
                    expandedMap[key] = expanded;
                }
            }
        } else {
            expandedMap[key] = val;
        }
    }
}

void ExpandAttr(cyphering::NodeT& node, const std::string& keyword) {
    // on create
    {
        const std::map<std::string, std::string>* map = &node.attr.on_create;
        const std::map<std::string, std::string>* expandedMap = &node.attr.__on_create;
        ExpandAttr(node, *map, *expandedMap, keyword);
    }

    // on update
    {
        const std::map<std::string, std::string>* map = &node.attr.on_update;
        const std::map<std::string, std::string>* expandedMap = &node.attr.__on_update;
        ExpandAttr(node, *map, *expandedMap, keyword);
    }
}

void ExpandList(
    cyphering::NodeT& node,
    const std::list<std::string>& list,
    std::list<std::string> expandedList,
    const std::string& keyword
) {
    // \$.*\.
    // .*\$(.*)\..*

    for (const std::string& val: list) {
        std::smatch match_results;

        if (std::regex_search(val, match_results, std::regex(X_ATTR_REGEX_ENTRY_MATCH))) {
            if (std::regex_search(val, match_results, std::regex(X_ATTR_REGEX_ENTRY_GROUP))) {
                std::string alias = keyword;

                if (!alias.empty()) {

                    std::string replacement = alias + std::string(X_ATTR_REGEX_SEPARATOR);
                    std::string regex = X_ATTR_REGEX_ENTRY_MATCH;
                    std::string expanded = ExpandAttrStr(val, replacement, regex);
                    expandedList.push_back(expanded);

                } else {

                    std::string replacement = X_ATTR_KEYWORD_REPLACE;
                    std::string regex = X_ATTR_REGEX_ENTRY_MATCH;
                    std::string expanded = ExpandAttrStr(val, replacement, regex);
                    expandedList.push_back(expanded);
                }
            }
        } else {
            expandedList.push_back(val);
        }
    }
}

void ExpandConstraints(cyphering::NodeT& node) {
    const std::list<std::string>* list = &node.constraints;
    const std::list<std::string>* expandedList = &node.__constraints;
    ExpandList(node, *list, *expandedList, node.alias);
}

void ExpandIndexes(cyphering::NodeT& node) {
    const std::list<std::string>* list = &node.index;
    const std::list<std::string>* expandedList = &node.__index;
    ExpandList(node, *list, *expandedList, node.alias);
}

void ExpandRelationship(cyphering::NodeT& node) {
    // (\\$\\w*)\\s.*(>|-|<)\\s.*(\\$\\w*)

    std::smatch match_results;

    std::stringstream ss;
    ss << "(\\";
    ss << std::string(X_ATTR_REGEX_PREFIX);
    ss << "\\w*)\\s.*(>|-|<)\\s.*(\\";
    ss << std::string(X_ATTR_REGEX_PREFIX);
    ss << "\\w*)";

    // TODO validate if this exists or not...

    if (std::regex_search(node.type, match_results, std::regex(ss.str()))) {
        std::string node0 = match_results[1];
        std::string reldir =  match_results[2];
        std::string node1 = match_results[3];

        // TODO validate direction is either one of <,-,>
        // TODO refactor this

        // node0
        if (std::regex_search(node0, match_results, std::regex(X_ATTR_REGEX_ENTRY_MATCH))) {
            if (std::regex_search(node0, match_results, std::regex(X_ATTR_REGEX_ENTRY_GROUP))) {
                std::string alias = match_results[1];

                if (!alias.empty()) {

                    std::string replacement = alias + std::string(X_ATTR_REGEX_SEPARATOR);
                    std::string regex = X_ATTR_REGEX_ENTRY_MATCH;
                    std::string expanded = ExpandAttrStr(node0, replacement, regex);
                    node.__type_node0 = expanded;
                    node.depends_on.insert(expanded);

                } else {

                    std::string replacement = X_ATTR_KEYWORD_REPLACE;
                    std::string regex = X_ATTR_REGEX_ENTRY_MATCH;
                    std::string expanded = ExpandAttrStr(node0, replacement, regex);
                    node.__type_node0 = expanded;
                    node.depends_on.insert(expanded);
                }
            }
        } else {
            node.__type_node0 = node0;
            node.depends_on.insert(node0);
        }

        // direction

        node.__type_dir = reldir;

        // node0
        if (std::regex_search(node1, match_results, std::regex(X_ATTR_REGEX_ENTRY_MATCH))) {
            if (std::regex_search(node1, match_results, std::regex(X_ATTR_REGEX_ENTRY_GROUP))) {
                std::string alias = match_results[1];

                if (!alias.empty()) {

                    std::string replacement = alias + std::string(X_ATTR_REGEX_SEPARATOR);
                    std::string regex = X_ATTR_REGEX_ENTRY_MATCH;
                    std::string expanded = ExpandAttrStr(node1, replacement, regex);
                    node.__type_node1 = expanded;
                    node.depends_on.insert(expanded);

                } else {

                    std::string replacement = X_ATTR_KEYWORD_REPLACE;
                    std::string regex = X_ATTR_REGEX_ENTRY_MATCH;
                    std::string expanded = ExpandAttrStr(node1, replacement, regex);
                    node.__type_node1 = expanded;
                    node.depends_on.insert(expanded);
                }
            }
        } else {
            node.__type_node1 = node1;
            node.depends_on.insert(node1);
        }
    }
}