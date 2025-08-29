# QuadTree Extended Test Battery Results

Generated: 2025-08-11 15:05:29

## Scalability Analysis

| Dataset Size | Insert Rate (pts/s) | Query Rate (q/s) | Memory/Point (KB) | Tree Depth | Subdivisions |
|--------------|---------------------|------------------|-------------------|------------|---------------|
| 1,000 | 221872 | 52146 | 0.000 | 5 | 117 |
| 2,000 | 251547 | 27288 | 0.000 | 6 | 290 |
| 5,000 | 214508 | 11609 | 0.158 | 6 | 628 |
| 10,000 | 244031 | 4379 | 2.666 | 7 | 1339 |
| 20,000 | 248936 | 2028 | 4.246 | 7 | 2547 |
| 50,000 | 236434 | 637 | 27.933 | 8 | 6073 |

## Memory Profile Analysis

| Test Pattern | Memory/Object (KB) | Overhead Ratio | Total Memory (MB) |
|--------------|-------------------|----------------|-------------------|
| small_objects | 0.000 | 0.0x | 0.00 |
| medium_objects | 0.000 | 0.0x | 0.00 |
| large_objects | 0.000 | 0.0x | 0.00 |
| variable_objects | 0.000 | 0.0x | 0.00 |
