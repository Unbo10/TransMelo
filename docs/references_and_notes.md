# Arrays

The `ctypes` library was used to access functions and predefined variables of C to create a pointer to the head of the array and allocate memory for `capacity` amount of contiguous positions (https://docs.python.org/3/library/ctypes.html).

> `CDLL` is used in case a shared library needs to be imported (which isn't the case here).

### Reference handling

In the `__setitem__` method of `ObjArr`, `Py_IncRef` and `Py_DecRef` are used to increase and decrease the reference count of the object, respectively. The reference count is a mecanism that Python's garbage collector usually manages automatically, but since the objects are being managed in C, outisde of its scope, the mecanism needs to be implemented manually.

> Each object in Python has a reference count that let's the garbage collector know how many memory positions are pointing to it. If none are, then it knows it can be safely deleted. This, for instance, manages the assigning of values to certain values that imply the replacement of others.

### `py_object`

Represents the `PyObject` type in C. "This is a type which contains the information Python needs to treat a pointer to an object as an object". Therefore, any Python object can be casted into this type.

In terms of efficiency, it occupies 7 times more memory than an integer, according to Chat.

### Bracket notation (`[]`)

According to Chat, since `self.__arr` is a pointer in C, the `self.__arr[index]` operation is done in C, so it is equivalent to `*(self.__arr + index)`.


# DataArray

### `create_data_array`

Since every row is separated by a single breakline (`\n`, can be checked printing `repr(lines)`), it traverses every row of the string tracking the first index of the row and the last one (before the breakline).

> The first line will always be 89 characters long.

> EOF means End Of File. When accessing a CSV file using Python, it sets the EOF to be an empty string (`""`)

# Algorithm
- Description: Reinforcement learning algorithm using max and min functions