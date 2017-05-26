import os

from nose.tools import with_setup, raises, ok_, eq_

from alize.workspace import Workspace
from alize.exception import *

class TestWorkspace(object):
    @classmethod
    def setup(cls):
        cls.test_path = os.path.normpath(os.path.join(os.path.dirname(__file__), "tmp"))
        cls.workspace = Workspace(cls.test_path)

    @classmethod
    def teardown(cls):
        cls.workspace.rmdir("")

    @with_setup(setup, teardown)
    @raises(WorkspaceError)
    def test_workspace_failed_01(self):
        test_fail_path = 1
        workspace = Workspace(test_fail_path, clear=True)
        workspace.rm(test_fail_path)

    @with_setup(setup, teardown)
    @raises(WorkspaceError)
    def test_workspace_success_01(self):
        test_fail_path = os.path.join("test")
        workspace = Workspace(test_fail_path)
        workspace.rm(test_fail_path)

    @with_setup(setup, teardown)
    def test_workspace_mkdir_success_01(self):
        reference = os.path.join(self.workspace.root(), "test01")
        result = self.workspace.mkdir("test01")
        ok_(os.path.exists(result))
        eq_(result, reference)

    @with_setup(setup, teardown)
    def test_workspace_mkdir_success_02(self):
        reference = os.path.join(self.workspace.root(), "test01", "test02")
        result = self.workspace.mkdir(os.path.join("test01","test02"))
        ok_(os.path.exists(result))
        eq_(result, reference)


    @with_setup(setup, teardown)
    @raises(WorkspaceError)
    def test_workspace_mkdir_failed_01(self):
        result = self.workspace.mkdir(12)
        ok_(os.path.exists(result))

    @with_setup(setup, teardown)
    def test_workspace_mkdir_failed_02(self):
        result = self.workspace.mkdir("test01")
        result2 = self.workspace.mkdir("test02", host=result)
        result = self.workspace.mkdir("test01", clear=True)
        ok_(os.path.exists(result))
        ok_(not os.path.exists(result2))

    @with_setup(setup, teardown)
    def test_workspace_rmdir_success(self):
        result = self.workspace.mkdir("test01")
        ok_(os.path.exists(result))
        self.workspace.rmdir("test01")
        ok_(not os.path.exists(result))

    @with_setup(setup, teardown)
    @raises(WorkspaceError)
    def test_workspace_rmdir_failed_01(self):
        result = self.workspace.rmdir(12)
        ok_(os.path.exists(result))

    @with_setup(setup, teardown)
    def test_workspace_rmdir_failed_02(self):
        ok_(not os.path.exists(os.path.join(self.workspace.root(), "test01")))
        result = self.workspace.rmdir("test01")
        ok_(not os.path.exists(result))

    @with_setup(setup, teardown)
    def test_workspace_rmdir_failed_03(self):
        vhost = os.path.join(self.workspace.root(), "test02")
        ok_(not os.path.exists(os.path.join(vhost, "test01")))
        result = self.workspace.rmdir("test01", host=vhost)
        ok_(not os.path.exists(result))

    @with_setup(setup, teardown)
    def test_workspace_touch_sucess_01(self):
        ok_(not os.path.exists(os.path.join(self.workspace.root(), "test01.txt")))
        self.workspace.touch("test01.txt")
        ok_(os.path.exists(os.path.join(self.workspace.root(), "test01.txt")))

    @with_setup(setup, teardown)
    def test_workspace_touch_sucess_02(self):
        ok_(not os.path.exists(os.path.join(self.workspace.root(), "test02", "test01.txt")))
        self.workspace.touch("test01.txt", host=os.path.join(self.workspace.root(), "test02"))
        ok_(os.path.exists(os.path.join(self.workspace.root(), "test02", "test01.txt")))

    @with_setup(setup, teardown)
    @raises(WorkspaceError)
    def test_workspace_touch_failed_01(self):
        self.workspace.touch(12)

    @with_setup(setup, teardown)
    @raises(WorkspaceError)
    def test_workspace_touch_failed_02(self):
        self.workspace.touch("test01.txt")
        self.workspace.touch("test01.txt")

    @with_setup(setup, teardown)
    def test_workspace_unique_success_01(self):
        result = self.workspace.unique()
        ok_(os.path.exists(result))

    @with_setup(setup, teardown)
    def test_workspace_unique_success_02(self):
        result = self.workspace.unique(host=os.path.join(self.workspace.root(),"test01"))
        ok_(os.path.exists(result))

    @with_setup(setup, teardown)
    def test_workspace_rm_sucess_01(self):
        ok_(not os.path.exists(os.path.join(self.workspace.root(), "test01.txt")))
        result = self.workspace.touch("test01.txt")
        ok_(os.path.exists(os.path.join(self.workspace.root(), "test01.txt")))
        self.workspace.rm(result)
        ok_(not os.path.exists(os.path.join(self.workspace.root(), "test01.txt")))

    @with_setup(setup, teardown)
    @raises(WorkspaceError)
    def test_workspace_rm_failed_01(self):
        self.workspace.rm(12)
