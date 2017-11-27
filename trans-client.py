#! /usr/bin/env python3

import os.path
import urllib.request
import mmap
import urllib.parse

server_url   = "http://localhost:8181"      # TODO Hard cored
fpath = "/Users/Ryo/Downloads/CLion-2017.2.3.dmg" # TODO Hard corded
with open(fpath, "rb") as f, mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ) as mmaped_file_as_str:

  # ========== Send =========

  print("Making a request...")
  # Send file
  req = urllib.request.Request(server_url, mmaped_file_as_str)
  req.add_header("Content-Length", os.path.getsize(fpath))
  print("Sending...")
  res = urllib.request.urlopen(req)

  # Get File ID
  file_id = res.read().decode('utf-8').rstrip()

  print(file_id)



  # ========== GET =========

  # Get file
  url = urllib.parse.urljoin(server_url, file_id)
  print("url:", url)
  req = urllib.request.Request(url)
  print("Getting...")
  res = urllib.request.urlopen(req)

  print(type(res))

  # Get File content

  with open(file_id, "wb") as outf:
    outf.write(res.read())
