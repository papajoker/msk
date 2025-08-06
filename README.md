
[![ui](https://i.postimg.cc/Kck4sWC5/screen.avif)](https://postimg.cc/nMxHX3Fs)

### Usage

load with plugins

```
uv run -m msm-test
```

load with one plugin

```
uv run -m msm-test --users
```

standalone plugin

```
~/WORK/msm-test/modules/kernels/main.py
~/WORK/msm-test/modules/mirrors/main.py
~/WORK/msm-test/modules/users/main.py
```

### user config

user can create ini file `/home/$USER/.config/msk.ini`, as

```
[kernels]
order = 55
title = "Noyaux"

[users]
title="Utilisateurs"
#category = "others"
color = "#f00"

[mirrors]
disable = 1
title = "Miroirs"
order = 999

[msm]
iconsize = 32
```
