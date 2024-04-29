#include <iostream>

#include "cyphering.h"

static cyphering::ModelT model;

void readYaml() {

    std::string filename = "cyphering/tests/examples/relationship.yaml";
    std::string content = readFile(filename);
    char* contentBuffer = const_cast<char*>(content.c_str());

    ryml::Tree tree = ryml::parse_in_place(contentBuffer);

    // root
    ryml::ConstNodeRef root = tree.rootref();

    // nodes
    // TODO: validate if this exists first..
    {
        ryml::ConstNodeRef nodes = tree["nodes"];
        auto res = ReadNodes(nodes);
        model.nodes = res;
    }

    // rels
    // TODO: validate if this exists first..
    {
        ryml::ConstNodeRef nodes = tree["rels"];
        auto res = ReadRels(nodes);
        model.rels = res;
    }

    // build reference map

    for (cyphering::NodeT const& node: model.nodes) {
        model.__aliasMap[node.alias] = &node;
    }

    for (cyphering::NodeT const& node: model.rels) {
        model.__aliasMap[node.alias] = &node;
    }

    // TODO: add model validation

    // expand model nodes attr
    for (cyphering::NodeT node: model.nodes) {
        ExpandAttr(node, X_ATTR_KEYWORD);
    }

    // expand model rels attr
    for (cyphering::NodeT node: model.rels) {
       ExpandAttr(node, X_ATTR_KEYWORD);
    }

    // expand model nodes indexes and constraints
    for (cyphering::NodeT node: model.nodes) {
       ExpandIndexes(node);
       ExpandConstraints(node);
    }

    // expand model node indexes and constraints
    for (cyphering::NodeT node: model.rels) {
       ExpandIndexes(node);
       ExpandConstraints(node);
    }

    // expand type (of relationship)
    for (cyphering::NodeT node: model.rels) {
       ExpandRelationship(node);
    }
}

int main() {
    //std::cout << "Hello, World!" << std::endl;
    readYaml();
    return 0;
}
