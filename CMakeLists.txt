cmake_minimum_required(VERSION 3.22)
project(c_test)

set(CMAKE_CXX_STANDARD 20)

find_package(LibFTDI1 REQUIRED)
include ( ${LIBFTDI_USE_FILE} )

add_subdirectory(thirdparty/pybind11)

pybind11_add_module(c_test Device.cpp pymodule.cpp)
add_executable(example Device.cpp main.cpp)


#include_directories("${LIBFTDI_INCLUDE_DIRS}")
#add_executable(c_test main.cpp)
target_link_libraries(c_test PRIVATE ${LIBFTDI_LIBRARIES} "ftdipp1")
target_link_libraries(example PRIVATE ${LIBFTDI_LIBRARIES} "ftdipp1")
