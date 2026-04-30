# Edit this configuration file to define what should be installed on
# your system. Help is available in the configuration.nix(5) man page
# and in the NixOS manual (accessible by running `nixos-help`).

{ config, pkgs, ... }:

{
  imports =[
      ./hardware-configuration.nix
    ];

  boot.loader.grub.enable = true;
  boot.loader.grub.device = "/dev/sda"; # or "nodev" for efi only

  # Nix settings
  nix.settings.max-jobs = 4;
  nix.gc.automatic = true;
  nix.gc.options = "--delete-older-than 1d";
  nix.settings.experimental-features = [ "nix-command" "flakes" ];

  networking.hostName = "inixos";

  # Power Management
  services.tlp.enable = true;
  powerManagement.enable = true;
  powerManagement.cpuFreqGovernor = null; # will be managed by tlp

  # Network
  networking.networkmanager.enable = true;
  networking.nameservers =[ "8.8.8.8" "8.8.4.4" ];
  networking.networkmanager.connectionConfig = {
    "ethernet.mtu" = "1462";
    "wifi.mtu" = "1462";
  };
  programs.nm-applet.enable = true;

  # Variables
  environment.variables = {
    EDITOR = "micro";
    BROWSER = "firefox";
    _JAVA_OPTIONS = "-Dsun.java2d.uiScale=2";
    _JAVA_AWT_WM_NONREPARENTING = "1";
    QT_STYLE_OVERRIDE = "kvantum";
    TERMINAL = "sakura";
  };
  environment.sessionVariables.TERMINAL = [ "sakura" ];

  # Nano config
  programs.nano.nanorc = ''
    set softwrap
    set tabsize 4
    set tabstospaces
    set linenumbers
  '';

  # Git config
  programs.git = {
    enable = true;
    config = {
      user.name = "Hammer2900";
      user.email = "evgeny2900@gmail.com";
      github.user = "Hammer2900";
      init.defaultBranch = "main";
    };
  };

  programs.firefox.enable = true;
  programs.firefox.languagePacks =["uk" "ru" "en-US"];

  # Fish shell
  programs.fish = {
    enable = true;
    vendor.completions.enable = false;
    shellInit = "neofetch";
    shellAliases = { g = "git"; };
  };

  # Locale & Time
  console.font = "Lat2-Terminus16";
  time.timeZone = "Europe/Kyiv";

  # ================================================================= #
  # ГРАФИКА: X11, LightDM (Окно входа) и XFCE (Рабочий стол)
  # ================================================================= #
  services.xserver = {
    enable = true;

    # Включаем менеджер входа в систему
    displayManager.lightdm.enable = true;

    # Включаем XFCE
    desktopManager.xfce.enable = true;

    # Настройки клавиатуры
    xkb = {
      layout = "us,ru";
      options = "grp:switch,grp:alt_shift_toggle,grp:rctrl_toggle";
    };
  };

  # ================================================================= #
  # ЗВУК (Современный PipeWire)
  # ================================================================= #
  security.rtkit.enable = true;
  services.pipewire = {
    enable = true;
    alsa.enable = true;
    alsa.support32Bit = true;
    pulse.enable = true;
  };

  # User
  users.users.izot = {
    isNormalUser = true;
    initialPassword = "123456";
    home = "/home/izot2";
    shell = pkgs.bash;
    extraGroups =[ "wheel" "vboxusers" "networkmanager" "docker" "audio" "video" ];
    packages = with pkgs;[
      firefox tree fish lf navi btop htop
    ];
  };

  # OpenGL (Для ускорения графики)
  hardware.graphics = {
    enable = true;
    enable32Bit = true;
    extraPackages32 = with pkgs.pkgsi686Linux;[ libva ];
  };

  # Packages
  environment.systemPackages = with pkgs;[
    pcmanfm jetbrains.pycharm-community telegram-desktop sakura arandr keyd dmenu yad lxappearance feh
    pavucontrol winbox doublecmd protonup-qt bottles python3Packages.fabric black pdm hurl sniffnet navi duf ddgr ctop linux-wifi-hotspot
    antimicrox moltengamepad qjoypad
    vim git google-chrome firefox rofi micro broot python312 python311 neofetch flameshot xarchiver freefont_ttf terminus_font
    wget blueman cht-sh sshfs
    docker docker-compose cookiecutter clipit rofi-top rofi-rbw rofi-systemd rofi-bluetooth
  ];

  nixpkgs.config.allowUnfree = true;
  nixpkgs.config.permittedInsecurePackages =[
    "openssl-1.1.1w" "openssl-1.1.1u" "openssl-1.1.1v" "electron-12.2.3"
  ];

  programs.gnupg.agent = {
     enable = true;
     enableSSHSupport = true;
  };

  programs.bash.shellAliases = {
    hg = "history | grep";
    pin = "ping -D -O 8.8.8.8";
  };

  services.openssh.enable = true;

  security.sudo.wheelNeedsPassword = false;

  # Custom Services
  systemd.user.services."unclutter" = {
    enable = true;
    description = "hide cursor after X seconds idle";
    wantedBy = [ "default.target" ];
    serviceConfig = {
      Restart = "always";
      RestartSec = 2;
      ExecStart = "${pkgs.unclutter}/bin/unclutter";
    };
  };

  systemd.user.services."autocutsel" = {
    enable = true;
    description = "AutoCutSel";
    wantedBy =[ "default.target" ];
    serviceConfig = {
      Type = "forking";
      Restart = "always";
      RestartSec = 2;
      ExecStartPre = "${pkgs.autocutsel}/bin/autocutsel -fork";
      ExecStart = "${pkgs.autocutsel}/bin/autocutsel -selection PRIMARY -fork";
    };
  };

  nix.extraOptions = ''
    binary-caches-parallel-connections = 3
    connect-timeout = 5
  '';

  system.stateVersion = "24.05";

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

  # ВИРТУАЛБОКС. Гостевые дополнения (общий буфер обмена, адаптивное разрешение и драйверы)
  virtualisation.virtualbox.guest.enable = true;

  zramSwap.enable = true;
  zramSwap.algorithm = "lz4";
  zramSwap.memoryPercent = 50;

  services.blueman.enable = true;
  services.tumbler.enable = true;

  # Оставляем композитный менеджер для красоты (тени, прозрачность)
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