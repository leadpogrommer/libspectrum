## Building libspectrum on Windows

Run the bootstrap script to build vcpkg

```cmd
> .\thirdparty\vcpkg\bootstrap-vcpkg.bat
```

Install libftdi1 using the provided overlay port

```cmd
> .\thirdparty\vcpkg\vcpkg.exe install libftdi1:x64-windows --overlay-ports .\thirdparty\vcpkg_ports
```

Generate makefiles with CMake

```cmd
> mkdir build
> cd build
> cmake .. -G [desired-makefile-generator]
```

Build libspectrum with your favourite build system
