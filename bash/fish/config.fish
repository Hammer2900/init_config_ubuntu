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
