{
  pkgs ? import <nixpkgs> { },
  lib ? pkgs.lib,
  themes ? [
    "catppuccin"
    "dracula"
    "everforest"
    "gruvbox"
    "kanagawa"
    "monokai"
    "rose-pine"
    "tokyo-storm"
  ],
}:

# gowall convert <path>/argenteuil_1970.17.42.jpg --output <PATH>/$THEME/ -t $THEME
let
  buildBelsedarWallpapers =
    {
      pkgs,
      pname,
      src,
      themes,
    }:
    pkgs.stdenvNoCC.mkDerivation {
      inherit pname src;
      version = "0.1";
      nativeBuildInputs = [
        pkgs.gowall
        pkgs.xdg-utils
      ];
      dontBuild = true;
      installPhase = ''
        export HOME=$(pwd)/.home
        mkdir -p $HOME  # else gowall cries
        ls -hal $src

        for theme in ${toString themes}; do
          echo "Converting to theme: $theme"
          mkdir -p "$out/share/backgrounds/belsedar/$theme"
          gowall convert --dir "$src" \
            --output "$out/share/backgrounds/belsedar/$theme/" \
            --theme "$theme" || echo "Warning: gowall returned nonzero exit code"
        done
        cp -r "$src" "$out/share/backgrounds/belsedar/origin"
      '';
    };
in
{
  baroque = buildBelsedarWallpapers {
    inherit pkgs;
    inherit themes;
    pname = "baroque";
    src = builtins.fetchTarball {
      url = "https://pixeldrain.com/api/file/heRJbiin?download=true";
      sha256 = "sha256:163j7dwpqxg1783pvhw4w8iwvjhwnns06r8s1fyk9gvjfijc1pvx";
    };
  };
  impressionist = buildBelsedarWallpapers {
    inherit pkgs;
    inherit themes;
    pname = "impressionist";
    src = builtins.fetchTarball {
      url = "https://pixeldrain.com/api/file/6Ju71xWo?download=true";
      sha256 = "sha256:0a2m6i01svczjx7rxhd4gjz8dps9gkqijh4kj1wvp8jzjl3hb47a";
    };
  };
  romantic = buildBelsedarWallpapers {
    inherit pkgs;
    inherit themes;
    pname = "romantic";
    src = builtins.fetchTarball {
      url = "https://pixeldrain.com/api/file/PmKL8X81?download=true";
      sha256 = "sha256:0i5jl74s4dqvsf0iygk18dlkxbsqy0iqf4lwdym6kmljgafp8bm9";
    };
  };
  general = buildBelsedarWallpapers {
    inherit pkgs;
    inherit themes;
    pname = "general";
    src = builtins.fetchTarball {
      url = "https://pixeldrain.com/api/file/ahiL5QGu?download=true";
      sha256 = "sha256:091wiikaczq2wbqk4hn02n822cvvq6gg24p9qyiwl35rdn56vsyc";
    };
  };
  pcc0 = buildBelsedarWallpapers {
    inherit pkgs;
    inherit themes;
    pname = "pcc0";
    src = builtins.fetchTarball {
      url = "https://pixeldrain.com/api/file/hjZAnHoV?download=true";
      sha256 = "sha256:0ldpb6hm02jb1v292iij51n1fr42y5j2h3kfihpddv6j9yy7sfcs";
    };
  };
}
