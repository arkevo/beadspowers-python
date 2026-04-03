# Planning Context

Complementary planning information for risk assessment, red flags, and testing strategy. Use alongside `/superpowers:writing-plans` for comprehensive implementation planning.

**Purpose:** Provide additional context that enhances planning without duplicating the core planning workflow.

---

## Pre-Planning Risk Assessment

Before diving into implementation details, assess these risk factors:

### Technical Risk Matrix

| Factor | Low | Medium | High |
|--------|-----|--------|------|
| **Scope** | Single file change | 2-5 files | 6+ files or new module |
| **Complexity** | Simple logic | Moderate state | Complex async/state |
| **Dependencies** | None | Internal only | External packages |
| **Platform** | Single OS | 2 platforms | 3+ platforms or embedded |
| **Data** | Read-only | Local writes | Remote APIs, auth |
| **Testing** | Existing tests cover | Some new tests | Significant test work |

**Overall Risk Score:**
- 0-2 Low factors: Low risk - proceed with standard planning
- 3-4 Low factors: Medium risk - add extra verification steps
- 5-6 High factors: High risk - consider phased approach

---

## Red Flags Checklist

Watch for these warning signs during planning:

### Requirement Red Flags
- [ ] Vague acceptance criteria ("make it better", "fix the issue")
- [ ] Missing edge case definitions
- [ ] Unstated performance requirements
- [ ] Unclear error handling expectations
- [ ] No mention of backwards compatibility

### Technical Red Flags
- [ ] Touching core infrastructure (auth, state, routing)
- [ ] Modifying generated code patterns
- [ ] Changing database schema
- [ ] Updating critical dependencies
- [ ] Cross-platform behavioral differences expected

### Process Red Flags
- [ ] No existing tests for affected code
- [ ] Undocumented code being modified
- [ ] Multiple PRs touching same files
- [ ] Deadline pressure overriding quality

**If 3+ red flags:** Pause and clarify requirements before proceeding.

---

## Testing Strategy Template

### Test Coverage Planning

| Layer | What to Test | Approach |
|-------|-------------|----------|
| **Unit** | Business logic, utilities, models | Fakes over mocks, edge cases |
| **Integration** | Multi-component flows, repositories | pytest fixtures, fakes |
| **End-to-End** | HTTP endpoints, CLI entry points | pytest + httpx/TestClient |

### Edge Cases to Plan For

**Input Validation:**
- Null/empty values
- Boundary values (0, -1, max)
- Invalid formats
- Unicode/special characters

**State Transitions:**
- Initial → Loading → Success
- Initial → Loading → Error
- Error → Retry → Success
- Offline → Online sync

**Async Operations:**
- Network timeout
- Concurrent requests
- Cancellation mid-flight
- Retry exhaustion

---

## Dependency Impact Analysis

When adding or updating dependencies:

### Questions to Answer
1. **Why this package?** What problem does it solve?
2. **Alternatives considered?** Built-in solutions?
3. **Maintenance status?** Last update, issue response time?
4. **Size impact?** Package/install size increase?
5. **Breaking changes?** Migration path for updates?

### Dependency Check Commands
```bash
# Check installed packages
pip list

# See dependency tree
pip show <package_name>

# Check for vulnerabilities
pip-audit

# Check for outdated packages
pip list --outdated
```

---

## Rollback Planning

For significant changes, document the rollback strategy:

### Rollback Checklist
- [ ] Can changes be reverted with a single commit?
- [ ] Are database migrations reversible?
- [ ] Is feature flagged for gradual rollout?
- [ ] What's the blast radius if this fails in production?

### Feature Flag Template
```python
import os

class FeatureFlags:
    @staticmethod
    def new_feature_enabled() -> bool:
        return os.getenv("ENABLE_NEW_FEATURE", "false").lower() == "true"

# Usage
if FeatureFlags.new_feature_enabled():
    return NewImplementation()
else:
    return LegacyImplementation()
```

---

## Performance Considerations

### Questions for Performance-Sensitive Changes

1. **Hot path impact?** Will this slow down critical execution paths?
2. **Large data handling?** Using generators/itertools for large sequences?
3. **Caching?** Appropriate use of `@functools.lru_cache` or `@functools.cache`?
4. **Network calls?** Connection pooling, timeouts, retries?
5. **Memory?** Proper cleanup of resources, context managers?

### Performance Warning Signs
- Expensive operations in properties (should be methods)
- Loading entire datasets into memory (should use generators)
- Missing connection pooling for HTTP clients
- Unbounded caches or growing collections
- Missing `__slots__` on high-volume data classes

---

## Documentation Requirements

### When to Update Docs
- [ ] New public API added → Google-style docstrings
- [ ] Architecture change → Update relevant memory file
- [ ] New dependency → Note in README or relevant doc
- [ ] Breaking change → Migration guide

### Memory File Candidates
After implementation, consider if these warrant memory updates:
- New architectural patterns introduced
- Complex business logic that needs explanation
- Integration details with external services
- Common pitfalls discovered during implementation

---

## Usage

Invoke this command before `/superpowers:writing-plans` to:
1. Assess risk level of the planned work
2. Identify red flags that need clarification
3. Plan testing strategy upfront
4. Consider rollback and performance implications

**Example workflow:**
```
1. User describes feature
2. /planning-context → Risk assessment, red flags
3. /superpowers:writing-plans → Detailed implementation plan
4. Review and approve plan
5. /superpowers:execute-plan → Implementation
```

---

## Beads Task Context Loading

When planning a Beads task, Claude auto-loads context before invoking `/superpowers:writing-plans`:

1. Check for current in_progress task (ask if none)
2. Fetch task details: `bd show <id>`
3. Display context:
   ```
   ## Task Context (from Beads)
   **Task:** bd-xxxx "[Task Title]"
   **Epic:** bd-yyyy "[Epic Title]"
   **Priority:** P[X]
   **Blocks:** [tasks waiting on this]
   **Description:** [Task description]
   ```
4. Search `docs/plans/` for existing plan matching task
5. If found → offer: use existing plan vs write new plan
6. If not found → ask for additional requirements → start planning

Update `.beads/.workflow-step` to `Planning` when entering planning phase.

---

## Integration with Beads

When planning Beads tasks:
- Reference task ID and description from `bd show <id>`
- Note any blocking/blocked dependencies
- Ensure plan addresses the full task scope
- Flag if task should be split into smaller tasks
