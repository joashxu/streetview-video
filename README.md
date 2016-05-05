# Streetview-Video

This is a small command line tool using Google Street View API, that takes in a start & destination, then compile Street view images into a short video.

Requirements:

- A Google Maps API key.
- Google-maps-services-python.
- LatLon Python library.
- OpenCV with ffmpeg support.

Take a look at the requirements.txt for exact package name.
OpenCV is not installed via pip and you need to install it along with ffmpeg.

On MacOSX you can run:
    
    $ brew install opencv3 --with-ffmpeg

Usage:

    $ python walkthrough <source_address> <destination_address> <video>

Example:

    $ python one.py "Sydney Town Hall" "Parramatta, NSW" video.avi
