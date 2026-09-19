import argparse
import sys

def init_env(args):
    print("Initializing environment...")

def run_tests(args):
    import pytest
    pytest.main(["tests/"])

def main():
    parser = argparse.ArgumentParser(description="PRAMAAN CLI")
    subparsers = parser.add_subparsers(dest="command")
    
    parser_init = subparsers.add_parser("init")
    parser_init.set_defaults(func=init_env)
    
    parser_test = subparsers.add_parser("run-tests")
    parser_test.set_defaults(func=run_tests)
    
    args = parser.parse_args()
    if args.command:
        args.func(args)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
