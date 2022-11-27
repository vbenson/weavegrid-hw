from http import HTTPStatus
import os
import tempfile
import shutil
import unittest

from server_lib import add_content, delete_content, get_content, replace_content


class TestServerLib(unittest.TestCase):
    def setUp(self):
        self.maxDiff = None
        # Create tmp directories & files having the following structure:
        # dir_root
        #       |- dir_a
        #       |- dir_b
        #       |      |- file_b
        #       |- dir_hidden
        #       |      |- file_c
        #       |- dir_private
        #       |- file_a
        #       |- file_hidden

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
        self.file_b.write(b'Original text.')
        self.file_b.flush()
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
        output = get_content(self.dir_root.name)
        expected_output = [
            self.mk_dict(self.dir_a.name, os.sep, 0, 'appuser', '700'),
            self.mk_dict(self.dir_b.name, os.sep, 0, 'appuser', '755'),
            self.mk_dict(self.dir_hidden.name, os.sep, 0, 'appuser', '700'),
            self.mk_dict(self.dir_private.name, os.sep, 0, 'appuser', '000'),
            self.mk_dict(self.file_a.name, '', 0, 'appuser', '640'),
            self.mk_dict(self.file_hidden.name, '', 12, 'appuser', '600')]
        self.assertCountEqual(output, expected_output)

    def test_read_hidden_dir(self):
        output = get_content(self.dir_hidden.name)
        expected_output = [
            self.mk_dict(self.file_c.name, '', 0, 'appuser', '600')
        ]
        self.assertCountEqual(output, expected_output)

    def test_read_empty_dir(self):
        output = get_content(self.dir_a.name)
        expected_output = []
        self.assertCountEqual(output, expected_output)

    @unittest.expectedFailure
    def test_read_nonexistent_dir(self):
        get_content('dir_that_does_not_exist')

    @unittest.expectedFailure
    def test_read_private_dir(self):
        get_content(self.dir_private.name)

    def test_add_empty_file(self):
        new_file_path = os.path.join(self.dir_b.name, 'new_file.txt')
        info = {'make_dir': False}
        output = add_content(new_file_path, info)
        expected_output = self.dir_b.name, HTTPStatus.FOUND
        self.assertEqual(output, expected_output)
        self.assertTrue(os.path.exists(new_file_path))
        f = open(new_file_path, 'r')
        self.assertEqual(f.read(), '')
        f.close()

        # Cleanup
        os.remove(new_file_path)

    def test_add_file_invalid_content(self):
        new_file_path = os.path.join(self.dir_b.name, 'new_file.txt')
        info = {'make_dir': False, 'text': 123}
        output = add_content(new_file_path, info)
        expected_output = self.dir_b.name, HTTPStatus.FOUND
        self.assertEqual(output, expected_output)
        self.assertTrue(os.path.exists(new_file_path))
        f = open(new_file_path, 'r')
        self.assertEqual(f.read(), '')
        f.close()

        # Cleanup
        os.remove(new_file_path)

    def test_add_file_with_content(self):
        new_file_path = os.path.join(self.dir_b.name, 'new_file.txt')
        text = 'Hello World!'
        info = {'make_dir': False, 'text': text}
        output = add_content(new_file_path, info)
        expected_output = self.dir_b.name, HTTPStatus.FOUND
        self.assertEqual(output, expected_output)
        self.assertTrue(os.path.exists(new_file_path))
        f = open(new_file_path, 'r')
        self.assertEqual(f.read(), text)
        f.close()

        # Cleanup
        os.remove(new_file_path)

    def test_add_existing_file(self):
        new_file_path = self.file_b.name
        info = {'make_dir': False, 'text': 'Hello World!'}
        output = add_content(new_file_path, info)
        expected_output = self.dir_b.name, HTTPStatus.NOT_MODIFIED
        self.assertEqual(output, expected_output)
        self.assertTrue(os.path.exists(new_file_path))

        # Ensure that the contents were not overwritten.
        f = open(new_file_path, 'r')
        self.assertEqual(f.read(), 'Original text.')
        f.close()

    def test_add_dir(self):
        new_file_path = os.path.join(self.dir_b.name, 'new_dir')
        info = {'make_dir': True}
        output = add_content(new_file_path, info)
        expected_output = new_file_path, HTTPStatus.FOUND
        self.assertEqual(output, expected_output)
        self.assertTrue(os.path.exists(new_file_path))
        self.assertTrue(os.path.isdir(new_file_path))

        # Cleanup
        os.rmdir(new_file_path)

    def test_add_invalid_make_dir(self):
        new_file_path = os.path.join(self.dir_b.name, 'new_content')
        info = {'make_dir': 123}
        output = add_content(new_file_path, info)
        expected_output = new_file_path, HTTPStatus.NOT_MODIFIED
        self.assertEqual(output, expected_output)
        self.assertFalse(os.path.exists(new_file_path))

    def test_add_existing_dir(self):
        new_file_path = self.dir_root.name
        orig_content = os.listdir(new_file_path)
        info = {'make_dir': True}
        output = add_content(new_file_path, info)
        expected_output = new_file_path, HTTPStatus.NOT_MODIFIED
        self.assertEqual(output, expected_output)
        self.assertTrue(os.path.exists(new_file_path))
        self.assertTrue(os.path.isdir(new_file_path))

        # Ensure that the dir contents were not modified.
        self.assertCountEqual(os.listdir(new_file_path), orig_content)

    def test_add_invalid_info(self):
        new_file_path = os.path.join(self.dir_b.name, 'new_content')
        info = {'missing': 123}
        output = add_content(new_file_path, info)
        expected_output = new_file_path, HTTPStatus.NOT_MODIFIED
        self.assertEqual(output, expected_output)
        self.assertFalse(os.path.exists(new_file_path))

    def test_replace_file(self):
        src_path = self.file_b.name
        dst_path = self.file_a.name
        info = {'src_path': src_path}
        output = replace_content(dst_path, info)
        expected_output = self.dir_root.name, HTTPStatus.FOUND
        self.assertEqual(output, expected_output)

        # Ensure that the contents were overwritten.
        f = open(dst_path, 'r+')
        self.assertEqual(f.read(), 'Original text.')

        # Cleanup
        f.truncate(0)
        f.close()

    def test_replace_dir(self):
        src_path = self.dir_b.name
        src_files = os.listdir(src_path)
        dst_path = self.dir_a.name
        info = {'src_path': src_path}

        output = replace_content(dst_path, info)
        expected_output = dst_path, HTTPStatus.FOUND
        self.assertEqual(output, expected_output)

        # Ensure that the contents are now the same.
        self.assertCountEqual(src_files, os.listdir(dst_path))

        # Cleanup
        shutil.rmtree(dst_path)

    def test_replace_file_with_dir_invalid(self):
        src_path = self.dir_b.name
        dst_path = self.file_a.name
        info = {'src_path': src_path}

        output = replace_content(dst_path, info)
        expected_output = self.dir_root.name, HTTPStatus.NOT_MODIFIED
        self.assertEqual(output, expected_output)

    def test_replace_dir_with_file_invalid(self):
        src_path = self.file_a.name
        dst_path = self.dir_b.name
        info = {'src_path': src_path}

        output = replace_content(dst_path, info)
        expected_output = dst_path, HTTPStatus.NOT_MODIFIED
        self.assertEqual(output, expected_output)

    def test_replace_nonexistent_src(self):
        src_path = 'fake_path_that_does_not_exist'
        dst_path = self.dir_b.name
        info = {'src_path': src_path}

        output = replace_content(dst_path, info)
        expected_output = dst_path, HTTPStatus.NOT_MODIFIED
        self.assertEqual(output, expected_output)

    def test_replace_nonexistent_dst(self):
        src_path = self.dir_b.name
        dst_path = 'fake_path_that_does_not_exist'
        info = {'src_path': src_path}

        output = replace_content(dst_path, info)
        expected_output = dst_path, HTTPStatus.NOT_MODIFIED
        self.assertEqual(output, expected_output)

    def test_replace_invalid_request(self):
        src_path = self.dir_b.name
        dst_path = self.dir_a.name
        orig_dst_files = os.listdir(dst_path)
        info = {'bad_src_path': src_path}

        output = replace_content(dst_path, info)
        expected_output = dst_path, HTTPStatus.NOT_MODIFIED
        self.assertEqual(output, expected_output)
        self.assertEqual(orig_dst_files, os.listdir(dst_path))

    def test_replace_same_file(self):
        src_path = self.dir_b.name
        dst_path = self.dir_b.name
        orig_dst_files = os.listdir(dst_path)
        info = {'bad_src_path': src_path}

        output = replace_content(dst_path, info)
        expected_output = dst_path, HTTPStatus.NOT_MODIFIED
        self.assertEqual(output, expected_output)
        self.assertEqual(orig_dst_files, os.listdir(dst_path))

    def test_delete_file(self):
        output = delete_content(self.file_b.name)
        expected_output = self.dir_b.name, HTTPStatus.FOUND
        self.assertEqual(output, expected_output)
        self.assertFalse(os.path.exists(self.file_b.name))

    def test_delete_dir(self):
        output = delete_content(self.dir_b.name)
        expected_output = self.dir_root.name, HTTPStatus.FOUND
        self.assertEqual(output, expected_output)
        self.assertFalse(os.path.exists(self.dir_b.name))
        self.assertFalse(os.path.exists(self.file_b.name))

    def test_delete_nonexistent_path(self):
        path = 'fake_path_that_does_not_exist'
        output = delete_content(path)
        expected_output = path, HTTPStatus.NOT_MODIFIED
        self.assertEqual(output, expected_output)


if __name__ == '__main__':
    unittest.main()
