# -*- python -*-
#
#       OpenAlea.SoftBus: OpenAlea Software Bus
#
#       Copyright or (C) or Copr. 2006 INRIA - CIRAD - INRA  
#
#       File author(s): Christophe Pradal <christophe.prada@cirad.fr>
#                       Samuel Dufour-Kowalski <samuel.dufour@sophia.inria.fr>
#
#       Distributed under the Cecill-C License.
#       See accompanying file LICENSE.txt or copy at
#           http://www.cecill.info/licences/Licence_CeCILL-C_V1-en.html
# 
#       OpenAlea WebSite : http://openalea.gforge.inria.fr
#



__doc__= """
Test the composite node module
"""

libraryname = "Library"


from openalea.core.pkgmanager import PackageManager
from openalea.core.compositenode import CompositeNodeFactory, CompositeNode
from openalea.core.core import Package, RecursionError 


# Test instantiation
def test_instantiate_compositenode():
       
    pm = PackageManager ()
    pm.init()

    sgfactory = CompositeNodeFactory(pm, "addition")

    # build the compositenode factory
    addid = sgfactory.add_nodefactory ('add1', (libraryname, "+"))
    val1id = sgfactory.add_nodefactory ('f1', (libraryname, "float")) 
    val2id = sgfactory.add_nodefactory ('f2', (libraryname, "float"))
    val3id = sgfactory.add_nodefactory ('f3', (libraryname, "float"))

    sgfactory.add_connection (val1id, 0, addid, 0)
    sgfactory.add_connection (val2id, 0, addid, 1)
    sgfactory.add_connection (addid, 0, val3id, 0)


    # allocate the compositenode
    sg = sgfactory.instantiate()

    sg.get_node_by_id(val1id).set_input(0, 2.)
    sg.get_node_by_id(val2id).set_input(0, 3.)

    # evaluation
    sg()

    assert sg.get_node_by_id(val3id).get_input(0) == 5.


# Test conversion Composite Node to its Factory
def test_to_factory():
    """ Create a compositenode, generate its factory and reintantiate it """

    pm = PackageManager ()
    pm.init()

    sg = CompositeNode()

    n1 = pm.get_node(libraryname, "float")
    n2 = pm.get_node(libraryname, "float")
    
    e1 = sg.add_node(n1)
    e2 = sg.add_node(n2)
    sg.connect(e1, 0, e2, 0)

    n1.set_input(0,34.)
    sg()
    assert n2.get_input(0) == 34.

    sgfactory = CompositeNodeFactory(pm, "factorytest")
    sg.to_factory(sgfactory)

    sg2 = sgfactory.instantiate()

    assert len(sg2.node_id.keys()) == 2
    assert len(sg2.connections.keys()) == 1

    sg2.get_node_by_id(e1).set_input(0, 3.)
    sg2()
    assert sg2.get_node_by_id(e2).get_input(0) == 3.
    
    
    

# Test Recursion detection
def test_recursion_factory():

    pm = PackageManager ()
    pm.init()
    pkg = Package("compositenode", {})

    sgfactory1 = CompositeNodeFactory(pm, "graph1")
    sgfactory2 = CompositeNodeFactory(pm,  "graph2")

    map (pkg.add_factory, (sgfactory1, sgfactory2))

    assert len(pkg.get_names()) == 2

    pm.add_package(pkg)
    
    # build the compositenode factory

    sgfactory1.add_nodefactory ('g1', ("compositenode", "graph2"))
    sgfactory2.add_nodefactory ('g2', ("compositenode", "graph1"))

    try:
        sg = sgfactory1.instantiate ()
        assert False
    except RecursionError:
        assert True
        

# Test IO
def test_compositenodeio():

    pm = PackageManager ()
    pm.init()

    pkg = Package("compositenode", {})

    # create a compositenode with 2 in and 1 out
    # the compositenode does an addition
    sgfactory = CompositeNodeFactory(pm, "additionsg")
    sgfactory.set_nb_input(2)
    sgfactory.set_nb_output(1)
        
    addid = sgfactory.add_nodefactory ('add1', (libraryname, "+"))
    
    sgfactory.add_connection ('in', 0, addid, 0)
    sgfactory.add_connection ('in', 1, addid, 1)
    sgfactory.add_connection (addid, 0, 'out', 0)

    pkg.add_factory(sgfactory)
    pm.add_package(pkg)


    sgfactory2 = CompositeNodeFactory(pm, "testio")
    addid = sgfactory2.add_nodefactory ('g1', ("compositenode", "additionsg"))
    val1id = sgfactory2.add_nodefactory('f1', (libraryname, "float"))
    val2id = sgfactory2.add_nodefactory('f2', (libraryname, "float"))
    val3id = sgfactory2.add_nodefactory('f3', (libraryname, "float"))

    sgfactory2.add_connection (val1id, 0, addid, 0)
    sgfactory2.add_connection (val2id, 0, addid, 1)
    sgfactory2.add_connection (addid, 0, val3id, 0)

    # allocate the compositenode
        
    sg = sgfactory2.instantiate()

    sg.get_node_by_id(val1id).set_input(0,2.)
    sg.get_node_by_id(val2id).set_input(0,3.)

    
    # evaluation
    sg()

    assert sg.get_node_by_id(val3id).get_input(0) == 5.


# Test  node addition
def test_addnode():

    pm = PackageManager ()
    pm.init()

    sgfactory = CompositeNodeFactory(pm, "testaddnode")

    # build the compositenode factory
    val1id = sgfactory.add_nodefactory ('f1', (libraryname, "float"))
    val2id = sgfactory.add_nodefactory ('f2', (libraryname, "float"))

    sgfactory.add_connection (val1id, 0, val2id, 0)


    # allocate the compositenode

    sg = sgfactory.instantiate()

    sg.get_node_by_id(val1id).set_input(0,2.)
    sg()
    assert sg.get_node_by_id(val2id).get_input(0) == 2.


    # Add a new node
    addid = sgfactory.add_nodefactory ('add1', (libraryname, "+"))
    
    sg = sgfactory.instantiate()
    sg.get_node_by_id(val1id).set_input(0, 3.)
    sg()
    assert sg.get_node_by_id(val2id).get_input(0) == 3.


# Test multiple out connection
def test_multi_out_eval():

    pm = PackageManager ()
    pm.init()

    sgfactory = CompositeNodeFactory(pm, "testlazyeval")

    # build the compositenode factory
    val1id = sgfactory.add_nodefactory('s1', (libraryname, "string"))
    val2id = sgfactory.add_nodefactory('s2', (libraryname, "string"))
    val3id = sgfactory.add_nodefactory('s3', (libraryname, "string"))

    sgfactory.add_connection (val1id, 0, val2id, 0)
    sgfactory.add_connection (val1id, 0, val3id, 0)


    # allocate the compositenode
    sg = sgfactory.instantiate()

    sg.get_node_by_id(val1id).set_input(0,"teststring")
    sg()
    assert sg.get_node_by_id(val2id).get_input(0) == "teststring"
    assert sg.get_node_by_id(val3id).get_input(0) == "teststring"

    #partial evaluation
    sg.get_node_by_id(val1id).set_input(0, "teststring2")
    sg.eval_as_expression(val2id)
    assert sg.get_node_by_id(val2id).get_input(0) == "teststring2"
    
    sg.eval_as_expression(val3id)
    assert sg.get_node_by_id(val3id).get_input(0) == "teststring2"


