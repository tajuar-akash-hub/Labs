# Chapter 4: Batch Processing

**Course:** DataCamp — Introduction to Shell  
**Chapter:** 4 — Batch Processing

## Learning Objectives

By the end of this chapter, you should understand how to:

- Work with shell variables and environment variables.
- Inspect variables using `set`, `env`, `printenv`, and `grep`.
- Write Bash `for` loops.
- Repeat commands across multiple values and files.
- Combine commands inside loops using pipes.
- Handle filenames containing spaces safely.
- Avoid common mistakes when writing shell commands and loops.

---

## 1. Shell Variables

### What is a variable?

A **variable** is a named place where the shell stores a value.

Instead of typing the same value repeatedly, you can store it in a variable and refer to it by name.

For example:

```bash
filetype=pdf
echo "$filetype"
```

Output:

```text
pdf
```

Here:

- `filetype` is the variable name.
- `pdf` is the stored value.
- `$filetype` accesses the value.
- `echo` prints the value.

### Environment Variables

An **environment variable** stores information about the shell session or user environment. Such variables can also be made available to programs launched by the shell.

Common environment variables include:

| Variable | Purpose | Example |
|---|---|---|
| `HOME` | User's home directory | `/home/repl` |
| `PWD` | Present working directory | Depends on the current directory |
| `SHELL` | Shell program | `/bin/bash` |
| `USER` | Current username | `repl` |
| `HISTFILESIZE` | Maximum number of command-history lines kept in the history file | `2000` in the course exercise |

These example values may differ on your computer.

### Inspecting Variables with `set`

The `set` command displays shell variables and other shell information.

```bash
set
```

The output can be long because it includes many variables and other details.

To find a specific variable, combine `set` with `grep`:

```bash
set | grep HISTFILESIZE
```

Example output:

```text
HISTFILESIZE=2000
_=HISTFILESIZE
__bp_last_argument_prev_command=HISTFILESIZE
```

The relevant value for the exercise is:

```text
HISTFILESIZE=2000
```

The other lines appear because `grep` displays every line containing the search text. They represent other shell state, not necessarily the setting being requested.

### Understanding the Pipe

Compare these commands:

```bash
set grep HISTFILESIZE
```

```bash
set | grep HISTFILESIZE
```

The first command has no pipe. The shell treats `grep` and `HISTFILESIZE` as additional arguments to `set`.

The second command contains a pipe (`|`):

1. `set` produces output.
2. `|` sends that output to the next command.
3. `grep HISTFILESIZE` filters the output.
4. Only lines containing `HISTFILESIZE` are displayed.

**Key concept:** A space separates command arguments. A pipe connects one command's output to another command's input.

### Other Commands for Environment Variables

You can also use:

```bash
env
```

or:

```bash
printenv
```

These commands commonly display environment variables.

---

## 2. Bash `for` Loops

### What is a loop?

A **loop** repeats a set of commands. Loops are useful when you want to perform the same operation for several values or files.

For example, instead of writing three separate `echo` commands, you can use one loop to print three file extensions.

### Basic Syntax

```bash
for variable in list; do
    commands
done
```

| Component | Purpose |
|---|---|
| `for` | Starts the loop |
| `variable` | Stores the current item |
| `in` | Introduces the list of items |
| `list` | Contains the values to process |
| `do` | Starts the loop body |
| `commands` | Commands executed during each iteration |
| `done` | Ends the loop |

### Example: Print File Extensions

```bash
for filetype in docx odt pdf; do
    echo "$filetype"
done
```

Output:

```text
docx
odt
pdf
```

### How It Works

**Iteration 1**

```bash
filetype=docx
```

The command prints:

```text
docx
```

**Iteration 2**

```bash
filetype=odt
```

The command prints:

```text
odt
```

**Iteration 3**

```bash
filetype=pdf
```

The command prints:

```text
pdf
```

After processing all three values, the loop finishes.

### One-Line Loop

The same loop can be written on one line:

```bash
for filetype in docx odt pdf; do echo "$filetype"; done
```

Semicolons (`;`) separate commands when writing the loop on a single line.

### Important Rules

- Use `do` to begin the loop body.
- Use `done` to end the loop.
- The variable changes to the current item on every iteration.
- Use `$variable` to access its value.
- Quoting variable expansions is good practice, especially when working with filenames.

---

## 3. Using Wildcards in Loops

### What is a wildcard?

A wildcard is a pattern that matches filenames.

For example:

```bash
*.csv
```

matches filenames ending in `.csv` in the current directory.

To match CSV files inside the `seasonal` directory:

```bash
seasonal/*.csv
```

### Example: Loop Through CSV Files

```bash
for file in seasonal/*.csv; do
    echo "$file"
done
```

Suppose the directory contains:

```text
seasonal/spring.csv
seasonal/summer.csv
seasonal/autumn.csv
seasonal/winter.csv
```

The loop processes each matching file path.

### How It Works

1. The shell expands `seasonal/*.csv` into matching filenames.
2. The first filename is assigned to `file`.
3. `echo "$file"` prints that filename.
4. The next filename is assigned to `file`.
5. The loop continues until all matching files have been processed.

The exact output depends on which files exist in the directory.

### Why Use a Variable?

Without a loop, you might need to run a command separately for every file.

With a loop, you write the command once:

```bash
for file in seasonal/*.csv; do
    echo "$file"
done
```

This becomes especially useful when processing dozens or hundreds of files.

---

## 4. Combining Loops with `grep` and `tail`

Loops can contain pipelines. This allows you to process each file using multiple commands.

### Example

```bash
for file in seasonal/*.csv; do
    grep '2017-07' "$file" | tail -n 1
done
```

This command searches every CSV file in the `seasonal` directory and prints the last matching line from each file.

### Step-by-Step Explanation

**Step 1: Start the loop**

```bash
for file in seasonal/*.csv; do
```

The shell matches the CSV files and assigns the current filename to `file` during each iteration.

**Step 2: Search the current file**

```bash
grep '2017-07' "$file"
```

`grep` prints lines from the current file that contain `2017-07`.

**Step 3: Pass the results through a pipe**

```bash
|
```

The pipe sends the matching lines from `grep` to `tail`.

**Step 4: Select the last matching line**

```bash
tail -n 1
```

`tail -n 1` prints the last line of the input it receives.

**Step 5: Finish the iteration**

```bash
done
```

The loop moves to the next file and repeats the same process.

### Why Doesn't `tail` Need `$file`?

Consider:

```bash
grep '2017-07' "$file" | tail -n 1
```

Here, `grep` reads the file directly. `tail` receives the output from `grep` through the pipe.

Therefore, `tail` does not need the filename.

Compare the following commands.

**Command A: Print the final line of a file**

```bash
tail -n 1 "$file"
```

This prints the file's final line, regardless of its contents.

**Command B: Print the final line that matches a pattern**

```bash
grep '2017-07' "$file" | tail -n 1
```

This first filters the file to matching lines. Then `tail` prints the last line from those results.

The commands produce different results because their input is different.

### Correct Loop Structure

```bash
for file in seasonal/*.csv; do
    grep '2017-07' "$file" | tail -n 1
done
```

Remember:

- `do` begins the loop body.
- The commands inside the body execute for each file.
- `done` closes the loop.

Do not place another `do` at the end of the pipeline.

---

## 5. Filenames Containing Spaces

### Why Can Spaces Cause Problems?

The shell uses spaces to separate command arguments.

Suppose these files exist:

```text
current.csv
last year.csv
```

Now consider this command:

```bash
rm current.csv last year.csv
```

You might expect it to delete two files. However, the shell interprets the arguments as:

```text
current.csv
last
year.csv
```

The filename `last year.csv` has been split into two separate arguments.

### What Happens?

The `rm` command attempts to remove all three paths:

1. `current.csv`
2. `last`
3. `year.csv`

If only `current.csv` and `last year.csv` exist:

- `current.csv` is deleted.
- `rm` reports errors for `last` and `year.csv`.
- The successful deletion of `current.csv` is not automatically undone.

Therefore, the correct answer to the course exercise is **Both of the above**: the first file is deleted, and errors occur because the spaced filename was interpreted incorrectly.

### Method 1: Use Single Quotes

```bash
rm current.csv 'last year.csv'
```

Single quotes keep the filename together as one argument.

### Method 2: Use Double Quotes

```bash
rm current.csv "last year.csv"
```

Double quotes also keep the filename together.

### Method 3: Escape the Space

```bash
rm current.csv last\ year.csv
```

The backslash (`\`) tells the shell to treat the space as part of the filename rather than as an argument separator.

### Recommended Practice

Quote filenames and filename variables:

```bash
cat "last year.csv"
```

```bash
grep '2017-07' "$file"
```

This helps prevent the shell from splitting paths containing spaces.

**Safety note:** `rm` deletes files. Check the paths before running it.

---

## 6. Important Syntax Reference

| Syntax | Meaning |
|---|---|
| `$variable` | Expands to the value of a shell variable |
| `for x in a b c; do ...; done` | Runs the loop body for each listed value |
| `*.csv` | Matches filenames ending in `.csv` |
| `seasonal/*.csv` | Matches CSV files inside `seasonal` |
| `"$file"` | Expands a filename variable while keeping spaces within one argument |
| `\|` | Sends one command's standard output to another command's standard input |
| `grep PATTERN FILE` | Prints lines matching a pattern |
| `tail -n 1` | Prints the last line of its input |
| `set` | Displays shell variables and other shell information |
| `env` | Displays environment variables |
| `printenv` | Displays environment variables |
| `set \| grep NAME` | Filters `set` output to matching lines |
| `'filename with spaces.csv'` | Keeps a spaced filename as one argument |
| `last\ year.csv` | Escapes a space in a filename |

---

## 7. Common Mistakes and Fixes

### Mistake 1: Forgetting the Pipe

**Incorrect:**

```bash
set grep HISTFILESIZE
```

**Correct:**

```bash
set | grep HISTFILESIZE
```

**Why?** The pipe connects the output of `set` to `grep`.

### Mistake 2: Forgetting `done`

**Incorrect:**

```bash
for filetype in docx odt pdf; do echo "$filetype";
```

**Correct:**

```bash
for filetype in docx odt pdf; do echo "$filetype"; done
```

**Why?** `done` marks the end of the loop.

### Mistake 3: Using `do` Twice

**Incorrect:**

```bash
for file in seasonal/*.csv; do grep '2017-07' "$file" | tail -n 1; do
```

**Correct:**

```bash
for file in seasonal/*.csv; do grep '2017-07' "$file" | tail -n 1; done
```

**Why?** `do` starts the loop body, while `done` ends it.

### Mistake 4: Leaving a Filename with Spaces Unquoted

**Incorrect:**

```bash
rm current.csv last year.csv
```

**Correct:**

```bash
rm current.csv 'last year.csv'
```

**Why?** Unquoted spaces split the filename into separate arguments.

### Mistake 5: Confusing a Pipeline with a Filename Argument

```bash
grep '2017-07' "$file" | tail -n 1
```

Here, `tail` reads the output from the pipe.

Adding `"$file"` to `tail` would make it read the file directly instead of processing the piped text.

---

## 8. Practical Examples

### Example A: Print Multiple File Extensions

```bash
for filetype in docx odt pdf; do
    echo "$filetype"
done
```

### Example B: Display Every CSV Filename

```bash
for file in seasonal/*.csv; do
    echo "$file"
done
```

### Example C: Print the Last Matching Line from Each CSV

```bash
for file in seasonal/*.csv; do
    grep '2017-07' "$file" | tail -n 1
done
```

### Example D: Find a Shell Setting

```bash
set | grep HISTFILESIZE
```

### Example E: Remove Two Files, One with a Space in Its Name

```bash
rm current.csv 'last year.csv'
```

---

## 9. Self-Assessment Questions

Try to answer each question before checking the solution.

### Question 1: What does this loop print?

```bash
for x in red blue; do echo "$x"; done
```

**Answer:**

```text
red
blue
```

### Question 2: What does `done` do?

**Answer:** It marks the end of a `for` loop.

### Question 3: What does this command do?

```bash
set | grep HISTFILESIZE
```

**Answer:** It filters the output of `set` and displays lines containing `HISTFILESIZE`.

### Question 4: Why does `tail` not need a filename here?

```bash
grep '2017-07' "$file" | tail -n 1
```

**Answer:** `tail` receives matching lines from `grep` through standard input.

### Question 5: How should you refer to a file named `last year.csv`?

**Answer:** Use quotes or escape the space:

```bash
"last year.csv"
```

```bash
'last year.csv'
```

```bash
last\ year.csv
```

### Question 6: What can go wrong with this command?

```bash
rm current.csv last year.csv
```

**Answer:** The shell splits `last year.csv` into `last` and `year.csv`. `current.csv` may be deleted, while `rm` reports errors for the other paths if they do not exist.

---

## 10. Chapter Summary

Chapter 4 focuses on automating repeated shell work.

- **Variables** store values that commands and loops can reuse.
- **Environment variables** provide information about the shell session and user environment.
- **`set`, `env`, and `printenv`** help inspect shell or environment information.
- **Pipes (`|`)** pass output between commands.
- **`for` loops** repeat commands for each value in a list.
- **Wildcards**, such as `seasonal/*.csv`, match filenames and can be used in loops.
- **Pipelines inside loops** let you process each file through multiple commands.
- **Quotes and escaped spaces** prevent filenames containing spaces from being split into multiple arguments.

### Mental Model of Batch Processing

```text
List of values or matching files
              |
              v
       Assign current item
         to loop variable
              |
              v
       Execute loop commands
              |
              v
      Move to the next item
              |
              v
       Repeat until finished
```

**Main takeaway:** Use variables to reuse values, loops to repeat tasks, pipes to connect commands, wildcards to match files, and quoting to handle filenames safely.
