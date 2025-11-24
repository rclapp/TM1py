# DataService Usage Examples

This document provides concrete examples of how to use the new DataService builder pattern compared to the existing CellService.

## Table of Contents
1. [Read Operations](#read-operations)
2. [Write Operations](#write-operations)
3. [Advanced Scenarios](#advanced-scenarios)
4. [Migration Examples](#migration-examples)

---

## Read Operations

### Example 1: Simple MDX Query to DataFrame

**Before (CellService)**:
```python
from TM1py import TM1Service

with TM1Service(address='localhost', port=12354, user='admin', password='apple') as tm1:
    mdx = """
    SELECT
        {[Product].[Product].[Bike]} ON ROWS,
        {[Period].[Period].[2024-Q1]} ON COLUMNS
    FROM [Sales]
    """
    
    df = tm1.cells.execute_mdx_dataframe(
        mdx=mdx,
        skip_zeros=True,
        skip_consolidated_cells=False,
        skip_rule_derived_cells=False,
        use_blob=False,
        sandbox_name=None
    )
```

**After (DataService)**:
```python
from TM1py import TM1Service

with TM1Service(address='localhost', port=12354, user='admin', password='apple') as tm1:
    mdx = """
    SELECT
        {[Product].[Product].[Bike]} ON ROWS,
        {[Period].[Period].[2024-Q1]} ON COLUMNS
    FROM [Sales]
    """
    
    df = tm1.data.mdx(mdx).skip_zeros().as_dataframe()
```

**Benefits**: Cleaner, more readable, only specify options you need.

---

### Example 2: High-Performance MDX Query with Blob

**Before (CellService)**:
```python
with TM1Service(**config) as tm1:
    mdx = "SELECT ... FROM [LargeCube]"
    
    df = tm1.cells.execute_mdx_dataframe(
        mdx=mdx,
        skip_zeros=True,
        skip_consolidated_cells=True,
        skip_rule_derived_cells=True,
        use_blob=True,
        use_compact_json=False,
        sandbox_name="Development",
        include_attributes=True
    )
```

**After (DataService)**:
```python
with TM1Service(**config) as tm1:
    mdx = "SELECT ... FROM [LargeCube]"
    
    df = (tm1.data.mdx(mdx)
          .skip_zeros()
          .skip_consolidated()
          .skip_rule_derived()
          .use_blob()
          .sandbox("Development")
          .include_attributes()
          .as_dataframe())
```

**Benefits**: Method chaining makes it clear what optimizations are applied.

---

### Example 3: View Query to CSV

**Before (CellService)**:
```python
with TM1Service(**config) as tm1:
    csv_data = tm1.cells.execute_view_csv(
        cube_name="Sales",
        view_name="Budget View",
        private=False,
        skip_zeros=True,
        use_blob=True
    )
```

**After (DataService)**:
```python
with TM1Service(**config) as tm1:
    csv_data = (tm1.data.view("Sales", "Budget View")
                .skip_zeros()
                .use_blob()
                .as_csv())
```

**Benefits**: Shorter, more intuitive.

---

### Example 4: Get Single Cell Value

**Before (CellService)**:
```python
with TM1Service(**config) as tm1:
    value = tm1.cells.get_value(
        cube_name="Sales",
        elements="2024,Actual,North,Product1",
        sandbox_name="Development"
    )
```

**After (DataService)**:
```python
with TM1Service(**config) as tm1:
    value = (tm1.data.coordinates("Sales", "2024,Actual,North,Product1")
             .sandbox("Development")
             .as_value())
```

**Benefits**: Clear intent, consistent pattern.

---

### Example 5: Async Parallel Queries

**Before (CellService)**:
```python
with TM1Service(**config) as tm1:
    queries = [
        "SELECT ... FROM [Sales]",
        "SELECT ... FROM [Budget]",
        "SELECT ... FROM [Forecast]"
    ]
    
    df = tm1.cells.execute_mdx_dataframe_async(
        mdx_list=queries,
        max_workers=8,
        skip_zeros=True,
        use_blob=True
    )
```

**After (DataService)**:
```python
with TM1Service(**config) as tm1:
    queries = [
        "SELECT ... FROM [Sales]",
        "SELECT ... FROM [Budget]",
        "SELECT ... FROM [Forecast]"
    ]
    
    df = (tm1.data.mdx_async(queries)
          .max_workers(8)
          .skip_zeros()
          .use_blob()
          .as_dataframe())
```

**Benefits**: Consistent with single query pattern.

---

### Example 6: MDX with Pagination

**Before (CellService)**:
```python
with TM1Service(**config) as tm1:
    mdx = "SELECT ... FROM [Sales]"
    
    # Get rows 100-200
    df = tm1.cells.execute_mdx_dataframe(
        mdx=mdx,
        skip=100,
        top=100,
        skip_zeros=True
    )
```

**After (DataService)**:
```python
with TM1Service(**config) as tm1:
    mdx = "SELECT ... FROM [Sales]"
    
    # Get rows 100-200
    df = (tm1.data.mdx(mdx)
          .skip(100)
          .top(100)
          .skip_zeros()
          .as_dataframe())
```

**Benefits**: Clear pagination logic.

---

## Write Operations

### Example 7: Simple Write with Dictionary

**Before (CellService)**:
```python
with TM1Service(**config) as tm1:
    data = {
        ('2024', 'Actual', 'North', 'Product1'): 1000,
        ('2024', 'Actual', 'South', 'Product1'): 2000,
    }
    
    tm1.cells.write(
        cube_name="Sales",
        cellset_as_dict=data,
        use_blob=False,
        use_ti=False
    )
```

**After (DataService)**:
```python
with TM1Service(**config) as tm1:
    data = {
        ('2024', 'Actual', 'North', 'Product1'): 1000,
        ('2024', 'Actual', 'South', 'Product1'): 2000,
    }
    
    tm1.data.write("Sales", data).execute()
```

**Benefits**: Simpler, auto-selects best write method.

---

### Example 8: High-Performance Write with Blob

**Before (CellService)**:
```python
with TM1Service(**config) as tm1:
    data = {
        # ... large dataset
    }
    
    tm1.cells.write(
        cube_name="Sales",
        cellset_as_dict=data,
        use_blob=True,
        skip_non_updateable=True,
        deactivate_transaction_log=True,
        reactivate_transaction_log=True
    )
```

**After (DataService)**:
```python
with TM1Service(**config) as tm1:
    data = {
        # ... large dataset
    }
    
    (tm1.data.write("Sales", data)
     .use_blob()
     .skip_non_updateable()
     .deactivate_transaction_log()
     .reactivate_transaction_log()
     .execute())
```

**Benefits**: Each option is explicit and self-documenting.

---

### Example 9: Incremental Write

**Before (CellService)**:
```python
with TM1Service(**config) as tm1:
    increments = {
        ('2024', 'Actual', 'North', 'Product1'): 100,  # Add 100
        ('2024', 'Actual', 'South', 'Product1'): -50,  # Subtract 50
    }
    
    tm1.cells.write(
        cube_name="Sales",
        cellset_as_dict=increments,
        increment=True,
        use_blob=True
    )
```

**After (DataService)**:
```python
with TM1Service(**config) as tm1:
    increments = {
        ('2024', 'Actual', 'North', 'Product1'): 100,  # Add 100
        ('2024', 'Actual', 'South', 'Product1'): -50,  # Subtract 50
    }
    
    (tm1.data.write("Sales", increments)
     .increment()
     .use_blob()
     .execute())
```

**Benefits**: Clear that this is an incremental operation.

---

### Example 10: DataFrame Write

**Before (CellService)**:
```python
import pandas as pd

with TM1Service(**config) as tm1:
    df = pd.DataFrame({
        'Year': ['2024', '2024'],
        'Scenario': ['Actual', 'Actual'],
        'Region': ['North', 'South'],
        'Product': ['Product1', 'Product1'],
        'Value': [1000, 2000]
    })
    
    tm1.cells.write_dataframe(
        cube_name="Sales",
        df=df,
        use_blob=True
    )
```

**After (DataService)**:
```python
import pandas as pd

with TM1Service(**config) as tm1:
    df = pd.DataFrame({
        'Year': ['2024', '2024'],
        'Scenario': ['Actual', 'Actual'],
        'Region': ['North', 'South'],
        'Product': ['Product1', 'Product1'],
        'Value': [1000, 2000]
    })
    
    tm1.data.write_dataframe("Sales", df).use_blob().execute()
```

**Benefits**: Consistent pattern with dict writes.

---

### Example 11: Write to Sandbox with Changeset

**Before (CellService)**:
```python
with TM1Service(**config) as tm1:
    data = {
        # ... data
    }
    
    tm1.cells.write(
        cube_name="Sales",
        cellset_as_dict=data,
        sandbox_name="Development",
        use_changeset=True,
        use_blob=True
    )
```

**After (DataService)**:
```python
with TM1Service(**config) as tm1:
    data = {
        # ... data
    }
    
    (tm1.data.write("Sales", data)
     .sandbox("Development")
     .use_changeset()
     .use_blob()
     .execute())
```

**Benefits**: Clear what context and options are being used.

---

## Advanced Scenarios

### Example 12: Complex Read Pipeline

**Before (CellService)**:
```python
with TM1Service(**config) as tm1:
    mdx = """
    SELECT
        NON EMPTY {[Product].[Product].Members} ON ROWS,
        NON EMPTY {[Period].[Period].Members} ON COLUMNS
    FROM [Sales]
    WHERE ([Scenario].[Actual], [Region].[North])
    """
    
    df = tm1.cells.execute_mdx_dataframe(
        mdx=mdx,
        skip_zeros=True,
        skip_consolidated_cells=True,
        skip_rule_derived_cells=True,
        use_blob=True,
        use_compact_json=True,
        sandbox_name="Development",
        include_attributes=True,
        top=10000
    )
    
    # Process DataFrame
    df_filtered = df[df['Value'] > 1000]
```

**After (DataService)**:
```python
with TM1Service(**config) as tm1:
    mdx = """
    SELECT
        NON EMPTY {[Product].[Product].Members} ON ROWS,
        NON EMPTY {[Period].[Period].Members} ON COLUMNS
    FROM [Sales]
    WHERE ([Scenario].[Actual], [Region].[North])
    """
    
    df = (tm1.data.mdx(mdx)
          .skip_zeros()
          .skip_consolidated()
          .skip_rule_derived()
          .use_blob()
          .use_compact_json()
          .sandbox("Development")
          .include_attributes()
          .top(10000)
          .as_dataframe())
    
    # Process DataFrame
    df_filtered = df[df['Value'] > 1000]
```

**Benefits**: All query options are visible and organized.

---

### Example 13: Using mdxpy with DataService

**Before (CellService)**:
```python
from mdxpy import MdxBuilder, MdxHierarchySet, Member

with TM1Service(**config) as tm1:
    mdx = (MdxBuilder.from_cube("Sales")
           .add_hierarchy_set_to_row_axis(
               MdxHierarchySet.all_members("Product", "Product")
           )
           .add_member_tuple_to_columns(Member.of("Period", "2024-Q1"))
           .to_mdx())
    
    df = tm1.cells.execute_mdx_dataframe(mdx, skip_zeros=True, use_blob=True)
```

**After (DataService)**:
```python
from mdxpy import MdxBuilder, MdxHierarchySet, Member

with TM1Service(**config) as tm1:
    mdx = (MdxBuilder.from_cube("Sales")
           .add_hierarchy_set_to_row_axis(
               MdxHierarchySet.all_members("Product", "Product")
           )
           .add_member_tuple_to_columns(Member.of("Period", "2024-Q1")))
    
    # Can pass MdxBuilder directly
    df = tm1.data.mdx(mdx).skip_zeros().use_blob().as_dataframe()
```

**Benefits**: Seamless integration with mdxpy, consistent builder pattern.

---

## Migration Examples

### Example 14: Gradual Migration

You can use both CellService and DataService side-by-side:

```python
with TM1Service(**config) as tm1:
    # Old code still works
    df1 = tm1.cells.execute_mdx_dataframe(mdx1, skip_zeros=True)
    
    # New code uses builder pattern
    df2 = tm1.data.mdx(mdx2).skip_zeros().as_dataframe()
    
    # Mix and match as needed
    combined = pd.concat([df1, df2])
```

---

### Example 15: Refactoring Helper Function

**Before**:
```python
def get_sales_data(tm1, period, region, use_sandbox=False):
    mdx = f"""
    SELECT
        {{[Product].[Product].Members}} ON ROWS,
        {{[Period].[Period].[{period}]}} ON COLUMNS
    FROM [Sales]
    WHERE ([Region].[{region}])
    """
    
    kwargs = {
        'mdx': mdx,
        'skip_zeros': True,
        'use_blob': True
    }
    
    if use_sandbox:
        kwargs['sandbox_name'] = 'Development'
    
    return tm1.cells.execute_mdx_dataframe(**kwargs)
```

**After**:
```python
def get_sales_data(tm1, period, region, use_sandbox=False):
    mdx = f"""
    SELECT
        {{[Product].[Product].Members}} ON ROWS,
        {{[Period].[Period].[{period}]}} ON COLUMNS
    FROM [Sales]
    WHERE ([Region].[{region}])
    """
    
    query = tm1.data.mdx(mdx).skip_zeros().use_blob()
    
    if use_sandbox:
        query = query.sandbox('Development')
    
    return query.as_dataframe()
```

**Benefits**: More readable, easier to add conditional options.

---

## Summary

The DataService builder pattern provides:

1. **Better Readability**: Code reads like natural language
2. **Easier Discovery**: IDE autocomplete guides you
3. **Flexibility**: Only specify options you need
4. **Consistency**: Same pattern for all operations
5. **Type Safety**: Better type hints and validation
6. **Backward Compatibility**: CellService still works

Start using DataService for new code, and gradually migrate existing code as needed.
