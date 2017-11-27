#! /usr/bin/env python3

import os.path
import urllib.request
import mmap

url   = "http://localhost:8181"      # TODO Hard cored
fpath = "/Users/Ryo/Downloads/0.png" # TODO Hard corded
with open(fpath, "rb") as f, mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ) as mmaped_file_as_str:
  # Send file
  req = urllib.request.Request(url, mmaped_file_as_str)
  req.add_header("Content-Length", os.path.getsize(fpath))
  res = urllib.request.urlopen(req)

  # Get File ID
  file_id = res.read().decode('utf-8').rstrip()

  print(file_id)
