0.  Prepare (just once):

    ```
    mkdir -p imasdb/test/3/{0,1,2,3,4,5,6,7,8,9}
    docker build -t imas/inotify .
    ```

1.  First terminal:

    ```
    docker run -it --rm --name=inotify --volume "$(pwd)/imasdb:/home/imas/public/imasdb:ro" imas/inotify

    git clone https://github.com/tzok/imas-inotify.git
    imas-inotify/imas-inotify.py
    ```

2.  Second terminal:

    ```
    docker run -it --rm --name=imas --volume "$(pwd)/imasdb:/home/imas/public/imasdb" imas/fc2k
    git clone https://github.com/tzok/imas-hello-world.git
    imas-hello-world/python/hello.py
    touch public/imasdb/test/3/0/ids_10001.populate
    ```

Expected outcome:
- In the first terminal you should see:

    ```
    INFO:root:Establishing watches for /home/imas/public/imasdb with action ./handler-new-pulsefile.py
    Data ready for user=imas tokamak=test version=3 shot=1 run=1
    ```
