from pydent.aqhttp import AqHTTP
from pydent.models import FieldType


def test_field_type_constructor_with_sample_type(fake_session, monkeypatch):
    def fake_post(*_, **kwargs):
        json_data = kwargs["json_data"]
        if json_data["model"] == "SampleType" and json_data["id"] == 5:
            return {"id": 5}

    monkeypatch.setattr(AqHTTP, "post", fake_post)

    ft = fake_session.FieldType.load(
        {"id": 4, "parent_id": 5, "parent_class": "SampleType"}
    )
    assert ft.sample_type.id == 5
    assert ft.operation_type is None


def test_field_type_constructor_with_operation_type(fake_session, monkeypatch):
    def fake_post(*_, **kwargs):
        json_data = kwargs["json_data"]
        if json_data["model"] == "OperationType" and json_data["id"] == 5:
            return {"id": 5}

    monkeypatch.setattr(AqHTTP, "post", fake_post)

    ft = fake_session.FieldType.load(
        {"id": 4, "parent_id": 5, "parent_class": "OperationType"}
    )
    assert ft.operation_type.id == 5
    assert ft.sample_type is None


def test_field_type_constructor2(fake_session):
    ft = fake_session.FieldType.load(
        {"id": 4, "operation_type": {"id": 4}, "parent_class": "OperationType"}
    )

    assert ft.operation_type.id == 4
    assert ft.sample_type is None


def test_field_type_is_parameter(fake_session):
    ft = FieldType.load_from({"ftype": "sample"}, fake_session)
    assert not ft.is_parameter()

    ft.ftype = "string"
    assert ft.is_parameter


def test_initialize_field_value(fake_session):
    ft = fake_session.FieldType.load(
        {
            "id": 5,
            "name": "Plasmid",
            "role": "input",
            "allowable_field_types": [{"id": 1}],
        }
    )

    fake_sample = fake_session.Sample.load({"id": 6})
    fv = ft.initialize_field_value(parent=fake_sample)
    assert fv.parent_id == 6
    assert fv.parent_class == "Sample"

    assert fv.field_type == ft
    assert fv.field_type_id == ft.id
    assert fv.role == ft.role
    assert fv.name == ft.name
    assert fv.allowable_field_type_id == ft.allowable_field_types[0].id
    assert fv.allowable_field_type == ft.allowable_field_types[0]
