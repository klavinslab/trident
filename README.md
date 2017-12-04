pydent deserializes nested data
```python
# nested deserialization
# pydent knows to automatically deserialize 'sample_type' to a 'SampleType' model
from pydent.models import Sample, SampleType

s = Sample.load({'id': 1, 'sample_type': {'id': 3}})
assert isinstance(s, Sample)
assert isinstance(s.sample_type, SampleType)
```


you can also include already processed models
```python
Sample.load({
    'id': 1
    'sample_type': SampleType(id=1, name="primer")
}
```


pydent find relationships using requests
```python
from pydent.models import Sample, SampleType
from pydent import AqSession

nursery = AqSession("username", "password", "url")

# create new sample
s = Sample(name='MyPrimer', sample_type_id=1)

# connect sample with session (will throw warning if no session is connected)
s.connect_to_session(nursery)

# find the sample type using 'sample_type_id'
s.sample_type

assert isinstance(s.sample_type, SampleType)
print(s.sample_type)

"""
<class 'pydent.models.SampleType'>: {
    "id": 1,
    "created_at": "2013-10-08T10:18:01-07:00",
    "name": "Primer",
    "description": "A short double stranded piece of DNA for PCR and sequencing",
    "updated_at": "2015-11-29T07:55:20-08:00",
"samples": "<HasMany (model=Sample, callback=where_using_session, params=(<function HasMany.__init__.<locals>.<lambda> at 0x10c3b7620>,))>",
    "field_types": "<Many (model=FieldType, callback=where_using_session, params=(<function SampleType.<lambda> at 0x10c3b76a8>,))>"
}
"""
```

pydent serialization
```python
s = session.SampleType.find(1)
s.dump()

"""
{'created_at': '2013-10-08T10:18:01-07:00',
 'description': 'A short double stranded piece of DNA for PCR and sequencing',
 'id': 1,
 'name': 'Primer',
 'updated_at': '2015-11-29T07:55:20-08:00'}
"""
```

serialize with only some fields
```python
s.dump(only=('data', 'name', 'description'))
# {'name': 'IAA1-Nat-F', 'description': None, 'data': None}
```

serialize with some relations
```python
from pydent import pprint

pprint(s.dump(relations=('items',)))
```


serialize with all relations
```python
from pydent import pprint

pprint(s.dump(all_relations=True))
"""
{'created_at': '2013-10-08T10:18:48-07:00',
'data': None,
'description': None,
'field_values': [{'allowable_field_type_id': None,
                       'child_item_id': None,
                       'child_sample_id': None,
                       'column': None,
                       'created_at': '2016-05-09T20:41:06-07:00',
                       'field_type_id': None,
                       'id': 67853,
                        ...
...
}
"""


```
logging in
```python
from pydent import AqSession

nursery = AqSession("username", "password", "url")
production = AqSession("username", "password", "url2")
```

interactive login
```python
nursery = AqSession.interactive()
# enters interactive shell
```

getting models
```python
session # your AqSession

# find Sample with id=1
session.Sample.find(1)

# find SampleTypes with name="Primer"
session.SampleType.find_by_name("Primer")

# find all SampleTypes
session.SampleType.all()

# find Operations where name="Transfer to 96 Well Plate"
session.Operations.where({'name': 'Transfer to 96 Well Plate'})

# list all available models
session.models
```

set timout
```python
# raises timeout exception if request takes too long
try:
    session.FieldValue.all()
except Exception:
    print("Request took too long!")

session.set_timeout(60)
session.FieldValue.all()
print("Great!")
```

magic chaining
you can chain together attributes and function calls
```python
[s.name for s in session.SampleType.find(1).samples][:10]
pprint(session.SampleType.find(1).samples.name[:10])

['IAA1-Nat-F',
 'prKL1573',
 'prKL744',
 'prKL1927',
 'prKL1928',
 'prKL1929',
 'prKL1930',
 'prKL506',
 'prKL1708',
 'lacI_h2']
 ```

```python

pcr = session.OperationType.find_by_name("Make PCR Fragment")

pprint(pcr.operations[0:5].field_values.name
[['Forward Primer', 'Reverse Primer', 'Template', 'Fragment'],
 ['Forward Primer', 'Reverse Primer', 'Template', 'Fragment'],
 ['Forward Primer', 'Reverse Primer', 'Template', 'Fragment'],
 ['Forward Primer', 'Reverse Primer', 'Template', 'Fragment'],
 ['Forward Primer', 'Reverse Primer', 'Template', 'Fragment']]

pprint(pcr.operations[0:5].field_values.item.id)
[[114549, 62943, 22929, 114553],
 [114564, 62943, 22929, 114566],
 [114737, 62943, 22929, 114739],
 [114748, 62943, 22929, 114750],
 [114782, 62943, 22929, 114784]]
```


utils
```python
session.utils.
```