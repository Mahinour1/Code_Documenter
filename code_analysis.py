
def read_python_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return content
    except FileNotFoundError:
        print(f"File not found: {file_path}")
        raise
    except IOError as e:
        print(f"Error reading file {file_path}: {str(e)}")
        raise
    except Exception as e:
        print(f"Unexpected error reading file {file_path}: {str(e)}")
        raise

def extract_imports(code, file_path):
    try:
            
        # Split into lines and find imports
        import_lines = []
        for line in code.split('\n'):
            line = line.strip()
            if line.startswith('import ') or line.startswith('from '):
                import_lines.append(line)
                
        return import_lines
        
    except Exception as e:
        print(f"Error extracting imports from file {file_path}: {str(e)}")
        return []