from pytest import fixture, mark
import pkg_resources
from nchelpers import CFDataset

class arguments():
    def __init__(self):
        self.group_by = None
        self.top = None
        self.min = None
        self.max = None
        self.mean = None
        self.sum = None
        self.count = False
        self.limit_to = None


    def parser_mocker(self, command):
        key_value_pair = command.split(": ")
        args = key_value_pair[-1].split("\n")[0].split(" ")
        
        for idx, arg in enumerate(args):
            if arg[:2] == "--":
                if arg[2:] == "input":
                    self.input = pkg_resources.resource_filename("tests","data/input.csv")
                if arg[2:] == "group-by":
                    self.group_by = args[idx+1]
                if arg[2:] == "top":
                    self.top = (args[idx+1], args[idx+2])
                if arg[2:] == "min":
                    if self.min == None:
                        self.min = []
                    self.min.append(args[idx+1])  
                if arg[2:] == "max":
                    if self.max == None:
                        self.max = []
                    self.max.append(args[idx+1])  
                if arg[2:] == "mean":
                    if self.mean == None:
                        self.mean = []
                    self.mean.append(args[idx+1])    
                if arg[2:] == "sum":
                    if self.sum == None:
                        self.sum = []
                    self.sum.append(args[idx+1])
                if arg[2:] == "count":
                    self.count = True
                if arg[2:] == "limit-to":
                    self.limit_to = int(args[idx+1])

@fixture
def test_args(request):
    command_log = pkg_resources.resource_filename("tests","data/command.log")
    with open(command_log, "r") as commands:
        for cmd in commands:
            key_value_pair = cmd.split(": ")
            if key_value_pair[0] == request.param:
                args = arguments()
                args.parser_mocker(cmd)
                return args

@fixture
def expected_output(request):
    expected_output_csv = pkg_resources.resource_filename("tests","data/{}/output.csv".format(request.param))
    with open(expected_output_csv, "r") as csv:
        return csv.read()

@fixture
def expected_error(request):
    expected_error_log = pkg_resources.resource_filename("tests","data/{}/error.log".format(request.param))
    with open(expected_error_log, "r") as err:
        return err.read()
