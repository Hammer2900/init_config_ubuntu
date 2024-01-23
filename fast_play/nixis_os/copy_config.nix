{ config, pkgs, ... }:
let
  git = pkgs.gitMinimal;
  source = pkgs.fetchgit {
    url = "https://github.com/Hammer2900/init_config_ubuntu.git";
    name = "init_config_ubuntu";
#    rev = "replace_with_your_rev"; # Your commit, branch, etc. here
#    sha256 = "replace_with_your_sha256"; # Hash of your repo (can use "lib.fakeSha256" for testing)
#    fetchSubmodules = false;
  };
in pkgs.stdenv.mkDerivation {
  name = "my-package";
  src = source;
  buildInputs = [ git ];
  buildCommand = ''
    pwd
    lsblk
    ls
  '';
}