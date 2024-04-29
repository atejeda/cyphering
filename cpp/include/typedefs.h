#ifndef RELATIONSHIP_H
#define RELATIONSHIP_H

#include<iostream>
#include <map>
#include <set>
#include <list>

namespace cyphering 
{

// common structures

enum ElementType {
    ELEMENT_TYPE_NODE,
    ELEMENT_TYPE_RELATIONSHIP
};

typedef struct {
    std::map<std::string, std::string> on_create;
    std::map<std::string, std::string> __on_create;
    std::map<std::string, std::string> on_update;
    std::map<std::string, std::string> __on_update;
} AttrT;


typedef struct {
    // core
    std::string label;
    std::string alias;
    std::string mode;

    std::string type;
    std::string __type_node0;
    std::string __type_node1;
    std::string __type_dir;

    AttrT attr;
    
    std::list<std::string> index;
    std::list<std::string> __index;

    std::list<std::string> constraints;
    std::list<std::string> __constraints;

    // type
    ElementType __type;

    // depends on
    std::set<std::string> depends_on;
} NodeT;

// model

typedef struct {
    std::list<NodeT> nodes;
    std::list<NodeT> rels;
    std::map<std::string, const NodeT*> __aliasMap;
} ModelT;

} // namespace cyphering

#endif // RELATIONSHIP_H
