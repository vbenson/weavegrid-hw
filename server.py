"""Launch a web server to browse, create, modify, and delete files/directories.
"""

import os
import json
import sys

from absl import flags
from flask import Flask, redirect, request, url_for

from server_lib import add_content, delete_content, get_content, replace_content

FLAGS = flags.FLAGS
flags.DEFINE_string("root_dir", None, "Root directory to browse.")
flags.mark_flag_as_required("root_dir")

app = Flask(__name__)


@app.route('/',
           defaults={'path': ''},
           methods=['GET', 'POST', 'PUT', 'DELETE'])
@app.route('/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def view_dir(path):
    full_path = os.path.join(app.config.get('root_dir'), path)

    if request.method == 'GET':
        return json.dumps(get_content(full_path))

    if request.method == 'POST':
        redirect_path, code = add_content(full_path, request.get_json())
        return redirect(url_for('view_dir', path=redirect_path), code=code)

    if request.method == 'PUT':
        redirect_path, code = replace_content(
            full_path, request.get_json(), app.config.get('root_dir'))
        return redirect(url_for('view_dir', path=redirect_path), code=code)

    if request.method == 'DELETE':
        redirect_path, code = delete_content(full_path)
        return redirect(url_for('view_dir', path=redirect_path), code=code)


if __name__ == '__main__':
    # Force flags library to parse argv in order to access flags.
    FLAGS(sys.argv)
    app.config['root_dir'] = FLAGS.root_dir
    app.run(debug=True, host='0.0.0.0')
