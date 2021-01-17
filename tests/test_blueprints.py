import unittest, types, os

from BluePrint import BluePrint
from tests import Dummy_Module as Dummy_Module
from pathlib import Path

class TestValidConstraints(unittest.TestCase):

    def setUp(self):
        self.bp = BluePrint("test", load_existing=False, custom_dir=None, skip_prompts=True,
                            primitive=int, module=Dummy_Module, list=[Dummy_Module.A, Dummy_Module.B])

    def test_primitive_constraint(self):
        self.assertEqual(self.bp.primitive, int)

    def test_module_constraint(self):
        self.assertEqual(self.bp.module,[Dummy_Module.A, Dummy_Module.B, Dummy_Module.C])

    def test_list_constraint(self):
        self.assertEqual([cls.__name__ for cls in self.bp.list], ["A","B"])

class TestSaveAndReload(unittest.TestCase):

    def setUp(self):
        self.dir = Path(__file__).parent  / "TEMP"
        self.dir.mkdir(exist_ok=True)

    def test_reload_with_primitive_types_only(self):
        bp = BluePrint("test", False, None, a=int, b=float, c=str, d=bool)
        bp.save(self.dir)
        bp2 = BluePrint("test")
        bp2.load(self.dir)
        self.assertEqual(bp, bp2)

    def test_reload_with_module_only(self):
        bp = BluePrint("test", False, None, skip_prompts=True, module=Dummy_Module)
        bp.save(self.dir)
        bp2 = BluePrint("test")
        bp2.load(self.dir)
        self.assertEqual(bp, bp2)

    def test_reload_with_list_only(self):
        bp = BluePrint("test", False, None, skip_prompts=True, list=[Dummy_Module.A, Dummy_Module.B, Dummy_Module.C])
        bp.save(self.dir)
        bp2 = BluePrint("test")
        bp2.load(self.dir)
        self.assertEqual(bp, bp2)

    def test_reload_with_mixed_constraints(self):
        bp = BluePrint("test", False, None, skip_prompts=True, a=int, b=float, c=str, d=bool, 
                       list=[Dummy_Module.A, Dummy_Module.B, Dummy_Module.C], module=Dummy_Module)
        bp.save(self.dir)
        bp2 = BluePrint("test")
        bp2.load(self.dir)
        self.assertEqual(bp, bp2)

    def tearDown(self):
        for name in os.listdir(self.dir):
            (self.dir / name).unlink()
        self.dir.rmdir()

class TestVariableAccess(unittest.TestCase):
    def setUp(self):
        self.bp = BluePrint("test", load_existing=False, custom_dir=None, skip_prompts=True,
                            a=int, b=float, c=str, d=bool, 
                            module=Dummy_Module, list=[Dummy_Module.A, Dummy_Module.B])

    def test_getitem_primitives(self):
        self.assertEqual(self.bp["a"], int)
        self.assertEqual(self.bp["b"], float)
        self.assertEqual(self.bp["c"], str)
        self.assertEqual(self.bp["d"], bool)

    def test_getitem_module(self):
        self.assertEqual(self.bp["module"], [Dummy_Module.A, Dummy_Module.B, Dummy_Module.C])

    def test_getitem_list(self):
        self.assertEqual(self.bp["list"], [Dummy_Module.A, Dummy_Module.B])    

    def test_setitem_primitive(self):
        self.bp["new"] = bool
        self.assertEqual(self.bp["new"], bool)


    def test_setitem_module(self):
        self.bp["newModule"] = Dummy_Module
        self.assertEqual(self.bp["newModule"], [Dummy_Module.A, Dummy_Module.B, Dummy_Module.C])

    def test_setitem_list(self):
        self.bp["newList"] = [Dummy_Module.A, Dummy_Module.B]
        self.assertEqual(self.bp["newList"], [Dummy_Module.A, Dummy_Module.B])

    def test_primitive_in_blueprint(self):
        self.assertIn("a", self.bp)
        self.assertIn("b", self.bp)
        self.assertIn("c", self.bp)
        self.assertIn("d", self.bp)
        
    def test_module_in_blueprint(self):
        self.assertIn("module", self.bp)

    def test_list_in_blueprint(self):
        self.assertIn("list", self.bp)

    def test_check_int(self):
        self.assertTrue(self.bp.check("a", 10))

    def test_check_float(self):
        self.assertTrue(self.bp.check("b", 0.5))

    def test_check_str(self):
        self.assertTrue(self.bp.check("c", "hello"))

    def test_check_bool(self):
        self.assertTrue(self.bp.check("d", True))

    def test_check_module_class(self):
        self.assertTrue(self.bp.check("module", Dummy_Module.C))

    def test_check_list_class(self):
        self.assertTrue(self.bp.check("list", Dummy_Module.A))

if __name__ == '__main__':
    unittest.main()