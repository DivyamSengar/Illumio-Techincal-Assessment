**README.md**  
# Flow Log Parser

A Python script to parse AWS VPC flow logs and map entries to tags based on a lookup table. Generates counts for tags and counts for unique port/protocol combinations.

---

## Requirements
- Python 3.x
- Input files:
  - `lookup_file.csv`: Maps `dstport,protocol` combinations to tags.
  - `flow_logs.txt`: Flow logs in AWS VPC format (version 2).
  - `protocols.csv`: Maps protocol numbers to names (included in the repository).

---

## Usage
```bash
python3 flow_log_parser.py <lookup_file.csv> <flow_logs.txt>
```

### Outputs
1. **tag_counts.csv**: Count of matches for each tag (or `untagged`).
2. **port_protocol_counts.csv**: Count of each unique `port,protocol` combination.

---

## Key Assumptions
1. **Flow Log Format**: Only supports [AWS VPC flow logs version 2](https://docs.aws.amazon.com/vpc/latest/userguide/flow-log-records.html) with default fields.
   - Destination port is the 7th field (index 6).
   - Protocol is the 8th field (index 7).
2. **Lookup Table Format**: The lookup table's first line is a header line describing the csv contents, such as `dstport,protocol,tag`.
3. **Case Insensitivity**: Lookup table protocol names are matched case-insensitively (meaning `TCP` ≡ `tcp`).
4. **Protocol Mappings**: 
   - Uses `protocols.csv` to resolve protocol numbers to names. If missing, the script exits with an error.
   - Unmapped protocols retain their numeric value.
5. **Untagged Entries**: Log entries with no matching `dstport,protocol` in the lookup file are counted as `untagged`.
6. **Input Validation**: Invalid log lines (e.g., fewer than 8 fields) are skipped.

---
## Design Choices
1. **Protocol Mapping CSV**:  
   - The `protocols.csv` file is read at runtime for flexibility. If unavailable, the script errors out.  
   - *Alternative*: Protocol mappings could be hardcoded, but using a CSV simplifies updates and maintains separation of concerns, as a software engineering principle.

2. **Efficiency**:  
   - Uses `defaultdict` for O(1) lookups during counting.
   - Processes files line-by-line to handle large files (up to 10 MB) with minimal memory usage.

3. **Case Handling**:  
   - Converts all protocol names and tags to lowercase for case-insensitive matching.

---

## Limitations
- Does not support custom flow log formats or versions other than AWS VPC v2.
- Limited input validation (e.g., no checks for valid port ranges).

---
## Testing
A sample test suite is provided in the repository. To run tests, use the included `test_flow_logs.txt` and `test_lookup.csv`.

### Test Files
1. **test_flow_logs.txt**:
2. **test_lookup.csv**:

### Expected Outputs
1. **tag_counts.csv**:
    ```
    Tag Counts:
    Tag,Count
    untagged,10
    sv_p2,1
    sv_p1,2
    email,3
    ```

2. **port_protocol_counts.csv**:
    ```
    Port/Protocol Combination Counts:
    Port,Protocol,Count
    49153,tcp,2
    49154,tcp,2
    49155,tcp,1
    49156,tcp,1
    49157,tcp,1
    49158,tcp,1
    80,tcp,1
    1024,tcp,1
    443,tcp,1
    23,tcp,1
    25,tcp,1
    110,tcp,1
    993,tcp,1
    143,tcp,1
    ```

### Edge Cases Tested
1. **Invalid Protocol**: A log entry with protocol `999` (not in `protocols.csv`) retains its numeric value.
2. **Case Sensitivity**: Lookup entries with protocol `TCP` match log entries with protocol `tcp`.
3. **Untagged Entries**: Log entries with no matching `dstport,protocol` are counted as `untagged`.
---
## Test Instructions
1. Save sample logs to `test_flow_logs.txt`.
2. Save the lookup table to `test_lookup.csv`.
3. Run:
   ```bash
   python3 flow_log_parser.py test_lookup.csv test_flow_logs.txt
   ```
4. Verify generated outputs with the expected, as listed above.