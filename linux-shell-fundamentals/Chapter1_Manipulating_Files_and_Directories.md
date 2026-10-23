# Chapter 1: Manipulating Files and Directories

**Course:** DataCamp — Introduction to Shell  
**Status:** Completed  
**Focus:** Linux filesystem navigation, paths, copying, moving, creating, and removing files and directories.

> These are independently written study notes based on the concepts practiced in the course, with additional Linux and MLOps examples.

## Table of contents

1. [What is a shell?](#1-what-is-a-shell)
2. [Understanding the Linux filesystem](#2-understanding-the-linux-filesystem)
3. [`pwd` — Print working directory](#3-pwd--print-working-directory)
4. [`ls` — List files and directories](#4-ls--list-files-and-directories)
5. [`cd` — Change directory](#5-cd--change-directory)
6. [Absolute and relative paths](#6-absolute-and-relative-paths)
7. [`cp` — Copy files and directories](#7-cp--copy-files-and-directories)
8. [`mv` — Move and rename](#8-mv--move-and-rename)
9. [`rm` — Remove files](#9-rm--remove-files)
10. [`rmdir` — Remove empty directories](#10-rmdir--remove-empty-directories)
11. [`mkdir` — Create directories](#11-mkdir--create-directories)
12. [`/tmp` — Temporary files](#12-tmp--temporary-files)
13. [What happens inside Linux?](#13-what-happens-inside-linux)
14. [Common mistakes](#14-common-mistakes)
15. [Command cheat sheet](#15-command-cheat-sheet)
16. [Practical MLOps lab](#16-practical-mlops-lab)
17. [Knowledge check](#17-knowledge-check)
18. [Chapter summary](#18-chapter-summary)

---

## 1. What is a shell?

A **shell** is a program that interprets commands and lets you interact with the operating system. **Bash** (Bourne Again Shell) is a common Linux shell. A **terminal** is the interface where you type commands.

```bash
pwd
ls
cd seasonal
```

| Term | Meaning |
|---|---|
| Terminal | Application or interface for entering commands |
| Shell | Program that interprets commands |
| Bash | A particular shell, primarily implemented in C |
| Linux kernel | Core OS component managing processes, memory, filesystems, and hardware |

**What happens when you type `ls`?**

```text
You type: ls
    |
    v
Bash parses the command
    |
    v
Bash locates and starts the ls program
    |
    v
ls reads directory information through the OS
    |
    v
The terminal displays the output
```

**Important:** `cd` is a Bash built-in; `ls` and `cp` are usually external programs.

## 2. Understanding the Linux filesystem

Linux organizes files and directories into a hierarchy starting at the root directory, `/`. Unlike typical Windows paths such as `C:\Users\...`, Linux uses forward slashes.

### Example filesystem structure

The following is an **illustrative** layout based on the DataCamp practice environment. The tree is inside a fenced `text` block so GitHub preserves every line and indentation.

```text
/
├── home/
│   └── repl/
│       ├── course.txt
│       ├── seasonal/
│       │   ├── spring.csv
│       │   ├── summer.csv
│       │   ├── autumn.csv
│       │   └── winter.csv
│       ├── people/
│       │   └── agarwal.txt
│       ├── backup/
│       └── bin/
├── tmp/
├── etc/
└── usr/
```

| Directory | Purpose |
|---|---|
| `/` | Filesystem root |
| `/home` | Home directories for regular users |
| `/home/repl` | Home directory in the DataCamp exercises |
| `/tmp` | Temporary files |
| `/etc` | System and application configuration |
| `/usr` | Many installed programs and shared resources |
| `/var` | Variable data such as logs and caches |
| `/bin` | Essential commands; often a link to `/usr/bin` on modern Linux |

A directory contains entries referring to files and other directories.

## 3. `pwd` — Print working directory

`pwd` prints the current working directory.

```bash
pwd
```

Example output:

```text
/home/repl
```

**Why it matters:** Relative paths are resolved from your current working directory. If you're in `/home/repl`, `course.txt` means `/home/repl/course.txt`. If you're in `/home/repl/seasonal`, the same name refers to `/home/repl/seasonal/course.txt`, which might not exist.

Every process has a current working directory.

## 4. `ls` — List files and directories

List the current directory:

```bash
ls
```

Possible output:

```text
backup  bin  course.txt  people  seasonal
```

List a specific directory without entering it:

```bash
ls seasonal
```

Possible output:

```text
autumn.csv  spring.csv  summer.csv  winter.csv
```

### Common options

| Command | Meaning |
|---|---|
| `ls` | List visible entries |
| `ls -l` | Long listing, including metadata |
| `ls -a` | Include hidden entries |
| `ls -lh` | Long listing with human-readable file sizes |
| `ls -R` | List directories recursively |
| `ls -F` | Append type indicators such as `/` for directories |
| `ls -la` | Long listing including hidden entries |

Example:

```bash
ls -lh
```

```text
-rw-r--r-- 1 repl repl 2.1K Oct 20 course.txt
drwxr-xr-x 2 repl repl 4.0K Oct 20 seasonal
```

The first character indicates the file type: `-` regular file, `d` directory, and `l` symbolic link. The remaining characters include permission information.

### Hidden files

Linux treats names beginning with `.` as hidden in a normal `ls` listing, for example `.bashrc`, `.gitconfig`, and `.ssh`. Show them with:

```bash
ls -a
```

## 5. `cd` — Change directory

`cd` changes the shell's current working directory.

```bash
cd seasonal
pwd
```

If you started in `/home/repl`, the output is:

```text
/home/repl/seasonal
```

| Command | Meaning |
|---|---|
| `cd seasonal` | Enter the `seasonal` directory |
| `cd ..` | Go up one directory level |
| `cd ../..` | Go up two levels |
| `cd /home/repl` | Go to an absolute path |
| `cd ~` | Go to your home directory |
| `cd` | Also go home |
| `cd -` | Return to the previous working directory |

### Why is `cd` built into Bash?

An external program can change its **own** working directory but cannot directly change its parent shell's working directory. Bash implements `cd` internally so the shell itself can change directory.

## 6. Absolute and relative paths

An **absolute path** begins at `/`:

```text
/home/repl/seasonal/spring.csv
```

A **relative path** begins from your current directory. From `/home/repl`, the same file can be written as:

```text
seasonal/spring.csv
```

| Symbol | Meaning | Example |
|---|---|---|
| `/` | Root at the start of a path; separator between path components | `/home/repl` |
| `.` | Current directory | `./script.sh` |
| `..` | Parent directory | `../course.txt` |
| `~` | Your home directory when expanded by the shell | `~/seasonal` |

### Example

```text
Current directory: /home/repl/seasonal
Relative path:     ../course.txt
Resolved path:     /home/repl/course.txt
```

**Common mistake:** `cd /seasonal` looks for `/seasonal` directly under root. From `/home/repl`, use `cd seasonal` or `cd /home/repl/seasonal`.

## 7. `cp` — Copy files and directories

Basic syntax:

```bash
cp SOURCE DESTINATION
```

Copy and rename:

```bash
cp course.txt course-backup.txt
```

Copy into another directory:

```bash
cp seasonal/spring.csv backup/
```

Copy multiple files into a directory:

```bash
cp seasonal/spring.csv seasonal/summer.csv backup/
```

Copy a directory recursively:

```bash
cp -r seasonal backup/
```

If `backup/` already exists, this creates or updates `backup/seasonal/`. If it doesn't exist, the result depends on the source/destination conditions; be explicit about the intended layout.

| Option | Meaning |
|---|---|
| `-r` or `-R` | Copy directories recursively |
| `-i` | Ask before overwriting |
| `-v` | Show copied files |
| `-n` | Avoid overwriting existing files (behavior can vary by implementation) |

**Safety:** `cp` may overwrite an existing destination. Use `cp -i` when you want confirmation.

## 8. `mv` — Move and rename

Basic syntax:

```bash
mv SOURCE DESTINATION
```

Rename a file:

```bash
mv course.txt notes.txt
```

Move it into another directory:

```bash
mv notes.txt backup/
```

Rename a directory:

```bash
mv backup old-backup
```

| Feature | `cp` | `mv` |
|---|---|---|
| Main purpose | Copy | Move or rename |
| Source remains at original path | Yes | No, after a successful move |
| Can work with directories | Yes, generally with `-r` | Yes |

**Deeper detail:** Within the same filesystem, a move often updates directory entries without copying file contents. Across filesystems, moving may involve copying and then removing the original.

## 9. `rm` — Remove files

Remove a file:

```bash
rm notes.txt
```

Remove several files:

```bash
rm file1.txt file2.txt
```

| Command | Meaning |
|---|---|
| `rm file.txt` | Remove a file |
| `rm -i file.txt` | Ask before removing |
| `rm -r directory/` | Recursively remove directory contents |
| `rm -f file.txt` | Force removal, suppressing ordinary prompts |
| `rm -rf directory/` | Force recursive removal — potentially destructive |

> **Warning:** `rm` normally does not send files to the desktop recycle bin. Always verify the path before deleting anything, especially when using `-r` or `-f`.

Inspect first:

```bash
ls directory/
```

## 10. `rmdir` — Remove empty directories

`rmdir` removes an **empty** directory:

```bash
mkdir test
rmdir test
```

If `test` contains `notes.txt`, `rmdir test` fails.

| Command | Behavior |
|---|---|
| `rmdir test` | Removes `test` only if empty |
| `rm -r test` | Recursively removes `test` and its contents |

Prefer `rmdir` when you only want to clean up an empty directory.

## 11. `mkdir` — Create directories

Create one directory:

```bash
mkdir projects
```

Create several directories:

```bash
mkdir data models logs
```

Create nested directories, including missing parents:

```bash
mkdir -p mlops/experiments/run1
```

The `-p` option creates missing parent directories and does not fail just because the requested directory already exists.

### MLOps example

Desired structure:

```text
ml-project/
├── data/
│   ├── raw/
│   └── processed/
├── models/
├── logs/
└── experiments/
```

Commands:

```bash
mkdir -p ml-project/data/raw
mkdir -p ml-project/data/processed
mkdir -p ml-project/models
mkdir -p ml-project/logs
mkdir -p ml-project/experiments
```

## 12. `/tmp` — Temporary files

`/tmp` is commonly used for temporary data:

```bash
cd /tmp
mkdir practice
```

Do not assume files in `/tmp` will remain forever. Linux systems may clean it automatically, and temporary containers or VMs may discard their files when reset.

## 13. What happens inside Linux?

Consider:

```bash
cp seasonal/spring.csv backup/
```

The simplified execution flow is:

```text
Bash parses the command
          |
          v
Bash starts the cp process
          |
          v
cp accesses source and destination paths
          |
          v
Linux kernel handles filesystem requests
          |
          v
Destination file is created or updated
```

The filesystem stores file contents and metadata such as permissions, ownership, and timestamps. Programs interact with it through operating-system interfaces rather than directly manipulating disk sectors.

**RAM vs disk:** Copying a large file does not usually require loading the entire file into RAM. Data can be copied incrementally through buffers, which is useful for datasets and model artifacts.

## 14. Common mistakes

| Mistake | Problem | Better approach |
|---|---|---|
| `cd spring.csv` | `cd` expects a directory | `cd seasonal` |
| `ls seasonal/spring.csv/` | Trailing slash treats the path as a directory | `ls seasonal/spring.csv` |
| `cp file.txt` | Missing destination | `cp file.txt backup/` |
| `mv file.txt` | Missing destination | `mv file.txt new.txt` |
| `mkdir a/b/c` | Parent directories may not exist | `mkdir -p a/b/c` |
| `rmdir folder` fails | Directory is not empty | Inspect the directory first |
| `rm folder` fails | Ordinary `rm` does not remove directories | Use `rmdir` for empty directories |
| `cd /seasonal` fails | Wrong absolute path | `cd seasonal` from `/home/repl` |
| `ls _F` fails | `_F` is a filename, not an option | `ls -F` |

## 15. Command cheat sheet

| Command | Purpose | Example |
|---|---|---|
| `pwd` | Print working directory | `pwd` |
| `ls` | List entries | `ls seasonal` |
| `ls -l` | Detailed listing | `ls -l` |
| `ls -a` | Include hidden entries | `ls -a` |
| `ls -R` | Recursive listing | `ls -R` |
| `ls -F` | Show file type indicators | `ls -F` |
| `cd` | Change directory | `cd seasonal` |
| `cd ..` | Go to parent | `cd ..` |
| `cd ~` | Go home | `cd ~` |
| `cd -` | Return to previous directory | `cd -` |
| `cp` | Copy files | `cp a.txt b.txt` |
| `cp -r` | Copy directories | `cp -r data backup` |
| `mv` | Move or rename | `mv old.txt new.txt` |
| `rm` | Delete files | `rm old.txt` |
| `rmdir` | Delete empty directory | `rmdir empty` |
| `mkdir` | Create directory | `mkdir project` |
| `mkdir -p` | Create nested directories | `mkdir -p a/b/c` |

## 16. Practical MLOps lab

Run these commands in Ubuntu or WSL. They create a separate practice folder in your home directory.

### Step 1: Create the directory structure

```bash
cd ~
mkdir -p shell-chapter1-lab/data/raw
mkdir -p shell-chapter1-lab/data/processed
mkdir -p shell-chapter1-lab/models
mkdir -p shell-chapter1-lab/logs
```

### Step 2: Navigate and inspect

```bash
cd shell-chapter1-lab
pwd
ls
```

### Step 3: Create a sample file

`touch` creates an empty file if one does not exist; it is an extra command beyond the main chapter topics.

```bash
touch data/raw/train.csv
```

### Step 4: Copy it

```bash
cp data/raw/train.csv data/processed/train-copy.csv
```

### Step 5: Rename the copy

```bash
mv data/processed/train-copy.csv data/processed/train-clean.csv
```

### Step 6: Inspect the result

```bash
ls -R
```

Expected structure (tree-style illustration; `ls -R` itself uses a different display format):

```text
shell-chapter1-lab/
├── data/
│   ├── processed/
│   │   └── train-clean.csv
│   └── raw/
│       └── train.csv
├── logs/
└── models/
```

### Step 7: Delete the practice copy

```bash
rm data/processed/train-clean.csv
rmdir data/processed
```

The original `data/raw/train.csv` remains.

## 17. Knowledge check

Try answering before opening the solutions.

1. Which command shows your current working directory: `ls`, `pwd`, `cd`, or `mkdir`?
2. If you are in `/home/repl/seasonal`, where does `cd ..` take you?
3. Which command creates missing parent directories?
4. Which command removes an empty directory?
5. What happens when you run `cp file.txt backup/`?

<details>
<summary>Show answers</summary>

1. `pwd`.
2. `/home/repl`.
3. `mkdir -p a/b/c`.
4. `rmdir folder`.
5. It copies `file.txt` into the existing `backup/` directory, leaving the original in place.

</details>

## 18. Chapter summary

- **Navigation:** `pwd`, `ls`, and `cd` help you locate files and directories.
- **Paths:** Absolute paths begin at `/`; relative paths depend on the working directory.
- **File management:** `cp` copies, `mv` moves or renames, and `rm` removes files.
- **Directory management:** `mkdir` creates directories, `mkdir -p` creates missing parents, and `rmdir` removes empty directories.
- **Safety:** Verify source and destination paths before overwriting or deleting data.

These fundamentals are essential for working with datasets, model files, logs, scripts, Docker build contexts, and remote Linux servers.

---

**Source acknowledgment:** Concepts and exercise context from DataCamp's *Introduction to Shell*. Explanations and extended examples are written as independent study notes.
