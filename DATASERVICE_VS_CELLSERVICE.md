# DataService vs CellService: Quick Reference

This document clarifies which operations belong in DataService (new builder pattern) vs CellService (existing service).

## Philosophy

**DataService**: Simplified, fluent interface for **common data operations**
- Read data (MDX, views, coordinates)
- Write data (dict, DataFrame)
- Async/parallel operations
- Focus on ease of use and discoverability

**CellService**: Comprehensive service for **all cell operations** including advanced/specialized features
- All DataService operations (via delegation)
- Cell tracing and analysis
- Low-level cellset manipulation
- Transaction log management
- Specialized operations

## Quick Decision Tree

```
Need to read/write data? 
├─ Yes, common operation → Use DataService
│  ├─ MDX query → tm1.data.mdx(...)
│  ├─ View query → tm1.data.view(...)
│  ├─ Single cell → tm1.data.coordinates(...)
│  └─ Write data → tm1.data.write(...) or tm1.data.write_dataframe(...)
│
└─ Need specialized operation? → Use CellService
   ├─ Cell tracing → tm1.cells.trace_cell_calculation(...)
   ├─ Feeder checking → tm1.cells.check_cell_feeders(...)
   ├─ Manual cellset → tm1.cells.create_cellset(...)
   └─ Transaction log → tm1.cells.activate_transactionlog(...)
```

---

## DataService Operations (New Builder Pattern)

### ✅ Included in DataService

#### Read Operations
| Operation | DataService Pattern | Description |
|-----------|-------------------|-------------|
| MDX Query | `tm1.data.mdx(query).as_dataframe()` | Execute MDX, get DataFrame |
| MDX Query | `tm1.data.mdx(query).as_dict()` | Execute MDX, get dict |
| MDX Query | `tm1.data.mdx(query).as_csv()` | Execute MDX, get CSV |
| MDX Query | `tm1.data.mdx(query).as_values()` | Execute MDX, get values only |
| MDX Query | `tm1.data.mdx(query).as_pivot()` | Execute MDX, get pivoted DataFrame |
| MDX Query | `tm1.data.mdx(query).count()` | Get cell count |
| View Query | `tm1.data.view(cube, view).as_dataframe()` | Execute view, get DataFrame |
| View Query | `tm1.data.view(cube, view).as_dict()` | Execute view, get dict |
| View Query | `tm1.data.view(cube, view).as_csv()` | Execute view, get CSV |
| Single Cell | `tm1.data.coordinates(cube, elements).as_value()` | Get single cell value |
| Multiple Cells | `tm1.data.coordinates(cube, elements).as_values()` | Get multiple cell values |
| Async Queries | `tm1.data.mdx_async(queries).as_dataframe()` | Execute queries in parallel |

#### Write Operations
| Operation | DataService Pattern | Description |
|-----------|-------------------|-------------|
| Write Dict | `tm1.data.write(cube, data).execute()` | Write dictionary to cube |
| Write DataFrame | `tm1.data.write_dataframe(cube, df).execute()` | Write DataFrame to cube |
| Write with Blob | `tm1.data.write(cube, data).use_blob().execute()` | Fast write via blob |
| Write with TI | `tm1.data.write(cube, data).use_ti().execute()` | Write via TI process |
| Incremental Write | `tm1.data.write(cube, data).increment().execute()` | Increment cell values |

#### Query Options (Fluent Methods)
| Option | Method | Description |
|--------|--------|-------------|
| Sandbox | `.sandbox("name")` | Execute in sandbox |
| Skip Zeros | `.skip_zeros()` | Skip cells with zero values |
| Skip Consolidated | `.skip_consolidated()` | Skip consolidated cells |
| Skip Rule-Derived | `.skip_rule_derived()` | Skip rule-derived cells |
| Use Blob | `.use_blob()` | Use blob for performance |
| Use Compact JSON | `.use_compact_json()` | Use compact JSON format |
| Include Attributes | `.include_attributes()` | Include element attributes |
| Pagination | `.top(n).skip(m)` | Limit and skip results |
| Max Workers | `.max_workers(n)` | Set parallel workers (async) |

#### Write Options (Fluent Methods)
| Option | Method | Description |
|--------|--------|-------------|
| Increment | `.increment()` | Increment instead of replace |
| Skip Non-Updateable | `.skip_non_updateable()` | Skip non-updateable cells |
| Use Blob | `.use_blob()` | Write via blob (fast) |
| Use TI | `.use_ti()` | Write via TI process |
| Use Cellset | `.use_cellset()` | Write via cellset |
| Deactivate TX Log | `.deactivate_transaction_log()` | Deactivate before write |
| Reactivate TX Log | `.reactivate_transaction_log()` | Reactivate after write |
| Use Changeset | `.use_changeset()` | Group writes in changeset |
| Precision | `.precision(n)` | Set precision for TI writes |
| Allow Spread | `.allow_spread()` | Allow spreading |

---

## CellService Operations (Existing Service)

### ❌ NOT Included in DataService (Use CellService)

#### Cell Tracing & Analysis
| Operation | CellService Method | Description |
|-----------|-------------------|-------------|
| Trace Calculation | `tm1.cells.trace_cell_calculation(...)` | Trace how cell is calculated |
| Trace Feeders | `tm1.cells.trace_cell_feeders(...)` | Trace cell feeders |
| Check Feeders | `tm1.cells.check_cell_feeders(...)` | Check if feeders work |

**Why CellService?** These are specialized debugging/analysis operations used less frequently.

---

#### Clear Operations (For Now)
| Operation | CellService Method | Description |
|-----------|-------------------|-------------|
| Clear Cube | `tm1.cells.clear(cube)` | Clear entire cube |
| Clear with MDX | `tm1.cells.clear_with_mdx(cube, mdx)` | Clear cells matching MDX |
| Clear with DataFrame | `tm1.cells.clear_with_dataframe(cube, df)` | Clear cells from DataFrame |
| Relative Proportional Spread | `tm1.cells.relative_proportional_spread(...)` | Spreading operations |
| Clear Spread | `tm1.cells.clear_spread(...)` | Clear spread |

**Why CellService?** Clear operations are less common and can be added to DataService later if needed.

---

#### Low-Level Cellset Operations
| Operation | CellService Method | Description |
|-----------|-------------------|-------------|
| Create Cellset | `tm1.cells.create_cellset(mdx)` | Create cellset manually |
| Delete Cellset | `tm1.cells.delete_cellset(cellset_id)` | Delete cellset manually |
| Update Cellset | `tm1.cells.update_cellset(...)` | Update existing cellset |
| Extract Cellset Raw | `tm1.cells.extract_cellset_raw(...)` | Low-level extraction |
| Extract Cellset Metadata | `tm1.cells.extract_cellset_metadata_raw(...)` | Get cellset metadata |
| Extract Cellset Partition | `tm1.cells.extract_cellset_partition(...)` | Extract partition |

**Why CellService?** These are low-level operations for advanced users who need fine-grained control.

---

#### Transaction Log Management
| Operation | CellService Method | Description |
|-----------|-------------------|-------------|
| Check TX Log Status | `tm1.cells.transaction_log_is_active(cube)` | Check if TX log is active |
| Activate TX Log | `tm1.cells.activate_transactionlog(cube)` | Activate transaction log |
| Deactivate TX Log | `tm1.cells.deactivate_transactionlog(cube)` | Deactivate transaction log |

**Why CellService?** Direct transaction log management is advanced. DataService provides `.deactivate_transaction_log()` and `.reactivate_transaction_log()` as write options.

---

#### Changeset Management
| Operation | CellService Method | Description |
|-----------|-------------------|-------------|
| Begin Changeset | `tm1.cells.begin_changeset()` | Begin changeset manually |
| End Changeset | `tm1.cells.end_changeset(changeset)` | End changeset manually |
| Undo Changeset | `tm1.cells.undo_changeset(changeset)` | Undo changeset |

**Why CellService?** Manual changeset management is advanced. DataService provides `.use_changeset()` as a write option.

---

#### Specialized Output Formats
| Operation | CellService Method | Description |
|-----------|-------------------|-------------|
| UI Dygraph | `tm1.cells.execute_mdx_ui_dygraph(...)` | Format for Dygraph charting |
| UI Array | `tm1.cells.execute_mdx_ui_array(...)` | Format for UI arrays |
| Elements-Value Dict | `tm1.cells.execute_mdx_elements_value_dict(...)` | Special dict format |

**Why CellService?** These are specialized formats for specific UI frameworks. Can be added to DataService if there's demand.

---

## Migration Strategy

### When to Use DataService
✅ **Use DataService when**:
- Reading data for analysis (MDX, views)
- Writing data from Python (dict, DataFrame)
- You want clean, readable code
- You're new to TM1py
- You want IDE autocomplete to guide you

### When to Use CellService
✅ **Use CellService when**:
- Debugging cell calculations (tracing)
- Need low-level cellset control
- Managing transaction logs directly
- Using specialized output formats
- Migrating old code (backward compatibility)

### Both Work Together
You can use both in the same code:

```python
with TM1Service(**config) as tm1:
    # Use DataService for common operations
    df = tm1.data.mdx(query).skip_zeros().as_dataframe()
    
    # Use CellService for specialized operations
    trace = tm1.cells.trace_cell_calculation(
        cube_name="Sales",
        elements="2024,Actual,North,Product1"
    )
    
    # Write with DataService
    tm1.data.write("Sales", data).use_blob().execute()
```

---

## Future Considerations

### May Be Added to DataService Later
- Clear operations (if there's demand)
- Additional specialized output formats
- More advanced query options

### Will Likely Stay in CellService
- Cell tracing (specialized debugging)
- Low-level cellset manipulation (advanced users)
- Direct transaction log management (advanced users)
- Manual changeset management (advanced users)

---

## Summary

| Aspect | DataService | CellService |
|--------|-------------|-------------|
| **Purpose** | Common data operations | All cell operations |
| **Interface** | Fluent builder pattern | Traditional method calls |
| **Target Users** | All users, especially new users | All users, especially power users |
| **Scope** | Read/write data | Everything including advanced features |
| **Discoverability** | High (IDE autocomplete) | Medium (need to know method names) |
| **Backward Compatibility** | N/A (new) | 100% (unchanged) |
| **When to Use** | Default choice for data ops | Specialized/advanced operations |

**Recommendation**: Start with DataService for all new code. Use CellService when you need specialized features not available in DataService.
