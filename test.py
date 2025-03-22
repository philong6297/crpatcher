from pathlib import Path

print(is_filename_only(Path("file.txt")))


print(is_filename_only(Path("subdir/file.txt")))


print(is_filename_only(Path("/etc/passwd")))


print(is_filename_only(Path("just_a_name")))
