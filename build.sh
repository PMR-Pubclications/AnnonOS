# 1. Configure Buildroot with your external tree
make BR2_EXTERNAL=../annonos-external annonos_defconfig

# 2. Compile the kernel, rootfs, and SquashFS image
make -j$(nproc)
