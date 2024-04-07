# MBFL features dataset on 182 bug versions of JsonCpp


## 1. 데이터셋 버그 버전 개수
* 총 버그 개수: 181개
* 버그 출처
    출처 | 개수
    --- | ---
    github issue | 1개
    ossfuzz | 2개
    mutant based | 178개
* 총 버그 버전 181개 중 46개 버그 버전이 acc@10을 보여준다.
* 각 버그 버전 별 rank 정보는 ``mbfl_dataset/statistics_summary.csv`` 통계 자료 파일에서 확인할 수 있다.


## 2. 데이터셋 디렉토리 정보
각 디렉토리에 담긴 정보는 다음과 같습니다:
* ``mbfl_dataset/buggy_code_file_per_bug_version/``: 각 버그 버전의 버그 코드가 담긴 jsoncpp 소스 코드 파일
* ``mbfl_dataset/buggy_line_key_per_bug_version/``: 각 버그 버전의 버그 라인을 명시하는 키 정보
* ``mbfl_dataset/bug_version_mutation_info.csv``: 각 버그 버전을 만든 돌연변이(mutations) 정보
* ``mbfl_dataset/lines_executed_by_failing_tc_per_bug_version/``: 각 버그 버전에서 실패하는 테스트 케이스들이 실행하는 라인 정보
* ``mbfl_dataset/mbfl_features_per_bug_version/``: 각 버그 버전의 MBFL 특징 데이터셋 **(모델 학습 데이터로 사용)**
* ``mbfl_dataset/mutant_info_per_bug_version/``: 각 버그 버전의 버그 라인을 탐지하기 위해 사용된 돌연변이(mutants)들의 정보
* ``mbfl_dataset/README.md``: 데이터셋에 대한 내용 정리 문서
* ``mbfl_dataset/statistics_summary.csv``: 각 버그 버전들의 MBFL 결과 통계 자료
* ``mbfl_dataset/test_case_info_per_bug_version/``: 각 버전의 테스트 케이스 결과 정보

```
mbfl_dataset/
├── buggy_code_file_per_bug_version/
├── buggy_line_key_per_bug_version/
├── bug_version_mutation_info.csv
├── lines_executed_by_failing_tc_per_bug_version/
├── mbfl_features_per_bug_version/
├── mutant_info_per_bug_version/
├── README.md
├── statistics_summary.csv
└── test_case_info_per_bug_version/
```


## 3. 데이터셋 검증된 내용
1. ``mbfl_dataset/mbfl_features_per_bug_version/`` 디렉토리에 담긴 각 버그들의 mbfl feature CSV 파일은 bug 열의 값이 1인 행은 하나만 존재하는 것을 검증합니다.
2. 각 버그 버전의 failing TC들이 해당 버그 버전의 buggy line을 실행하는 것을 검증합니다.


## 4. MBFL 데이터셋의 특징 정보
각 라인에 대해서 의심도 점수는 다음 공식들로 계산된다.

### Metallaxis
* met_1: $ \max_{m \in \text{mut}_\text{killed}(s)} (kill(m)) $
* met_2: $ \max_{m \in \text{mut}_\text{killed}(s)} \frac{1}{\sqrt{kill(m)}} $
* met_3: $ \max_{m \in \text{mut}_\text{killed}(s)} \frac{1}{\sqrt{kill(m) + notkill(m)}} $
* met_4: $ \max_{m \in \text{mut}_\text{killed}(s)} \frac{1}{\sqrt{{kill(m)}({kill(m)}+{notkill(m)})}} $

    where:
    * $ \text{mut}_\text{killed}(s) $ is a set of killed mutants generated at statment $s$
    * $ \text{kill}(m) $ represents the number of test cases that kill $m$
    * $ \text{notkill}(m)$ represents the number of test cases that do not kill $m$

### MUSE
* muse_1: $ \frac{1}{{|\text{mut}(s)| + 1}} $
* muse_2: $ \sum_{m \in \text{mut}(s)} |f_P(s) \cap p_m| $
* muse_3: $ \sum_{m \in \text{mut}(s)} |p_P(s) \cap f_m| $
* muse_4: $ \frac{1}{{(|\text{mut}(s)|+1)(f2p+1)}} \times \sum_{m \in \text{mut}(s)} \left( |f_P(s) \cap p_m| \right) $
* muse_5: $ \frac{1}{{(|\text{mut}(s)|+1)(p2f+1)}} \times \sum_{m \in \text{mut}(s)} \left( |p_P(s) \cap f_m| \right) $
* muse_6: $ \frac{1}{{(|\text{mut}(s)|+1)(f2p+1)}} \times \sum_{m \in \text{mut}(s)} \left( |f_P(s) \cap p_m| \right) - \frac{1}{{(|\text{mut}(s)|+1)(p2f+1)}} \times \sum_{m \in \text{mut}(s)} \left( |p_P(s) \cap f_m| \right) $

    where:
    - $\text{mut}(s)$: Number of mutants generated on set $s$
    - $f_P(s) (\text{or } p_P(s))$: Set of tests that cover $s$ and fail (or pass) on target program $P$
    - $f_m (\text{or }p_m)$: Set of tests that fail (or pass) on mutant $m$
    - $f2p (\text{or }p2f)$: Number of test results that change from fail to pass (or pass to fail) for all mutants of $P$
