# weavegrid-hw
WeaveGrid interview hw assignment: Directory browser API

This API returns all subdirectories and files within a directory. The user must 
specify a root directory when launching the application. Then all all 
directories from the root and downward are browsable using this API. 

To view the contents of a directory, send a GET request supplying the path from 
the root directory to the desired diectory.

# Requirements
* Docker

# Usage
```bash
# Build the docker container image
docker build -t weavegrid-hw:dev .

# Run the application in the container. Make sure to specify a port mapping
docker run -p 5000:5000 --mount type=bind,source=<local directory to browse>,target=/root_dir --rm weavegrid-hw:dev /root_dir

# To test, run the above two commands, then in a separate terminal first run:
docker ps

# Note the CONTAINER ID output from the last command and use it to run the test.
docker exec -it <container id>  python server_test.py
```

# Known Issues
When running via a Docker container the owner of all files/directories will
be reassigned to the user which docker is using to run. This defaults to the 
'root' user since we do not explicitly set it in either the Dockerfile nor the 
Usage commands shown above.