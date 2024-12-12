import json
import argparse
import jmespath
import sys

def main():
    parser = argparse.ArgumentParser(description='Filter GitHub repo JSON data using JMESPath.')
    parser.add_argument('input_file', nargs='?', default='-', help='Input JSON file (default: stdin)')
    parser.add_argument('query', help='JMESPath query string')
    args = parser.parse_args()

    if args.input_file == '-':
        repos = json.load(sys.stdin)
    else:
        with open(args.input_file) as f:
            repos = json.load(f)

    results = []
    for repo in repos:
        result = jmespath.search(args.query, repo)
        if result:
            results.append(repo)
            
    json.dump(results, sys.stdout, indent=2)

if __name__ == '__main__':
    main()