# QuadTree Extended Test Battery Results

Generated: 2025-08-11 14:14:27

## Scalability Analysis

| Dataset Size | Insert Rate (pts/s) | Query Rate (q/s) | Memory/Point (KB) | Tree Depth | Subdivisions |
|--------------|---------------------|------------------|-------------------|------------|---------------|
| 1,000 | 262226 | 52157 | 0.000 | 5 | 122 |
| 2,000 | 244358 | 29826 | 0.000 | 6 | 275 |
| 5,000 | 244901 | 11933 | 0.052 | 6 | 648 |
| 10,000 | 244278 | 4697 | 2.772 | 7 | 1341 |
| 20,000 | 244785 | 1950 | 4.235 | 7 | 2552 |
| 50,000 | 221655 | 700 | 28.231 | 8 | 6104 |

## Memory Profile Analysis

| Test Pattern | Memory/Object (KB) | Overhead Ratio | Total Memory (MB) |
|--------------|-------------------|----------------|-------------------|
| small_objects | 0.000 | 0.0x | 0.00 |
| medium_objects | 0.000 | 0.0x | 0.00 |
| large_objects | 0.000 | 0.0x | 0.00 |
| variable_objects | 0.000 | 0.0x | 0.00 |
