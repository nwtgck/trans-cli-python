# (from: http://developer.wonderpla.net/entry/blog/engineer/python_cli_tool_implementation_and_distribution/)

from setuptools import setup, find_packages

setup(
  name='trans-cli',
  version='1.0-SNAPSHOT',
  packages=find_packages(),
  install_requires=[],
  entry_points={
    'console_scripts':
      'trans-cli = trans_cli.main:main'
  },
  zip_safe=False,
  classifiers=[
    'Environment :: Console',
    'Intended Audience :: Developers',
    'Programming Language :: Python',
  ]
)