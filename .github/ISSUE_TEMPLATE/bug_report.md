---
name: Bug report
about: Describe and document unintended/broken behavior
title: ''
labels: ''
assignees: ''

---

**Describe the bug**
A clear and concise description of what the bug is.

**Current Behavior**
Describe a set of steps that results in an error or incorrect behavior, or a formatted minimum reproducible example that showcases the issue.

**Expected behavior**
A clear and concise description of what you expected to happen instead.

**Additional context**
Add any other context about the issue here, if seemingly relevant.

**Please also include the following:**
Draftsman version: `X.X.X`
Python version: `X.X.X`

If your issue is related to mod-loading with `draftsman-update`, in addition to the above information, please also include:
1. The exact `draftsman-update` command that fails/produces incorrect behavior
2. The error produced by the command (if the command does fail)
3. The mod list with their versions used with the command

The 3rd item can be created manually, but can generated automatically and quickly by running the command:
```
draftsman-update --path mods/that/failed --report
```
The result can then be (preferably) added alongside the issue body or (if too large for concise viewing) included as a file attachment.
