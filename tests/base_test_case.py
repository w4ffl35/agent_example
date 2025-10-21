from typing import List
import unittest


class BaseTestCase(unittest.TestCase):
    target_class = None
    public_methods: List[str] = []
    public_properties: List[str] = []
    _setup_args = [[""]]
    _setup_kwargs = {}

    def setUp(self):
        if self.target_class is None:
            self.skipTest("BaseTestCase is abstract and should not run directly")
        self.obj = self.target_class(*self._setup_args, **self._setup_kwargs)

    def tearDown(self):
        del self.obj

    def test_instantiation(self):
        self.assertIsInstance(self.obj, self.target_class)

    def test_has_public_methods(self):
        for method in self.public_methods:
            self.assertTrue(
                hasattr(self.obj, method),
                f"{self.target_class.__name__} is missing public method: {method}",
            )
            self.assertTrue(
                callable(getattr(self.obj, method, None)),
                f"{self.target_class.__name__} public method is not callable: {method}",
            )

    def test_has_public_properties(self):
        for prop in self.public_properties:
            self.assertTrue(
                hasattr(self.obj, prop),
                f"{self.target_class.__name__} is missing public property: {prop}",
            )
