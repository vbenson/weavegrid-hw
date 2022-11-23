import os
import json
import sys

from absl import app as absl_app, flags
from flask import Flask

from server_lib import get_contents

FLAGS = flags.FLAGS
flags.DEFINE_string("root_dir", None, "Root directory to browse.")
flags.mark_flag_as_required("root_dir")

app = Flask(__name__)

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def view_dir(path):
    full_path = os.path.join(app.config.get('root_dir'), path)
    return json.dumps(get_contents(full_path))

if __name__ == '__main__':
    # Force flags library to parse argv in order to access flags.
    FLAGS(sys.argv)
    app.config['root_dir'] = FLAGS.root_dir
    app.run(debug=True, host='0.0.0.0')