import argparse
import json
import sys

from pydantic import ValidationError

from .data_model import DataObjectJSON


parser = argparse.ArgumentParser(description='Call_Me_Maybe')
parser.add_argument('--functions_definition', type=int)
parser.add_argument('--input',  type=int)
parser.add_argument('--output', type=str)
