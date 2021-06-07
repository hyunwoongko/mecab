#include "gmock/gmock.h"
#include "gtest/gtest.h"
#include "iostream"
#include "string_utils.h"

TEST(mecab_utils_string_utils, test_tokenize) {
  std::vector<std::string> tokenized;
  std::string source = "hello,My,Name,Is";
  MeCab::tokenize(source, ",", tokenized);

  ASSERT_THAT(tokenized, testing::ElementsAre("hello", "My", "Name", "Is"));
}

TEST(mecab_utils_string_utils, test_tokenize_continuous_delimiter) {
  std::vector<std::string> tokenized;
  std::string source = "hello   My Name Is";
  MeCab::tokenize(source, " ", tokenized);

  ASSERT_THAT(tokenized, testing::ElementsAre("hello", "", "" ,"My", "Name", "Is"));
}

TEST(mecab_utils_string_utils, test_tokenize_continuous_delimiter_tokenize2) {
  char* container[4];
  std::string source = "hello   My Name Is ABCD";
  
  MeCab::tokenize2((char*)source.c_str(), " ", container, 4);
  std::vector<std::string> tokenized;

  for(int i=0; i<4; i++){
      std::string elem(container[i]);
      tokenized.push_back(elem);
  }

  ASSERT_THAT(tokenized, testing::ElementsAre("hello", "My", "Name", "Is"));
}


TEST(mecab_utils_string_utils, test_decode_charset) {
  ASSERT_EQ(MeCab::decode_charset("utf8"), MeCab::UTF8);
  ASSERT_EQ(MeCab::decode_charset("utf16le"), MeCab::UTF16LE);
  ASSERT_EQ(MeCab::decode_charset("invalid"), MeCab::UTF8);
}

TEST(mecab_utils_string_utils, test_create_filename) {
  ASSERT_EQ(MeCab::create_filename("path", "file"), "path/file");
}

TEST(mecab_utils_string_utils, test_remove_filename) {
  ASSERT_EQ(MeCab::remove_filename("/some-path/to/file"), "/some-path/to");
  ASSERT_EQ(MeCab::remove_filename("some-relative/path/to/file"), "some-relative/path/to");
  ASSERT_EQ(MeCab::remove_filename("not-a-path"), ".");
}

TEST(mecab_utils_string_utils, test_remove_pathname) {
  ASSERT_EQ(MeCab::remove_pathname("/some-path/to/file"), "file");
  ASSERT_EQ(MeCab::remove_pathname("some/relative/path"), "path");
  ASSERT_EQ(MeCab::remove_pathname("not-a-path"), ".");
}

TEST(mecab_utils_string_utils, test_replace_string) {
  ASSERT_EQ(MeCab::replace_string("example-string", "string", "test"), "example-test");
  ASSERT_EQ(MeCab::replace_string("test this string", "this", "that"), "test that string");
}

TEST(mecab_utils_string_utils, test_to_lower) {
  ASSERT_EQ(MeCab::to_lower("TesT ThIS StRINg"), "test this string");
}

TEST(mecab_utils_string_utils, test_get_escaped_char) {
  ASSERT_EQ(MeCab::getEscapedChar('0'), '\0');
  ASSERT_EQ(MeCab::getEscapedChar('a'), '\a');
  ASSERT_EQ(MeCab::getEscapedChar('f'), '\f');
  ASSERT_EQ(MeCab::getEscapedChar('u'), '\0');  // unknown
}