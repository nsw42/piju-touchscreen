# pijuui

Touch-screen UI for <https://github.com/nsw42/piju>

## Hardware setup

Additional hardware needed:

* The 7" touchscreen LCD: <https://www.okdo.com/p/official-raspberry-pi-7-touch-screen-lcd/>
* A case: <https://thepihut.com/collections/raspberry-pi-screens/products/raspberry-pi-7-touchscreen-display-case-clear?variant=32291995353150>

Cable up as per the Okdo instructions and put it in the case.  Add power and the screen shows Alpine Linux.

Following the Okdo instructions left the screen upside down. Adding `lcd_rotate=2` to usercfg.txt (see below) fixes that.

Note that this seemed quite electrically noisy, interfering with DAB radio reception when the screen was on. I've tried adding copper shielding tape to the inside of the case, which has helped a little.

## Install the X environment

As root:

* `setup-xorg-base`
* `apk add mesa-dri-vc4 mesa-dri-swrast mesa-gbm xf86-video-fbdev xfce4 xfce4-terminal`
* `mount -o remount,rw /media/mmcblk0p1`
* Edit /media/mmcblk0p1/usercfg.txt, to add:

    ```text
    dtoverlay=vc4-fkms-v3d
    gpu_mem=256
    lcd_rotate=2
    ```

* Create `/etc/X11/xorg.conf`:

    ```text
    Section "Device"
      Identifier "default"
      Driver "fbdev"
    EndSection
    ```

* `lbu commit -d`
* `reboot`

## Install the piju local UI

* Install dependencies. As root:

    ```sh
    apk add py3-gobject3
    ```

* Download (or git clone) <https://github.com/nsw42/pijuui>
* `pip install -r requirements.txt`

## Make the UI start automatically

There are several different ways to do this. One is to write a custom init
script, and you'll find an example of this if you hunt in the history of this
git repository.

The cleaner approach, though, is to configure automatic login for the `piju`
user on the console, and for that user's login script to startx:

* As root:

    ```sh
    apk add util-linux
    ```

* Also as root, edit `/etc/inittab` so that the `tty1` line reads as follows:

    ```text
    tty1::respawn:/sbin/agetty --autologin piju --noclear 38400 tty1
    ```

* If you reboot at this point, you should be automatically logged in (to an ash prompt) as the `piju` user.
* As the `piju` user, create `$HOME/.profile`:

    ```sh
    if [ -z "${DISPLAY}" -a -z "${SSH_CONNECTION}" ]; then
            exec startx
    fi
    ```

* Note that many examples online will test `$XDG_VTNR`, but that env var is specific to systemd, which Alpine does not use. Testing `$SSH_CONNECTION` ensures that you can still ssh to the server to fix/update things.
* If you log out now, you should be automatically logged back in, and this time X should start automatically.
    * If X doesn't start, citing permission errors, check that you did `sudo addgroup piju video`
    * If keyboard/mouse/touchscreen aren't working, check that you did `sudo addgroup piju input`
* All that remains is to start the PijuUI when X starts.
* Note that this contains hard-coded paths for log files, which are specific to my configuration.
* Write a `~/.xinitrc` file:

  ```sh
  #! /bin/sh

  startxfce4 &
  sleep 10
  exec $(dirname $0)/pijuui/run.sh
  ```

  TODO: This runs `startxfce4` because the python application wasn't filling the screen otherwise. It shouldn't be necessary to run the window manager, though.

