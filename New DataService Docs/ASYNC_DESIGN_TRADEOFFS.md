# Async Design: Tradeoffs Analysis

## The Question

Should async be:
- **Option A**: Separate entry point (`mdx_async()`)
- **Option B**: Fluent option (`.async_mode()` or auto-detect)

## Option A: Separate Entry Point (Current Design)

### Usage
```python
# Single query (sync)
df = tm1.data.mdx(query).skip_zeros().as_dataframe()

# Multiple queries (async)
df = tm1.data.mdx_async([query1, query2, query3]).max_workers(8).skip_zeros().as_dataframe()
```

### ✅ Pros

1. **Clear Intent**: Immediately obvious this is async
   ```python
   mdx_async([...])  # "I'm doing async!"
   ```

2. **Type Safety**: Different signatures
   ```python
   def mdx(self, mdx: Union[str, MdxBuilder]) -> MdxQueryBuilder:
       # Single query
   
   def mdx_async(self, mdx_list: List[Union[str, MdxBuilder]]) -> AsyncQueryBuilder:
       # Multiple queries
   ```

3. **Different Return Types**: Can return different builder types
   - `MdxQueryBuilder` for single queries
   - `AsyncQueryBuilder` for multiple queries
   - Each can have specialized methods

4. **No Conditional Logic**: Builder doesn't need to check "am I async?"
   ```python
   class MdxQueryBuilder:
       def as_dataframe(self):
           # Always sync, simple
           return self._cell_service.execute_mdx_dataframe(...)
   
   class AsyncQueryBuilder:
       def as_dataframe(self):
           # Always async, simple
           return self._cell_service.execute_mdx_dataframe_async(...)
   ```

5. **Follows CellService Pattern**: CellService has separate methods
   - `execute_mdx_dataframe()` vs `execute_mdx_dataframe_async()`

6. **Easier to Implement**: No conditional logic in builders

### ❌ Cons

1. **More Entry Points**: Users need to know two methods
   - `mdx()` for single
   - `mdx_async()` for multiple

2. **Less Fluent**: Can't chain from single to async
   ```python
   # Can't do this:
   tm1.data.mdx(query).async_mode()  # ❌
   ```

3. **Duplication**: Two builders with similar code
   - `MdxQueryBuilder` 
   - `AsyncQueryBuilder`

---

## Option B: Async as Fluent Option

### Approach B1: Explicit `.async_mode()`

```python
# Single query (sync)
df = tm1.data.mdx(query).skip_zeros().as_dataframe()

# Multiple queries (async)
df = tm1.data.mdx([query1, query2, query3]).async_mode().max_workers(8).skip_zeros().as_dataframe()
```

### Approach B2: Auto-detect based on input type

```python
# Single query (sync) - auto-detected
df = tm1.data.mdx(query).skip_zeros().as_dataframe()

# Multiple queries (async) - auto-detected
df = tm1.data.mdx([query1, query2, query3]).max_workers(8).skip_zeros().as_dataframe()
```

### ✅ Pros

1. **Single Entry Point**: Only need to know `mdx()`
   ```python
   tm1.data.mdx(...)  # Works for both sync and async
   ```

2. **More Fluent**: Consistent pattern
   ```python
   tm1.data.mdx(...).skip_zeros().use_blob().as_dataframe()
   # Works for both single and multiple queries
   ```

3. **Less Code**: One builder instead of two
   - No `AsyncQueryBuilder` needed
   - All logic in `MdxQueryBuilder`

4. **Flexible**: Can switch between sync/async easily
   ```python
   # Easy to change from sync to async
   queries = [query1] if single else [query1, query2, query3]
   df = tm1.data.mdx(queries).as_dataframe()
   ```

### ❌ Cons

1. **Type Complexity**: Union types everywhere
   ```python
   def mdx(self, mdx: Union[str, MdxBuilder, List[Union[str, MdxBuilder]]]) -> MdxQueryBuilder:
       # Complex signature
   ```

2. **Conditional Logic**: Builder needs to check mode
   ```python
   class MdxQueryBuilder:
       def __init__(self, cell_service, mdx):
           if isinstance(mdx, list):
               self._is_async = True
               self._mdx_list = mdx
           else:
               self._is_async = False
               self._mdx = mdx
       
       def as_dataframe(self):
           if self._is_async:
               return self._cell_service.execute_mdx_dataframe_async(...)
           else:
               return self._cell_service.execute_mdx_dataframe(...)
   ```

3. **Hidden Behavior**: Not obvious when async happens
   ```python
   # Is this async? Have to check the input
   df = tm1.data.mdx(queries).as_dataframe()
   ```

4. **Method Availability Confusion**: Some methods only work in async
   ```python
   # max_workers only makes sense for async
   tm1.data.mdx(single_query).max_workers(8)  # ❌ Doesn't make sense
   # But type system can't prevent it
   ```

5. **Error Handling Complexity**: Different errors for sync vs async
   ```python
   def max_workers(self, n: int):
       if not self._is_async:
           raise ValueError("max_workers only available for async queries")
       self._max_workers = n
       return self
   ```

6. **Return Type Ambiguity**: What does `as_dataframe()` return?
   ```python
   # For sync: returns DataFrame
   # For async: returns combined DataFrame
   # Type hints can't express this easily
   def as_dataframe(self) -> pd.DataFrame:
       # Actually returns different things depending on mode
   ```

---

## Detailed Comparison

| Aspect | Option A: Separate Entry | Option B: Fluent Option |
|--------|-------------------------|------------------------|
| **Clarity** | ✅ Very clear | ⚠️ Less clear (hidden) |
| **Type Safety** | ✅ Strong types | ❌ Weak types (unions) |
| **Simplicity** | ✅ Simple logic | ❌ Complex conditionals |
| **Discoverability** | ⚠️ Two methods to learn | ✅ One method to learn |
| **Consistency** | ⚠️ Different entry points | ✅ Same pattern |
| **Implementation** | ✅ Easy (separate classes) | ❌ Hard (conditional logic) |
| **Maintenance** | ⚠️ Two classes to maintain | ✅ One class to maintain |
| **Error Messages** | ✅ Clear (wrong method) | ❌ Runtime errors |
| **IDE Support** | ✅ Good (separate signatures) | ⚠️ Confusing (union types) |
| **Flexibility** | ❌ Can't switch easily | ✅ Easy to switch |

---

## Code Complexity Comparison

### Option A: Separate Entry Point

```python
class DataService:
    def mdx(self, mdx: Union[str, MdxBuilder]) -> MdxQueryBuilder:
        return MdxQueryBuilder(self._cell_service, mdx)
    
    def mdx_async(self, mdx_list: List[Union[str, MdxBuilder]]) -> AsyncQueryBuilder:
        return AsyncQueryBuilder(self._cell_service, mdx_list)

class MdxQueryBuilder:
    def __init__(self, cell_service, mdx):
        self._cell_service = cell_service
        self._mdx = mdx
    
    def as_dataframe(self):
        return self._cell_service.execute_mdx_dataframe(self._mdx, ...)

class AsyncQueryBuilder:
    def __init__(self, cell_service, mdx_list):
        self._cell_service = cell_service
        self._mdx_list = mdx_list
        self._max_workers = 8
    
    def max_workers(self, n: int):
        self._max_workers = n
        return self
    
    def as_dataframe(self):
        return self._cell_service.execute_mdx_dataframe_async(
            self._mdx_list, 
            max_workers=self._max_workers,
            ...
        )
```

**Lines of Code**: ~50 (two simple classes)
**Complexity**: Low (no conditionals)

---

### Option B: Fluent Option (Auto-detect)

```python
class DataService:
    def mdx(self, mdx: Union[str, MdxBuilder, List[Union[str, MdxBuilder]]]) -> MdxQueryBuilder:
        return MdxQueryBuilder(self._cell_service, mdx)

class MdxQueryBuilder:
    def __init__(self, cell_service, mdx):
        self._cell_service = cell_service
        
        # Detect mode
        if isinstance(mdx, list):
            self._is_async = True
            self._mdx_list = [m.to_mdx() if isinstance(m, MdxBuilder) else m for m in mdx]
            self._max_workers = 8
        else:
            self._is_async = False
            self._mdx = mdx.to_mdx() if isinstance(mdx, MdxBuilder) else mdx
    
    def max_workers(self, n: int):
        if not self._is_async:
            raise ValueError("max_workers is only available for async queries (pass a list of queries)")
        self._max_workers = n
        return self
    
    def skip_zeros(self, skip: bool = True):
        self._skip_zeros = skip
        return self
    
    def as_dataframe(self):
        if self._is_async:
            return self._cell_service.execute_mdx_dataframe_async(
                mdx_list=self._mdx_list,
                max_workers=self._max_workers,
                skip_zeros=self._skip_zeros,
                ...
            )
        else:
            return self._cell_service.execute_mdx_dataframe(
                mdx=self._mdx,
                skip_zeros=self._skip_zeros,
                ...
            )
    
    def as_dict(self):
        if self._is_async:
            return self._cell_service.execute_mdx_async(
                mdx_list=self._mdx_list,
                max_workers=self._max_workers,
                ...
            )
        else:
            return self._cell_service.execute_mdx(
                mdx=self._mdx,
                ...
            )
    
    # Every terminal method needs if/else
    def as_csv(self): ...
    def as_values(self): ...
    def count(self): ...
```

**Lines of Code**: ~80 (one complex class)
**Complexity**: High (conditionals everywhere)

---

## Real-World Usage Comparison

### Scenario 1: Simple Read

**Option A**:
```python
df = tm1.data.mdx(query).skip_zeros().as_dataframe()
```

**Option B**:
```python
df = tm1.data.mdx(query).skip_zeros().as_dataframe()
```

**Winner**: Tie ✅

---

### Scenario 2: Async Read

**Option A**:
```python
df = tm1.data.mdx_async([q1, q2, q3]).max_workers(16).skip_zeros().as_dataframe()
```

**Option B**:
```python
df = tm1.data.mdx([q1, q2, q3]).max_workers(16).skip_zeros().as_dataframe()
```

**Winner**: Option B (slightly cleaner) ⚠️

---

### Scenario 3: Dynamic Query Count

**Option A**:
```python
queries = get_queries()  # Could be 1 or many

if len(queries) == 1:
    df = tm1.data.mdx(queries[0]).skip_zeros().as_dataframe()
else:
    df = tm1.data.mdx_async(queries).max_workers(8).skip_zeros().as_dataframe()
```

**Option B**:
```python
queries = get_queries()  # Could be 1 or many

# Works for both!
df = tm1.data.mdx(queries if len(queries) > 1 else queries[0]).skip_zeros().as_dataframe()
```

**Winner**: Option B (more flexible) ✅

---

### Scenario 4: Type Hints in User Code

**Option A**:
```python
def process_data(builder: MdxQueryBuilder) -> pd.DataFrame:
    return builder.skip_zeros().as_dataframe()

# Clear types
sync_builder = tm1.data.mdx(query)
async_builder = tm1.data.mdx_async([q1, q2])
```

**Option B**:
```python
def process_data(builder: MdxQueryBuilder) -> pd.DataFrame:
    return builder.skip_zeros().as_dataframe()

# Same type, but different behavior
builder = tm1.data.mdx(query_or_queries)  # Could be sync or async!
```

**Winner**: Option A (clearer types) ✅

---

## Recommendation

### 🏆 Recommended: **Option A (Separate Entry Point)**

**Rationale**:
1. **Clarity > Brevity**: Being explicit about async is more important than saving a few characters
2. **Type Safety**: Strong typing prevents errors at development time
3. **Simplicity**: Easier to implement, test, and maintain
4. **Follows Patterns**: Consistent with CellService and Python conventions
5. **Better Errors**: Wrong method = clear error, not runtime confusion

### 🎯 Compromise: Make it Easy to Switch

Even with separate entry points, we can make it easy to switch:

```python
# Helper method for dynamic cases
class DataService:
    def mdx_auto(self, mdx: Union[str, MdxBuilder, List[Union[str, MdxBuilder]]]):
        """Auto-detect sync vs async based on input type"""
        if isinstance(mdx, list):
            return self.mdx_async(mdx)
        else:
            return self.mdx(mdx)

# Usage
queries = get_queries()  # Could be 1 or many
df = tm1.data.mdx_auto(queries).skip_zeros().as_dataframe()
```

This gives you:
- ✅ Clear separate methods for explicit cases
- ✅ Auto-detect helper for dynamic cases
- ✅ Type safety where it matters
- ✅ Flexibility where you need it

---

## Final Verdict

| Criteria | Winner |
|----------|--------|
| Clarity | Option A ✅ |
| Type Safety | Option A ✅ |
| Implementation Simplicity | Option A ✅ |
| Maintenance | Option A ✅ |
| Flexibility | Option B ⚠️ |
| Brevity | Option B ⚠️ |

**Overall Winner: Option A (Separate Entry Point)** with optional `mdx_auto()` helper for dynamic cases.

---

## Implementation Recommendation

```python
class DataService:
    # Primary methods (explicit)
    def mdx(self, mdx: Union[str, MdxBuilder]) -> MdxQueryBuilder:
        """Execute single MDX query"""
        return MdxQueryBuilder(self._cell_service, mdx)
    
    def mdx_async(self, mdx_list: List[Union[str, MdxBuilder]]) -> AsyncQueryBuilder:
        """Execute multiple MDX queries in parallel"""
        return AsyncQueryBuilder(self._cell_service, mdx_list)
    
    # Helper method (for dynamic cases)
    def mdx_auto(self, mdx: Union[str, MdxBuilder, List[Union[str, MdxBuilder]]]):
        """Auto-detect sync vs async based on input type.
        
        Use this when you don't know at development time whether you'll have
        one query or multiple queries.
        """
        if isinstance(mdx, list):
            return self.mdx_async(mdx)
        else:
            return self.mdx(mdx)
```

This gives users:
- **Explicit control** when they know what they want
- **Flexibility** when they need it
- **Clear documentation** about what's happening
