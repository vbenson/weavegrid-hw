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

def delete_content(path):
    """Deletes the supplied directory (including all contents) or file.

    Args:
        path: A string giving the file system path to a directory or file.
    
    Returns:
        An info string.
    """
    if os.path.isdir(path):
        shutil.rmtree(path)
        return "Removed directory: " + path
    elif os.path.isfile(path):
        os.remove(path)
        return "Removed file: " + path
    else:
        return "Flie/Directory does not exist: " + path