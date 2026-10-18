# 1. Configure Buildroot with your external tree
make BR2_EXTERNAL=../annonos-external annonos_defconfig

# 2. Compile the kernel, rootfs, and SquashFS image
make -j$(nproc)

# 1. Load your configuration profile
make annonos_defconfig

# 2. Build the entire toolchain, kernel, modules, and ISO image
make -j$(nproc)

