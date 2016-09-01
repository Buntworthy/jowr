from . import core

class Pipeline:
    """Applies a series of image processing functions on an image.

    This class sequentially applies image processing functions which take as
    input, and return, an image. Steps in the pipeline are passed as functions
    requiring a single input to the add_step method.

    Attributes:
        steps: A list of the image processing functions to be applied
        labels: A list of strings describing each step in the pipeline

    """

    def __init__(self):
        self.steps = []
        self.labels = []

    def __repr__(self):
        return_string = "A jowr Pipeline object with %d steps" % len(self.steps)
        if self.steps:
            return_string += ':\n'
            for label in self.labels:
                return_string += '\t' + label + '\n'
        return return_string

    def add_step(self, func, label=''):
        """Add a step to the Pipeline.

        Note: Func should take as input, and return, a single image

        Args:
            func: The function to apply in the image processing step
            label: String label to describe func

        """
        if not callable(func):
            raise TypeError("Pipeline step should be a callable function")

        self.steps.append(func)
        if label:
            self.labels.append(label)
        else:
            self.labels.append('Step ' + str(len(self.steps)))

    def run(self, image):
        """Run the Pipeline."""
        for step in self.steps:
            image = step(image)

    def run_and_show(self, image):
        """Run the Pipeline and display each step."""
        for step, label in zip(self.steps, self.labels):
            image = step(image)
            core.show(image, window_name=label)
