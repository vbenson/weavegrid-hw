import os
import tempfile
import unittest

from server_lib import get_contents, delete_content

class TestServerLib(unittest.TestCase):
    def setUp(self):
        self.maxDiff = None
        # Create tmp directories & files.
        self.dir_root = tempfile.TemporaryDirectory()
        self.dir_a = tempfile.TemporaryDirectory(dir=self.dir_root.name)
        self.dir_b = tempfile.TemporaryDirectory(
            dir=self.dir_root.name)
        os.chmod(self.dir_b.name, 0o755)
        self.dir_hidden = tempfile.TemporaryDirectory(
            prefix='.', dir=self.dir_root.name)
        self.dir_private = tempfile.TemporaryDirectory(dir=self.dir_root.name)
        os.chmod(self.dir_private.name, 0o000)

        self.file_a = tempfile.NamedTemporaryFile(dir=self.dir_root.name)
        os.chmod(self.file_a.name, 0o640)
        self.file_b = tempfile.NamedTemporaryFile(
            dir=self.dir_b.name, delete=False)
        self.file_hidden = tempfile.NamedTemporaryFile(
            prefix='.', dir=self.dir_root.name)
        self.file_hidden.write(b'Hello World!')
        self.file_hidden.flush()
        self.file_c = tempfile.NamedTemporaryFile(dir=self.dir_hidden.name)

    def tearDown(self):
        self.file_c.close()
        self.file_hidden.close()
        self.file_b.close()
        self.file_a.close()
        self.dir_private.cleanup()
        self.dir_hidden.cleanup()
        self.dir_b.cleanup()
        self.dir_a.cleanup()
        self.dir_root.cleanup()

        return super().tearDown()
        

    def mk_dict(self, name, suffix, size, owner, permissions):
        return {
            'name': str(os.path.basename(name) + suffix),
            'size': size, 
            'owner': owner, 
            'permissions': permissions
            }

    def test_read_basic_dir(self):
        output = get_contents(self.dir_root.name)
        expected_output = [
            self.mk_dict(self.dir_a.name, os.sep, 0, 'appuser', '700'),
            self.mk_dict(self.dir_b.name, os.sep, 0, 'appuser', '755'),
            self.mk_dict(self.dir_hidden.name, os.sep, 0, 'appuser', '700'),
            self.mk_dict(self.dir_private.name, os.sep, 0, 'appuser', '000'),
            self.mk_dict(self.file_a.name, '', 0, 'appuser', '640'),
            self.mk_dict(self.file_hidden.name, '', 12, 'appuser', '600')]
        self.assertCountEqual(output, expected_output)


    def test_read_hidden_dir(self):
        output = get_contents(self.dir_hidden.name)
        expected_output = [
            self.mk_dict(self.file_c.name, '', 0, 'appuser', '600')
        ]
        self.assertCountEqual(output, expected_output)
    
    def test_read_empty_dir(self):
        output = get_contents(self.dir_a.name)
        expected_output = []
        self.assertCountEqual(output, expected_output)

    @unittest.expectedFailure
    def test_read_nonexistent_dir(self):
        get_contents('dir_that_does_not_exist')

    @unittest.expectedFailure
    def test_read_private_dir(self):
        get_contents(self.dir_private.name)

    def test_delete_file(self):
        output = delete_content(self.file_b.name)
        expected_output = self.dir_b.name, 302
        self.assertEqual(output, expected_output)
        self.assertFalse(os.path.exists(self.file_b.name))

    def test_delete_dir(self):
        output = delete_content(self.dir_b.name)
        expected_output = self.dir_root.name, 302
        self.assertEqual(output, expected_output)
        self.assertFalse(os.path.exists(self.dir_b.name))
        self.assertFalse(os.path.exists(self.file_b.name))

    def test_delete_nonexistent_path(self):
        path = "fake_path_that_does_not_exist"
        output = delete_content(path)
        expected_output = path, 304
        self.assertEqual(output, expected_output)

if __name__ == '__main__':
    unittest.main()