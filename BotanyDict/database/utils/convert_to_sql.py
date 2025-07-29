from collections import deque, defaultdict

def parse_division(file_path):
    """
    Parse division.dmp file into a dictionary.
    Key: division_id (int)
    Value: tuple(code, name, comment) all strings
    """
    divisions = {}
    with open(file_path, 'r') as f:
        for line in f:
            parts = line.strip().split('\t|\t')
            division_id = int(parts[0])
            code = parts[1].strip()
            name = parts[2].strip()
            comment = parts[3].strip()
            divisions[division_id] = (code, name, comment)
    return divisions

def parse_nodes_with_division(file_path):
    """
    Parse nodes.dmp file into a dictionary.
    Key: tax_id (int)
    Value: tuple(parent_id (int), rank (str), division_id (int))
    """
    nodes = {}
    with open(file_path, 'r') as f:
        for line in f:
            parts = line.strip().split('\t|\t')
            tax_id = int(parts[0])
            parent_id = int(parts[1])
            rank = parts[2].strip()
            division_id = int(parts[4])
            nodes[tax_id] = (parent_id, rank, division_id)
    return nodes

def get_descendants(nodes, root=3193):
    """
    Given the entire nodes dict, find all descendant tax_ids under Plantae.
    Uses BFS with a child map for efficient traversal.
    Returns a set of tax_ids including root.
    """
    # Build a parent to children mapping for fast lookup
    children_map = defaultdict(list)
    for tax_id, (parent_id, _, _) in nodes.items():
        children_map[parent_id].append(tax_id)

    taxids = set()
    queue = deque([root])

    while queue:
        current = queue.popleft()
        taxids.add(current)
        for child in children_map.get(current, []):
            if child not in taxids:
                queue.append(child)

    return taxids

def parse_names(file_path, taxid_filter):
    """
    Parse names.dmp file to extract scientific names for tax_ids in taxid_filter.
    Returns dict {tax_id: scientific_name}
    """
    names = {}
    with open(file_path, 'r') as f:
        for line in f:
            parts = line.strip().split('\t|\t')
            tax_id = int(parts[0])
            name_txt = parts[1].strip()
            name_class = parts[3].strip()
            if tax_id in taxid_filter and name_class == 'scientific name':
                names[tax_id] = name_txt
    return names

def export_sql_with_division(nodes, names, taxids, divisions, output_file):
    """
    Export SQL schema and insert statements for division, taxon, and taxon_name tables.
    Only includes taxa under Plantae.
    """
    with open(output_file, 'w') as f:
        # Create division table and insert divisions
        f.write('CREATE TABLE division (\n')
        f.write('  division_id INTEGER PRIMARY KEY,\n')
        f.write('  division_code TEXT,\n')
        f.write('  division_name TEXT,\n')
        f.write('  comments TEXT\n')
        f.write(');\n\n')
        for div_id, (code, name, comment) in divisions.items():
            f.write(f"INSERT INTO division VALUES ({div_id}, '{code}', '{name}', '{comment}');\n")

        f.write('\n')

        # Create taxon and taxon_name tables
        f.write('CREATE TABLE taxon (\n')
        f.write('  tax_id INTEGER PRIMARY KEY,\n')
        f.write('  parent_tax_id INTEGER,\n')
        f.write('  rank TEXT,\n')
        f.write('  division_id INTEGER\n')
        f.write(');\n\n')

        f.write('CREATE TABLE taxon_name (\n')
        f.write('  tax_id INTEGER,\n')
        f.write('  name TEXT,\n')
        f.write('  UNIQUE(tax_id, name)\n')
        f.write(');\n\n')

        # Insert taxa in Plantae subtree
        for tax_id in sorted(taxids):
            parent_id, rank, division_id = nodes[tax_id]
            # Escape single quotes in rank if any
            rank_sql = rank.replace("'", "''")
            f.write(f"INSERT INTO taxon VALUES ({tax_id}, {parent_id}, '{rank_sql}', {division_id});\n")

        f.write('\n')

        # Insert scientific names
        for tax_id, name in names.items():
            name_sql = name.replace("'", "''")  # Escape single quotes
            f.write(f"INSERT INTO taxon_name VALUES ({tax_id}, '{name_sql}');\n")

if __name__ == '__main__':
    # File paths - adjust if needed
    division_file = 'division.dmp'
    nodes_file = 'nodes.dmp'
    names_file = 'names.dmp'
    output_sql_file = 'taxonomy.sql'

    # Parse input files
    divisions = parse_division(division_file)
    nodes = parse_nodes_with_division(nodes_file)

    # Extract Plantae subtree tax_ids efficiently
    taxids = get_descendants(nodes)

    # Parse names only for Plantae taxa
    names = parse_names(names_file, taxids)

    # Export to SQL file
    export_sql_with_division(nodes, names, taxids, divisions, output_sql_file)

    print(f"SQL export complete: {output_sql_file}")

