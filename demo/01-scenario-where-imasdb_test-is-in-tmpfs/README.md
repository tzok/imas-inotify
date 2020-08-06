0.  Prepare (just once):

    ```
    mkdir -p imasdb/test/3/{0,1,2,3,4,5,6,7,8,9}
    docker build -t imas/inotify .
    ```

1.  First terminal:

    ```
    docker run -it --rm --name=inotify --volume "$(pwd)/imasdb:/home/imas/public/imasdb" --mount 'type=tmpfs,destination=/home/imas/public/imasdb/test' imas/inotify

    git clone https://github.com/tzok/imas-inotify.git
    imas-inotify/imas-inotify.py
    ```

2.  Second terminal:

    ```
    docker run -it --rm --name=imas --volume "$(pwd)/imasdb:/home/imas/public/imasdb" imas/fc2k

    eval $(imasdb test)
    git clone https://github.com/tzok/imas-hello-world.git
    imas-hello-world/python/hello.py
    touch public/imasdb/test/3/0/ids_10001.populate
    # inotify watcher on the first terminal will not notice new data, because they are in `test` tokamak

    eval $(imasdb jet)
    sed -i 's/test/jet/' imas-hello-world/python/hello.py
    imas-hello-world/python/hello.py
    touch public/imasdb/jet/3/0/ids_10001.populate
    # new data will be noticed, because they are in `jet` tokamak
    ```

Expected outcome:
- In the first terminal you should see:

    ```
    INFO:root:Establishing watches for /home/imas/public/imasdb with action ./handler-new-pulsefile.py
    Data ready for user=imas tokamak=jet version=3 shot=1 run=1
    ```
