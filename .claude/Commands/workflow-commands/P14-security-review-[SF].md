# Security Review (Phase 14)

Code review for security vulnerabilities, with focus on Python security patterns.

**Verification Levels:** Standard* (auto-triggered), Full
**Auto-triggers when:** Files match sensitive patterns (see below)

## Auto-Trigger Patterns

This phase runs in Standard and Full verification only when a file in the changed
set matches one of these patterns; an unknown changed set counts as a match. Both
tiers carry the same list in their Phase 14 gate, so keep all three in step.

### Path Patterns
- `src/**/auth/**`, `src/**/api/**`, `src/**/service*/**`, `src/**/repository/**`,
  `src/**/network/**`, `src/**/http/**` - code that handles auth, requests and
  data access
- `**/migrations/**`, `alembic/versions/**`, `**/*.sql` - schema and database
  authorization changes
- settings modules (`**/settings.py`, `**/settings/**`) - debug flags and secrets
- environment files (`.env`, `.env.*`) - secrets that must never be committed

### Content Patterns (file contains)
- `apiKey`, `api_key`, `secret`, `token`, `password`, `credential` (any case)
- `requests`, `httpx`, `http`
- `eval(`, `exec(`, `pickle`, `yaml.load`, `subprocess`, `shell=True`,
  `verify=False`, `DEBUG`, `random.`
- `GRANT`, `REVOKE`, `CREATE POLICY`, `ROW LEVEL SECURITY`, `SECURITY DEFINER`

---

## Analysis Workflow

### Step 1: Identify Changed Files

**For local changes:**
```bash
# Check session state for modified files
cat .beads/.session-state.json | jq -r '.modified_files[]'
```

**For PR:**
```bash
gh pr diff --name-only
```

Filter to files matching auto-trigger patterns.

### Step 2: Python-Specific Security Checks

For each changed Python file, check:

#### 2.1 Hardcoded Secrets
```python
# BAD: Hardcoded API keys
api_key = 'sk_live_abc123'
db_password = 'supersecret123'

# GOOD: Environment variables or python-dotenv
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.environ.get('API_KEY')
```

**Search pattern:**
```bash
grep -rn "api_key\s*=\s*['\"]" src/
grep -rn "secret\s*=\s*['\"]" src/
grep -rn "password\s*=\s*['\"]" src/
```

#### 2.2 HTTPS Enforcement
```python
# BAD: HTTP URLs (except localhost)
url = 'http://api.example.com/data'

# GOOD: Always HTTPS for external URLs
url = 'https://api.example.com/data'
```

#### 2.3 SQL Injection
```python
# BAD: String interpolation in SQL queries
cursor.execute(f"SELECT * FROM users WHERE id = {user_id}")
cursor.execute("SELECT * FROM users WHERE name = '%s'" % name)

# GOOD: Parameterized queries
cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
cursor.execute("SELECT * FROM users WHERE name = %s", (name,))
```

#### 2.4 Dangerous Functions
```python
# BAD: eval/exec on untrusted data
result = eval(user_input)
# exec(user_code) -- never use on untrusted input

# BAD: pickle.loads on untrusted data
# data = pickle.loads(untrusted_bytes)  -- do not deserialize untrusted data

# BAD: yaml.load without a safe loader on untrusted data
# config = yaml.load(untrusted_text)  -- use yaml.safe_load instead

# GOOD: Use safe alternatives (ast.literal_eval, json, etc.)
import ast
result = ast.literal_eval(user_input)  # only for literals
data = json.loads(untrusted_string)
```

#### 2.5 Subprocess Safety
```python
# BAD: shell=True with user input
import subprocess
subprocess.run(cmd, shell=True)

import os
os.system(user_input)

# GOOD: Pass arguments as list, avoid shell=True
subprocess.run(['ls', '-la', path], shell=False)
```

#### 2.6 SSL Verification
```python
# BAD: Disabling SSL certificate verification
requests.get(url, verify=False)
httpx.get(url, verify=False)

# GOOD: Always verify certificates
requests.get(url)  # verify=True by default
```

#### 2.7 Debug Mode in Production
```python
# BAD: Debug mode enabled in production config
DEBUG = True
app.run(debug=True)

# GOOD: Read from environment
DEBUG = os.environ.get('DEBUG', 'false').lower() == 'true'
app.run(debug=DEBUG)
```

#### 2.8 Insecure Random
```python
# BAD: Using random module for security-sensitive values
import random
token = random.randint(100000, 999999)
session_id = ''.join(random.choices(string.ascii_letters, k=32))

# GOOD: Use secrets module for security-sensitive values
import secrets
token = secrets.randbelow(900000) + 100000
session_id = secrets.token_urlsafe(32)
```

#### 2.9 Sensitive Data Logging
```python
# BAD: Logging sensitive data
print(f"Password: {password}")
print(f"Token: {auth_token}")
logger.debug(f"API key: {api_key}")

# GOOD: Use logging module, never log sensitive values
import logging
logger = logging.getLogger(__name__)
logger.debug("Authentication attempted for user %s", username)  # no password
```

#### 2.10 Database Authorization
Read every `GRANT`, `REVOKE`, row-level security policy (`CREATE POLICY`,
`ROW LEVEL SECURITY`) and `SECURITY DEFINER` function in the changed migrations
and SQL for cross-user access:

```sql
-- BAD: any signed-in user can read every row
CREATE POLICY read_all ON documents FOR SELECT USING (true);

-- GOOD: the policy names the requesting user
CREATE POLICY read_own ON documents FOR SELECT
  USING (owner_id = current_setting('app.user_id')::int);
```

The application-side authorization check that the policy backs must still exist.

### Step 6: Error Handling Security

**Distinct from Phase 7 (Silent Failure Hunt):**
- Phase 7 focuses on error HANDLING (don't fail silently)
- Phase 14 focuses on error EXPOSURE (don't leak sensitive info)

```python
# BAD: Exposing internal details in user-facing errors
raise Exception(f"Database connection failed: {connection_string}")

# GOOD: Generic user message, detailed logging
logger.exception("DB connection failed")
raise UserFacingError("Service temporarily unavailable")
```

---

## Output Format

Generate findings in this format:

```markdown
## Security Review Findings

### CRITICAL (Must fix before merge)
- [ ] `src/auth/auth_service.py:45` - Hardcoded API key found
- [ ] `src/api/client.py:12` - SQL injection vulnerability

### HIGH (Should fix before merge)
- [ ] `src/network/api.py:89` - HTTP URL (should be HTTPS)
- [ ] `src/data/user_repo.py:23` - Token logged in debug statement

### MEDIUM (Consider fixing)
- [ ] `src/utils/tokens.py:34` - Using random module for security token

### LOW (Informational)
- [ ] `src/services/cdn.py:67` - SSL verification disabled in test helper

### Not Applicable
- No hardcoded credentials detected in changed files
- No SQL injection patterns found
```

---

## Severity Definitions

| Severity | Definition | Action |
|----------|------------|--------|
| **CRITICAL** | Immediate security risk, data exposure | Block merge |
| **HIGH** | Significant vulnerability, requires attention | Should fix |
| **MEDIUM** | Security best practice violation | Recommend fix |
| **LOW** | Minor improvement opportunity | Informational |

---

## Tools to Use

- `Grep` - Pattern searching for secrets/sensitive strings
- `Glob` - Locate files matching security-relevant patterns
- `Read` - Inspect suspicious code sections

---

## Important Notes

- This phase complements, not replaces, Phase 7 (Silent Failure Hunt)
- Phase 7 = "Are errors handled?" Phase 14 = "Are errors secure?"
- Never report false positives for:
  - Environment variable references (`os.environ.get`)
  - `python-dotenv` usage (`load_dotenv`)
  - Test files with mock credentials
- Check `.env.example` files are not committed with real values
- Verify `.gitignore` includes sensitive files (`.env`, `*.pem`, `*.key`)
- Check that no `.env` file is committed to git (`git ls-files | grep '\.env'`)
