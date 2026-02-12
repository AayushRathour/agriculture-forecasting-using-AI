{ pkgs }: {
  deps = [
    pkgs.postgresql
    pkgs.python310Full
    pkgs.python310Packages.pip
    pkgs.python310Packages.setuptools
    pkgs.python310Packages.wheel
  ];
}
