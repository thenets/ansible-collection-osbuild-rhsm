=========================
Lab.Osbuild Release Notes
=========================

.. contents:: Topics


v1.1.0
======

Release Summary
---------------

Added AWS build blueprint

Major Changes
-------------

- Added AWS image build capabilities.
- Added AWS setup role.
- Added Azure setup role.

Breaking Changes / Porting Guide
--------------------------------

- Changed file names to align with conventions in osbuilder documentation.
- Removed variables that were specific to Azure or replaced with cloud naming conventions.

v1.0.2
======

Release Summary
---------------

Bug fixes

Minor Changes
-------------

- Updated use of `shell` command to `copy` and `cmd` since the shell command does not report on stderror.

v1.0.1
======

Release Summary
---------------

Update repository removing unused variables and README cleanup.

Major Changes
-------------

- Renamed `setup_host` role to `host_setup` to match naming conventions.

Minor Changes
-------------

- Added mdlint file.
- Changed hosts to be "all" instead of "rhel-dev".
- README updates.

v1.0.0
======

Release Summary
---------------

Created collection of roles for osbuild deployment.

Major Changes
-------------

- Migrated repository to collection layout with roles.
- Resolved ansible-lint issues.
