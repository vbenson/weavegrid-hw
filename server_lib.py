"""Library functions to handle file interactions."""

from http import HTTPStatus
import os
from pwd import getpwuid
import shutil


def get_dir(path):
    """Returns path if is a directory, else returns its parent directory."""
    if os.path.isdir(path):
        return path
    else:
        return os.path.dirname(path)


def get_content(path):
    """Returns a list of file/directory info showing the contents of 'path'.

    Args:
        path: A string giving the file system path to a directory.

    Returns:
        A list of dicts, one for each file/directory within path. Each dict 
        contains the keys: 'name', 'size', 'owner' and 'permissions' (standard 
        octal representation). 
    """
    content_list = []
    for dir_entry in os.scandir(path):
        content = {}
        stats = dir_entry.stat(follow_symlinks=False)
        if dir_entry.is_dir():
            content['name'] = dir_entry.name + '/'
            content['size'] = 0
        else:
            content['name'] = dir_entry.name
            content['size'] = stats.st_size

        content['owner'] = getpwuid(stats.st_uid).pw_name
        # st_mode returns file type then permissions, just grab the last 3 octal
        # bits to get the permissions.
        content['permissions'] = oct(stats.st_mode)[-3:]

        content_list.append(content)

    return content_list


def add_content(path, info):
    """Creates a directory or a file with optional content.

    If the directory or file already exists then does nothing.

    Args:
        path: A string giving the file system path to a directory or file.
        info: A dictionary with required field 'make_dir' (boolean), and 
        optional field 'text' (string). If make_dir is True a directory is 
        created, else a file is created with 'text' written to it, if supplied.

    Returns:
        A tuple of either the added directory or the directory of the added file
        and a statuscode.
    """
    if os.path.exists(path):
        return get_dir(path), HTTPStatus.NOT_MODIFIED

    if 'make_dir' not in info or not isinstance(info['make_dir'], bool):
        return path, HTTPStatus.NOT_MODIFIED

    if info['make_dir']:
        os.mkdir(path)
        return path, HTTPStatus.FOUND
    else:
        with open(path, 'w+') as fp:
            if 'text' in info and isinstance(info['text'], str):
                fp.write(info['text'])
        return os.path.dirname(path), HTTPStatus.FOUND


def replace_content(dst_path, info, root_dir=''):
    """Replaces the content of an existing directory/file with another.

    Does not replace the original permissions nor owner.
    If the original directory or file does not exist then does nothing.

    Args:
        dst_path: A string giving the file system path to a directory or file.
        info: A dictionary with the required field 'src_path' (string). If
        path points to a directory, content path must also point to a directory,
        and similarly for a file.
        root_dir: Optional argument to prepend to 'src_path' to form full path.

    Returns:
        A tuple of either the modified directory or the directory of the 
        modified file and a statuscode.
    """
    if not os.path.exists(dst_path):
        return dst_path, HTTPStatus.NOT_MODIFIED

    if 'src_path' not in info or not isinstance(info['src_path'], str):
        return get_dir(dst_path), HTTPStatus.NOT_MODIFIED

    src_path = os.path.join(root_dir, info['src_path'])
    if not os.path.exists(src_path) or dst_path == src_path:
        return get_dir(dst_path), HTTPStatus.NOT_MODIFIED

    if os.path.isdir(dst_path) and os.path.isdir(src_path):
        # Replace directory.
        shutil.rmtree(dst_path)
        shutil.copytree(src_path, dst_path)
        return dst_path, HTTPStatus.FOUND

    elif not os.path.isdir(dst_path) and not os.path.isdir(src_path):
        # Replace file.
        shutil.copyfile(src_path, dst_path)
        return os.path.dirname(dst_path), HTTPStatus.FOUND

    else:
        # Invalid call.
        return get_dir(dst_path), HTTPStatus.NOT_MODIFIED


def delete_content(path):
    """Deletes the supplied directory (including all contents) or file.

    Args:
        path: A string giving the file system path to a directory or file.

    Returns:
        A tuple of the parent directory if successful, else the original path
        and a statuscode.
    """
    if os.path.isdir(path):
        shutil.rmtree(path)
        return os.path.dirname(path), HTTPStatus.FOUND
    elif os.path.isfile(path):
        os.remove(path)
        return os.path.dirname(path), HTTPStatus.FOUND
    else:
        return path, HTTPStatus.NOT_MODIFIED
