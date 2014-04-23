Django Routing Numbers
======================

A model that automatically fetches routing numbers from the Federal Reserve, checks for updates daily.

Installation
------------

```
./manage.py syncdb
```

Example
-------

```python
from django_routing_numbers import Institution
obj = Institution.objects.get(routing_number='011000015')
```

Fields
------

Field specifications follow http://www.fededirectory.frb.org/format_ACH.cfm

```
obj.routing_number
obj.office_code
obj.servicing_frb_number
...
```




