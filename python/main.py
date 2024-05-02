import cyphering

def main():
    # TODO: validate by using a schema

    filename = "../tests/model/test0.yaml"
    data = cyphering.read_yaml(filename)
    #print(data)

    # model
    model = cyphering.ModelT()

    # read nodes
    elements = data.nodes
    res = cyphering.parse_nodes(elements)
    model.nodes = res

    # read rels
    elements = data.rels
    res = cyphering.parse_rels(elements)
    model.rels = res

    # reference map
    model.alias_map = {
        e.alias: e for e in model.nodes + model.rels
    }

    # expand model nodes and rels attrs
    cyphering.expand_map(model.nodes + model.rels)

    # expand model nodes and rels indexes
    cyphering.expand_key(model.nodes + model.rels)

    # expand model nodes and rels indexes
    cyphering.expand_index(model.nodes + model.rels)

    # expand model nodes and rels constraint
    cyphering.expand_constraint(model.nodes + model.rels)

    # expand relationship type
    cyphering.expand_rels(model.rels)

    # rendering

    # node, create

    render = cyphering.render_model(
       'nodes.create.j2',
       searchpath='../tests/template',
       model=model
    )
    with open('../tests/nodes.create.cypher', 'w') as file:
        file.write(render)

    # node, drop

    render = cyphering.render_model(
       'nodes.drop.j2',
       searchpath='../tests/template',
       model=model
    )
    with open('../tests/nodes.drop.cypher', 'w') as file:
        file.write(render)

    # node, create index

    render = cyphering.render_model(
       'nodes.index.create.j2',
       searchpath='../tests/template',
       model=model
    )
    with open('../tests/nodes.index.create.cypher', 'w') as file:
        file.write(render)

    # node, drop index

    render = cyphering.render_model(
       'nodes.index.drop.j2',
       searchpath='../tests/template',
       model=model
    )
    with open('../tests/nodes.index.drop.cypher', 'w') as file:
        file.write(render)

    # node, create constraint

    render = cyphering.render_model(
       'nodes.constraint.create.j2',
       searchpath='../tests/template',
       model=model
    )
    with open('../tests/nodes.constraint.create.cypher', 'w') as file:
        file.write(render)

    # node, drop constraint

    render = cyphering.render_model(
       'nodes.constraint.drop.j2',
       searchpath='../tests/template',
       model=model
    )
    with open('../tests/nodes.constraint.drop.cypher', 'w') as file:
        file.write(render)

    # relationship, create

    render = cyphering.render_model(
       'rels.create.j2',
       searchpath='../tests/template',
       model=model
    )
    with open('../tests/rels.create.cypher', 'w') as file:
        file.write(render)

    # relationship, drop

    # relationship, create index

    render = cyphering.render_model(
       'rels.index.create.j2',
       searchpath='../tests/template',
       model=model
    )
    with open('../tests/rels.index.create.cypher', 'w') as file:
        file.write(render)

    # relationship, drop index

    render = cyphering.render_model(
       'rels.index.drop.j2',
       searchpath='../tests/template',
       model=model
    )
    with open('../tests/rels.index.drop.cypher', 'w') as file:
        file.write(render)

    # relationship, create constraints

    # relationship, drop constraints

if __name__ == '__main__':
    main()