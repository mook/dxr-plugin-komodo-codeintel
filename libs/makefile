# Crappy makefile for building libraries required for Komodo codeintel

OBJDIR ?= ${CURDIR}/../obj

all:
	# actual rules are in the SilverCity section
.PHONY: all

clean:
	rm -rf "${OBJDIR}/"
.PHONY: clean

###
# Scintilla
###

SCINTILLA_DIR = ${OBJDIR}/scintilla

# Phony scintilla target (for manual building)
scintilla: ${SCINTILLA_DIR}/bin/scintilla.a
.PHONY: scintilla

# Scintilla main library
${SCINTILLA_DIR}/bin/scintilla.a:                                              \
		${SCINTILLA_DIR}/.patch-status/DONE                            \
		${NULL}
	${MAKE} -C ${SCINTILLA_DIR}/gtk

# Prepare scintilla sources
${SCINTILLA_DIR}/.patch-status/DONE:                                           \
		${SCINTILLA_DIR}/include/Scintilla.h                           \
		${SCINTILLA_DIR}/include/SciLexer.h                            \
		${NULL}
	cd ${SCINTILLA_DIR}/src && python LexGen.py
	touch $@

${SCINTILLA_DIR}/.patch-status/patched-all:                                    \
		$(patsubst patches/scintilla/%.patch,                          \
			${SCINTILLA_DIR}/.patch-status/%.patched,              \
			$(wildcard patches/scintilla/*.patch))                 \
		${SCINTILLA_DIR}/.patch-status/.mkdir                          \
		${SCINTILLA_DIR}/.patch-status/LexTCL.removed                  \
		${SCINTILLA_DIR}/.patch-status/lexers.added                    \
		${NULL}
	touch $@

# Regenerate interfaces
${SCINTILLA_DIR}/include/Scintilla.h:                                          \
		${SCINTILLA_DIR}/include/SciLexer.h                            \
		${NULL}

${SCINTILLA_DIR}/include/SciLexer.h:                                           \
		${SCINTILLA_DIR}/include/Scintilla.iface                       \
		${SCINTILLA_DIR}/include/HFacer.py                             \
		${NULL}
	cd "${SCINTILLA_DIR}/include" && python HFacer.py

${SCINTILLA_DIR}/include/HFacer.py:                                            \
		${SCINTILLA_DIR}/.patch-status/patched-all                     \
		${NULL}

${SCINTILLA_DIR}/include/Scintilla.iface:                                      \
		${SCINTILLA_DIR}/.patch-status/patched-all                     \
		${NULL}
	
# Copy (unpatched) scintilla source code into object directory
${SCINTILLA_DIR}/version.txt:                                                  \
		${SCINTILLA_DIR}/.mkdir                                        \
		scintilla/version.txt                                          \
		${NULL}
	cp -rT scintilla/ ${SCINTILLA_DIR}

# Patch scintilla source code
${SCINTILLA_DIR}/.patch-status/%.patched:                                      \
		patches/scintilla/%.patch                                      \
		${SCINTILLA_DIR}/version.txt                                   \
		${SCINTILLA_DIR}/.patch-status/.mkdir                          \
		${NULL}
	patch -d ${SCINTILLA_DIR} -p0 --batch -i $(abspath $<)
	touch $@

# Add extra lexers
${SCINTILLA_DIR}/.patch-status/lexers.added:                                   \
		${SCINTILLA_DIR}/version.txt                                   \
		${SCINTILLA_DIR}/.patch-status/.mkdir                          \
		patches/scintilla/lexers/*                                     \
		${NULL}
	cp -f $(filter patches/%,$+) ${SCINTILLA_DIR}/lexers/
	touch $@

# Remove unwanted lexers
${SCINTILLA_DIR}/.patch-status/LexTCL.removed:                                 \
		${SCINTILLA_DIR}/version.txt                                   \
		${SCINTILLA_DIR}/.patch-status/.mkdir                          \
		${NULL}
	rm -f ${SCINTILLA_DIR}/lexers/LexTCL.cxx
	touch $@	


###
# SilverCity
###

SILVERCITY_DIR = ${OBJDIR}/silvercity

all:  ${OBJDIR}/pylib/SilverCity/__init__.py

# Prepare scintilla sources
${SILVERCITY_DIR}/.patch-status/DONE:                                          \
		$(patsubst patches/silvercity-%.patch,                         \
			${SILVERCITY_DIR}/.patch-status/%.patched,             \
			$(wildcard patches/silvercity-*.patch))                \
		${SILVERCITY_DIR}/.patch-status/.mkdir                         \
		${SILVERCITY_DIR}/setup.py                                     \
		${NULL}
	touch $@

# Copy (unpatched) scintilla source code into object directory
${SILVERCITY_DIR}/setup.py:                                                    \
		${OBJDIR}/.mkdir                                               \
		silvercity/setup.py                                            \
		${NULL}
	cp -rT silvercity/ ${SILVERCITY_DIR}

# Patch SilverCity source code
${SILVERCITY_DIR}/.patch-status/%.patched:                                     \
		patches/silvercity-%.patch                                     \
		${SILVERCITY_DIR}/setup.py                                     \
		${SILVERCITY_DIR}/.patch-status/.mkdir                         \
		${NULL}
	patch -d ${SILVERCITY_DIR} -p0 --batch -i $(abspath $<)
	touch $@

${SILVERCITY_DIR}/PySilverCity/Src/write_scintilla.py:                         \
		${SILVERCITY_DIR}/.patch-status/DONE                           \
		${NULL}


${SILVERCITY_DIR}/PySilverCity/SilverCity/ScintillaConstants.py:               \
		${SCINTILLA_DIR}/include/Scintilla.iface                       \
		${SILVERCITY_DIR}/PySilverCity/Src/write_scintilla.py          \
		${NULL}
	python ${SILVERCITY_DIR}/PySilverCity/Src/write_scintilla.py ${SCINTILLA_DIR}/include/ $< $@

${OBJDIR}/pylib/SilverCity/__init__.py:                                        \
		${SILVERCITY_DIR}/PySilverCity/SilverCity/ScintillaConstants.py\
		${SCINTILLA_DIR}/.patch-status/DONE                            \
		${SILVERCITY_DIR}/libpcre.a                                    \
		${OBJDIR}/pylib/.mkdir                                         \
		${NULL}
	cd ${SILVERCITY_DIR} && python setup.py install                        \
		--prefix=bitbucket --install-data=bitbucket                    \
		--install-scripts=bitbucket                                    \
		--install-lib=${OBJDIR}/pylib


###
# PCRE
###

PCRE_DIR = ${OBJDIR}/pcre

${SILVERCITY_DIR}/libpcre.a:                                                   \
		${PCRE_DIR}/.libs/libpcre.a                                    \
		${NULL}
	cp -f $< $@

${PCRE_DIR}/.patch-status/DONE:                                                \
		$(patsubst patches/pcre_%.patch,                               \
			${PCRE_DIR}/.patch-status/%.patched,                   \
			$(wildcard patches/pcre_*.patch))                      \
		${@D}/.mkdir                                                   \
		${NULL}
	touch $@

${PCRE_DIR}/.patch-status/%.patched:                                           \
		patches/pcre_%.patch                                           \
		${PCRE_DIR}/VERSION                                            \
		${PCRE_DIR}/.patch-status/.mkdir                               \
		${NULL}
	patch -d ${PCRE_DIR} -p0 --batch -i $(abspath $<)
	touch $@

${PCRE_DIR}/VERSION:                                                           \
		pcre/VERSION                                                   \
		${PCRE_DIR}/.mkdir                                             \
		${NULL}
	cp -rT "${<D}" "${@D}"

# PCRE appears to be pre-patched in the Komodo tree.  Don't patch it.
${PCRE_DIR}/Makefile:                                                          \
		${PCRE_DIR}/VERSION                                            \
		${NULL}
	cd "${@D}" &&                                                          \
		CFLAGS='-O2 -fPIC -g'                                          \
		"${PCRE_DIR}/configure"                                        \
		--prefix="${@D}/install"                                       \
		--libdir="${@D}/install/lib"                                   \
		--enable-shared=no                                             \
		--enable-utf8                                                  \
		--enable-unicode-properties                                    \
		${NULL}

${PCRE_DIR}/.libs/libpcre.a:                                                   \
		${PCRE_DIR}/Makefile                                           \
		${NULL}
	${MAKE} -C ${PCRE_DIR}


###
# ciElementTree
###

CIETREE_DIR = ${OBJDIR}/ciElementTree

# ciElementTree has a series of patches; unfortunately, they must be applied in
# order.  This ugly CIETREE_PATCHES_ORDER hack is used to tell make all patches
# depend on previous ones; i.e., 1 depends on 0, 2 depends on both 0 and 1, etc.
CIETREE_PATCHES := $(sort $(patsubst patches-codeintel/ciElementTree-%.patch,  \
			${CIETREE_DIR}/.patch-status/%.patched,                \
			$(wildcard patches-codeintel/ciElementTree-*.patch)))  \

define CIETREE_PATCHES_ORDER =
    CIETREE_PATCHES_LAST := $$(lastword $${CIETREE_PATCHES})
    CIETREE_PATCHES := $$(filter-out $${CIETREE_PATCHES_LAST},$${CIETREE_PATCHES})
    # Mark the patch marker as precious so they don't get deleted, causing
    $$(eval .PRECIOUS: $${CIETREE_PATCHES_LAST})
    ifneq ($${CIETREE_PATCHES},)
        $$(eval $${CIETREE_PATCHES_LAST}: $${CIETREE_PATCHES})
        $$(eval $${CIETREE_PATCHES_ORDER})
    endif
endef
$(eval ${CIETREE_PATCHES_ORDER})

# Actually mark our "all done" flag as depending on every patch applying
${CIETREE_DIR}/.patch-status/DONE:                                             \
		$(patsubst patches-codeintel/ciElementTree-%.patch,            \
			${CIETREE_DIR}/.patch-status/%.patched,                \
			$(wildcard patches-codeintel/ciElementTree-*.patch))   \
		${CIETREE_DIR}/.mkdir                                          \
		${NULL}
	touch $@

# Apply each individual patch
${CIETREE_DIR}/.patch-status/%.patched:                                        \
		patches-codeintel/ciElementTree-%.patch                        \
		${CIETREE_DIR}/setup.py                                        \
		${CIETREE_DIR}/.patch-status/.mkdir                            \
		${NULL}
	# Work around patch setting time stamps (and the fact that one of the
	# files we want to patch is setup.py, our dependency)
	touch -r ${CIETREE_DIR}/setup.py $(patsubst %.patched,%.time,$@)
	patch -d ${CIETREE_DIR} -p1 --batch -i $(abspath $<)
	touch -r $(patsubst %.patched,%.time,$@) ${CIETREE_DIR}/setup.py
	touch $@

# Copy the pristine source over
${CIETREE_DIR}/setup.py:                                                       \
		cElementTree/setup.py                                          \
		${CIETREE_DIR}/.mkdir                                          \
		${NULL}
	tar -cC ${<D} --exclude-vcs . | tar -xpC ${@D} .

# Build the python module
${CIETREE_DIR}/ciElementTree.pyd:                                              \
		${CIETREE_DIR}/.patch-status/DONE                              \
		${NULL}
	cd "${CIETREE_DIR}" && python setup.py build
	cd "${CIETREE_DIR}" && python setup.py install --skip-build            \
		--prefix=bitbucket --install-data=bitbucket                    \
		--install-scripts=bitbucket --install-lib="${OBJDIR}/pylib"

all: ${CIETREE_DIR}/ciElementTree.pyd

###
# inflector (needed for Ruby codeintel)
###

INF_DIR := ${OBJDIR}/pylib/inflector

all: ${INF_DIR}/__init__.py

${INF_DIR}/__init__.py:                                                        \
		inflector/__init__.py                                          \
		${INF_DIR}/.mkdir                                              \
		${NULL}
	tar -cC ${<D} --exclude-vcs . | tar -xpC ${@D} .

###
# Utilities
###

%/.mkdir:
	mkdir -p ${@D}
	touch $@
# mark the .mkdir flag files as precious; otherwise make kills the one for
# ciElementTree patching, which makes it want to re-make it on next invocation
# (because it has no prerequisites), which causes it to re-apply the patches
.PRECIOUS: %/.mkdir
