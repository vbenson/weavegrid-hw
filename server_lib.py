import os
from pwd import getpwuid
import shutil

def get_contents(path):
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
        if os.path.isdir(path):
            return path, 304
        else:
            return os.path.dirname(path), 304

    if 'make_dir' not in info or not isinstance(info['make_dir'], bool):
        return path, 304
    
    if info['make_dir']:
        os.mkdir(path)
        return path, 302
    else:
        with open(path, 'w+') as fp:
            if 'text' in info and isinstance(info['text'], str):
                fp.write(info['text'])
        return os.path.dirname(path), 302

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
        return os.path.dirname(path), 302
    elif os.path.isfile(path):
        os.remove(path)
        return os.path.dirname(path), 302
    else:
        return path, 304