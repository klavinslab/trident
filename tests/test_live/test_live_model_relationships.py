import warnings
import pytest
from marshmallow import pprint
from pydent import models, ModelRegistry
from pydent.exceptions import TridentRequestError


@pytest.fixture(scope="module", params=ModelRegistry.models.values())
def model_relationships(session, request):
    """
    Tries to access nested relationships in an a model

    :param session: pytest fixture that has returned a live trident session
    :type session: AqSession
    :param request: parameter from the fixture
    :type request: dict
    :return: None
    :rtype: None
    """

    # TODO: This code is sloppy...
    # Try to find a live model
    model_class = request.param
    model_class_name = model_class.__name__  # e.g. "FieldType"
    model_instance = None
    for iden in [1, 100, 1000, 5000, 10000, 54069, 130000, 200000][::-1]:
        try:
            print("Finding '{}' model with {}".format(model_class_name, iden))
            model_instance = session.model_interface(model_class_name).find(iden)
        except TridentRequestError as e:
            print(e)
        if model_instance:
            break
    if model_instance is None:
        raise Exception("Could not find a {}".format(model_class))


    # Get the model class
    print(model_instance)
    pprint(model_instance.raw)

    # Discover and access model relationships
    relationships = model_class.get_relationships()
    if len(relationships) == 0:
        warnings.warn("No relationships found for model '{}'".format(model_class_name))
        return
    print("\nRelationships:")
    pprint(relationships)
    for attr, relationship in relationships.items():
        print("\tGetting attribute '{}'".format(attr))
        val = getattr(model_instance, attr)
        nested_model = ModelRegistry.get_model(relationship.nested)
        if relationship.many:
            if len(val) == 0:
                warnings.warn("Attribute {}.{} was empty list".format(model_class.__name__, attr))
            else:
                assert isinstance(val[0], nested_model)
        else:
            nested_model = ModelRegistry.get_model(relationship.nested)
            if val:
                assert isinstance(val, nested_model)
            else:
                warnings.warn("Attribute {}.{} was null".format(model_class.__name__, attr))


def test_model_relationships(model_relationships):
    """Test all relationship access for all models.
    This is not a permanent test nor a comprehensive test."""
    pass
