# Chapter 3: Combining Tools

> **Course:** DataCamp — Introduction to Shell  
> **Chapter:** 3 — Combining Tools  
> **Status:** Completed  
> **Purpose:** Learn how to combine shell commands, redirect output, count and sort text, and build useful data-processing pipelines.

## Table of Contents

1. [Why Combine Commands?](#1-why-combine-commands)
2. [Standard Input, Output, and Error](#2-standard-input-output-and-error)
3. [Redirecting Output with `>`](#3-redirecting-output-with-)
4. [Appending Output with `>>`](#4-appending-output-with-)
5. [Pipelines with `|`](#5-pipelines-with-)
6. [Redirection vs. Pipelines](#6-redirection-vs-pipelines)
7. [Counting with `wc`](#7-counting-with-wc)
8. [Sorting with `sort`](#8-sorting-with-sort)
9. [Removing Adjacent Duplicates with `uniq`](#9-removing-adjacent-duplicates-with-uniq)
10. [Combining `cut`, `grep`, `sort`, and `uniq`](#10-combining-cut-grep-sort-and-uniq)
11. [Command Reference](#11-command-reference)
12. [Common Mistakes](#12-common-mistakes)
13. [Practice Exercises](#13-practice-exercises)
14. [Solutions](#14-solutions)
15. [Key Takeaways](#15-key-takeaways)

---

## 1. Why Combine Commands?

A shell command often performs one focused task. You can connect commands to create a larger workflow without writing a separate program.

For example, you might want to:

1. Extract a column from a CSV file.
2. Remove header lines.
3. Sort the values.
4. Count repeated values.
5. Save the result in a file.

Instead of doing each step manually, combine commands:

```bash
cut -d , -f 2 seasonal/winter.csv | grep -v Tooth | sort | uniq -c
```

Each command performs one part of the job, and the output flows to the next command.

**Real-world use:** A data engineer can combine shell tools to inspect logs, summarize CSV data, or prepare files before loading them into a data pipeline.

## 2. Standard Input, Output, and Error

Programs commonly use three standard streams.

| Stream | File descriptor | Purpose |
|---|---:|---|
| Standard input (`stdin`) | `0` | Data a command reads |
| Standard output (`stdout`) | `1` | Normal output produced by a command |
| Standard error (`stderr`) | `2` | Error messages and diagnostic output |

Think of a command as a tool with an input and output:

- It reads data from standard input, a file, or another source.
- It writes normal results to standard output.
- It writes diagnostic messages to standard error.

For example:

```bash
head -n 3 seasonal/winter.csv
```

By default, `head` writes its result to the terminal through standard output.

You can redirect that standard output to a file:

```bash
head -n 3 seasonal/winter.csv > result.txt
```

This note focuses on standard output redirection and pipelines. Standard error is introduced here to help distinguish normal results from error messages.

## 3. Redirecting Output with `>`

The `>` operator sends a command's standard output to a file.

### Basic syntax

```bash
command > output_file.txt
```

Example:

```bash
head -n 3 seasonal/winter.csv > result.txt
```

This command:

1. Opens `seasonal/winter.csv`.
2. Selects its first three lines.
3. Writes those lines to `result.txt` instead of displaying them in the terminal.

### What if the destination file does not exist?

Bash creates the file in the current working directory, unless you provide a different path.

If your current directory is `/home/repl`, then this command:

```bash
head -n 3 seasonal/winter.csv > result.txt
```

creates or writes to:

```text
/home/repl/result.txt
```

You can check your current directory with:

```bash
pwd
```

### What if the file already exists?

`>` normally **overwrites the file's existing contents** by truncating it before the command writes its output.

For example:

```bash
echo "old content" > result.txt
echo "new content" > result.txt
```

After the second command, `result.txt` contains:

```text
new content
```

The old content is gone.

> **Caution:** Be careful with `>`. It can erase existing file contents.

### Redirection is a shell operator, not a command argument

These commands are all valid in Bash and produce the same result for this example:

```bash
> result.txt head -n 3 seasonal/winter.csv
```

```bash
head -n 3 seasonal/winter.csv > result.txt
```

```bash
head -n 3 > result.txt seasonal/winter.csv
```

They save the first three lines of `seasonal/winter.csv` into `result.txt`.

Why? Bash interprets the redirection and connects the command's standard output to the file before the command runs. The `head` command still reads the input file and selects the first three lines.

The redirection does not process the text itself. It determines where the command's output goes.

## 4. Appending Output with `>>`

The `>>` operator appends output to the end of a file instead of replacing its existing contents.

### Syntax

```bash
command >> output_file.txt
```

Example:

```bash
echo "First line" > notes.txt
echo "Second line" >> notes.txt
```

The file contains:

```text
First line
Second line
```

Compare the operators:

| Operator | Behavior |
|---|---|
| `>` | Creates a file if needed; otherwise replaces its contents |
| `>>` | Creates a file if needed; otherwise adds output to the end |

Use `>` when you want a fresh result. Use `>>` when you want to keep existing content and add more output.

## 5. Pipelines with `|`

A pipe (`|`) connects the standard output of one command to the standard input of another command.

### Basic syntax

```bash
command1 | command2
```

Example:

```bash
cut -d , -f 2 seasonal/winter.csv | grep -v Tooth
```

The data flows like this:

```text
seasonal/winter.csv
        |
        v
cut -d , -f 2
(extracts column 2)
        |
        v
grep -v Tooth
(removes lines containing "Tooth")
        |
        v
filtered output in the terminal
```

`cut` produces text. The pipe passes that text to `grep`. `grep` filters the incoming lines and displays the remaining lines.

### A pipeline can contain more than two commands

```bash
cut -d , -f 2 seasonal/winter.csv | grep -v Tooth | sort
```

The output of `cut` becomes the input of `grep`. The output of `grep` becomes the input of `sort`.

You can chain several small tools into one workflow.

## 6. Redirection vs. Pipelines

This is one of the most important concepts in the chapter.

- `>` sends standard output to a **file**.
- `|` sends standard output to **another command**.

### Correct: filter first, then save

```bash
cut -d , -f 2 seasonal/*.csv | grep -v Tooth > teeth-only.txt
```

The flow is:

```text
CSV files
   |
   v
cut
(extract column 2)
   |
   v
grep -v Tooth
(remove header lines containing "Tooth")
   |
   v
> teeth-only.txt
(save filtered output)
```

The file receives the filtered output.

### Different behavior: redirect `cut` before the pipe

```bash
cut -d , -f 2 seasonal/*.csv > teeth-only.txt | grep -v Tooth
```

Here, `cut`'s standard output is redirected to `teeth-only.txt`. The pipe does not receive `cut`'s normal output, so `grep` gets no lines from that pipe and exits when it reaches end-of-file.

As a result, `teeth-only.txt` receives the extracted column **including its header lines**. `grep` does not filter the contents of the file because it has not been told to read that file.

### Important mental model

For this command:

```bash
command1 | command2 > result.txt
```

- `command1` sends its output through the pipe.
- `command2` reads that output.
- `command2` sends its own output to `result.txt`.

The output file is connected to the command associated with the redirection—not automatically to the entire pipeline as a single filtering operation.

### Compare the patterns

| Command | Result |
|---|---|
| `command > file` | Save command output to a file |
| `command1 \| command2` | Send command 1 output to command 2 |
| `command1 \| command2 > file` | Send command 1 output to command 2, then save command 2 output |
| `command1 > file \| command2` | Send command 1 output to the file; command 2 receives no normal output through that pipe |

## 7. Counting with `wc`

`wc` means **word count**. It can count lines, words, bytes, and characters.

### Common options

| Option | Counts |
|---|---|
| `-l` | Lines |
| `-w` | Words |
| `-c` | Bytes |
| `-m` | Characters |

Examples:

```bash
wc -l seasonal/winter.csv
```

Counts the lines in the file.

```bash
wc -w course.txt
```

Counts the words in `course.txt`.

```bash
wc -c course.txt
```

Counts the bytes in the file.

```bash
wc -m course.txt
```

Counts characters. For multibyte text, the character count can differ from the byte count.

You can combine options:

```bash
wc -wc course.txt
```

This reports the word and byte counts.

### Count lines that match a pattern

```bash
grep '2017-07' seasonal/spring.csv | wc -l
```

This works in two stages:

1. `grep '2017-07' seasonal/spring.csv` outputs lines containing `2017-07`.
2. `wc -l` counts the lines it receives.

In the course example, this returns `3`, meaning three lines matched.

## 8. Sorting with `sort`

`sort` arranges lines of text in order.

Example:

```bash
sort animals.txt
```

By default, `sort` sorts lines lexicographically according to the active locale. For simple lowercase words, the result often looks alphabetical.

To sort the extracted tooth names:

```bash
cut -d , -f 2 seasonal/winter.csv | grep -v Tooth | sort
```

This extracts the second column, removes the header line, and sorts the remaining values.

### Sort and save the result

```bash
sort animals.txt > sorted-animals.txt
```

This saves the sorted output in `sorted-animals.txt`. If the destination exists, `>` replaces its existing contents.

### Get sorted unique lines with `sort -u`

```bash
sort -u animals.txt
```

The `-u` option outputs unique lines in sorted order. This is often a convenient alternative to `sort animals.txt | uniq`.

## 9. Removing Adjacent Duplicates with `uniq`

`uniq` removes **consecutive, adjacent duplicate lines**. It does not automatically find every repeated value if duplicates are separated by other lines.

Suppose `animals.txt` contains:

```text
cat
dog
cat
cat
```

Running:

```bash
uniq animals.txt
```

produces:

```text
cat
dog
cat
```

The two adjacent `cat` lines at the end are collapsed, but the first `cat` remains because it is separated from the others by `dog`.

### Sort before using `uniq`

```bash
sort animals.txt | uniq
```

Sorting places identical lines next to one another. `uniq` can then remove the repeated adjacent lines.

### Count repeated lines with `uniq -c`

```bash
sort animals.txt | uniq -c
```

This prints a count beside each unique line. For the example file, the result is equivalent to:

```text
      2 cat
      1 dog
```

### `uniq` vs. `sort -u`

```bash
sort animals.txt | uniq
```

and

```bash
sort -u animals.txt
```

both provide sorted unique lines for ordinary text input. Use `sort -u` for a compact command, or use `sort | uniq -c` when you need counts.

## 10. Combining `cut`, `grep`, `sort`, and `uniq`

The power of shell pipelines comes from combining small tools.

### Example 1: Extract a column and remove headers

```bash
cut -d , -f 2 seasonal/winter.csv | grep -v Tooth
```

- `cut -d , -f 2`: split each line using a comma and select field 2.
- `grep -v Tooth`: output lines that do **not** contain `Tooth`.

`grep -v` inverts the match: matching lines are excluded, and nonmatching lines are retained.

**CSV limitation:** `cut` is a simple delimiter-based tool. It does not correctly parse every CSV format, especially fields containing quoted commas.

### Example 2: Sort the values

```bash
cut -d , -f 2 seasonal/winter.csv | grep -v Tooth | sort
```

The final `sort` receives the filtered values and sorts them.

### Example 3: Count each category

```bash
cut -d , -f 2 seasonal/winter.csv | grep -v Tooth | sort | uniq -c
```

The pipeline does this:

1. `cut` extracts the second column.
2. `grep -v Tooth` removes the header line.
3. `sort` groups identical values together by sorting them.
4. `uniq -c` counts each group of identical adjacent lines.

For the course's `seasonal/winter.csv` data, the counts are:

```text
      4 bicuspid
      7 canine
      6 incisor
      4 molar
      4 wisdom
```

The counts add up to 25 records.

### Example 4: Save the counts

```bash
cut -d , -f 2 seasonal/winter.csv | grep -v Tooth | sort | uniq -c > tooth-counts.txt
```

The pipeline processes the data, and `>` saves the final output in `tooth-counts.txt`.

To inspect the saved result:

```bash
cat tooth-counts.txt
```

## 11. Command Reference

| Command or symbol | Purpose | Example |
|---|---|---|
| `>` | Redirect output; overwrite destination contents | `head -n 3 file.csv > result.txt` |
| `>>` | Append output to a file | `echo "new line" >> notes.txt` |
| `\|` | Pipe one command's output to another command | `cat file.txt \| sort` |
| `wc -l` | Count lines | `wc -l file.txt` |
| `wc -w` | Count words | `wc -w file.txt` |
| `wc -c` | Count bytes | `wc -c file.txt` |
| `wc -m` | Count characters | `wc -m file.txt` |
| `sort` | Sort lines | `sort names.txt` |
| `sort -u` | Sort and output unique lines | `sort -u names.txt` |
| `uniq` | Remove adjacent duplicate lines | `sort names.txt \| uniq` |
| `uniq -c` | Count adjacent duplicate lines | `sort names.txt \| uniq -c` |
| `grep -v PATTERN` | Output lines that do not match | `grep -v Tooth` |
| `cut -d , -f 2` | Select field 2 using comma as delimiter | `cut -d , -f 2 data.csv` |
| `cat` | Display file contents | `cat result.txt` |
| `pwd` | Display current directory | `pwd` |

## 12. Common Mistakes

### Mistake 1: Using `>` when you meant to append

```bash
echo "second" > notes.txt
```

This replaces existing contents. Use `>>` to append instead.

### Mistake 2: Assuming `uniq` removes all duplicates

```bash
uniq animals.txt
```

This only removes adjacent repeated lines. Use:

```bash
sort animals.txt | uniq
```

or:

```bash
sort -u animals.txt
```

### Mistake 3: Saving output before filtering it

Incorrect for the intended filter:

```bash
cut -d , -f 2 seasonal/*.csv > teeth-only.txt | grep -v Tooth
```

Correct:

```bash
cut -d , -f 2 seasonal/*.csv | grep -v Tooth > teeth-only.txt
```

Put the redirection after the command whose output you want to save.

### Mistake 4: Thinking `>` copies an existing file

`>` does not copy a source file. It directs a command's output into a destination file. Bash creates the destination if necessary or truncates it if it already exists.

### Mistake 5: Thinking a pipe saves output

A pipe does not save output to a file by itself. It passes output to another command. Use `>` or `>>` when you want to save output.

### Mistake 6: Treating `cut` as a full CSV parser

`cut -d ,` splits on commas without understanding CSV quoting rules. For complex CSV files, use a CSV-aware tool or programming language.

## 13. Practice Exercises

Try these before looking at the solutions.

### Exercise 1: Save the first five lines

Write a command that saves the first five lines of `seasonal/winter.csv` to `first-five.txt`.

### Exercise 2: Append output

Append the first two lines of `seasonal/winter.csv` to `first-five.txt` without replacing its existing contents.

### Exercise 3: Count matching lines

Count how many lines in `seasonal/spring.csv` contain `2017-07`.

### Exercise 4: Remove duplicate values

Extract the second column from `seasonal/winter.csv`, remove the header line containing `Tooth`, and output each category only once in sorted order.

### Exercise 5: Count categories

Extend Exercise 4 so the output includes the count for each category.

### Exercise 6: Save filtered data

Extract the second column from all CSV files in `seasonal/`, remove lines containing `Tooth`, and save the remaining lines to `teeth-only.txt`.

### Exercise 7: Explain the difference

In your own words, explain why these commands behave differently:

```bash
cut -d , -f 2 seasonal/*.csv | grep -v Tooth > teeth-only.txt
```

```bash
cut -d , -f 2 seasonal/*.csv > teeth-only.txt | grep -v Tooth
```

### Exercise 8: Find the issue

A file contains:

```text
pear
apple
pear
```

Why might `uniq` fail to remove both occurrences of `pear`? Write a command that outputs each value once.

## 14. Solutions

### Solution 1

```bash
head -n 5 seasonal/winter.csv > first-five.txt
```

### Solution 2

```bash
head -n 2 seasonal/winter.csv >> first-five.txt
```

### Solution 3

```bash
grep '2017-07' seasonal/spring.csv | wc -l
```

In the course example, the output is `3`.

### Solution 4

```bash
cut -d , -f 2 seasonal/winter.csv | grep -v Tooth | sort -u
```

### Solution 5

```bash
cut -d , -f 2 seasonal/winter.csv | grep -v Tooth | sort | uniq -c
```

### Solution 6

```bash
cut -d , -f 2 seasonal/*.csv | grep -v Tooth > teeth-only.txt
```

### Solution 7

In the first command, `cut` sends its output to `grep`, and `grep`'s filtered output is saved to the file. In the second, `cut`'s output goes directly to the file, so `grep` receives no normal output through the pipe.

### Solution 8

`uniq` only removes adjacent duplicates. The two `pear` lines are separated by `apple`, so sort the lines first:

```bash
sort fruit.txt | uniq
```

Or use:

```bash
sort -u fruit.txt
```

## 15. Key Takeaways

1. **`>` redirects output to a file** and normally overwrites existing contents.
2. **`>>` appends output** to a file without removing existing contents.
3. **`|` passes output from one command to another.**
4. **`wc` counts lines, words, bytes, or characters.**
5. **`sort` orders lines; `uniq` removes adjacent duplicates.**
6. **`sort | uniq -c` counts repeated values.**
7. Put redirection after the command whose output you want to save.
8. Small commands become powerful when combined into a pipeline.

### A useful pattern to remember

```bash
cut -d , -f 2 data.csv | grep -v Header | sort | uniq -c > summary.txt
```

Read it from left to right: extract, filter, sort, count, save.

---

## Next Steps

- Practice the commands on small text files before using them on important data.
- Try combining `grep`, `cut`, `sort`, `uniq`, and `wc` in different orders.
- Before running a command with `>`, check whether the destination file already contains information you need.
- Keep this chapter as a reference while moving to the next section of the course.
