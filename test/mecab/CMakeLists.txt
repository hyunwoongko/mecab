CMAKE_MINIMUM_REQUIRED(VERSION 3.15.0)

SET(proj_name "Pecab_Mecab_Integration_Test")
PROJECT( ${proj_name} )

# C++ settings
SET(CMAKE_CXX_STANDARD 14)

set(TEST_CODE
      tests/test_darts.cc
      tests/test_string_utils.cc
      )

add_subdirectory(./googletest)

enable_testing()
include_directories(./sources)

add_executable(run-test ${TEST_CODE})
target_link_libraries(run-test gtest gmock gtest_main)
add_test(NAME run-test COMMAND ./run-test)