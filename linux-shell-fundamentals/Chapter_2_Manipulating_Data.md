# Chapter 2: Manipulating Data

**Course:** DataCamp — Introduction to Shell  
**Chapter:** 2 — Manipulating Data  
**Level:** Beginner  
**Status:** Covered

> **Learning objective:** Learn to inspect, extract, search, and combine text data using Linux shell commands without opening a spreadsheet or text editor.

## Table of Contents

1. [What does manipulating data mean?](#1-what-does-manipulating-data-mean)
2. [Example dataset and file structure](#2-example-dataset-and-file-structure)
3. [`cat` — Display file contents](#3-cat--display-file-contents)
4. [`less` — Read long files interactively](#4-less--read-long-files-interactively)
5. [`head` — View the beginning of a file](#5-head--view-the-beginning-of-a-file)
6. [`tail` — View the end of a file](#6-tail--view-the-end-of-a-file)
7. [Command options and flags](#7-command-options-and-flags)
8. [`cut` — Extract fields from text](#8-cut--extract-fields-from-text)
9. [Delimiters, indexing, and CSV limitations](#9-delimiters-indexing-and-csv-limitations)
10. [`grep` — Search and filter lines](#10-grep--search-and-filter-lines)
11. [`paste` — Combine files side by side](#11-paste--combine-files-side-by-side)
12. [How these tools work internally](#12-how-these-tools-work-internally)
13. [Common mistakes and troubleshooting](#13-common-mistakes-and-troubleshooting)
14. [Command cheat sheet](#14-command-cheat-sheet)
15. [Practice exercises](#15-practice-exercises)
16. [Knowledge check](#16-knowledge-check)
17. [Chapter summary](#17-chapter-summary)

---

## 1. What does manipulating data mean?

In Chapter 1, you used commands such as `ls`, `cd`, `cp`, and `mv` to work with **files as objects**. In Chapter 2, you work with the **text stored inside files**.

For example, a CSV file may contain:

```csv
Date,Tooth
2017-01-03,bicuspid
2017-01-05,incisor
2017-01-07,canine
```

You might want to:

- Display its contents.
- Read a long file one screen at a time.
- View only the first or last few rows.
- Extract a particular column.
- Find rows containing a word or date.
- Join lines from two files side by side.

These are common tasks in data engineering, DevOps, and MLOps, especially when inspecting logs, datasets, configuration files, or model outputs on remote servers.

### Basic command structure

```bash
command [options] [arguments]
```

For example:

```bash
head -n 5 seasonal/winter.csv
```

- `head` is the command.
- `-n 5` is an option specifying how many lines to display.
- `seasonal/winter.csv` is the file argument.

The brackets in `command [options] [arguments]` are documentation notation; you do not type them literally.

---

## 2. Example dataset and file structure

The exercises use a directory named `seasonal` containing CSV files for different seasons.

```text
/home/repl/
├── course.txt
├── seasonal/
│   ├── spring.csv
│   ├── summer.csv
│   ├── autumn.csv
│   └── winter.csv
├── people/
│   └── agarwal.txt
├── backup/
└── bin/
```

> This tree illustrates the course practice environment; your own Linux or WSL directories may be different.

A typical CSV has a header row followed by data rows:

```csv
Date,Tooth
2017-01-03,bicuspid
2017-01-05,incisor
```

The comma separates the fields `Date` and `Tooth`.

**Important:** The shell utilities in this chapter generally treat files as **lines of text**, not as structured database tables. This distinction explains several limitations later in the chapter.

---

## 3. `cat` — Display file contents

`cat` is short for **concatenate**. It writes the contents of one or more files to standard output (normally your terminal).

### View one file

```bash
cat seasonal/winter.csv
```

Example output:

```csv
Date,Tooth
2017-01-03,bicuspid
2017-01-05,incisor
```

### View multiple files

```bash
cat seasonal/spring.csv seasonal/winter.csv
```

The contents are displayed sequentially: the first file, followed by the second. If both files contain headers, both headers appear.

### When should you use `cat`?

Use it when the file is short enough to read comfortably in the terminal. For long files, `less` is usually more convenient.

**Remember:** `cat` displays content; it does not understand the meaning of CSV columns.

---

## 4. `less` — Read long files interactively

`less` is a **pager**. It lets you navigate a long text file without printing all of its contents onto the terminal at once.

```bash
less seasonal/winter.csv
```

Unlike `cat`, `less` opens an interactive viewing interface.

### Essential `less` controls

| Key | Action |
| --- | --- |
| `Space` | Move forward one screen |
| `b` | Move backward one screen |
| `q` | Quit `less` |
| `/word` | Search forward for `word` |
| `n` | Jump to the next search match |
| `:n` | View the next file when multiple files were opened |
| `:p` | View the previous file when multiple files were opened |

### Open several files

```bash
less seasonal/spring.csv seasonal/summer.csv
```

Press `:n` to switch to the next file and `:p` to switch back.

### Example: Search inside a file

```bash
less seasonal/winter.csv
```

Then type:

```text
/incisor
```

Press `Enter` to search and `n` to find the next occurrence.

### `cat` vs `less`

| Feature | `cat` | `less` |
| --- | --- | --- |
| Prints content to terminal output | Yes | Interactive display instead |
| Useful for short files | Yes | Yes |
| Comfortable for long files | Usually not | Yes |
| Interactive navigation | No | Yes |
| Search within viewer | No | Yes |
| Exit with `q` | Not necessary | Yes |

---

## 5. `head` — View the beginning of a file

`head` displays the first part of a file. By default, it displays the first **10 lines**.

```bash
head seasonal/winter.csv
```

### Specify the number of lines

```bash
head -n 5 seasonal/winter.csv
```

This prints the first five **lines**, not necessarily five data records.

Suppose the file begins:

```csv
Date,Tooth
2017-01-03,bicuspid
2017-01-05,incisor
2017-01-07,canine
2017-01-09,molar
2017-01-11,wisdom
```

Then:

```bash
head -n 5 seasonal/winter.csv
```

prints:

```csv
Date,Tooth
2017-01-03,bicuspid
2017-01-05,incisor
2017-01-07,canine
2017-01-09,molar
```

That is **one header plus four data rows**.

To view the header and the first five data records:

```bash
head -n 6 seasonal/winter.csv
```

> **Key idea:** `head` counts physical lines. It does not automatically exclude CSV headers.

---

## 6. `tail` — View the end of a file

`tail` displays the final part of a file. By default, it shows the last **10 lines**.

```bash
tail seasonal/winter.csv
```

### Display the last seven lines

```bash
tail -n 7 seasonal/winter.csv
```

### Display from a specific line onward

```bash
tail -n +7 seasonal/winter.csv
```

This means **start at line 7 and continue to the end**, including line 7.

Compare:

| Command | Meaning |
| --- | --- |
| `tail -n 7 file.csv` | Last seven lines |
| `tail -n +7 file.csv` | From line seven through the end |
| `head -n 7 file.csv` | First seven lines |

The plus sign changes the interpretation of the number for `tail`.

### Skip the CSV header

```bash
tail -n +2 seasonal/winter.csv
```

Because the header is line 1, starting at line 2 skips it.

### Follow a growing file

```bash
tail -f application.log
```

The `-f` option keeps watching the file and displays newly appended lines. This is particularly useful for application logs. Press `Ctrl+C` to stop.

> `tail -f` is an additional practical example relevant to DevOps; it is not necessary for understanding the basic DataCamp `tail` exercises.

---

## 7. Command options and flags

An **option** (or **flag**) changes how a command behaves.

For example:

```bash
head -n 5 seasonal/winter.csv
```

Here `-n` tells `head` that you are specifying a line count, and `5` supplies that count.

### Short and long options

Some programs support both forms:

```bash
head -n 5 seasonal/winter.csv
```

```bash
head --lines=5 seasonal/winter.csv
```

These have the same effect in GNU `head`.

- `-n` is a short option.
- `--lines` is a long option.

Not every program supports the same options or long names.

### Combine short flags

For example:

```bash
ls -R -F /home/repl
```

- `-R` lists subdirectories recursively.
- `-F` adds indicators such as `/` after directory names.

Options that take no separate values can often be combined:

```bash
ls -RF /home/repl
```

### Read the manual

```bash
man head
```

```bash
man grep
```

Manual pages often contain sections such as `NAME`, `SYNOPSIS`, `DESCRIPTION`, and `OPTIONS`.

In a synopsis, notation such as `[OPTION]` usually indicates something optional. It is not normally literal shell syntax.

Press `q` to exit the manual viewer.

---

## 8. `cut` — Extract fields from text

`cut` selects parts of each input line. In this chapter, its main use is extracting **delimiter-separated fields**.

### Basic syntax

```bash
cut -d DELIMITER -f FIELD_NUMBER FILE
```

- `-d` selects the delimiter separating fields.
- `-f` selects which field(s) to print.
- Field numbering starts at **1**, not 0.

### Example: Extract the first CSV column

Suppose `students.csv` contains:

```csv
Name,Age,City
Akash,28,Comilla
Rahim,25,Dhaka
Karim,30,Chattogram
```

Run:

```bash
cut -d , -f 1 students.csv
```

Output:

```text
Name
Akash
Rahim
Karim
```

### Extract the second column

```bash
cut -d , -f 2 students.csv
```

Output:

```text
Age
28
25
30
```

### Extract multiple columns

```bash
cut -d , -f 1,3 students.csv
```

Output:

```csv
Name,City
Akash,Comilla
Rahim,Dhaka
Karim,Chattogram
```

### Extract a range of columns

```bash
cut -d , -f 2-3 students.csv
```

Output:

```csv
Age,City
28,Comilla
25,Dhaka
30,Chattogram
```

### DataCamp example

```bash
cut -d , -f 2 seasonal/winter.csv
```

This prints the `Tooth` column, including the header `Tooth`.

### Spaces in command syntax

These are equivalent for this single-character comma delimiter:

```bash
cut -d, -f1 students.csv
```

```bash
cut -d , -f 1 students.csv
```

Both pass a comma as the delimiter and select field 1.

---

## 9. Delimiters, indexing, and CSV limitations

### What is a delimiter?

A delimiter is a character used to separate fields in a line.

Examples:

```text
Akash,28,Comilla
```

Delimiter: comma (`,`)

```text
Akash:28:Comilla
```

Delimiter: colon (`:`)

```text
Akash|28|Comilla
```

Delimiter: vertical bar (`|`)

### Example: Colon-separated fields

Suppose `values.txt` contains:

```text
first:second:third:
```

Run:

```bash
cut -d : -f 2-4 values.txt
```

Output:

```text
second:third:
```

Why? The trailing `:` creates an **empty fourth field**:

| Field number | Value |
| --- | --- |
| 1 | `first` |
| 2 | `second` |
| 3 | `third` |
| 4 | Empty string |

The delimiter before the empty final field remains visible in the output.

### Important: `cut` is not a complete CSV parser

Consider:

```csv
Name,Age
"Johel,Ranjit",28
```

A proper CSV parser treats `"Johel,Ranjit"` as **one field** because the comma is inside quotation marks.

But:

```bash
cut -d , -f 1 data.csv
```

would treat the comma inside the quoted name as a delimiter. The extracted text for that row would be incomplete:

```text
"Johel
```

**Why this matters:** `cut` does not understand CSV quoting rules. Use a real CSV parser (for example, Python's `csv` module) for complex CSV files containing quoted commas, embedded newlines, or other CSV-specific rules.

### When is `cut` appropriate?

It is convenient for simple, consistently delimited text such as basic logs, uncomplicated CSV files, or colon-separated records.

---

## 10. `grep` — Search and filter lines

`grep` searches text for a pattern and prints matching lines.

### Basic syntax

```bash
grep PATTERN FILE
```

### Find matching records

```bash
grep molar seasonal/autumn.csv
```

This prints lines in `autumn.csv` that contain `molar`.

### Useful `grep` options

| Option | Meaning | Example |
| --- | --- | --- |
| `-c` | Count matching **lines** | `grep -c incisor file.csv` |
| `-h` | Suppress filename prefixes | `grep -h molar *.csv` |
| `-i` | Ignore letter case | `grep -i molar file.csv` |
| `-l` | Print names of files containing a match | `grep -l molar *.csv` |
| `-n` | Include original line numbers | `grep -n molar file.csv` |
| `-v` | Print lines that **do not** match | `grep -v molar file.csv` |

### `grep -v`: Invert the match

```bash
grep -v molar seasonal/spring.csv
```

This prints lines **not containing** `molar`.

### Combine options

```bash
grep -v -n molar seasonal/spring.csv
```

This prints nonmatching lines and their **original line numbers**.

For example, with this illustrative file:

```text
1:Date,Tooth
2:2017-01-03,molar
3:2017-01-05,incisor
4:2017-01-07,canine
```

The output would be:

```text
1:Date,Tooth
3:2017-01-05,incisor
4:2017-01-07,canine
```

The `-n` numbers refer to positions in the original file, not renumbered positions after filtering.

### Count matching lines

```bash
grep -c incisor seasonal/autumn.csv seasonal/winter.csv
```

With multiple input files, GNU `grep` normally prints a separate count for each file, prefixed by its filename.

**Important:** `grep -c` counts matching **lines**, not total occurrences of the pattern. If a line contains the word twice, it still counts as one matching line.

### Case-insensitive search

```bash
grep -i molar seasonal/autumn.csv
```

Matches `molar`, `Molar`, `MOLAR`, and other case variations.

### Show only filenames with matches

```bash
grep -l incisor seasonal/*.csv
```

Prints the names of matching files, rather than the matching lines.

### Suppress filename prefixes

```bash
grep -h incisor seasonal/*.csv
```

When searching multiple files, `-h` omits filename prefixes from the printed matching lines.

### A useful warning about patterns

By default, `grep` interprets its pattern as a **basic regular expression**, not necessarily a literal string. Characters such as `.` can have special meanings.

For an exact literal substring search, GNU `grep -F` is often easier:

```bash
grep -F '2017-07' seasonal/spring.csv
```

This is an additional practical tip beyond the core course exercises.

---

## 11. `paste` — Combine files side by side

`paste` joins corresponding **lines** from two or more files.

### Example

Suppose `names.txt` contains:

```text
Akash
Rahim
Karim
```

And `cities.txt` contains:

```text
Comilla
Dhaka
Chattogram
```

Run:

```bash
paste -d , names.txt cities.txt
```

Output:

```csv
Akash,Comilla
Rahim,Dhaka
Karim,Chattogram
```

The `-d ,` option tells `paste` to place a comma between the joined values. Without this option, `paste` normally uses a tab delimiter.

### DataCamp example

```bash
paste -d , seasonal/autumn.csv seasonal/winter.csv
```

This joins the two files **by line position**:

- Line 1 of autumn with line 1 of winter.
- Line 2 of autumn with line 2 of winter.
- And so on.

For example, if both files start with `Date,Tooth`, the combined header becomes:

```csv
Date,Tooth,Date,Tooth
```

### What if files have different numbers of lines?

If one file runs out of lines, `paste` fills its missing contribution with empty text while continuing to print lines from the longer file.

Example:

`left.txt`:

```text
A
B
C
```

`right.txt`:

```text
1
2
```

Command:

```bash
paste -d , left.txt right.txt
```

Output:

```text
A,1
B,2
C,
```

The last line has an empty second field. Depending on how a downstream tool interprets missing fields, this may create data-quality problems.

### Why `paste` is not a database join

`paste` does **not** match records by an ID, date, or other key. It simply matches line 1 with line 1, line 2 with line 2, and so forth.

Therefore, it can incorrectly combine unrelated records if the files are not aligned or sorted consistently.

For key-based joins, use a suitable data-processing tool rather than assuming `paste` matches corresponding records semantically.

---

## 12. How these tools work internally

These commands are useful because they generally operate on streams of text and can process data without opening a graphical application.

### High-level execution flow

```text
You type a command
        |
        v
Bash parses the command
        |
        v
Linux starts the program
        |
        v
Program reads file data
        |
        v
Program processes text
        |
        v
Output appears in terminal
```

For example:

```bash
grep molar seasonal/autumn.csv
```

At a simplified level:

1. Bash identifies `grep` and its arguments.
2. The operating system runs the `grep` program.
3. `grep` reads the file's contents through the filesystem.
4. `grep` checks lines for the requested pattern.
5. Matching lines are written to standard output.

### Standard input and output

| Stream | File descriptor | Typical role |
| --- | --- | --- |
| Standard input (`stdin`) | `0` | Input data |
| Standard output (`stdout`) | `1` | Normal program output |
| Standard error (`stderr`) | `2` | Error messages |

You will use these concepts more directly in **Chapter 3: Combining Tools**, when studying pipes (`|`) and redirection (`>`, `>>`).

### Does the entire file have to fit in RAM?

Usually not. Tools such as `grep`, `cut`, and `head` can process input incrementally rather than loading a whole file into memory first.

That makes them particularly useful when working with large text files and server logs. Exact memory usage and implementation details vary by command.

---

## 13. Common mistakes and troubleshooting

| Mistake | Why it is a problem | Correct approach |
| --- | --- | --- |
| `head -n 5 file.csv` expecting five data records | The CSV header is also a line | Use `head -n 6` for a header plus five records |
| `tail -n 7 file.csv` expecting to start at line 7 | It means the **last** seven lines | Use `tail -n +7 file.csv` |
| `cut -d , -f 0 file.csv` | Field indexing begins at 1 | Use `-f 1` for the first field |
| Using `cut` on quoted CSV fields containing commas | `cut` ignores CSV quotation rules | Use a CSV-aware parser |
| `grep -c word file` interpreted as counting every occurrence | It counts matching lines | Use a different approach if occurrence counts are needed |
| `grep -v word file` expecting matching lines | `-v` inverts the match | Omit `-v` to print matches |
| `paste` used to match rows by date | It joins by line number, not date | Use a key-aware join or parser |
| Running `less` and thinking the terminal is stuck | `less` is interactive | Press `q` to exit |
| Treating `-n` or `-f` as separate commands | Options modify a command | Place them with the appropriate command |

---

## 14. Command cheat sheet

| Command | Purpose |
| --- | --- |
| `cat file.txt` | Print file contents |
| `cat file1 file2` | Print multiple files in sequence |
| `less file.txt` | Read file interactively |
| `head file.txt` | Show first 10 lines |
| `head -n 5 file.txt` | Show first 5 lines |
| `tail file.txt` | Show last 10 lines |
| `tail -n 7 file.txt` | Show last 7 lines |
| `tail -n +7 file.txt` | Show from line 7 onward |
| `tail -f app.log` | Follow appended log lines |
| `cut -d , -f 2 file.csv` | Extract second comma-separated field |
| `cut -d , -f 1,3 file.csv` | Extract fields 1 and 3 |
| `cut -d : -f 2-4 file.txt` | Extract fields 2 through 4 using `:` |
| `grep molar file.csv` | Show lines containing `molar` |
| `grep -v molar file.csv` | Show lines not containing `molar` |
| `grep -n molar file.csv` | Include original line numbers |
| `grep -c molar file.csv` | Count matching lines |
| `grep -i molar file.csv` | Ignore case |
| `grep -l molar *.csv` | Show matching filenames |
| `grep -h molar *.csv` | Hide filename prefixes |
| `paste -d , file1 file2` | Combine corresponding lines with commas |
| `man grep` | Open the manual for `grep` |

---

## 15. Practice exercises

The following exercises are based on the concepts studied in Chapter 2. Run them from `/home/repl` in the course environment, or adapt the paths to your local dataset.

### Exercise 1 — Inspect a dataset

```bash
cat seasonal/winter.csv
```

**Question:** Is the file short enough for `cat` to be convenient, or would `less` be better?

### Exercise 2 — Read a long file

```bash
less seasonal/autumn.csv
```

Search for `molar` with `/molar`, jump to the next match with `n`, and quit with `q`.

### Exercise 3 — View the first five lines

```bash
head -n 5 seasonal/winter.csv
```

**Question:** How many of those lines are actual data records if the file has one header row?

**Answer:** Four.

### Exercise 4 — View the last seven lines

```bash
tail -n 7 seasonal/winter.csv
```

### Exercise 5 — Start at line seven

```bash
tail -n +7 seasonal/winter.csv
```

**Question:** How is this different from Exercise 4?

**Answer:** It starts at the seventh line of the file and continues to the end, instead of displaying the final seven lines.

### Exercise 6 — Extract tooth names

```bash
cut -d , -f 2 seasonal/winter.csv
```

**Question:** Why does `Tooth` appear in the output?

**Answer:** Because `cut` also processes the CSV header line.

### Exercise 7 — Search for molars

```bash
grep molar seasonal/autumn.csv
```

### Exercise 8 — Exclude molars and show line numbers

```bash
grep -v -n molar seasonal/spring.csv
```

**Question:** Do the line numbers get reassigned after filtering?

**Answer:** No. They refer to the original file.

### Exercise 9 — Count incisor records in two files

```bash
grep -c incisor seasonal/autumn.csv seasonal/winter.csv
```

**Question:** Why might you see two counts instead of one?

**Answer:** `grep -c` normally reports a separate count for each named input file.

### Exercise 10 — Combine two files line by line

```bash
paste -d , seasonal/autumn.csv seasonal/winter.csv
```

**Question:** Does this match records by date?

**Answer:** No. It matches lines by position.

---

## 16. Knowledge check

Try answering these before reading the answers.

1. What is the main difference between `cat` and `less`?
2. Does `head -n 5 file.csv` necessarily display five data records?
3. What does the `+` mean in `tail -n +7 file.csv`?
4. Are `cut` fields numbered from zero or one?
5. What does `grep -v Tooth file.csv` do?
6. Does `grep -c` count matching lines or every occurrence of a word?
7. Why can `cut` fail on a valid CSV containing quoted commas?
8. Does `paste` join records by a shared key?

<details>
<summary><strong>Show answers</strong></summary>

1. `cat` prints the content; `less` opens an interactive pager.
2. No. A header is also counted as a line.
3. Start from line 7, inclusive, and continue to the end.
4. One.
5. Prints lines that do not contain `Tooth`.
6. Matching lines.
7. It treats every delimiter character as a separator without interpreting CSV quoting rules.
8. No. It combines corresponding line positions.

</details>

---

## 17. Chapter summary

Chapter 2 introduces several essential text-processing tools:

- **Display text:** `cat`.
- **Browse text:** `less`.
- **Inspect the beginning or end:** `head`, `tail`.
- **Extract delimiter-separated fields:** `cut`.
- **Search and filter lines:** `grep`.
- **Combine files side by side:** `paste`.
- **Understand command behavior:** flags, delimiters, line numbering, and manual pages.

### Key mental model

```text
Text file
   |
   +--> cat   : display all contents
   |
   +--> less  : browse interactively
   |
   +--> head  : first lines
   |
   +--> tail  : last lines
   |
   +--> cut   : selected fields
   |
   +--> grep  : matching or nonmatching lines
   |
   +--> paste : combine lines with another file
```

These utilities are the foundation for **Chapter 3: Combining Tools**, where you connect commands with pipes and redirect their output into files.

---

*Notes prepared as an independent, beginner-friendly study guide based on the topics and exercises discussed while learning DataCamp's Introduction to Shell. Example data and explanatory examples are illustrative unless identified as course commands.*
