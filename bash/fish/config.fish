if status is-interactive
    # Commands to run in interactive sessions can go here
end

# Define the function
function find-and-activate
  for dir in (find . -type d)
    if test -f $dir/activate.fish
      . $dir/activate.fish
      return
    end
  end
end

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