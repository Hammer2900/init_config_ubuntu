# Edit this configuration file to define what should be installed on
# your system.  Help is available in the configuration.nix(5) man page
# and in the NixOS manual (accessible by running `nixos-help`).

{ config, pkgs, ... }:

{
  imports =
    [
      ./hardware-configuration.nix
    ];

  boot.loader.grub.enable = true;
  # boot.loader.grub.efiSupport = true;
  # boot.loader.grub.efiInstallAsRemovable = true;
  # boot.loader.efi.efiSysMountPoint = "/boot/efi";
  # Define on which hard drive you want to install Grub.
  boot.loader.grub.device = "/dev/sda"; # or "nodev" for efi only

  nix.maxJobs = 4;
  nix.gc.automatic = true;
  nix.gc.options = "--delete-older-than 1d";

  networking.hostName = "inixos"; # Define your hostname.
  # Pick only one of the below networking options.
  # networking.wireless.enable = true;  # Enables wireless support via wpa_supplicant.

  services.tlp.enable = true;
  powerManagement.enable = true;
  powerManagement.cpuFreqGovernor = null; # will be managed by tlp

  networking.networkmanager.enable = true;  # Easiest to use and most distros use this by default.
  networking.nameservers = [ "8.8.8.8" "8.8.4.4" ];
  networking.networkmanager.connectionConfig = {
    "ethernet.mtu" = 1462;
    "wifi.mtu" = 1462;
  };
  programs.nm-applet.enable = true;
  environment.variables.EDITOR = "micro";
  environment.variables.BROWSER = "firefox";
#  environment.variables.GDK_SCALE = "2";
#  environment.variables.GDK_DPI_SCALE = "0.5";
  environment.variables._JAVA_OPTIONS = "-Dsun.java2d.uiScale=2";
  environment.variables._JAVA_AWT_WM_NONREPARENTING = "1";
  environment.variables.QT_STYLE_OVERRIDE = "kvantum";
  environment.variables.TERMINAL = "sakura";
  environment.sessionVariables.TERMINAL = [ "sakura" ];
  programs.nano.nanorc = ''
    set softwrap
    set tabsize 4
    set tabstospaces
    set linenumbers
  '';
  programs.git.enable = true;
#  programs.git.config.userName = "Hammer2900";
  programs.git.config.user.name = "Hammer2900";
  programs.git.config.user.email = "evgeny2900@gmail.com";
  programs.git.config.github.user = "Hammer2900";
  programs.git.config.init.defaultBranch = "main";
  programs.firefox.enable = true;
  programs.firefox.languagePacks = ["uk"];
  programs.fish.enable = true;
  programs.fish.vendor.completions.enable = false;
  programs.fish.shellInit = "neofetch";
  programs.fish.shellAliases = { g = "git"; };
  programs.hyprland.enable = true;

  # Set your time zone.
  console.font = "Lat2-Terminus16";
  time.timeZone = "Europe/Kyiv";

  # Configure network proxy if necessary
  # networking.proxy.default = "http://user:password@proxy:port/";
  # networking.proxy.noProxy = "127.0.0.1,localhost,internal.domain";

  # Select internationalisation properties.



















  # i18n.defaultLocale = "en_US.UTF-8";
  # console = {
  #   font = "Lat2-Terminus16";
  #   keyMap = "us";
  #   useXkbConfig = true; # use xkbOptions in tty.
  # };

  # Enable the X11 windowing system.
  services.xserver.enable = true;
  services.xserver.windowManager.default = "i3";
  services.xserver.windowManager.i3.enable = true;
  services.xserver.windowManager.i3.extraSessionCommands = "bindsym F7 exec sakura -e mc";

#  services.xserver.windowManager.awesome.enable = true;
#  services.xserver.windowManager.awesome.luaModules = [pkgs.luaPackages.vicious];





  # Configure keymap in X11
  services.xserver.layout = "us,ru";
  services.xserver.xkbOptions = "grp:switch,grp:alt_shift_toggle,grp:rctrl_toggle";

  # Enable CUPS to print documents.
  # services.printing.enable = true;

  # Enable sound.
  sound.enable = true;
  hardware.pulseaudio.enable = true;

  # Enable touchpad support (enabled default in most desktopManager).
  # services.xserver.libinput.enable = true;

  # Define a user account. Don't forget to set a password with ‘passwd’.
  users.users.izot = {
    isNormalUser = true;
    initialPassword = "123456";
    home = "/home/izot2";
    shell = pkgs.bash;
    extraGroups = [ "wheel" "vboxusers" "networkmanager" "docker" "audio" ];
    packages = with pkgs; [
      firefox
      tree fish lf navi btop htop
    ];
  };

  hardware.opengl.driSupport32Bit = true;
  hardware.opengl.extraPackages32 = with pkgs.pkgsi686Linux; [ libva ];
  hardware.pulseaudio.support32Bit = true;

  # List packages installed in system profile. To search, run:
  # $ nix search wget
  environment.systemPackages = with pkgs; [
    pcmanfm jetbrains.pycharm-community sublime4 telegram-desktop sakura arandr keyd dmenu yad lxappearance feh
    pavucontrol winbox doublecmd protonup-qt bottles Fabric black unify pdm hurl sniffnet navi duf ddgr ctop spaceFM linux-wifi-hotspot
    wifite2 retroarchFull antimicrox moltengamepad qjoypad
    vim git google-chrome firefox rofi micro broot python312 python311 neofetch flameshot xarchiver freefont_ttf ubuntu_font_family nerdfonts terminus_font
    wget i3 i3lock i3status i3blocks blueman
    i3wsr i3-easyfocus i3lock-pixeled docker docker-compose cookiecutter clipit rofi-top rofi-rbw rofi-systemd rofi-bluetooth
  ];

  nixpkgs.config = {
      allowUnfree = true;
  };

  nixpkgs.config.permittedInsecurePackages = [
    "openssl-1.1.1w" "openssl-1.1.1u" "openssl-1.1.1v" "electron-12.2.3"
  ];

  # Some programs need SUID wrappers, can be configured further or are
  # started in user sessions.
  # programs.mtr.enable = true;
   programs.gnupg.agent = {
     enable = true;
     enableSSHSupport = true;
   };
   programs = {
   bash = {shellAliases = {hg = "history | grep"; pin = "ping -D -O 8.8.8.8";};};};

  # List services that you want to enable:

  # Enable the OpenSSH daemon.
   services.openssh.enable = true;

  # Open ports in the firewall.
  # networking.firewall.allowedTCPPorts = [ ... ];
  # networking.firewall.allowedUDPPorts = [ ... ];
  # Or disable the firewall altogether.
  # networking.firewall.enable = false;

  # Copy the NixOS configuration file and link it from the resulting system
  # (/run/current-system/configuration.nix). This is useful in case you
  # accidentally delete configuration.nix.
  # system.copySystemConfiguration = true;

  # This value determines the NixOS release from which the default
  # settings for stateful data, like file locations and database versions
  # on your system were taken. It's perfectly fine and recommended to leave
  # this value at the release version of the first install of this system.
  # Before changing this value read the documentation for this option
  # (e.g. man configuration.nix or on https://nixos.org/nixos/options.html).
  security.sudo.wheelNeedsPassword = false;
  systemd.user.services."unclutter" = {
    enable = true;
    description = "hide cursor after X seconds idle";
    wantedBy = [ "default.target" ];
    serviceConfig.Restart = "always";
    serviceConfig.RestartSec = 2;
    serviceConfig.ExecStart = "${pkgs.unclutter}/bin/unclutter";
  };
  systemd.user.services."autocutsel" = {
    enable = true;
    description = "AutoCutSel";
    wantedBy = [ "default.target" ];
    serviceConfig.Type = "forking";
    serviceConfig.Restart = "always";
    serviceConfig.RestartSec = 2;
    serviceConfig.ExecStartPre = "${pkgs.autocutsel}/bin/autocutsel -fork";
    serviceConfig.ExecStart = "${pkgs.autocutsel}/bin/autocutsel -selection PRIMARY -fork";
  };
  nix.extraOptions = ''
    binary-caches-parallel-connections = 3
    connect-timeout = 5
  '';
  system.stateVersion = "23.05"; # Did you read the comment?
  security.allowSimultaneousMultithreading = true;
  boot.kernel.sysctl = {
    "kernel.sysrq" = 1;
    "net.core.rmem_default" = 262144;
    "net.core.rmem_max" = 67108864;
    "net.core.wmem_default" = 262144;
    "net.core.wmem_max" = 67108864;
    "kernel.pid_max" = 4194304;
    "fs.aio-max-nr" = 1048576;
    "fs.inotify.max_user_watches" = 1048576;
    "fs.inotify.max_queued_events" = 524288;
    "fs.file-max" = 300000;
  };
  virtualisation.virtualbox.host.enable = true;
  zramSwap.enable = true;
  zramSwap.algorithm = "lz4";
  zramSwap.memoryPercent = 50;
  services.blueman.enable = true;
  services.tumbler.enable = true;
  services.picom = {
    enable = true;
    fade = true;
    shadow = true;
    fadeDelta = 4 ;
    inactiveOpacity = 0.9;
    activeOpacity = 1;
    settings = {
      blur = {
	    strength = 5;
      };
    };
  };

}

