#
# Makefile for Nftables/netfilter fullcone expression support.
#

# module name, should not have the same name as src file names
TARGET = nft_fullcone

obj-m += $(TARGET).o

$(TARGET)-objs := \
	nf_nat_fullcone.o \
	nft_ext_fullcone.o

# product
# NOTE: the kernel tree here is built with CONFIG_WERROR=y (from the MTK SDK), so
# kernel-API drift between nft_fullcone's original target kernels and 6.6.133
# turns every callback-signature mismatch into a hard error. The three
# nft_expr_ops callbacks (init/eval/dump/validate) only ever gain/lose trailing
# scalar args across these versions, which is ABI-safe for the extra arg to be
# ignored, so downgrade this one warning class instead of failing the whole build.
ccflags-y += -Wall -Wno-incompatible-pointer-types

# develop
#ccflags-y += -Wall -Wno-unused-function
