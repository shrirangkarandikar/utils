import nbformat as nbf
import re
import argparse
import os

def markdown_to_notebook(md_filepath):
    """
    Converts a Markdown file with Python code blocks to an IPython Notebook.

    Markdown text becomes Markdown cells.
    Python code blocks (```python ... ```) become Code cells.

    Args:
        md_filepath (str): The path to the input Markdown file.

    Returns:
        str: The path to the generated IPython Notebook file,
             or None if conversion failed.
    """
    if not os.path.exists(md_filepath):
        print(f"Error: File not found at {md_filepath}")
        return None

    # Determine output filename
    base_name = os.path.splitext(md_filepath)[0]
    ipynb_filepath = base_name + ".ipynb"

    print(f"Converting '{md_filepath}' to '{ipynb_filepath}'...")

    # Create a new notebook object
    nb = nbf.v4.new_notebook()

    try:
        with open(md_filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except Exception as e:
        print(f"Error reading file {md_filepath}: {e}")
        return None

    cells = []
    current_cell_lines = []
    in_code_block = False
    is_python_block = False

    # Regex to detect start of specifically Python code blocks
    python_block_start_pattern = re.compile(r"^```python\s*$", re.IGNORECASE)
    # Regex to detect start of any code block
    any_block_start_pattern = re.compile(r"^```.*$")
    # Regex to detect end of any code block
    block_end_pattern = re.compile(r"^```\s*$")

    for line in lines:
        is_start_python = python_block_start_pattern.match(line)
        is_end = block_end_pattern.match(line)
        is_start_any = any_block_start_pattern.match(line)

        if not in_code_block:
            if is_start_python:
                # Finish previous markdown cell if any
                if current_cell_lines:
                    # Join lines, removing trailing newline from the last line
                    md_source = "".join(current_cell_lines).rstrip('\n')
                    cells.append(nbf.v4.new_markdown_cell(md_source))
                    current_cell_lines = []
                # Start a new python code block
                in_code_block = True
                is_python_block = True
            elif is_start_any:
                 # Finish previous markdown cell if any
                if current_cell_lines:
                    md_source = "".join(current_cell_lines).rstrip('\n')
                    cells.append(nbf.v4.new_markdown_cell(md_source))
                    current_cell_lines = []
                # Start a non-python code block (treat as markdown for now)
                in_code_block = True
                is_python_block = False
                current_cell_lines.append(line) # Keep the fence for non-python blocks
            else:
                # Continue current markdown cell
                current_cell_lines.append(line)
        else: # Inside a code block
            if is_end:
                # Finish the current code block
                if is_python_block:
                    # Join lines, removing trailing newline from the last line
                    code_source = "".join(current_cell_lines).rstrip('\n')
                    cells.append(nbf.v4.new_code_cell(code_source))
                else:
                    # Treat non-python block as markdown
                    current_cell_lines.append(line) # Keep the closing fence
                    md_source = "".join(current_cell_lines).rstrip('\n')
                    cells.append(nbf.v4.new_markdown_cell(md_source))

                # Reset state
                current_cell_lines = []
                in_code_block = False
                is_python_block = False
            else:
                # Continue current code/markdown block
                 current_cell_lines.append(line)

    # Add any remaining markdown content as a final cell
    if current_cell_lines and not in_code_block:
        md_source = "".join(current_cell_lines).rstrip('\n')
        cells.append(nbf.v4.new_markdown_cell(md_source))
    elif current_cell_lines and in_code_block:
         # If the file ends mid-code block, treat it as code if python, else md
         print("Warning: File ended while inside a code block. Treating as cell content.")
         if is_python_block:
             code_source = "".join(current_cell_lines).rstrip('\n')
             cells.append(nbf.v4.new_code_cell(code_source))
         else: # Treat non-python block as markdown
             md_source = "".join(current_cell_lines).rstrip('\n')
             cells.append(nbf.v4.new_markdown_cell(md_source))


    nb['cells'] = cells

    try:
        with open(ipynb_filepath, 'w', encoding='utf-8') as f:
            nbf.write(nb, f)
        print(f"Successfully saved notebook to '{ipynb_filepath}'")
        return ipynb_filepath
    except Exception as e:
        print(f"Error writing notebook file {ipynb_filepath}: {e}")
        return None

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert a Markdown file with Python code blocks to an IPython Notebook.")
    parser.add_argument("markdown_file", help="Path to the input Markdown file (.md)")
    args = parser.parse_args()

    if not args.markdown_file.lower().endswith(".md"):
        print("Warning: Input file does not have a .md extension.")

    markdown_to_notebook(args.markdown_file)
