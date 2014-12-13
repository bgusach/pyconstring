Rules
=====

There is not a universal syntax for connection strings, therefore this can't work for every single possible syntax.
However, there is a set of general rules that keeps the problems at bay, and pyconstring has been implemented following
these generic rules. Those are:

- Keys are not case sensitive
- If a key contains an equal sign, it must be doubled in the connection string. For instance the key
  ``key=1`` will be serialized as ``key==1``.
- Surrounding white spaces around the key or value are ignored, unless the value is quoted.
- Quoting of value is necessary when it contains white spaces or semicolons, or it starts with any quote.
- If the value needs to be quoted, it can be quoted with single or double quotes.
- However, if the value needs to be quoted, and it contains the same type quotes, those have to be doubled. If it
  contains the other type of quotes, no special handling is needed. ``value"45`` can be serialized as  ``'value"45'``
  or ``"value""45"``.
- Normally the last appearance of a key in a connection string takes precedence, but there are some exceptions like
  ``Provider``, with which the first appearance will take precedence and will not be overridden.
