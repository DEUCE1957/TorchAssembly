import unittest, types, os

from BluePrint import BluePrint
from HyperParameters import HyperParameters
from tests import Dummy_Module as Dummy_Module
from pathlib import Path

class TestConstraintsWhenAddingNewItemsToHyperparameters(unittest.TestCase):

    def setUp(self):
        bp = BluePrint("test", load_existing=False, custom_dir=None, skip_prompts=True,
                       int=int, float=float, bool=bool, str=str, module=Dummy_Module, list=[Dummy_Module.A, Dummy_Module.B])
        self.hparams = HyperParameters("test", blueprint=bp)
        
    def test_add_value_that_is_int(self):
        self.hparams["int"] = 10
        self.assertIn("int", self.hparams)
        self.assertEqual(self.hparams["int"], 10)

    def test_add_value_that_is_float(self):
        self.hparams["float"] = 0.5
        self.assertIn("float", self.hparams)
        self.assertEqual(self.hparams["float"], 0.5)

    def test_add_value_that_is_bool(self):
        self.hparams["bool"] = True
        self.assertIn("bool", self.hparams)
        self.assertEqual(self.hparams["bool"], True)

    def test_add_value_that_is_str(self):
        self.hparams["str"] = "Hello"
        self.assertIn("str", self.hparams)
        self.assertEqual(self.hparams["str"],  "Hello")

    def test_add_value_that_is_module_class(self):
        self.hparams["module"] = Dummy_Module.A
        self.assertIn("module", self.hparams)
        self.assertEqual(self.hparams["module"],  Dummy_Module.A)

    def test_add_invalid_float_to_int(self):
        self.assertRaises(ValueError, self.hparams.__setitem__, "int", 0.5)

    def test_add_invalid_class_to_list(self):
        self.assertRaises(ValueError, self.hparams.__setitem__, "list", Dummy_Module.C) # Dummy_Module.C is not in list
        

class TestSaveAndReload(unittest.TestCase):

    def setUp(self):
        self.bp = BluePrint("test", load_existing=False, custom_dir=None, skip_prompts=True,
                            int=int, float=float, bool=bool, str=str, module=Dummy_Module, list=[Dummy_Module.A, Dummy_Module.B])
        self.dir = Path(__file__).parent  / "TEMP"
        self.dir.mkdir(exist_ok=True)

    def test_reload_with_primitive_types_only(self):
        hparams = HyperParameters("test", blueprint=self.bp, float=0.5, int=10, bool=True, str="Hello")
        hparams.save(self.dir)
        hparams2 = HyperParameters("test", blueprint=self.bp)
        hparams2.load(self.dir)
        self.assertEqual(hparams, hparams2)

    def test_reload_with_module_class_only(self):
        hparams = HyperParameters("test", blueprint=self.bp, module=Dummy_Module.C)
        hparams.save(self.dir)
        hparams2 = HyperParameters("test", blueprint=self.bp)
        hparams2.load(self.dir)
        self.assertEqual(hparams, hparams2)

    def test_reload_with_list_class_only(self):
        hparams = HyperParameters("test", blueprint=self.bp, list=Dummy_Module.A)
        hparams.save(self.dir)
        hparams2 = HyperParameters("test", blueprint=self.bp)
        hparams2.load(self.dir)
        self.assertEqual(hparams, hparams2)

    def test_reload_with_mixed_params(self):
        hparams = HyperParameters("test", blueprint=self.bp, int=0, float=0.9, bool=False, str="bye", module=Dummy_Module.C, list=Dummy_Module.B)
        hparams.save(self.dir)
        hparams2 = HyperParameters("test", blueprint=self.bp)
        hparams2.load(self.dir)
        self.assertEqual(hparams, hparams2)

    def tearDown(self):
        for name in os.listdir(self.dir):
            (self.dir / name).unlink()
        self.dir.rmdir()

class TestVariableAccess(unittest.TestCase):
    def setUp(self):
        bp = BluePrint("test", load_existing=False, custom_dir=None, skip_prompts=True,
                       int=int, float=float, bool=bool, str=str, module=Dummy_Module, list=[Dummy_Module.A, Dummy_Module.B],
                       newInt=int, newFloat=float, newBool=bool, newStr=str, newModule=Dummy_Module, newList=[Dummy_Module.A, Dummy_Module.B])
        self.hparams = HyperParameters("test", blueprint=bp, int=10, float=0.5, bool=True, str="hello", 
                                       module=Dummy_Module.C, list=Dummy_Module.A)

    def test_getitem_primitives(self):
        self.assertEqual(self.hparams["int"], 10)
        self.assertEqual(self.hparams["float"], 0.5)
        self.assertEqual(self.hparams["bool"], True)
        self.assertEqual(self.hparams["str"], "hello")

    def test_getitem_module(self):
        self.assertEqual(self.hparams["module"], (Dummy_Module.C, {}))

    def test_getitem_list(self):
        self.assertEqual(self.hparams["list"], (Dummy_Module.A, {}))    

    def test_setitem_primitive(self):
        self.hparams["newInt"] = -10
        self.assertEqual(self.hparams["newInt"], -10)
        self.hparams["newFloat"] = -0.5
        self.assertEqual(self.hparams["newFloat"], -0.5)
        self.hparams["newBool"] = False
        self.assertEqual(self.hparams["newBool"], False)
        self.hparams["newStr"] = "bye"
        self.assertEqual(self.hparams["newStr"],  "bye")

    def test_setitem_module(self):
        self.hparams["newModule"] = Dummy_Module.C
        self.assertEqual(self.hparams["newModule"], (Dummy_Module.C, {}))

    def test_setitem_list(self):
        self.hparams["newList"] = Dummy_Module.A
        self.assertEqual(self.hparams["newList"], (Dummy_Module.A, {}))
        
    def test_get_for_existing_key(self):
        self.assertEqual(self.hparams.get("int", 42), 10)
    
    def test_get_returns_default_for_nonexisting_key(self):
        self.assertEqual(self.hparams.get("BAD_KEY", 42), 42)

    def test_get_returns_None_if_no_default_provided_and_nonexisting_key(self):
        self.assertEqual(self.hparams.get("OTHER_BAD_KEY"), None)


if __name__ == '__main__':
    unittest.main()