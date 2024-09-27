import yaml
import os
import re
import argparse
import pandas as pd


def extract_frontmatter(content: str):
    yaml_delimeter = "---"
    if not content.startswith(yaml_delimeter):
        return None, content

    end = content.find(yaml_delimeter, len(yaml_delimeter))
    if end == -1:
        raise SyntaxError("Could not find end YAML delimeter.")

    return yaml.safe_load(content[len(yaml_delimeter):end]), content[end + len(yaml_delimeter):].strip()


def extract_headers(content: str):
    sections = {}

    matches = re.findall(r'(## .+)\n([\s\S]*?)(?=\n## |\Z)', content)

    for match in matches:
        header = match[0].strip().replace('## ', '').strip()
        body = match[1].strip()
        sections[header] = body

    return sections


def parse_frontmatter(frontmatter: dict):
    if not frontmatter:
        return {}

    frontmatter = {
        'authors': frontmatter.get('authors', None),
        'conference': frontmatter.get('conference', None),
        'tldr': frontmatter.get('tldr', None),
        'abstract': frontmatter.get('abstract', None),
    }

    if frontmatter['authors']:
        frontmatter['authors'] = ",".join(frontmatter['authors']).strip()

    if frontmatter['conference']:
        frontmatter['conference'] = frontmatter['conference'].strip()

    if frontmatter['tldr']:
        frontmatter['tldr'] = frontmatter['tldr'].strip()

    if frontmatter['abstract']:
        frontmatter['abstract'] = frontmatter['abstract'].strip()

    return frontmatter


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('input', help='Input directory')
    parser.add_argument('--ignore', help='Ignore files', nargs='*', default=[])
    args = parser.parse_args()

    filenames = os.listdir(args.input)
    filenames = filter(lambda x: x.endswith('.md'), filenames)
    filenames = filter(lambda x: os.path.join(args.input, x) not in args.ignore, filenames)

    rows = []

    for filename in filenames:
        filepath = os.path.join(args.input, filename)
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        title = filename.replace('.md', '')
        frontmatter, content = extract_frontmatter(content)
        sections = extract_headers(content)

        frontmatter_parsed = parse_frontmatter(frontmatter)

        row = pd.DataFrame([{'paper': title, **frontmatter_parsed, **sections}])
        rows.append(row)

    df = pd.concat(rows)
    df.to_csv("output.csv", index=False)
