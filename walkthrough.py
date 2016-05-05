# -*- coding: utf-8 -*-

import os
import argparse
import tempfile
import urllib
from urllib2 import URLError

import googlemaps
from LatLon import LatLon, Latitude, Longitude
from cv2 import VideoWriter, VideoWriter_fourcc, imread


API_KEY = '<Your API Key>'
GMAPS = googlemaps.Client(key=API_KEY)
STREETVIEW_URL = ("http://maps.googleapis.com/maps/api/streetview?sensor=false&"
                  "size=640x480&key=" + API_KEY)


def fetch_directions(source, destination):
    """
    Given source and destination address, return a list of lat and lon,
    from source to destination.
    """
    directions = []

    gmap_directions = GMAPS.directions(source, destination)

    if gmap_directions:
        # Check and get the direction elements.
        direction_elements = gmap_directions[0]
        direction_elements = direction_elements['legs'] if 'legs' in direction_elements else None
        direction_elements = direction_elements[0] if direction_elements else None

        if direction_elements:
            # Add the first location.
            directions.append(direction_elements['start_location'])
            # Only add the end location for each step, since the start location
            # is always previous entry end location.
            directions += [item['end_location'] for item in direction_elements['steps']]

    return directions


def get_heading(start, end):
    """
    Get heading from start point to end point.
    """
    start = LatLon(Latitude(start['lat']), Longitude(start['lng']))
    end = LatLon(Latitude(end['lat']), Longitude(end['lng']))
    heading = start.heading_initial(end)

    return '{0:.4f}'.format(heading)


def fetch_streetview_images(point_of_interest_list):
    """
    Fetch images from Google Street View and saved to unnamed temporary files.
    And then return list of the resulting path.
    """
    result_path = []
    poi_len = len(point_of_interest_list)

    for idx, item in enumerate(point_of_interest_list):
        try:
            # Create temporary file
            outfile = tempfile.NamedTemporaryFile(delete=False)
            # Close the file, since urlretrieve will open the file.
            outfile.close()

            lat_lon = str(item['lat']) + ',' + str(item['lng'])
            url = STREETVIEW_URL + "&location=" + lat_lon

            if idx + 1 < poi_len:
                next_item = point_of_interest_list[idx + 1]
                url += "&heading=" + get_heading(item,
                                                 next_item)

            # Fetch the image
            urllib.urlretrieve(url, outfile.name)
            # Add the path to our result list
            result_path.append(outfile.name)
        except URLError:
            # Since we can not download the file,
            # we need to remove the temporary file.
            os.unlink(outfile.name)

    return result_path


def make_video(images, output_path, fps=0.5, size=(640, 480), is_color=True):
    """
    Create a video from a list of images.
    """

    fourcc = VideoWriter_fourcc(*"XVID")
    vid = VideoWriter(output_path, fourcc, fps, size, is_color)
    for image in images:
        img = imread(image)
        vid.write(img)
    vid.release()
    return


def cleanup_tempfile(file_list):
    """
    Cleanup temporary files.
    """
    for item in file_list:
        os.unlink(item)

    return


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Make street view video out from directions.')
    parser.add_argument('source', help='Source address')
    parser.add_argument('destination', help='Destination address')
    parser.add_argument('output', help='The video file path')

    args = parser.parse_args()

    directions = fetch_directions(args.source, args.destination)
    image_path_list = fetch_streetview_images(directions)
    video = make_video(image_path_list, args.output)

    cleanup_tempfile(image_path_list)
