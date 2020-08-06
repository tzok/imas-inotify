0.  Prepare (just once):

        mkdir -p imasdb/test/3/{0,1,2,3,4,5,6,7,8,9}
        docker build -t imas/inotify .

1.  First terminal:

        docker run -it --rm --name=inotify --volume $(pwd)/imasdb:/mnt/imasdb imas/inotify

        git clone https://github.com/tzok/imas-inotify.git
        sudo pip3 install -r imas-inotify/requirements.txt
        imas-inotify/imas-inotify.py

2.  Second terminal:

        mkdir -p imasdb/jet/3/{0,1,2,3,4,5,6,7,8,9}

        docker run -it --rm --name=imas --volume $(pwd)/imasdb:/mnt/imasdb imas/fc2k
        git clone https://github.com/tzok/imas-hello-world.git
        eval $(imasdb jet)
        sed -i 's/test/jet/' imas-hello-world/python/hello.py
        imas-hello-world/python/hello.py
        touch public/imasdb/jet/3/0/ids_10001.populate


Expected outcome:
- In the first terminal you should see:

        Establishing watches for /home/imas/public/imasdb with action ./handler-new-pulsefile.py
        Establishing watches for /mnt/imasdb with action ./handler-new-tokamak.sh
