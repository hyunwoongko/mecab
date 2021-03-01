#include "gmock/gmock.h"
#include "gtest/gtest.h"
#include "darts.h"
#include <fstream>

template <typename T1, typename T2>
struct pair_1st_cmp : public std::binary_function<bool, T1, T2> {
  bool operator()(const std::pair<T1, T2>& x1, const std::pair<T1, T2>& x2) { return x1.first < x2.first; }
};

TEST(test_darts, test_darts_output){
    MeCab::Darts::DoubleArray da;

    // Token 을 고려하지 않은 테스트 입니다.
    // 오로지 string dictionary 만 테스트 합니다.
    // Token은 임의로 String 형으로 교체하여 테스트 합니다.
    // Darts 에 직접적으로 Token을 저장하지 않기 때문.
    std::vector<std::pair< std::string, std::string >> dic;
    dic.push_back({"cat", "c"});
    dic.push_back({"cat", "a"});
    dic.push_back({"cat", "t"});

    dic.push_back({"car", "ca"});
    dic.push_back({"car", "r"});

    dic.push_back({"한국어", "한국"});
    dic.push_back({"한국어", "어"});

    std::stable_sort(dic.begin(), dic.end(), pair_1st_cmp<std::string, std::string>());
    size_t bsize = 0;
    size_t idx = 0;
    std::string prev;
    std::vector<const char*> str;
    std::vector<size_t> len;
    std::vector<MeCab::Darts::DoubleArray::result_type> val;

    for (size_t i = 0; i < dic.size(); ++i) {
      if (i != 0 && prev != dic[i].first) {
        str.push_back(dic[idx].first.c_str());
        len.push_back(dic[idx].first.size());
        val.push_back(bsize + (idx << 8));
        bsize = 1;
        idx = i;
      } else {
        ++bsize;
      }
      prev = dic[i].first;
    }
    str.push_back(dic[idx].first.c_str());
    len.push_back(dic[idx].first.size());
    val.push_back(bsize + (idx << 8));

    da.build(str.size(), const_cast<char**>(&str[0]), &len[0], &val[0]);
    std::string output_s = "output.bin";
    const char* output = output_s.c_str();
    std::ofstream bofs(output, std::ios::binary | std::ios::out);
    bofs.write(reinterpret_cast<const char*>(da.array()), da.unit_size() * da.size());
    bofs.close();
}

int main(int argc, char **argv) {
  ::testing::InitGoogleTest(&argc, argv);
  return RUN_ALL_TESTS();
}