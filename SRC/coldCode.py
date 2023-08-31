def analyze_coldCode(filename, coverage_filename, relative_threshold=0.3):
    import clang.cindex

    def parseCovData(coverage_data):
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

    def findIfAndElseBlocks(vertex, filename, if_then_blocks, if_else_blocks):
        if vertex.location.file and vertex.location.file.name == filename:
            if vertex.kind == clang.cindex.CursorKind.IF_STMT:
                stmt_children = list(vertex.get_children())
                if len(stmt_children) >= 2: 
                    start_line = stmt_children[1].extent.start.line
                    end_line = stmt_children[1].extent.end.line
                    if_then_blocks[vertex.location.line] = (start_line, end_line)
                if len(stmt_children) == 3: 
                    start_line = stmt_children[2].extent.start.line
                    end_line = stmt_children[2].extent.end.line
                    if_else_blocks[vertex.location.line] = (start_line, end_line)

        for kid in vertex.get_children():
            findIfAndElseBlocks(kid, filename, if_then_blocks, if_else_blocks)

    def findColdBlocks(data, coverage_data, relative_threshold):
        cold_blocks = []
        for if_line, then_block in data.items():
            if_exec_count = coverage_data[if_line]
   
            then_exec_counts = []
            for line in range(then_block[0], then_block[1]+1):
                if line == if_line: continue
                then_exec_counts.append(coverage_data[line])

            max_then_exec_count = max(then_exec_counts) if then_exec_counts else 0
            
            #edge cases
            if if_exec_count == 0 or if_exec_count == 1 : continue
            
            perc = max_then_exec_count / if_exec_count

            if perc < relative_threshold:
                cold_blocks.append((if_line, then_block, perc))  

        return cold_blocks

    # Main part of the function

    idx = clang.cindex.Index.create()
    TU = idx.parse(filename)
    if TU.diagnostics:
        for diag in TU.diagnostics:
            print("Diagnostic:", diag)
        return

    TuCursor = TU.cursor

    with open(coverage_filename, 'r') as file:
        coverage_text = file.read()
    coverage_data = parseCovData(coverage_text)

    if_then_blocks = {}
    if_else_blocks = {}
    findIfAndElseBlocks(TuCursor, filename, if_then_blocks, if_else_blocks)

    cold_then_blocks = findColdBlocks(if_then_blocks, coverage_data, relative_threshold)
    cold_else_blocks = findColdBlocks(if_else_blocks, coverage_data, relative_threshold)

    comments = {}
    for block in cold_then_blocks: 
        if_line, then_block, perc = block
        comments[if_line] = f"Refactor this THEN block by moving it into seperate method ({round(perc*100,1)}%)."

    for block in cold_else_blocks:  
        if_line, else_block, perc = block
        comments[else_block[0]] = f"Refactor this ELSE block by moving it into seperate method ({round(perc*100,1)}%)."

    return comments
