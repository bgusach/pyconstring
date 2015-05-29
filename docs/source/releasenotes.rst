Release Notes
=============

New in 0.5.0
------------
- Now the ConnectionString class inherits from OrderedDict, and therefore the code has been substantially simplified.
  The only change in the API is that the class methods ``from_iterable`` and ``from_dict`` have been removed.
  Now you can just instantiate the class passing the iterable or the dict to the main constructor.
