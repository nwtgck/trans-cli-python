#! /usr/bin/env python

import argparse
import os.path
import urllib.request
import urllib.parse
import urllib.error
import mmap
import sys

SERVER_URL = "http://localhost:8181" # TODO Hard corded

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


def main():
  # (from: https://qiita.com/oohira/items/308bbd33a77200a35a3d)
  parser     = argparse.ArgumentParser(description="CLI for trans")
  subparsers = parser.add_subparsers()

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


  # Parse arguments
  args = parser.parse_args()

  # If it's known command
  if hasattr(args, 'handler'):
    # Handle command
    args.handler(args)
  else:
    # Show help
    parser.print_help()

if __name__ == '__main__':
    main()