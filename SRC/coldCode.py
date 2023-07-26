import clang.cindex
import sys

def parse_coverage_data(coverage_data):
    line_coverage = {}
    for line in coverage_data.splitlines():
        if ':' in line:
            execution_count, line_number, _ = line.split(':', 2)
            execution_count = execution_count.strip()
            line_number = int(line_number.strip())
            if line_number == 0: continue
            try:
                execution_count = int(execution_count)
            except:
                execution_count = 0

            line_coverage[line_number] = execution_count
    return line_coverage



def find_if_and_else_statements_and_blocks(node, filename, if_then_blocks, if_else_blocks):
    if node.location.file and node.location.file.name == filename:
        if node.kind == clang.cindex.CursorKind.IF_STMT:
            #print(f"IF_STMT at line {node.location.line}, column {node.location.column}")

            stmt_children = list(node.get_children())
            if len(stmt_children) >= 2: # Ensure there is a then-block
                start_line = stmt_children[1].extent.start.line
                end_line = stmt_children[1].extent.end.line
                if_then_blocks[node.location.line] = (start_line, end_line)
            if len(stmt_children) == 3: # There is an else-block
                start_line = stmt_children[2].extent.start.line
                end_line = stmt_children[2].extent.end.line
                if_else_blocks[node.location.line] = (start_line, end_line)

    # Regardless of the node type, check its children
    for child in node.get_children():
        find_if_and_else_statements_and_blocks(child, filename, if_then_blocks, if_else_blocks)


def find_cold_blocks(data, coverage_data, relative_threshold):
    cold_blocks = []
    for if_line, then_block in data.items():
        if_exec_count = coverage_data[if_line]

        then_exec_counts = []
        for line in range(then_block[0], then_block[1]+1):
            if line == if_line: continue
            then_exec_counts.append(coverage_data[line])

        max_then_exec_count = max(then_exec_counts) if then_exec_counts else 0

        if if_exec_count == 0: continue
        perc = max_then_exec_count / if_exec_count

        if perc < relative_threshold:
            cold_blocks.append((if_line, then_block, perc))  # Include perc in tuple

    return cold_blocks

def main():
    filename = sys.argv[1]
    index = clang.cindex.Index.create()
    translation_unit = index.parse(filename)
    if translation_unit.diagnostics:
        for diag in translation_unit.diagnostics:
            print("Diagnostic:", diag)
        return

    tu_cursor = translation_unit.cursor

    # Load coverage data
    with open(filename + ".gcov", 'r') as file:
        coverage_text = file.read()
    coverage_data = parse_coverage_data(coverage_text)

    # Initialize empty dictionary to store then-block and else-block extents
    if_then_blocks = {}
    if_else_blocks = {}
    find_if_and_else_statements_and_blocks(tu_cursor, filename, if_then_blocks, if_else_blocks)

    cold_then_blocks = find_cold_blocks(if_then_blocks, coverage_data, 0.3)
    cold_else_blocks = find_cold_blocks(if_else_blocks, coverage_data, 0.3)

    # Now we insert the comments into the source code
    with open(filename, 'r') as file:
        lines = file.readlines()

    for block in sorted(cold_then_blocks, key=lambda x: x[0], reverse=True):  # Sort by if_line in descending order
        if_line, then_block, perc = block
        lines.insert(if_line-1, f"// Cold block detected: THEN block has {round(perc*100,1)}% of the if condition's execution count.\n")

    for block in sorted(cold_else_blocks, key=lambda x: x[0], reverse=True):  # Sort by if_line in descending order
        if_line, else_block, perc = block
        lines.insert(else_block[0]-1, f"// Cold block detected: ELSE block has {round(perc*100,1)}% of the if condition's execution count.\n")

    for line in lines:
        print(line, end='')

if __name__ == '__main__':
    main()
