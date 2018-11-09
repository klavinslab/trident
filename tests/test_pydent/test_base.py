"""Tests for pydent.base.py"""

import copy

import pytest

from pydent import AqSession
from pydent import ModelBase, ModelRegistry
from pydent.marshaller import exceptions
from pydent.marshaller import add_schema, fields, SchemaRegistry
from pydent.exceptions import NoSessionError

# def test_model_base():
#     """
#     Upon instantiation, .session should be None
#     """
#     m = ModelBase()
#     assert m.session is None

@pytest.fixture(scope="function")
def base():
    old_schemas = dict(SchemaRegistry.schemas)
    old_models = dict(ModelRegistry.models)

    yield ModelBase

    new_schemas = set(SchemaRegistry.schemas.keys()).difference(set(old_schemas))
    new_models = set(ModelRegistry.models.keys()).difference(set(old_models))

    for s in new_schemas:
        SchemaRegistry.schemas.pop(s)

    for m in new_models:
        ModelRegistry.models.pop(m)


@pytest.fixture(scope="function")
def mymodel(base):
    @add_schema
    class MyModel(base):
        pass
    yield MyModel


def test_record_id():
    """
    Creating a ModelBase should create a new record id 'rid.'
    For each instance, a new 'rid' should be
    created.
    """
    @add_schema
    class MyModel(ModelBase):
        pass

    @add_schema
    class MyOtherModel(ModelBase):
        pass

    m = MyModel()
    m2 = MyOtherModel()
    m3 = MyModel()
    assert m.rid != m2.rid
    assert m2.rid != m3.rid
    assert m.rid != m3.rid


def test_basic_constructor(mymodel):
    """
    Model should absorb the kwargs.
    """
    m = mymodel(name="SomeName", id=2)
    assert m.name == "SomeName"
    assert m.id == 2
    data = m.dump()
    data.pop('rid')
    assert data == {"name": "SomeName", "id": 2}


def test_base_constructor_with_marshaller(mymodel):
    """MyModel initializes should absorb kwargs into attributes.
    With a schema, those
    attributes are also tracked and available for dumping."""
    m = mymodel(name="model", id=5)
    assert m.name == 'model'
    assert m.id == 5
    mdump = m.dump()
    del mdump['rid']
    assert mdump == {'name': 'model', 'id': 5}


def test_connect_to_session(mymodel, fake_session):
    """Upon instantiation, modelbases should have no session Connect to
    session should connect to a new session. Connecting to other sessions
    afterward should not be allowed."""
    m = mymodel()
    assert m.session is None

    # connect to session
    m.connect_to_session(fake_session)
    assert m.session == fake_session

    # attempt to connect to another session
    fake_session2 = copy.copy(fake_session)
    m.connect_to_session(fake_session2)
    assert not m.session == fake_session2
    assert m.session == fake_session


def test_empty_relationships(mymodel):
    m = mymodel()
    assert m.get_relationships() == {}


def test_check_for_session(mymodel, fake_session):
    """
    If session is none, _check_for_session should raise an AttributeError
    """
    m = mymodel()
    with pytest.raises(NoSessionError):
        m._check_for_session()

    m.connect_to_session(fake_session)
    m._check_for_session()


def test_model_registry(mymodel):
    """
    We expect get_model to return the value in the models dictionary
    """

    assert "MyModel" in ModelRegistry.models
    assert ModelRegistry.models["MyModel"] == mymodel
    assert ModelRegistry.get_model("MyModel") == mymodel
    del ModelRegistry.models["MyModel"]


def test_no_model_in_registry():
    """
    ModelRegistry should raise error if model doesn't exist
    """
    with pytest.raises(exceptions.ModelRegistryError):
        ModelRegistry.get_model("SomeModelThatDoesntExist")


def test_find_no_session(mymodel):
    """
    ModelBase should raise AttributeError if no session is attacheded
    """
    m = mymodel()
    with pytest.raises(NoSessionError):
        m.find_callback(None, None)


def test_where_no_session(mymodel):
    """
    ModelBase should raise AttributeError if no session is attacheded
    """
    m = mymodel()
    with pytest.raises(NoSessionError):
        m.where_callback(None, None)


def test_where_and_find(mymodel, monkeypatch, fake_session):
    """
    Calling the 'where' wrapper on a ModelBase should attempt to
    get a model interface and call 'where' or 'find' on the interface.
    In this case, a fake model interface is returned in which the methods
    return the parameter passed in
    """

    def fake_model_interface(self, model_name):
        """
        A fake model interface to test where
        """

        class FakeInterface:
            def find(id):
                return id

            def where(params):
                return params

        return FakeInterface

    monkeypatch.setattr(AqSession, AqSession.model_interface.__name__,
                        fake_model_interface)

    m = mymodel()
    ModelRegistry.models["FakeModel"] = ModelBase
    m.connect_to_session(fake_session)
    assert m.where_callback("FakeModel", 5) == 5
    assert m.find_callback("FakeModel", 6) == 6


def test_print(mymodel):
    m = mymodel()
    print(m)
    m.print()


def test_load_many(base, fake_session):

    @add_schema
    class Child(base):
        pass

    @add_schema
    class Parent(base):
        fields = dict(
            children=fields.Relationship('Child', 'get_children', many=True)
        )

        def get_children(self, model_name):
            return None

    parent = Parent.load_from({
        "id": 10,
        "children": [
            {"id": 1, "name": "Child1"},
            {"id": 2}
        ]
    }, fake_session.utils)
    print(parent.children)
    assert len(parent.children) == 2
    assert isinstance(parent.children[0], Child)
    assert parent.children[0].name == "Child1"