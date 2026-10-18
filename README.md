# AnnonOS-
This is a costume mobile OS for the visually impaired and First Responders.

Instructions to flash your phone.

Flashing AnnonOS to your mobile target depends on whether your target hardware boots from a MicroSD card (common for modular tactical phones like the PinePhone or development units) or directly to internal eMMC/UFS storage via fastboot.

Step 1: Locate Your Compiled Build Output
Once Buildroot finishes compiling your image, navigate to your output directory to find your flashable image files:
cd output/images/

Depending on your target board configuration, you will find:
sdcard.img (Complete bootable image containing the bootloader, kernel, device tree, and your read-only SquashFS rootfs).

rootfs.squashfs (The standalone compressed root file system).

Method 1: Flashing to a MicroSD Card (Recommended for Tactical Field Units)
If your mobile unit boots via an external MicroSD card, use dd or a reliable imaging tool to flash the sdcard.img directly.

Insert your MicroSD card into your host computer and identify its device identifier (e.g., /dev/sdX or /dev/mmcblkX). Be extremely careful to select the correct drive letter to avoid overwriting your host operating system.

Unmount the card partitions before writing:

bash in your terminal:

sudo umount /dev/sdX*

Flash the complete SD card image using dd:

bash in your terminal 

sudo dd if=output/images/sdcard.img of=/dev/sdX bs=4M status=progress conv=fdatasync

Eject and Insert: Once the write operation and sync complete, safely eject the MicroSD card and insert it into your mobile tactical device. Power it on to initialize the secure bootloader, framebuffer splash, and audible greeting.

Method 2: Flashing to Internal eMMC / UFS via Fastboot or Recovery
If your hardware requires flashing directly to the phone's internal storage partitions:

Boot the Phone into Fastboot / EDL Mode:
Power off the device.
Hold the designated hardware key combination (e.g., Volume Down + Power or recovery button) while connecting the USB cable to your host machine.

Verify Fastboot Connection:

bash in terminal 

fastboot devices

Flash the Kernel and SquashFS Rootfs Partitions:

bash in terminal 

# Flash the kernel image
fastboot flash boot output/images/zImage

# Flash the compressed read-only SquashFS root file system
fastboot flash rootfs output/images/rootfs.squashfs

# Reboot the device into AnnonOS
fastboot reboot

Step 3: First Boot Verification
When the phone powers up with AnnonOS:
Visual Display: You will see your role-differentiated boot animation render directly to the framebuffer (the Opening Book animation for civilian/trust admin profiles, or the Tactical HUD for first responders).

Audio Check: Immediately following verification, the system will output the accessibility startup greeting through the speaker, reminding the operator of the help command (anon list commands).
Voice Test: Speak your wake command or test the voice biometric gateway to ensure hands-free control is fully operational.