import ast

def extract_signatures(tree):
    # Helper to extract class/function signatures from AST
    signatures = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            args = [arg.arg for arg in node.args.args]
            signatures.append(f"def {node.name}({', '.join(args)})")
        elif isinstance(node, ast.ClassDef):
            signatures.append(f"class {node.name}")
    return ", ".join(signatures)

def generate_repo_map(file_tree: dict):
    # Traverse files, extract signatures
    # file_tree is expected to be {path: content}
    map_str = ""
    for file, content in file_tree.items():
        if file.endswith('.py'):
            try:
                tree = ast.parse(content)
                map_str += f"{file}: {extract_signatures(tree)}\n"
            except:
                map_str += f"{file}: (parse error)\n"
        else:
            map_str += f"{file}\n"
    return map_str
