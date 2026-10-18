################################################################################
#
# annonos-core
#
################################################################################

ANNONOS_CORE_VERSION = 1.0
ANNONOS_CORE_SITE = $(BR2_EXTERNAL_ANNONOS_PATH)/board/annonos-target/rootfs-overlay
ANNONOS_CORE_SITE_METHOD = local

define ANNONOS_CORE_INSTALL_TARGET_CMDS
	$(INSTALL) -d -m 0755 $(TARGET_DIR)/opt/annonos
	cp -dpfr $(ANNONOS_CORE_SITE)/opt/annonos/* $(TARGET_DIR)/opt/annonos/
endef

$(eval $(generic-package))
