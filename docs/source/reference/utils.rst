.. py:currentmodule:: draftsman.utils

:py:mod:`~draftsman.utils`
==========================

.. automodule:: draftsman.utils

Abstract Shape Classes
----------------------

.. autoclass:: Shape
    :members:

.. autoclass:: AABB
    :members:

.. autoclass:: Rectangle
    :members:

Encoding/Decoding Operations
----------------------------

.. autofunction:: string_to_JSON

.. autofunction:: JSON_to_string

.. autofunction:: encode_version

.. autofunction:: decode_version

.. autofunction:: version_string_to_tuple

.. autofunction:: version_tuple_to_string

Vector Operations
--------------------------

.. autofunction:: distance

.. autofunction:: rotate_vector

.. autofunction:: dot_product

.. autofunction:: magnitude

.. autofunction:: normalize

.. autofunction:: perpendicular

Collision Functions
-------------------

.. autofunction:: point_in_aabb

.. autofunction:: aabb_overlaps_aabb

.. autofunction:: point_in_circle

.. autofunction:: aabb_overlaps_circle

.. autofunction:: rect_overlaps_rect

.. autofunction:: extend_aabb

.. autofunction:: aabb_to_dimensions

.. autofunction:: flatten_entities

Miscellaneous
-------------

.. autodecorator:: reissue_warnings