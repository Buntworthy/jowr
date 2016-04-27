Image processing
================

Pipeline
--------

A :py:class:`~jowr.Pipeline` is a jowr class that tries helps in applying multiple processing
steps to an image. Each step in the Pipeline should be a function that accepts
and returns a single image. A convenient way to do this is to use lambdas. For
example you might specify a simple processing pipeline as follows::

    pipeline = Pipeline()
    pipeline.add_step(lambda image: cv2.GaussianBlur(image, None, 2), 'Blur')
    pipeline.add_step(lambda image: enhance_monkeys(image, type='Macaque'),
                                                    'Enhance Macaque')
    pipeline.add_step(lambda image: cv2.threshold(image, 100, 255, cv2.THRESH_BINARY),
                                                    'Threshold')

Then to run all the steps in the pipeline use :py:meth:`~jowr.Pipeline.run`, and to display
each output steps use :py:meth:`~jowr.Pipeline.run_and_show`.