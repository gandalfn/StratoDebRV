#!/bin/bash
# Das U-Boot flashing script
# Depends on prerequisites defined by P. Yavitz
# URL: https://github.com/pyavitz/debian-image-builder

# developer debug switch
VERBOSITY="0"
if [ $VERBOSITY -eq 1 ]; then set -x; fi

# check privilege
if [ "$USER" != "root" ]; then
	echo -e "Please run this as root or with sudo privileges."
	exit 1
fi

error_prompt () {
export NEWT_COLORS='root=,black'
whiptail --msgbox "    ${REPORT}" 0 0
exit 0
}

# check for u-boot directory
if [[ -d "/usr/lib/u-boot" ]]; then
	DIR="/usr/lib/u-boot"
else
	REPORT="Could not find u-boot directory."
	error_prompt
fi

# set device node variable
MMC=`findmnt -v -n -o SOURCE / | sed 's/..$//'`

# check node
if [[ "$MMC" =~ ^(/dev/mmcblk0|/dev/mmcblk1|/dev/mmcblk2)$ ]]; then
	# locate target device node
	if [[ -e "${MMC}boot0" ]]; then EMMC="1"; else EMMC="0"; fi
else
	REPORT="Could not find device node."
	error_prompt
fi

target_device () {
echo -en "${FAMILY}: " | sed -e 's/\(.*\)/\U\1/'
echo -e "${DEFAULT_MOTD}" | sed -e 's/\(.*\)/\U\1/'
if [ $EMMC -eq 1 ]; then echo -en "── eMMC: "; else echo -en "── SDCARD: "; fi
echo -e "$MMC"
}

flash_uboot(){
target_device
if [[ -f "${DIR}/bootinfo_emmc.bin" ]] && [[ -f "${DIR}/u-boot.bin" ]] && \
	[[ "${DIR}/fw_dynamic.bin" ]] && [[ "${DIR}/FSBL.bin" ]]; then
	sleep .50
	if [ $EMMC -eq 1 ]; then
		DEVICE=`ls /dev/mmcblk*boot0 | sed 's/^.....//'`
		echo 0 > /sys/block/${DEVICE}/force_ro
		sleep .50
		dd if="${DIR}/bootinfo_emmc.bin" of="/dev/${DEVICE}" bs=512 conv=notrunc
		dd if="${DIR}/FSBL.bin" of="/dev/${DEVICE}" bs=512 seek=1 conv=notrunc
	else
		dd if="${DIR}/bootinfo_emmc.bin" of="${MMC}" bs=512 conv=notrunc
		dd if="${DIR}/FSBL.bin" of="${MMC}" bs=512 seek=1 conv=notrunc
	fi
	dd if="${DIR}/fw_dynamic.bin" of="${MMC}" bs=512 seek=1280 conv=notrunc
	dd if="${DIR}/u-boot.bin" of="${MMC}" bs=512 seek=2048 conv=notrunc
fi
}

sleep .50
flash_uboot
sleep .50
ROOTFS=`findmnt -v -n -o SOURCE /`
PARTUUID=$(blkid -o export -- $ROOTFS | sed -ne 's/^PARTUUID=//p')
if [[ -f "/boot/extlinux/extlinux.conf" ]]; then sed -i "s,root=PARTUUID=[^ ]*,root=PARTUUID=${PARTUUID}," /boot/extlinux/extlinux.conf; fi
echo -e ""
echo -e "You may now reboot."

sync
exit 0
