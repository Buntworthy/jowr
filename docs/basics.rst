Basics
======

Loading images
--------------

In jowr images are represented as :py:class:`~jowr.data.Image` objects, with the corresponding NumPy numeric array data
stored in the field :py:attr:`~jowr.data.Image.image_data`. All jowr classes and functions will return an
:py:class:`~jowr.data.Image` and images can be created from numeric arrays by passing it into the constructor::

    image_array = np.zeros((100,100))
    image = Image(image_array)

