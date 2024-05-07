import logging
import pathlib
import glob

import click
import cyphering
import cyphering.typedefs

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

logger = logging.getLogger()

@click.command()
@click.option(
    '--model', 
    required=True, 
    help='Model filename', 
    #type=click.File('rb')
)
@click.option(
    '--template', 
    required=True, 
    help='template filename to use from "searchpath"'
)
@click.option(
    '--searchpath', 
    required=False, 
    help='Where to search templates, will default to builtin path', 
    type=click.Path(exists=True), 
    default=cyphering.DEFAULT_SEARCH_PATH
)
@click.option(
    '--output', 
    required=True, 
    help='Output filename',
)
def main(model, template, searchpath, output):
    try:
        render(model, template, searchpath, output)
    except Exception as e:
        logging.exception('got an error during parsing')


def render(modelfile, template, searchpath, output):
    modelfile = pathlib.Path(modelfile).resolve().absolute().as_posix()
    output = pathlib.Path(output).resolve().absolute().as_posix()
    searchpath = pathlib.Path(searchpath).resolve().absolute().as_posix()

    logger.info('--')
    logger.info(modelfile)
    logger.info(template)
    logger.info(searchpath)
    logger.info(output)

    data = cyphering.read_yaml(modelfile)

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

    # sanity checks
    elements = model.nodes + model.rels

    # aliases (all)
    # aliases = set([ a for e in elements for a in e.depends_on ])
    for e in elements:
        for a in e.depends_on:
            if a not in model.alias_map:
                message = f'Missing alias reference "{a}" for {e}'
                raise cyphering.typedefs.CypheringModelException(message)

    # modes (all)
    valid_modes = ['match', 'merge', 'create']
    for e in elements:
        if e.mode.lower() not in valid_modes:
            message = f'Not a valid mode "{e.mode}" for: {e}'
            raise cyphering.typedefs.CypheringModelException(message)

    # render

    torender = []

    if template.lower() == 'all':

        outputdir = pathlib.Path(output)
        if outputdir.is_file():
            outputdir = output.parent

        modelfile_name = pathlib.Path(modelfile).stem
        searchpath_star = (pathlib.Path(searchpath) / '*').as_posix()
        
        templates = glob.glob(searchpath_star)
        templates = sorted(templates)
        
        for template in templates:
            template_path = pathlib.Path(template)
            template_name = template_path.stem
            template_file = template_path.name

            output_filename = f'{modelfile_name}.{template_name}.cypher'
            output = (outputdir / output_filename).as_posix()
            torender.append((template_file, searchpath, modelfile, output))
    else:
        torender.append((template, searchpath, modelfile, output))

    for template, searchpath, modelfile, output in torender:
        logger.info('%s %s %s %s',template, searchpath, modelfile, output)

        render = cyphering.render_model(
           template, searchpath=searchpath, model=model
        )

        with open(output, 'w') as file:
            file.write(render)
    

def __():
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