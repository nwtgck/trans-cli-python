#! /usr/bin/env python

import argparse
import os.path
import urllib.request
import urllib.parse
import urllib.error
import mmap
import sys
import os
import json
import re
import pkg_resources

DEFAULT_SERVER_URL = "https://trans-akka.herokuapp.com"
CONFIG_DIR_NAME    = "trans-cli-python"
CONFIG_FILE_NAME   = "config.json"
VERSION            = pkg_resources.require("trans-cli")[0].version # (from: https://stackoverflow.com/a/2073599/2885946)


def write_server_url(new_server_url):
  with open(trans_config_file_path, 'w') as f:
    json.dump({
      "server_url": new_server_url,
    }, f)

def is_valid_url(url):
  # (from: https://stackoverflow.com/a/7160778/2885946)
  regex = re.compile(
    r'^(?:http|ftp)s?://'  # http:// or https://
    r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain...
    r'localhost|'  # localhost...
    r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
    r'(?::\d+)?'  # optional port
    r'(?:/?|[/?]\S+)$', re.IGNORECASE)
  return regex.match(url)

# "~/.config"
config_dir_path = os.path.join(os.environ['HOME'], ".config")
# If "~/.config" doesn't exist
if not os.path.exists(config_dir_path):
  # Make ~/.config
  os.mkdir(config_dir_path)


# "~/.config/<CONFIG_DIR_NAME>/"
trans_config_dir_path = os.path.join(config_dir_path, CONFIG_DIR_NAME)
# If "~/.config/<CONFIG_DIR_NAME>/" doesn't exist
if not os.path.exists(trans_config_dir_path):
  # Make "~/.config/<CONFIG_DIR_NAME>/"
  os.mkdir(trans_config_dir_path)


# "~/.config/<CONFIG_DIR_NAME>/<CONFIG_FILE_NAME>"
trans_config_file_path = os.path.join(trans_config_dir_path, CONFIG_FILE_NAME)
# If "~/.config/<CONFIG_DIR_NAME>/<CONFIG_FILE_NAME>" doesn't exist
if not os.path.exists(trans_config_file_path):
  # Write default setting
  write_server_url(DEFAULT_SERVER_URL)

# Load SERVER_URL from config
with open(trans_config_file_path, 'r') as f:
  config = json.load(f)
  SERVER_URL = config["server_url"]

  if not is_valid_url(SERVER_URL):
    print("Server URL (='%s') is NOT valid in '%s'" % (SERVER_URL, trans_config_file_path), file=sys.stderr)
    exit(1)


def joined_query_to_url(base_url, params_dict):
  """
  Join URL and GET parameters
  :param base_url:
  :param params_dict:
  :return:
  """

  # Generate GET params string
  get_params_str = urllib.parse.urlencode({k: v for k, v in params_dict.items() if v is not None})

  # Generate URL with GET params
  pase_result = urllib.parse.urlparse(base_url)
  url = urllib.parse.ParseResult(
    scheme   = pase_result.scheme,
    netloc   = pase_result.netloc,
    path     = pase_result.path,
    query    = get_params_str,
    params   = pase_result.params,
    fragment = pase_result.fragment
  ).geturl()
  return url

def help_command(args):
  print(args.parser.parse_args([args.command, '--help']))


# (from: https://stackoverflow.com/a/2504133/2885946)
def send_command(args):

  for file_path in args.file_paths:
    with open(file_path, "rb") as f, mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ) as mmaped_file:

      try:
        # Generate URL with GET params
        url = joined_query_to_url(SERVER_URL, {
          'duration'   : args.duration,
          'get-times'  : args.get_times,
          'id-length'  : args.id_length,
          'deletable'  : args.deletable,
          'delete-key' : args.delete_key
        })

        # Send file
        req = urllib.request.Request(url, mmaped_file)
        req.add_header("Content-Length", os.path.getsize(file_path))
        res = urllib.request.urlopen(req)

        # Get File ID
        file_id = res.read().decode('utf-8').rstrip()
        # Print File ID
        print(file_id)

      except urllib.error.URLError as e:
        print("'%s': '%s'" % (file_path, e))



def get_command(args):
  for file_id in args.file_ids:
    try:
      # Get the file
      url = urllib.parse.urljoin(SERVER_URL, file_id)
      req = urllib.request.Request(url)
      res = urllib.request.urlopen(req)

      if args.stdout:
        # Write to stdout
        sys.stdout.buffer.write(res.read()) # (from: https://stackoverflow.com/a/908440/2885946)
      else:
        # Save file content to a file
        with open(file_id, "wb") as outf:
          outf.write(res.read())
          print("'%s' is saved!" % file_id)

    except urllib.error.URLError as e:
      print("'%s': '%s'" % (file_id, e))

def delete_command(args):
  for file_id in args.file_ids:
    try:
      # Generate URL with GET params
      url = joined_query_to_url(urllib.parse.urljoin(SERVER_URL, file_id), {
        "delete-key": args.delete_key
      })
      # Delete the file
      req = urllib.request.Request(url)
      req.get_method = lambda: "DELETE"  # (from: https://stackoverflow.com/a/4511785/2885946)
      res = urllib.request.urlopen(req)

      server_res = res.read().decode('utf-8').rstrip()
      print("'%s': '%s'" % (file_id, server_res))
    except urllib.error.HTTPError as e:
      print("'%s': '%s'" % (file_id, e))


def server_url_command(args):
  if args.show:
    print(SERVER_URL)
  else:
    new_server_url = args.server_url
    if not is_valid_url(new_server_url):
      print("Server URL, '%s' is NOT valid" % (new_server_url), file=sys.stderr)
      exit(1)
    write_server_url(new_server_url)
    print("'%s' set" % (new_server_url))

def main():
  # (from: https://qiita.com/oohira/items/308bbd33a77200a35a3d)
  parser     = argparse.ArgumentParser(description="CLI for trans (version: %s)" % (VERSION))
  subparsers = parser.add_subparsers()

  parser.add_argument("-v", "--version", action="store_true")

  # "help" parser
  parser_help = subparsers.add_parser('help', help='see `help -h`')
  parser_help.add_argument('command', help='command name which help is shown')
  parser_help.set_defaults(handler=help_command, parser=parser)

  # "send" parser
  send_parser = subparsers.add_parser('send', help="send files")
  send_parser.add_argument('--duration',   help='Store duration')
  send_parser.add_argument('--get-times',  help='Download limit')
  send_parser.add_argument('--id-length',  help='Length of ID')
  send_parser.add_argument('--deletable',  help='File is deletable or not')
  send_parser.add_argument('--delete-key', help='Key for delete')
  send_parser.add_argument('file_paths', nargs='*', help="File paths you want to send") # (from: https://stackoverflow.com/a/22850525/2885946)
  send_parser.set_defaults(handler=send_command)

  # "get" parser
  send_parser = subparsers.add_parser('get', help="get files")
  send_parser.add_argument('--stdout', action="store_true", help="Output to stdout")
  send_parser.add_argument('file_ids', nargs='*', help="File IDs you want to get")  # (from: https://stackoverflow.com/a/22850525/2885946)
  send_parser.set_defaults(handler=get_command)

  # "delete" parser
  send_parser = subparsers.add_parser('delete', help="delete a file")
  send_parser.add_argument('--delete-key', help='Key for delete')
  send_parser.add_argument('file_ids', nargs='*', help="File IDs you want to delete")  # (from: https://stackoverflow.com/a/22850525/2885946)
  send_parser.set_defaults(handler=delete_command)

  # "server-url" parser
  send_parser = subparsers.add_parser('server-url', help="set server URL")
  send_parser.add_argument('--show', action="store_true", help='Show current server URL')
  send_parser.add_argument('server_url', nargs='?', help="Server URL you want to set")  # (from: https://stackoverflow.com/a/22850525/2885946)
  send_parser.set_defaults(handler=server_url_command)


  # Parse arguments
  args = parser.parse_args()

  if args.version:
    # Show version
    print("trans-cli (python) version %s" % VERSION)
  # If it's known command
  elif hasattr(args, 'handler'):
    # Handle command
    args.handler(args)
  else:
    # Show help
    parser.print_help()

if __name__ == '__main__':
    main()