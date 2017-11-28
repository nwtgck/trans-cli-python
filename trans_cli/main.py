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
import itertools

DEFAULT_SERVER_URL     = "https://trans-akka.herokuapp.com"
CONFIG_DIR_NAME        = "trans-cli-python"
CONFIG_FILE_NAME       = "config.json"
VERSION                = pkg_resources.require("trans-cli")[0].version # (from: https://stackoverflow.com/a/2073599/2885946)
# "~/.config"
CONFIG_DIR_PATH        = os.path.join(os.environ['HOME'], ".config")
# "~/.config/<CONFIG_DIR_NAME>/"
TRANS_CONFIG_DIR_PATH  = os.path.join(CONFIG_DIR_PATH, CONFIG_DIR_NAME)
# "~/.config/<CONFIG_DIR_NAME>/<CONFIG_FILE_NAME>"
TRANS_CONFIG_FILE_PATH = os.path.join(TRANS_CONFIG_DIR_PATH, CONFIG_FILE_NAME)
SERVER_URL             = None # NOTE: This will be stored by init()

def overwrite_config(sub_config_creator):
  with open(TRANS_CONFIG_FILE_PATH, 'r') as f:
    config = json.load(f)

    # Overwrite sub config to config
    for key,value_creator in sub_config_creator.items():
      config[key] = value_creator(config.get(key))

    # Write config file again
    with open(TRANS_CONFIG_FILE_PATH, 'w') as f:
      json.dump(config, f, sort_keys=True, indent=2)

def write_server_url(new_server_url):
  if is_valid_url(new_server_url):
    overwrite_config({
      "server_url": lambda prev: new_server_url
    })
  else:
    print("Server URL is NOT valid: '%s'" % new_server_url, file=sys.stderr)
    exit(1)

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

def init():
  global SERVER_URL

  # If "~/.config" doesn't exist
  if not os.path.exists(CONFIG_DIR_PATH):
    # Make ~/.config
    os.mkdir(CONFIG_DIR_PATH)

  # If "~/.config/<CONFIG_DIR_NAME>/" doesn't exist
  if not os.path.exists(TRANS_CONFIG_DIR_PATH):
    # Make "~/.config/<CONFIG_DIR_NAME>/"
    os.mkdir(TRANS_CONFIG_DIR_PATH)


  # If "~/.config/<CONFIG_DIR_NAME>/<CONFIG_FILE_NAME>" doesn't exist
  if not os.path.exists(TRANS_CONFIG_FILE_PATH):
    # Write empty setting
    with open(TRANS_CONFIG_FILE_PATH, 'w') as f:
      json.dump({}, f)

    # Write default setting
    write_server_url(DEFAULT_SERVER_URL)

    # Set default server aliases
    overwrite_config({
      "server_aliases": lambda prev: [
        {"name": "local80",   "url": "http://localhost"},
        {"name": "local8080", "url": "http://localhost:8080"},
        {"name": "local8181", "url": "http://localhost:8181"},
        {"name": "heroku",    "url": "https://trans-akka.herokuapp.com"}
      ]
    })

  # Load SERVER_URL from config
  with open(TRANS_CONFIG_FILE_PATH, 'r') as f:
    config = json.load(f)
    SERVER_URL = config["server_url"]

    if not is_valid_url(SERVER_URL):
      print("Server URL (='%s') is NOT valid in '%s'" % (SERVER_URL, TRANS_CONFIG_FILE_PATH), file=sys.stderr)
      exit(1)


def joined_query_to_url(base_url, params_dict):
  """
  Join URL and GET parameters
  :param base_url:
  :param params_dict:
  :return:
  """

  def v_mapper(v):
    if type(v) == bool:
      return "true" if v else "false"
    else:
      return v


  # Generate GET params string
  get_params_str = urllib.parse.urlencode({k: v_mapper(v) for k, v in params_dict.items() if v is not None})

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

def config_command(args):
  if args.list:
    with open(TRANS_CONFIG_FILE_PATH, 'r') as f:
      # Show config
      config_str = f.read()
      print(config_str)
  elif args.store_path:
    # Show store-path of config
    print(TRANS_CONFIG_FILE_PATH)
  elif args.server:
    server = args.server
    if is_valid_url(server):
      new_url = server
    else:
      with open(TRANS_CONFIG_FILE_PATH, 'r') as f:
        config = json.load(f)
        server_aliases = config.get("server_aliases")
        if server_aliases is None:
          print("Error: server_aliases is missing in config", file=sys.stderr)
          exit(1)
        found_alias = next(filter(lambda x: x["name"] == server, server_aliases), None)
        new_url = found_alias.get("url")
    # Set new server URL
    write_server_url(new_url)
    print("'%s' set" % (new_url))
  else:
    pass


def main():

  # Initialize config if need and get SERVER URL
  init()

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
  send_parser.add_argument('--duration',   help='Store duration (e.g. 10s, 5m, 12h, 3d)')
  send_parser.add_argument('--get-times',  help='Download limit (e.g. 1, 10)')
  send_parser.add_argument('--id-length',  help='Length of ID (e.g. 1, 3, 10)')
  send_parser.add_argument('--deletable',  action="store_true", help='Whether file is deletable or not')
  send_parser.add_argument('--delete-key', help='Key for delete')
  send_parser.add_argument('file_paths', nargs='*', help="File paths you want to send") # (from: https://stackoverflow.com/a/22850525/2885946)
  send_parser.set_defaults(handler=send_command)

  # "get" parser
  get_parser = subparsers.add_parser('get', help="get files")
  get_parser.add_argument('--stdout', action="store_true", help="Output to stdout")
  get_parser.add_argument('file_ids', nargs='*', help="File IDs you want to get")  # (from: https://stackoverflow.com/a/22850525/2885946)
  get_parser.set_defaults(handler=get_command)

  # "delete" parser
  delete_parser = subparsers.add_parser('delete', help="delete a file")
  delete_parser.add_argument('--delete-key', help='Key for delete')
  delete_parser.add_argument('file_ids', nargs='*', help="File IDs you want to delete")  # (from: https://stackoverflow.com/a/22850525/2885946)
  delete_parser.set_defaults(handler=delete_command)

  # "config" parser
  config_parser = subparsers.add_parser('config', help="set server URL or show config")
  config_parser.add_argument('--list', action="store_true", help='Show current config')
  config_parser.add_argument('--store-path', action="store_true", help='Show store path')
  config_parser.add_argument('--server',    help="Server URL you want to set")
  config_parser.set_defaults(handler=config_command)


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