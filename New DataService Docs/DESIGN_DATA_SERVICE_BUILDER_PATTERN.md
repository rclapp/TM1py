# DataService Builder Pattern Design

## Executive Summary

This document outlines the design for a new `DataService` that uses a fluent builder pattern (similar to mdxpy) to simplify data operations in TM1py. The current `CellService` has **~120 public methods** across **5,466 lines**, making it difficult for users to discover and use the right method for their needs.

## Current State Analysis

### CellService Complexity

**Total Methods**: ~120 public methods
**Lines of Code**: 5,466 lines
**Key Issues**:
1. **Method Explosion**: Multiple variations of similar operations (e.g., `execute_mdx`, `execute_mdx_async`, `execute_mdx_dataframe`, `execute_mdx_dataframe_async`, `execute_mdx_csv`, etc.)
2. **Parameter Overload**: Methods have 10-20+ parameters making them hard to use
3. **No Clear Pattern**: Users must know exact method names
4. **Difficult Discovery**: Hard to know which method to use for a given task

### Current Usage Patterns

#### Read Operations
```python
# Pattern 1: MDX → Dictionary
tm1.cells.execute_mdx(mdx, cell_properties=['Value'], skip_zeros=True, ...)

# Pattern 2: MDX → DataFrame
tm1.cells.execute_mdx_dataframe(mdx, skip_zeros=True, use_blob=True, ...)

# Pattern 3: MDX → CSV
tm1.cells.execute_mdx_csv(mdx, skip_zeros=True, use_blob=True, ...)

# Pattern 4: View → DataFrame
tm1.cells.execute_view_dataframe(cube, view, private=False, ...)

# Pattern 5: Async operations
tm1.cells.execute_mdx_dataframe_async(mdx_list, max_workers=8, ...)
```

#### Write Operations
```python
# Pattern 1: Write with auto-routing
tm1.cells.write(cube_name, cellset_dict, use_blob=True, ...)

# Pattern 2: Write through cellset
tm1.cells.write_through_cellset(cube_name, cellset_dict, ...)

# Pattern 3: Write through TI
tm1.cells.write_through_unbound_process(cube_name, cellset_dict, ...)

# Pattern 4: Write through blob
tm1.cells.write_through_blob(cube_name, cellset_dict, ...)

# Pattern 5: DataFrame write
tm1.cells.write_dataframe(cube_name, df, ...)
```

### Dependency Chains Identified

1. **Query Source** → **Query Options** → **Output Format**
   - Source: MDX, View, Coordinates
   - Options: skip_zeros, use_blob, sandbox, filters
   - Format: dict, DataFrame, CSV, values only

2. **Write Source** → **Write Method** → **Write Options**
   - Source: dict, DataFrame
   - Method: cellset, TI, blob
   - Options: increment, transaction log, changeset

3. **Performance Optimizations**:
   - `use_blob`: Fast read/write via CSV
   - `use_compact_json`: Reduced payload size
   - `use_iterative_json`: Memory efficient streaming
   - `async`: Parallel execution

## Proposed Design: DataService with Builder Pattern

### Core Concept

**Pattern**: `<source>.<options>.<output_format>()`

**Example Usage**:
```python
# Read operations
tm1.data.mdx(query).skip_zeros().as_dataframe()
tm1.data.mdx(query).use_blob().skip_consolidated().as_csv()
tm1.data.view(cube, view).sandbox("dev").as_dict()
tm1.data.coordinates(cube, elements).as_value()

# Write operations
tm1.data.write(cube, data).use_blob().increment().execute()
tm1.data.write(cube, data).use_ti().skip_non_updateable().execute()
tm1.data.write_dataframe(cube, df).use_blob().clear_first().execute()

# Async operations
tm1.data.mdx_async(queries).max_workers(16).as_dataframe()
```

### Architecture

```
DataService (Entry Point)
├── QueryBuilder (Read Operations)
│   ├── MdxQueryBuilder
│   ├── ViewQueryBuilder
│   ├── CoordinateQueryBuilder
│   └── AsyncQueryBuilder
│
└── WriteBuilder (Write Operations)
    ├── DictWriteBuilder
    ├── DataFrameWriteBuilder
    └── AsyncWriteBuilder
```

### Class Design

#### 1. DataService (Entry Point)

```python
class DataService(ObjectService):
    """Simplified data operations using builder pattern"""
    
    def __init__(self, tm1_rest: RestService):
        super().__init__(tm1_rest)
        self._cell_service = CellService(tm1_rest)  # Delegate to existing service
    
    # Read entry points
    def mdx(self, mdx: Union[str, MdxBuilder]) -> 'MdxQueryBuilder':
        """Start building an MDX query"""
        return MdxQueryBuilder(self._cell_service, mdx)
    
    def view(self, cube: str, view: str, private: bool = False) -> 'ViewQueryBuilder':
        """Start building a view query"""
        return ViewQueryBuilder(self._cell_service, cube, view, private)
    
    def coordinates(self, cube: str, elements: Union[str, Iterable]) -> 'CoordinateQueryBuilder':
        """Query specific cell coordinates"""
        return CoordinateQueryBuilder(self._cell_service, cube, elements)
    
    def mdx_async(self, mdx_list: List[Union[str, MdxBuilder]]) -> 'AsyncQueryBuilder':
        """Execute multiple MDX queries in parallel"""
        return AsyncQueryBuilder(self._cell_service, mdx_list)
    
    # Write entry points
    def write(self, cube: str, data: Dict) -> 'DictWriteBuilder':
        """Write dictionary data to cube"""
        return DictWriteBuilder(self._cell_service, cube, data)
    
    def write_dataframe(self, cube: str, df: 'pd.DataFrame') -> 'DataFrameWriteBuilder':
        """Write DataFrame to cube"""
        return DataFrameWriteBuilder(self._cell_service, cube, df)
```

#### 2. MdxQueryBuilder (Read Operations)

```python
class MdxQueryBuilder:
    """Builder for MDX query execution with fluent interface"""
    
    def __init__(self, cell_service: CellService, mdx: Union[str, MdxBuilder]):
        self._cell_service = cell_service
        self._mdx = mdx.to_mdx() if isinstance(mdx, MdxBuilder) else mdx
        
        # Query options (with defaults)
        self._sandbox_name: Optional[str] = None
        self._skip_zeros: bool = False
        self._skip_consolidated_cells: bool = False
        self._skip_rule_derived_cells: bool = False
        self._top: Optional[int] = None
        self._skip: Optional[int] = None
        self._cell_properties: List[str] = None
        
        # Performance options
        self._use_blob: bool = False
        self._use_compact_json: bool = False
        self._use_iterative_json: bool = False
        
        # Output options
        self._include_attributes: bool = False
        self._element_unique_names: bool = True
    
    # Sandbox operations
    def sandbox(self, name: str) -> 'MdxQueryBuilder':
        """Execute query in a sandbox"""
        self._sandbox_name = name
        return self
    
    # Filtering options
    def skip_zeros(self, skip: bool = True) -> 'MdxQueryBuilder':
        """Skip cells with zero values"""
        self._skip_zeros = skip
        return self
    
    def skip_consolidated(self, skip: bool = True) -> 'MdxQueryBuilder':
        """Skip consolidated cells"""
        self._skip_consolidated_cells = skip
        return self
    
    def skip_rule_derived(self, skip: bool = True) -> 'MdxQueryBuilder':
        """Skip rule-derived cells"""
        self._skip_rule_derived_cells = skip
        return self
    
    def top(self, n: int) -> 'MdxQueryBuilder':
        """Limit to top N cells"""
        self._top = n
        return self
    
    def skip(self, n: int) -> 'MdxQueryBuilder':
        """Skip first N cells"""
        self._skip = n
        return self
    
    # Performance options
    def use_blob(self, use: bool = True) -> 'MdxQueryBuilder':
        """Use blob for faster execution (10x faster)"""
        self._use_blob = use
        return self
    
    def use_compact_json(self, use: bool = True) -> 'MdxQueryBuilder':
        """Use compact JSON format"""
        self._use_compact_json = use
        return self
    
    def use_iterative_json(self, use: bool = True) -> 'MdxQueryBuilder':
        """Use iterative JSON for memory efficiency"""
        self._use_iterative_json = use
        return self
    
    # Attribute options
    def include_attributes(self, include: bool = True) -> 'MdxQueryBuilder':
        """Include element attributes in result"""
        self._include_attributes = include
        return self
    
    def cell_properties(self, properties: List[str]) -> 'MdxQueryBuilder':
        """Specify cell properties to retrieve"""
        self._cell_properties = properties
        return self
    
    # Terminal operations (return results)
    def as_dict(self, **kwargs) -> CaseAndSpaceInsensitiveTuplesDict:
        """Execute and return as dictionary"""
        return self._cell_service.execute_mdx(
            mdx=self._mdx,
            sandbox_name=self._sandbox_name,
            skip_zeros=self._skip_zeros,
            skip_consolidated_cells=self._skip_consolidated_cells,
            skip_rule_derived_cells=self._skip_rule_derived_cells,
            top=self._top,
            skip=self._skip,
            cell_properties=self._cell_properties,
            use_compact_json=self._use_compact_json,
            element_unique_names=self._element_unique_names,
            **kwargs
        )
    
    def as_dataframe(self, shaped: bool = False, **kwargs) -> 'pd.DataFrame':
        """Execute and return as pandas DataFrame"""
        return self._cell_service.execute_mdx_dataframe(
            mdx=self._mdx,
            sandbox_name=self._sandbox_name,
            skip_zeros=self._skip_zeros,
            skip_consolidated_cells=self._skip_consolidated_cells,
            skip_rule_derived_cells=self._skip_rule_derived_cells,
            top=self._top,
            skip=self._skip,
            use_blob=self._use_blob,
            use_compact_json=self._use_compact_json,
            use_iterative_json=self._use_iterative_json,
            include_attributes=self._include_attributes,
            shaped=shaped,
            **kwargs
        )
    
    def as_csv(self, **kwargs) -> str:
        """Execute and return as CSV string"""
        return self._cell_service.execute_mdx_csv(
            mdx=self._mdx,
            sandbox_name=self._sandbox_name,
            skip_zeros=self._skip_zeros,
            skip_consolidated_cells=self._skip_consolidated_cells,
            skip_rule_derived_cells=self._skip_rule_derived_cells,
            top=self._top,
            skip=self._skip,
            use_blob=self._use_blob,
            use_compact_json=self._use_compact_json,
            use_iterative_json=self._use_iterative_json,
            include_attributes=self._include_attributes,
            **kwargs
        )
    
    def as_values(self, **kwargs) -> List[Union[str, float]]:
        """Execute and return values only (no coordinates)"""
        return self._cell_service.execute_mdx_values(
            mdx=self._mdx,
            sandbox_name=self._sandbox_name,
            skip_zeros=self._skip_zeros,
            skip_consolidated_cells=self._skip_consolidated_cells,
            skip_rule_derived_cells=self._skip_rule_derived_cells,
            use_compact_json=self._use_compact_json,
            **kwargs
        )
    
    def as_pivot(self, **kwargs) -> 'pd.DataFrame':
        """Execute and return as pivoted DataFrame"""
        return self._cell_service.execute_mdx_dataframe_pivot(
            mdx=self._mdx,
            sandbox_name=self._sandbox_name,
            **kwargs
        )
    
    def count(self, **kwargs) -> int:
        """Get cell count without retrieving data"""
        return self._cell_service.execute_mdx_cellcount(
            mdx=self._mdx,
            sandbox_name=self._sandbox_name,
            **kwargs
        )
```

#### 3. ViewQueryBuilder (Similar to MdxQueryBuilder)

```python
class ViewQueryBuilder:
    """Builder for view query execution"""

    def __init__(self, cell_service: CellService, cube: str, view: str, private: bool):
        self._cell_service = cell_service
        self._cube = cube
        self._view = view
        self._private = private
        # ... same options as MdxQueryBuilder

    # Same fluent methods as MdxQueryBuilder
    def sandbox(self, name: str) -> 'ViewQueryBuilder': ...
    def skip_zeros(self, skip: bool = True) -> 'ViewQueryBuilder': ...
    # ... etc

    # Terminal operations delegate to execute_view_* methods
    def as_dict(self, **kwargs) -> CaseAndSpaceInsensitiveTuplesDict:
        return self._cell_service.execute_view(...)

    def as_dataframe(self, **kwargs) -> 'pd.DataFrame':
        return self._cell_service.execute_view_dataframe(...)
```

#### 4. CoordinateQueryBuilder (Single Cell Operations)

```python
class CoordinateQueryBuilder:
    """Builder for coordinate-based queries (get_value, get_values)"""

    def __init__(self, cell_service: CellService, cube: str, elements: Union[str, Iterable]):
        self._cell_service = cell_service
        self._cube = cube
        self._elements = elements
        self._dimensions: Optional[List[str]] = None
        self._sandbox_name: Optional[str] = None

    def dimensions(self, dims: List[str]) -> 'CoordinateQueryBuilder':
        """Specify dimension order"""
        self._dimensions = dims
        return self

    def sandbox(self, name: str) -> 'CoordinateQueryBuilder':
        """Execute in sandbox"""
        self._sandbox_name = name
        return self

    def as_value(self, **kwargs) -> Union[str, float]:
        """Get single cell value"""
        return self._cell_service.get_value(
            cube_name=self._cube,
            elements=self._elements,
            dimensions=self._dimensions,
            sandbox_name=self._sandbox_name,
            **kwargs
        )

    def as_values(self, **kwargs) -> List:
        """Get multiple cell values"""
        return self._cell_service.get_values(
            cube_name=self._cube,
            element_sets=self._elements,
            dimensions=self._dimensions,
            sandbox_name=self._sandbox_name,
            **kwargs
        )
```

#### 5. AsyncQueryBuilder (Parallel Execution)

```python
class AsyncQueryBuilder:
    """Builder for async/parallel query execution"""

    def __init__(self, cell_service: CellService, mdx_list: List[Union[str, MdxBuilder]]):
        self._cell_service = cell_service
        self._mdx_list = [m.to_mdx() if isinstance(m, MdxBuilder) else m for m in mdx_list]
        self._max_workers: int = 8
        # ... same options as MdxQueryBuilder

    def max_workers(self, n: int) -> 'AsyncQueryBuilder':
        """Set number of parallel workers"""
        self._max_workers = n
        return self

    # Same option methods as MdxQueryBuilder
    def skip_zeros(self, skip: bool = True) -> 'AsyncQueryBuilder': ...

    # Terminal operations
    def as_dataframe(self, **kwargs) -> 'pd.DataFrame':
        """Execute all queries in parallel and return combined DataFrame"""
        return self._cell_service.execute_mdx_dataframe_async(
            mdx_list=self._mdx_list,
            max_workers=self._max_workers,
            skip_zeros=self._skip_zeros,
            # ... other options
            **kwargs
        )
```

#### 6. DictWriteBuilder (Write Operations)

```python
class DictWriteBuilder:
    """Builder for writing dictionary data to cubes"""

    def __init__(self, cell_service: CellService, cube: str, data: Dict):
        self._cell_service = cell_service
        self._cube = cube
        self._data = data

        # Write options
        self._dimensions: Optional[List[str]] = None
        self._sandbox_name: Optional[str] = None
        self._increment: bool = False
        self._skip_non_updateable: bool = False

        # Write method (auto-select by default)
        self._use_ti: bool = False
        self._use_blob: bool = False
        self._use_cellset: bool = False

        # Transaction options
        self._deactivate_transaction_log: bool = False
        self._reactivate_transaction_log: bool = False
        self._use_changeset: bool = False

        # Advanced options
        self._precision: Optional[int] = None
        self._allow_spread: bool = False
        self._clear_view: Optional[str] = None

    # Configuration methods
    def dimensions(self, dims: List[str]) -> 'DictWriteBuilder':
        """Specify dimension order"""
        self._dimensions = dims
        return self

    def sandbox(self, name: str) -> 'DictWriteBuilder':
        """Write to sandbox"""
        self._sandbox_name = name
        return self

    def increment(self, inc: bool = True) -> 'DictWriteBuilder':
        """Increment values instead of replacing"""
        self._increment = inc
        return self

    def skip_non_updateable(self, skip: bool = True) -> 'DictWriteBuilder':
        """Skip non-updateable cells"""
        self._skip_non_updateable = skip
        return self

    # Write method selection
    def use_ti(self, use: bool = True) -> 'DictWriteBuilder':
        """Write via TI process (requires admin, fast)"""
        self._use_ti = use
        if use:
            self._use_blob = False
            self._use_cellset = False
        return self

    def use_blob(self, use: bool = True) -> 'DictWriteBuilder':
        """Write via blob (requires admin, 10x faster)"""
        self._use_blob = use
        if use:
            self._use_ti = False
            self._use_cellset = False
        return self

    def use_cellset(self, use: bool = True) -> 'DictWriteBuilder':
        """Write via cellset (no admin required)"""
        self._use_cellset = use
        if use:
            self._use_ti = False
            self._use_blob = False
        return self

    # Transaction control
    def deactivate_transaction_log(self, deactivate: bool = True) -> 'DictWriteBuilder':
        """Deactivate transaction log before write"""
        self._deactivate_transaction_log = deactivate
        return self

    def reactivate_transaction_log(self, reactivate: bool = True) -> 'DictWriteBuilder':
        """Reactivate transaction log after write"""
        self._reactivate_transaction_log = reactivate
        return self

    def use_changeset(self, use: bool = True) -> 'DictWriteBuilder':
        """Group writes in a changeset"""
        self._use_changeset = use
        return self

    # Advanced options
    def precision(self, p: int) -> 'DictWriteBuilder':
        """Set precision for TI writes"""
        self._precision = p
        return self

    def allow_spread(self, allow: bool = True) -> 'DictWriteBuilder':
        """Allow spreading to consolidated cells"""
        self._allow_spread = allow
        return self

    def clear_view(self, view_name: str) -> 'DictWriteBuilder':
        """Clear view before writing"""
        self._clear_view = view_name
        return self

    # Terminal operation
    def execute(self, **kwargs) -> Optional[str]:
        """Execute the write operation"""
        return self._cell_service.write(
            cube_name=self._cube,
            cellset_as_dict=self._data,
            dimensions=self._dimensions,
            sandbox_name=self._sandbox_name,
            increment=self._increment,
            skip_non_updateable=self._skip_non_updateable,
            use_ti=self._use_ti,
            use_blob=self._use_blob,
            deactivate_transaction_log=self._deactivate_transaction_log,
            reactivate_transaction_log=self._reactivate_transaction_log,
            use_changeset=self._use_changeset,
            precision=self._precision,
            allow_spread=self._allow_spread,
            clear_view=self._clear_view,
            **kwargs
        )
```

#### 7. DataFrameWriteBuilder (Similar to DictWriteBuilder)

```python
class DataFrameWriteBuilder:
    """Builder for writing DataFrame data to cubes"""

    def __init__(self, cell_service: CellService, cube: str, df: 'pd.DataFrame'):
        self._cell_service = cell_service
        self._cube = cube
        self._df = df
        # ... same options as DictWriteBuilder

    # Same fluent methods as DictWriteBuilder
    def use_blob(self, use: bool = True) -> 'DataFrameWriteBuilder': ...

    def execute(self, **kwargs) -> Optional[str]:
        """Execute the DataFrame write"""
        return self._cell_service.write_dataframe(
            cube_name=self._cube,
            df=self._df,
            # ... options
            **kwargs
        )
```

## Benefits of This Design

### 1. **Discoverability**
- IDE autocomplete guides users through available options
- Clear entry points: `mdx()`, `view()`, `coordinates()`, `write()`
- Method names describe what they do

### 2. **Simplicity**
- No need to remember 120+ method names
- Options are self-documenting
- Sensible defaults

### 3. **Flexibility**
- Chain only the options you need
- Terminal operations determine output format
- Easy to add new options without breaking existing code

### 4. **Backward Compatibility**
- CellService remains unchanged
- DataService delegates to CellService
- Users can migrate gradually

### 5. **Type Safety**
- Builder pattern enables better type hints
- Each builder returns itself for chaining
- Terminal operations have clear return types

## Usage Examples

### Read Examples

```python
# Simple MDX query
df = tm1.data.mdx("SELECT ...").as_dataframe()

# With options
df = tm1.data.mdx("SELECT ...") \
    .skip_zeros() \
    .skip_consolidated() \
    .use_blob() \
    .sandbox("dev") \
    .as_dataframe()

# View query
data = tm1.data.view("Sales", "Budget") \
    .skip_zeros() \
    .as_dict()

# Single cell
value = tm1.data.coordinates("Sales", "2024,Actual,London,P02") \
    .sandbox("dev") \
    .as_value()

# Async queries
df = tm1.data.mdx_async([query1, query2, query3]) \
    .max_workers(16) \
    .skip_zeros() \
    .as_dataframe()
```

### Write Examples

```python
# Simple write
tm1.data.write("Sales", cellset_dict).execute()

# With blob (fast)
tm1.data.write("Sales", cellset_dict) \
    .use_blob() \
    .skip_non_updateable() \
    .execute()

# With transaction control
tm1.data.write("Sales", cellset_dict) \
    .use_blob() \
    .deactivate_transaction_log() \
    .reactivate_transaction_log() \
    .execute()

# DataFrame write
tm1.data.write_dataframe("Sales", df) \
    .use_blob() \
    .increment() \
    .execute()
```

## Implementation Plan

### Phase 1: Core Infrastructure
1. Create `DataService` class
2. Implement `MdxQueryBuilder`
3. Implement `DictWriteBuilder`
4. Add to `TM1Service`

### Phase 2: Additional Builders
5. Implement `ViewQueryBuilder`
6. Implement `CoordinateQueryBuilder`
7. Implement `DataFrameWriteBuilder`

### Phase 3: Advanced Features
8. Implement `AsyncQueryBuilder`
9. Add specialized output formats (pivot, shaped, etc.)
10. Performance optimizations

### Phase 4: Testing & Documentation
11. Unit tests for all builders
12. Integration tests
13. Documentation and examples
14. Migration guide

## Testing Strategy

### Unit Tests
- Test each builder method in isolation
- Verify correct delegation to CellService
- Test method chaining
- Test default values

### Integration Tests
- Test against real TM1 instance
- Verify output matches CellService
- Test all output formats
- Test error handling

### Performance Tests
- Compare performance with CellService
- Verify no overhead from builder pattern
- Test async operations

## Migration Path

### For Users
1. **No Breaking Changes**: CellService remains available
2. **Gradual Adoption**: Use DataService for new code
3. **Side-by-Side**: Both services can coexist
4. **Documentation**: Clear examples for migration

### For Maintainers
1. **Delegation Pattern**: DataService delegates to CellService
2. **No Duplication**: Reuse existing logic
3. **Incremental**: Build one builder at a time
4. **Testing**: Ensure parity with CellService

## Design Decisions

1. ✅ **Naming**: `DataService` - Clear and focused on data operations
2. ✅ **Scope**: Focus on read/write operations only
   - **Included**: MDX queries, view queries, coordinate queries, writes, async operations
   - **Excluded**: Cell tracing (stays in CellService), cell feeders, calculation tracing
   - **Rationale**: Keep DataService focused on common data operations; specialized operations remain in CellService
3. ✅ **Async**: Separate entry point (`mdx_async()`) rather than method on builder
   - **Rationale**: Clearer intent, different return type, different use case
4. ⏳ **Defaults**: To be determined during implementation
   - Candidates for `True` by default: `skip_zeros` (common use case)
   - Candidates for `False` by default: `use_blob` (requires admin permissions)
   - Will gather user feedback during beta testing

## Out of Scope (Remains in CellService)

The following operations will **NOT** be included in DataService and will remain in CellService:

1. **Cell Tracing & Analysis**:
   - `trace_cell_calculation()` - Trace how a cell value is calculated
   - `trace_cell_feeders()` - Trace cell feeders
   - `check_cell_feeders()` - Check if feeders are working

2. **Specialized Clear Operations** (for now):
   - `clear()` - Clear entire cube
   - `clear_with_mdx()` - Clear with MDX
   - `clear_with_dataframe()` - Clear with DataFrame
   - `relative_proportional_spread()` - Spreading operations
   - `clear_spread()` - Clear spread

3. **Low-Level Cellset Operations**:
   - `create_cellset()` - Create cellset manually
   - `delete_cellset()` - Delete cellset manually
   - `extract_cellset_*()` - Low-level extraction methods
   - `update_cellset()` - Update existing cellset

4. **Transaction Log Management**:
   - `transaction_log_is_active()` - Check transaction log status
   - `activate_transactionlog()` - Activate transaction log
   - `deactivate_transactionlog()` - Deactivate transaction log
   - Note: Transaction log control via write builders is included (e.g., `.deactivate_transaction_log()`)

5. **Changeset Management**:
   - `begin_changeset()` - Begin changeset manually
   - `end_changeset()` - End changeset manually
   - `undo_changeset()` - Undo changeset
   - Note: Changeset usage via write builders is included (e.g., `.use_changeset()`)

**Rationale**: These are specialized, advanced operations that are used less frequently. Keeping them in CellService:
- Maintains backward compatibility
- Keeps DataService API surface small and focused
- Allows power users to access advanced features when needed
- Can be added to DataService later if there's demand

## Comparison: Before vs After

### Read Operations

| Task | Current (CellService) | New (DataService) |
|------|----------------------|-------------------|
| MDX → DataFrame | `tm1.cells.execute_mdx_dataframe(mdx, skip_zeros=True, use_blob=True, sandbox_name="dev")` | `tm1.data.mdx(mdx).skip_zeros().use_blob().sandbox("dev").as_dataframe()` |
| MDX → CSV | `tm1.cells.execute_mdx_csv(mdx, skip_zeros=True, use_blob=True)` | `tm1.data.mdx(mdx).skip_zeros().use_blob().as_csv()` |
| MDX → Dict | `tm1.cells.execute_mdx(mdx, skip_zeros=True, skip_consolidated_cells=True)` | `tm1.data.mdx(mdx).skip_zeros().skip_consolidated().as_dict()` |
| View → DataFrame | `tm1.cells.execute_view_dataframe(cube, view, private=False, skip_zeros=True)` | `tm1.data.view(cube, view).skip_zeros().as_dataframe()` |
| Get Cell Value | `tm1.cells.get_value(cube, elements, sandbox_name="dev")` | `tm1.data.coordinates(cube, elements).sandbox("dev").as_value()` |
| Async MDX | `tm1.cells.execute_mdx_dataframe_async(mdx_list, max_workers=16, skip_zeros=True)` | `tm1.data.mdx_async(mdx_list).max_workers(16).skip_zeros().as_dataframe()` |

### Write Operations

| Task | Current (CellService) | New (DataService) |
|------|----------------------|-------------------|
| Write with Blob | `tm1.cells.write(cube, data, use_blob=True, skip_non_updateable=True)` | `tm1.data.write(cube, data).use_blob().skip_non_updateable().execute()` |
| Write with TI | `tm1.cells.write(cube, data, use_ti=True, precision=2)` | `tm1.data.write(cube, data).use_ti().precision(2).execute()` |
| Incremental Write | `tm1.cells.write(cube, data, increment=True, use_blob=True)` | `tm1.data.write(cube, data).increment().use_blob().execute()` |
| DataFrame Write | `tm1.cells.write_dataframe(cube, df, use_blob=True)` | `tm1.data.write_dataframe(cube, df).use_blob().execute()` |

### Key Improvements

1. **Readability**: Method chains read like sentences
2. **Discoverability**: IDE autocomplete shows available options at each step
3. **Flexibility**: Only specify options you need
4. **Consistency**: Same pattern for all operations
5. **Type Safety**: Better type hints and return types

## Method Mapping: CellService → DataService

### Read Methods (execute_*)

| CellService Method | DataService Pattern | Notes |
|-------------------|---------------------|-------|
| `execute_mdx` | `mdx(...).as_dict()` | Returns dict |
| `execute_mdx_dataframe` | `mdx(...).as_dataframe()` | Returns DataFrame |
| `execute_mdx_csv` | `mdx(...).as_csv()` | Returns CSV string |
| `execute_mdx_values` | `mdx(...).as_values()` | Returns list of values |
| `execute_mdx_dataframe_pivot` | `mdx(...).as_pivot()` | Returns pivoted DataFrame |
| `execute_mdx_dataframe_shaped` | `mdx(...).as_dataframe(shaped=True)` | Returns shaped DataFrame |
| `execute_mdx_cellcount` | `mdx(...).count()` | Returns cell count |
| `execute_mdx_async` | `mdx(...).as_dict()` | Async handled by builder |
| `execute_mdx_dataframe_async` | `mdx_async([...]).as_dataframe()` | Dedicated async builder |
| `execute_view` | `view(...).as_dict()` | View-based query |
| `execute_view_dataframe` | `view(...).as_dataframe()` | View → DataFrame |
| `execute_view_csv` | `view(...).as_csv()` | View → CSV |
| `get_value` | `coordinates(...).as_value()` | Single cell |
| `get_values` | `coordinates(...).as_values()` | Multiple cells |

### Write Methods (write_*)

| CellService Method | DataService Pattern | Notes |
|-------------------|---------------------|-------|
| `write` | `write(...).execute()` | Auto-selects method |
| `write_through_cellset` | `write(...).use_cellset().execute()` | Explicit cellset |
| `write_through_unbound_process` | `write(...).use_ti().execute()` | TI-based write |
| `write_through_blob` | `write(...).use_blob().execute()` | Blob-based write |
| `write_dataframe` | `write_dataframe(...).execute()` | DataFrame input |
| `write_values` | `write(...).execute()` | Same as write |
| `write_values_through_cellset` | `write(...).use_cellset().execute()` | Explicit cellset |

### Options Mapping

| CellService Parameter | DataService Method | Type |
|----------------------|-------------------|------|
| `skip_zeros=True` | `.skip_zeros()` | Filter |
| `skip_consolidated_cells=True` | `.skip_consolidated()` | Filter |
| `skip_rule_derived_cells=True` | `.skip_rule_derived()` | Filter |
| `use_blob=True` | `.use_blob()` | Performance |
| `use_compact_json=True` | `.use_compact_json()` | Performance |
| `use_iterative_json=True` | `.use_iterative_json()` | Performance |
| `sandbox_name="dev"` | `.sandbox("dev")` | Context |
| `top=100` | `.top(100)` | Pagination |
| `skip=50` | `.skip(50)` | Pagination |
| `include_attributes=True` | `.include_attributes()` | Output |
| `increment=True` | `.increment()` | Write mode |
| `skip_non_updateable=True` | `.skip_non_updateable()` | Write filter |
| `use_ti=True` | `.use_ti()` | Write method |
| `use_changeset=True` | `.use_changeset()` | Transaction |
| `max_workers=8` | `.max_workers(8)` | Async |

## Next Steps

1. Review this design with stakeholders
2. Create implementation tasks
3. Set up test infrastructure
4. Begin Phase 1 implementation
```


