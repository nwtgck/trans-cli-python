# CLI for trans in Python

Command Line Interface for [trans server](https://github.com/nwtgck/trans-server-akka)

| branch | Travis status|
| --- | --- |
| [`master`](https://github.com/nwtgck/trans-cli-python/tree/master) | [![Build Status](https://travis-ci.org/nwtgck/trans-cli-python.svg?branch=master)](https://travis-ci.org/nwtgck/trans-cli-python) |
| [`develop`](https://github.com/nwtgck/trans-cli-python/tree/develop) | [![Build Status](https://travis-ci.org/nwtgck/trans-cli-python.svg?branch=develop)](https://travis-ci.org/nwtgck/trans-cli-python) |

## Installation

You can install `tran-cli` command by `pip`

```bash
pip3 install git+https://github.com/nwtgck/trans-cli-python
```

Then you can use `trans-cli` command.

## Basic usages

```bash
# Send a file
trans-cli send ~/Documents/hello.txt
```

```bash
# Get a file
trans-cli get d84
```
(File ID, `d84` is save as `d84` file in `$PWD`)

```bash
# Get a file
trans-cli delete d84
```

## Advanced usages

### Send

```bash
# Send a file with 30-second-store-duration
trans-cli send --duration=30s ~/Documents/hello.txt
```

```bash
# Send a file with download-once limit
trans-cli send --get-times=1 ~/Documents/hello.txt
```

```bash
# Send a file with delete-key
trans-cli send --delete-key=mydeletekey123 ~/Documents/hello.txt
```

```bash
# Send a file with longer id-length
trans-cli send --id-length=16 ~/Documents/hello.txt
```

You can get more information by `trans-cli send -h`


### Get 

```bash
# Get a file content in stdout and redirect to `my.txt`
trans-cli get --stdout d84 > my.txt
```

You can get more information by `trans-cli get -h`


## Delete


```bash
# Delete a file with delete-key
trans-cli delete --delete-key=mydeletekey123 d31
```

You can get more information by `trans-cli delete -h`
