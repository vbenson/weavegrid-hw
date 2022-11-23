import os
import tempfile
import unittest

from server_lib import get_contents

class TestServerLib(unittest.TestCase):
    def setUp(self):
        self.maxDiff = None
        # Create tmp directories & files.
        self.folder_root = tempfile.TemporaryDirectory()
        self.folder_a = tempfile.TemporaryDirectory(dir=self.folder_root.name)
        self.folder_b = tempfile.TemporaryDirectory(dir=self.folder_root.name)
        os.chmod(self.folder_b.name, 0o555)
        self.folder_hidden = tempfile.TemporaryDirectory(
            prefix='.', dir=self.folder_root.name)
        self.folder_private = tempfile.TemporaryDirectory(
            dir=self.folder_root.name)
        os.chmod(self.folder_private.name, 0o000)

        self.file_a = tempfile.NamedTemporaryFile(dir=self.folder_root.name)
        os.chmod(self.file_a.name, 0o640)
        self.file_hidden = tempfile.NamedTemporaryFile(
            prefix='.', dir=self.folder_root.name)
        self.file_hidden.write(b'Hello World!')
        self.file_hidden.flush()

        self.file_b = tempfile.NamedTemporaryFile(dir=self.folder_hidden.name)

    def tearDown(self):
        self.file_b.close()
        self.file_hidden.close()
        self.file_a.close()
        self.folder_private.cleanup()
        self.folder_hidden.cleanup()
        self.folder_b.cleanup()
        self.folder_a.cleanup()
        self.folder_root.cleanup()

        return super().tearDown()
        

    def mk_dict(self, name, suffix, size, owner, permissions):
        return {
            'name': str(os.path.basename(name) + suffix),
            'size': size, 
            'owner': owner, 
            'permissions': permissions
            }

    def test_basic_folder(self):
        output = get_contents(self.folder_root.name)
        expected_output = [
            self.mk_dict(self.folder_a.name, os.sep, 0, 'appuser', '700'),
            self.mk_dict(self.folder_b.name, os.sep, 0, 'appuser', '555'),
            self.mk_dict(self.folder_hidden.name, os.sep, 0, 'appuser', '700'),
            self.mk_dict(self.folder_private.name, os.sep, 0, 'appuser', '000'),
            self.mk_dict(self.file_a.name, '', 0, 'appuser', '640'),
            self.mk_dict(self.file_hidden.name, '', 12, 'appuser', '600')]
        self.assertCountEqual(output, expected_output)


    def test_hidden_folder(self):
        output = get_contents(self.folder_hidden.name)
        expected_output = [
            self.mk_dict(self.file_b.name, '', 0, 'appuser', '600')
        ]
        self.assertCountEqual(output, expected_output)
    
    def test_empty_folder(self):
        output = get_contents(self.folder_a.name)
        expected_output = []
        self.assertCountEqual(output, expected_output)

    @unittest.expectedFailure
    def test_nonexistent_folder(self):
        get_contents('dir_that_does_not_exist')

    @unittest.expectedFailure
    def test_private_folder(self):
        get_contents(self.folder_private.name)

if __name__ == '__main__':
    unittest.main()