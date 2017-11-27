#! /usr/bin/env python

import argparse

def help_command(args):
  print(args.parser.parse_args([args.command, '--help']))

def send_command(args):
  print(args)
  # TODO impl

def get_command(args):
  print(args)
  # TODO impl

def delete_command(args):
  print(args)
  # TODO impl

def main():
  # (from: https://qiita.com/oohira/items/308bbd33a77200a35a3d)
  parser     = argparse.ArgumentParser(description="Client for trans")
  subparsers = parser.add_subparsers()

  # "help" parser
  parser_help = subparsers.add_parser('help', help='see `help -h`')
  parser_help.add_argument('command', help='command name which help is shown')
  parser_help.set_defaults(handler=help_command, parser=parser)

  # "send" parser
  send_parser = subparsers.add_parser('send', help="send a file")
  send_parser.add_argument('--duration',   help='Store duration')
  send_parser.add_argument('--get-times',  help='Download limit')
  send_parser.add_argument('--id-length',  help='Length of ID')
  send_parser.add_argument('--deletable',  help='File is deletable or not')
  send_parser.add_argument('--delete-key', help='Key for delete')
  send_parser.add_argument('file_path', nargs='*', help="File paths you want to send") # (from: https://stackoverflow.com/a/22850525/2885946)
  send_parser.set_defaults(handler=send_command)

  # "get" parser
  send_parser = subparsers.add_parser('get', help="get a file")
  send_parser.add_argument('file_id', nargs='*', help="File IDs you want to get")  # (from: https://stackoverflow.com/a/22850525/2885946)
  send_parser.set_defaults(handler=get_command)

  # "delete" parser
  send_parser = subparsers.add_parser('delete', help="delete a file")
  send_parser.add_argument('--delete-key', help='Key for delete')
  send_parser.add_argument('file_id', nargs='*', help="File IDs you want to delete")  # (from: https://stackoverflow.com/a/22850525/2885946)
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