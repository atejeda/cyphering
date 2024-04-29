#ifndef FUNCTIONS_H
#define FUNCTIONS_H

#include <regex>

#include <ryml.hpp>
#include <ryml_std.hpp>
#include <c4/format.hpp>

#include "functions.h"

// references


#define X_ATTR_REGEX_PREFIX "$"
#define X_ATTR_REGEX_SEPARATOR "."
#define X_ATTR_REGEX_ALIAS ".*"

#define X_ATTR_KEYWORD "entry"
#define X_ATTR_KEYWORD_REPLACE X_ATTR_KEYWORD X_ATTR_REGEX_SEPARATOR

// usable

// \$.*\.
#define X_ATTR_REGEX_ENTRY_MATCH "\\" X_ATTR_REGEX_PREFIX X_ATTR_REGEX_ALIAS "\\" X_ATTR_REGEX_SEPARATOR

// .*(\$.*).*\.
#define X_ATTR_REGEX_ENTRY_GROUP ".*" "\\" X_ATTR_REGEX_PREFIX "(" X_ATTR_REGEX_ALIAS ")" "\\" X_ATTR_REGEX_SEPARATOR ".*"

// utils

std::string LowerFirst(const std::string& str);

bool fileExists(const std::string& filename);

std::string readFile(const std::string& filename);

// nodes

std::list<cyphering::NodeT> ReadNodes(const ryml::ConstNodeRef& node);

cyphering::NodeT ReadNode(const ryml::ConstNodeRef& node);

// rels

std::list<cyphering::NodeT> ReadRels(const ryml::ConstNodeRef& node);

cyphering::NodeT ReadRel(const ryml::ConstNodeRef& node);

// base

cyphering::NodeT ReadNodeBase(const ryml::ConstNodeRef& node);

std::string ReadNodeValStr(const ryml::ConstNodeRef& node, const std::string& key);

// expand

std::string ExpandAttrStr(
    const std::string& str, 
    const std::string& keyword,
    const std::string& regex
);

void ExpandAttr(
    cyphering::NodeT& node, 
    const std::map<std::string, std::string>& map,
    const std::string& keyword
);

void ExpandAttr(
    cyphering::NodeT& node, 
    const std::string& keyword
);

void ExpandList(
    cyphering::NodeT& node,
    const std::list<std::string>& list,
    std::list<std::string> expandedList,
    const std::string& keyword
);

void ExpandConstraints(cyphering::NodeT& node);

void ExpandIndexes(cyphering::NodeT& node);

void ExpandRelationship(cyphering::NodeT& node);

#endif // FUNCTIONS_H