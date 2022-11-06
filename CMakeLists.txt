cmake_minimum_required(VERSION 3.22)

if (WIN32)
  set(CMAKE_TOOLCHAIN_FILE "${CMAKE_CURRENT_SOURCE_DIR}/thirdparty/vcpkg/scripts/buildsystems/vcpkg.cmake"
    CACHE STRING "Vcpkg toolchain file")
endif()

project(c_test)

set(CMAKE_CXX_STANDARD 20)
set(PYMODULE_NAME _pyspectrum)

find_package(Boost REQUIRED)
find_package(LibFTDI1 REQUIRED)
include_directories ( ${Boost_INCLUDE_DIRS} )
include ( ${LIBFTDI_USE_FILE} )

add_subdirectory(thirdparty/pybind11)

pybind11_add_module(${PYMODULE_NAME} src/UsbRawSpectrometer.cpp src/pymodule.cpp  src/RawSpectrum.h)
#add_executable(example src/UsbRawSpectrometer.cpp src/main.cpp src/RawSpectrum.h)


#include_directories("${LIBFTDI_INCLUDE_DIRS}")
#add_executable(c_test main.cpp)
target_link_libraries(${PYMODULE_NAME} PRIVATE ${LIBFTDI_LIBRARIES} "ftdipp1")
target_compile_definitions(${PYMODULE_NAME} PRIVATE VERSION_INFO=${VERSION_INFO} PYMODULE_NAME=${PYMODULE_NAME})

#target_link_libraries(example PRIVATE ${LIBFTDI_LIBRARIES} "ftdipp1")
