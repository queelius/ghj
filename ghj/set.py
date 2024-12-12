import json
import argparse

def load_json(file):
    with open(file) as f:
        return json.load(f)

def save_json(data, file):
    with open(file, 'w') as f:
        json.dump(data, f, indent=2)

def main():
    parser = argparse.ArgumentParser(description='Set operations on GitHub repo JSON data.')
    parser.add_argument('operation', choices=['or', 'and', 'diff'], help='Set operation to perform')
    parser.add_argument('input_files', nargs='+', help='Input JSON files')
    parser.add_argument('-o', '--output', default='output.json', help='Output file')
    args = parser.parse_args()

    sets = []
    for file in args.input_files:
        data = load_json(file)
        repo_ids = {repo['id']: repo for repo in data}
        sets.append(repo_ids)

    if args.operation == 'or':
        result = {}
        for s in sets:
            result.update(s)
        data = list(result.values())
    elif args.operation == 'and':
        common_ids = set(sets[0]).intersection(*sets[1:])
        data = [sets[0][repo_id] for repo_id in common_ids]
    elif args.operation == 'diff':
        result = sets[0]
        for s in sets[1:]:
            for repo_id in s:
                result.pop(repo_id, None)
        data = list(result.values())

    save_json(data, args.output)

if __name__ == '__main__':
    main()