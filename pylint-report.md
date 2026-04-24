# Pylint Report

## Command

```bash
.venv/bin/python -m pylint app.py application domain infrastructure presentation seed.py
```

## Result

Final score:

```text
Your code has been rated at 8.89/10
```

## Cleanup Completed

* Wrapped Python lines that exceeded the default 100-character limit.
* Removed the `redefined-outer-name` warning in `app.py` by renaming the local
  Flask application variable.
* Removed the unused teardown callback argument warning in
  `infrastructure/database.py`.
* Moved password hashing helpers out of `application.services` so the service
  module can be imported without Flask's dependencies being installed.
* Removed extra blank lines between top-level Python definitions after feedback.
* Simplified duplicate category storage by using only the `meetup_categories`
  table for meetup classifications.
* Removed pass-through service methods that only forwarded simple repository
  reads.
* Verified the changed Python files with `py_compile`.

## Remaining Warning Categories

* `missing-module-docstring`, `missing-class-docstring`,
  `missing-function-docstring`: left unresolved because the project is a small
  course application with short modules, route handlers, repositories, and
  service methods whose names already describe their responsibilities. Adding
  placeholder docstrings to every function would add noise without improving
  behavior or maintainability.
* `too-many-instance-attributes`: left unresolved for the `Meetup` dataclass
  because it represents the fields shown by the UI and returned by the meetup
  listing/detail queries. Splitting it would make the simple data flow harder
  to follow.
* `too-many-arguments` and `too-many-positional-arguments`: left unresolved for
  meetup repository create/update methods because they map directly to the
  validated meetup form fields and raw SQL parameters. Introducing a new DTO
  only for Pylint would be larger than the current project needs.
* `duplicate-code`: left unresolved for the SQL insert shape shared by the
  repository and `seed.py`. The duplication is limited to raw SQL column lists;
  keeping the optional seed script independent avoids coupling development data
  generation to runtime repository code.
