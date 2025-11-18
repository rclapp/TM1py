# Cellset Support Analysis

## Current Gap Analysis

The current `QueryExecutor` implementation is missing two important capabilities from `CellService`:

### 1. Raw Response (`execute_mdx_raw`)

**CellService Method:**
```python
def execute_mdx_raw(
    self,
    mdx: str,
    cell_properties: Iterable[str] = None,
    elem_properties: Iterable[str] = None,
    member_properties: Iterable[str] = None,
    top: int = None,
    skip: int = None,
    skip_contexts: bool = False,
    skip_zeros: bool = False,
    skip_consolidated_cells: bool = False,
    skip_rule_derived_cells: bool = False,
    sandbox_name: str = None,
    include_hierarchies: bool = False,
    use_compact_json: bool = False,
    **kwargs,
) -> Dict:
    """Execute MDX and return the raw data from TM1"""
```

**What it returns:** The raw JSON response from TM1 with full metadata (Axes, Cells, etc.)

**Use cases:**
- Custom processing of TM1 response
- Debugging queries
- Advanced users who need full metadata
- Building custom transformations

### 2. Cellset ID (`create_cellset`)

**CellService Method:**
```python
def create_cellset(self, mdx: Union[str, MdxBuilder], sandbox_name: str = None, **kwargs) -> str:
    """Execute MDX in order to create cellset at server. return the cellset-id"""
```

**What it returns:** A cellset ID string (e.g., "8A3B5C7D...")

**Use cases:**
- Manual cellset operations
- Reusing cellsets for multiple extractions
- Advanced cellset manipulation
- Writing to cellsets
- Performance optimization (create once, extract multiple times)

**Related cellset operations in CellService:**
- `create_cellset()` - Create cellset, return ID
- `delete_cellset(cellset_id)` - Delete cellset
- `extract_cellset_raw(cellset_id, ...)` - Extract raw data from cellset
- `extract_cellset(cellset_id, ...)` - Extract formatted data
- `extract_cellset_csv(cellset_id, ...)` - Extract as CSV
- `extract_cellset_dataframe(cellset_id, ...)` - Extract as DataFrame
- `update_cellset(cellset_id, values)` - Write values to cellset

## Proposed Solution

Add two new terminal operations to `QueryExecutor`:

### 1. `as_raw()` - Get Raw TM1 Response

```python
def as_raw(
    self,
    elem_properties: Iterable[str] = None,
    member_properties: Iterable[str] = None,
    skip_contexts: bool = False,
    include_hierarchies: bool = False,
    **kwargs,
) -> Dict:
    """
    Execute MDX query and return the raw TM1 response.
    
    Terminal operation - executes the query and returns raw JSON.
    Useful for custom processing or debugging.
    
    :param elem_properties: Element properties to include
    :param member_properties: Member properties to include
    :param skip_contexts: Skip context information
    :param include_hierarchies: Include hierarchy information
    :param kwargs: Additional parameters
    :return: Raw TM1 response dictionary
    """
    return self._cell_service.execute_mdx_raw(
        mdx=self._mdx,
        cell_properties=self._cell_properties,
        elem_properties=elem_properties,
        member_properties=member_properties,
        top=self._top,
        skip=self._skip,
        skip_contexts=skip_contexts,
        skip_zeros=self._skip_zeros,
        skip_consolidated_cells=self._skip_consolidated_cells,
        skip_rule_derived_cells=self._skip_rule_derived_cells,
        sandbox_name=self._sandbox_name,
        include_hierarchies=include_hierarchies,
        use_compact_json=self._use_compact_json,
        **kwargs,
    )
```

### 2. `as_cellset_id()` - Get Cellset ID

```python
def as_cellset_id(self, **kwargs) -> str:
    """
    Execute MDX query and return the cellset ID.
    
    Terminal operation - creates a cellset on the server and returns its ID.
    The cellset remains on the server for manual operations.
    
    WARNING: You must manually delete the cellset using tm1.cells.delete_cellset(cellset_id)
    to avoid memory leaks on the TM1 server.
    
    :param kwargs: Additional parameters
    :return: Cellset ID string
    
    Example usage:
        # Create cellset
        cellset_id = tm1.data.mdx(query).sandbox('dev').as_cellset_id()
        
        # Use cellset for multiple operations
        raw_data = tm1.cells.extract_cellset_raw(cellset_id)
        csv_data = tm1.cells.extract_cellset_csv(cellset_id)
        
        # Clean up
        tm1.cells.delete_cellset(cellset_id)
    """
    return self._cell_service.create_cellset(
        mdx=self._mdx,
        sandbox_name=self._sandbox_name,
        **kwargs,
    )
```

## Updated Terminal Operations Summary

After adding these, `QueryExecutor` will have **8 terminal operations**:

1. **`as_dict()`** - Dictionary with coordinates and values
2. **`as_dataframe()`** - pandas DataFrame (flat format)
3. **`as_csv()`** - CSV string
4. **`as_values()`** - List of values only (no coordinates)
5. **`as_pivot()`** - pandas DataFrame (pivot format)
6. **`count()`** - Cell count (integer)
7. **`as_raw()`** ⭐ NEW - Raw TM1 JSON response
8. **`as_cellset_id()`** ⭐ NEW - Cellset ID for manual operations

## Implementation Tasks

Add to Phase 2 (MDX Query Builder):

**Task 2.16**: Implement `as_raw()` terminal operation
- Add method to QueryExecutor
- Delegate to CellService.execute_mdx_raw()
- Pass all relevant options

**Task 2.17**: Write tests for `as_raw()`
- Functional test
- Verify raw response structure
- Test with options

**Task 2.18**: Implement `as_cellset_id()` terminal operation
- Add method to QueryExecutor
- Delegate to CellService.create_cellset()
- Add warning in docstring about manual cleanup

**Task 2.19**: Write tests for `as_cellset_id()`
- Functional test
- Verify cellset ID returned
- Test cellset can be used with CellService methods
- Test cleanup with delete_cellset()

**Task 2.20**: Update parity tests
- Verify as_raw() matches execute_mdx_raw()
- Verify as_cellset_id() matches create_cellset()

## Benefits

1. **Complete Coverage** - DataService now covers all MDX execution patterns
2. **Advanced Use Cases** - Supports power users who need cellset manipulation
3. **Debugging** - `as_raw()` helps debug query issues
4. **Performance** - `as_cellset_id()` enables cellset reuse
5. **Backward Compatibility** - All CellService functionality accessible via DataService

## Migration Examples

### Before (CellService)
```python
# Get raw response
raw = tm1.cells.execute_mdx_raw(query, sandbox_name='dev')

# Get cellset ID
cellset_id = tm1.cells.create_cellset(query, sandbox_name='dev')
```

### After (DataService)
```python
# Get raw response
raw = tm1.data.mdx(query).sandbox('dev').as_raw()

# Get cellset ID
cellset_id = tm1.data.mdx(query).sandbox('dev').as_cellset_id()
```

## Notes

- `as_cellset_id()` does NOT auto-delete the cellset (unlike other terminal operations)
- Users must manually call `tm1.cells.delete_cellset(cellset_id)` to clean up
- This is intentional - the whole point is to keep the cellset for manual operations
- Consider adding a context manager in future for automatic cleanup

