# DataService Implementation Tasks

## Overview

This document outlines the incremental implementation plan for the DataService builder pattern in TM1py. The plan prioritizes:

1. **Readers first, writers second** - Read operations are more common and provide immediate value
2. **Incremental testing** - Each implementation step has corresponding tests
3. **Test-driven approach** - Tests written immediately after (or before) implementation
4. **Parity validation** - Ensure DataService matches CellService behavior

---

## Implementation Strategy

### Key Principles

- **Build → Test → Integrate** cycle for each feature
- **Mixin-based architecture** to reduce code duplication
- **Delegation pattern** to reuse existing CellService logic
- **Backward compatibility** - CellService remains unchanged
- **Type safety** - Strong type hints throughout

### Testing Approach

Each phase includes:
- **Unit tests** - Test builders in isolation
- **Integration tests** - Test with real TM1 instance
- **Parity tests** - Verify DataService === CellService output
- **Option chaining tests** - Verify fluent interface works correctly

---

## Phase 1: Foundation & Infrastructure ✅ COMPLETE (6 tasks)

**Goal**: Set up core infrastructure and base classes

### Tasks

1. ✅ **Create base mixin classes for code reuse**
   - ✅ `SandboxMixin` - sandbox() method
   - ✅ `FilterMixin` - skip_zeros(), skip_consolidated(), skip_rule_derived()
   - ✅ `PerformanceMixin` - use_blob(), use_compact_json(), use_iterative_json()
   - ✅ `PaginationMixin` - top(), skip()
   - ✅ `AttributeMixin` - include_attributes(), cell_properties()

2. ✅ **Write unit tests for mixin classes**
   - ✅ Test each mixin independently (60 tests)
   - ✅ Verify return self for chaining
   - ✅ Test default values

3. ✅ **Create DataService entry point class**
   - ✅ Inherit from ObjectService
   - ✅ Initialize with RestService
   - ✅ Create CellService instance for delegation

4. ✅ **Write tests for DataService initialization**
   - ✅ Test instantiation
   - ✅ Verify CellService delegation
   - ✅ Test basic structure

5. ✅ **Add DataService to TM1Service**
   - ✅ Add `self.data = DataService(self._tm1_rest)` to TM1Service.__init__

6. ✅ **Write integration test for TM1Service.data**
   - ✅ Verify `tm1.data` is accessible
   - ✅ Verify proper initialization

**Deliverable**: ✅ Working DataService infrastructure with tested mixins

---

## Phase 2: MDX Query Builder ✅ COMPLETE (24 tasks)

**Goal**: Implement complete MDX query functionality with all output formats

### Tasks Overview

✅ 1-5: Basic MDX infrastructure and as_dict()
✅ 6-7: as_dataframe() implementation
✅ 8-9: as_csv() implementation
✅ 10-11: as_values() implementation
✅ 12-13: as_pivot() implementation
✅ 14-15: count() implementation
✅ 16-17: as_raw() implementation (raw TM1 response)
✅ 18-19: as_cellset_id() implementation (cellset ID for manual operations)
✅ 20-23: Option chaining tests
✅ 24: Parity tests

**Note**: Originally named MdxQueryBuilder, renamed to QueryExecutor to avoid anti-pattern with mdxpy.MdxBuilder

**Deliverable**: ✅ Fully functional QueryExecutor with all 8 output formats (including raw and cellset_id)

---

## Phase 3: Additional Read Builders ✅ COMPLETE (29 tasks)

**Goal**: Implement ViewQueryExecutor and CoordinateQueryExecutor

### ViewQueryExecutor (18 tasks) ✅
- ✅ Skeleton class with mixin inheritance
- ✅ as_dict() - Execute view and return dictionary
- ✅ as_dataframe() - Execute view and return DataFrame
- ✅ as_csv() - Execute view and return CSV string
- ✅ as_values() - Execute view and return values list
- ✅ count() - Get cell count from view
- ✅ as_raw() - Get raw TM1 response
- ✅ as_cellset_id() - Get cellset ID for manual operations
- ✅ Option chaining tests (21 tests total)
- ✅ Parity tests with CellService
- ✅ DataService.view() entry point

### CoordinateQueryExecutor (8 tasks) ✅
- ✅ Skeleton class with SandboxMixin
- ✅ as_value() - Read single cell value
- ✅ as_values() - Read multiple cell values
- ✅ Smart coordinate detection (single vs multiple)
- ✅ Option chaining tests (17 tests total)
- ✅ Parity tests with CellService
- ✅ DataService.coordinates() entry point

### MdxBuilder Support (3 tasks) ✅ BONUS
- ✅ QueryExecutor accepts Union[str, MdxBuilder]
- ✅ DataService.mdx() signature updated
- ✅ 9 MdxBuilder-specific tests added

**Deliverable**: ✅ Complete read functionality (MDX, views, coordinates) with MdxBuilder support

---

## Phase 4: Async Read Operations (13 tasks)

**Goal**: Implement parallel query execution

### Tasks Overview
- AsyncQueryBuilder with max_workers()
- as_dataframe() and as_dict() for async
- Performance tests
- Optional mdx_auto() helper
- Parity tests

**Deliverable**: Async query execution with performance benefits

---

## Phase 5: Write Operations (15 tasks)

**Goal**: Implement write builders for dict and DataFrame

### DictWriteBuilder (10 tasks)
- WriteMixin base class
- Method selection (blob/TI/cellset)
- execute() implementation
- Option chaining and parity tests

### DataFrameWriteBuilder (5 tasks)
- Skeleton and execute()
- Tests and parity validation

**Deliverable**: Complete write functionality

---

## Phase 6: Documentation & Migration (7 tasks)

**Goal**: Comprehensive documentation and migration support

### Tasks
1. Usage examples document
2. Migration guide
3. Docstrings for DataService
4. Docstrings for builders
5. API reference
6. README updates
7. Changelog entry

**Deliverable**: Complete documentation suite

---

## Summary Statistics

- **Total Tasks**: 83 tasks across 6 phases
- **Phase 1**: 6 tasks (Foundation) ✅ COMPLETE
- **Phase 2**: 24 tasks (MDX Builder) - 20 complete, 4 new tasks for raw/cellset_id
- **Phase 3**: 18 tasks (View & Coordinate Builders)
- **Phase 4**: 13 tasks (Async)
- **Phase 5**: 15 tasks (Write Operations)
- **Phase 6**: 7 tasks (Documentation)

---

## Success Criteria

### Functional Requirements
- ✅ All read operations work (MDX, view, coordinates)
- ✅ All write operations work (dict, DataFrame)
- ✅ Async operations provide performance benefits
- ✅ All options chain correctly
- ✅ All output formats supported

### Quality Requirements
- ✅ 100% parity with CellService
- ✅ Comprehensive test coverage (unit + integration)
- ✅ Type hints throughout
- ✅ Complete documentation
- ✅ No breaking changes to existing code

### User Experience
- ✅ Intuitive fluent interface
- ✅ IDE autocomplete works well
- ✅ Clear error messages
- ✅ Easy migration path
- ✅ Better discoverability than CellService

---

## Next Steps

1. Review this implementation plan with stakeholders
2. Set up development branch
3. Begin Phase 1: Foundation & Infrastructure
4. Follow incremental build → test → integrate cycle
5. Regular progress reviews after each phase
