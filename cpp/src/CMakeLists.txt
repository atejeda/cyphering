include_directories(${PROJECT_SOURCE_DIR}/include)
include_directories(${PROJECT_SOURCE_DIR}/deps/include)

link_directories(${PROJECT_SOURCE_DIR}/deps/lib)

find_library(
    RYML_LIBRARY 
    NAMES ryml
    HINTS ${PROJECT_SOURCE_DIR}/deps/lib
) 

add_executable(cyphering functions.cpp main.cpp)
target_link_libraries(cyphering PUBLIC ${RYML_LIBRARY})
target_compile_features(cyphering PUBLIC cxx_std_14)