if status is-interactive
    # Commands to run in interactive sessions can go here
end

# Finds and activates the first 'activate.fish' script found in any subdirectory
# under the current directory.

# Usage:
# find-and-activate

# This function searches for any 'activate.fish' script in any subdirectory
# under the current directory. When it finds the first such script, it sources
# it (i.e., runs it in the current shell context) and returns immediately.
# The purpose of this function is to help set up development environments that
# require activation scripts to be sourced to add the necessary environment
# variables and settings.

# Note that this function assumes that each subdirectory contains at most one
# 'activate.fish' script, and that the first one found is the one to be sourced.
# If multiple scripts are found, only the first one will be used, and the others
# will be ignored. If no 'activate.fish' script is found, this function will
# simply return without doing anything.

# Example usage:
# $ cd myproject
# $ find-and-activate
function find-and-activate
  for dir in (find . -type d)
    if test -f $dir/activate.fish
      . $dir/activate.fish
      return
    end
  end
end

# create-or-remove-symlink: Creates or removes a symlink to a target file.

# This function takes one argument, which is the path to the target file. It creates a
# symlink to the target file in /usr/local/bin/ with a name in lowercase letters. If
# a symlink already exists at that path, it will be removed before creating the new one.

# Parameters:
#     $argv[1] (string): The path to the target file.

# Returns:
#     None.

# Example:
#     $ create-or-remove-symlink /path/to/target/file
function create-or-remove-symlink
  set target (readlink -f $argv[1])
  set linkname (basename $target | tr '[:upper:]' '[:lower:]')
  set linkpath /usr/local/bin/$linkname

  if test -L $linkpath
    echo Removing existing symlink: $linkpath
    sudo rm $linkpath
  else
    echo Creating symlink: $linkpath -\> $target
    sudo ln -s $target $linkpath
  end
end