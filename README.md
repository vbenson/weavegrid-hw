# weavegrid-hw
WeaveGrid interview hw assignment: Directory browser/modifier API

The user must specify a root directory when launching the application. Then all 
directories from the root and downward are available using this API. This runs
on http://localhost:5000/. Available operations:
* GET requests return all subdirectories and files within a directory. To use, 
supply the path from the root directory to the desired directory. The output is 
a json string giving the name, size, owner, and permissions for each item in the 
directory.
* DELETE requests delete the file/directory at the path (starting from the root 
directory again). If a directory is given, this will also delete all contents 
of the directory. If successful this will redirect to the parent directory,
otherwise it will redirect to the requested path.

# Requirements
* Docker

# Launching
Either run using the provided run.sh script or run the commands below yourself.
To run the run.sh script, simply provide the full local path you'd like to 
browse as an argument.
```bash
sh run.sh <local directory to browse>
```

Otherwise run these commands yourself.
```bash
# Build the docker container image.
docker build -t weavegrid-hw:dev .

# Run the application in the container. Make sure to specify a port mapping.
docker run -p 5000:5000 --mount type=bind,source=<local directory to browse>,target=/root_dir --rm weavegrid-hw:dev /root_dir

# To test, run the above two commands, then in a separate terminal first run:
docker ps

# Note the CONTAINER ID output from the last command and use it to run the test.
docker exec -it <container id>  python server_test.py
```

# Requests
cURL can be used to transfer data from the command line to URLs. After launching
the API, requests can be issued via the command line:
```bash
# Get the contents of the root directory.
curl http://localhost:5000/

# Get the contents of directory foo within the root directory.
curl http://localhost:5000/foo

# Delete the file bar.txt
curl -X DELETE http://localhost:5000/foo/bar.txt

# Delete the directory foo (and all its contents).
curl -X DELETE http://localhost:5000/foo
```

# Known Issues
When running via a Docker container the owner of all files/directories will
be reassigned to the user which docker is using to run. This defaults to the 
'root' user since we do not explicitly set it in either the Dockerfile nor the 
Usage commands shown above.