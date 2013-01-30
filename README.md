Komodo CodeIntel DXR Plugin
===========================

This is a DXR plugin to hook it up to Komodo's codeintel system.  At this point,
it is not very advanced, but it's better than without it.  Please note the
[bugs](#bugs) section below.

Building
--------

1. Check out the plugin into DXR's [plugins][dxr-plugins-dir] directory

    ```bash
    git clone git://github.com/mook/dxr-plugin-komodo-codeintel.git komodo_codeintel
    ```

2. Checkout the needed submodules

    ```bash
    cd komodo_codeintel
    git submodule init
    git submodule update
    ```

3. Edit DXR's [makefile][dxr-plugins-makefile] to add the new plugin

    ```make
    PLUGINS = clang pygmentize komodo_codeintel
    ```
4. Make sure you have Python 2 headers.
   In Ubuntu, this is the `python-dev` package.
5. Build DXR as normal
6. Make sure to enable the komodo_codeintel plugin in your DXR configuration

[dxr-plugins-dir]: https://github.com/mozilla/dxr/tree/testing/plugins
[dxr-plugins-makefile]: https://github.com/mozilla/dxr/blob/testing/makefile#L1


Bugs
----

* This plugin is most likely not safe with nb_jobs > 2.  Specifically, the
  various indexer processes are likely to run over each other when updating the
  per-directory indexes.
* Anything inherited from the Komodo code.  As much as possible, changes to the
  imported code should be done in an upstream-compatible way and bugs filed
  upstream so they can be picked up.
* Please file any bugs via [GitHub][github-issues]; do note however that this is
  a weekend hack and I am unlikely to be able to spend much time on this.
  Please also feel free to fork and create pull requests.

[github-issues]: https://github.com/mook/dxr-plugin-komodo-codeintel/issues

License
-------
MPL1.1/GPL2.1/LGPL2.1; unfortunately, this is so because that's what the Komodo
code is licensed under.  Anything in the plugin itself (not in `libs/` or
`komodo-bits/`) that are not derived from the Komodo code may additionally be
used under DXR's MIT license.

The Komodo code has various dependencies under `libs/` that are under their own
licenses; those are still under whatever license via which I got them from
Komodo's subversion server.
