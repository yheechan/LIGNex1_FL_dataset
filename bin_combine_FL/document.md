# JsonCpp 오픈 소스 프로젝트의 오류 탐지 (FL: Fault Localization) 데이터셋


## 1. 데이터셋 소개
본 데이터셋은 JsonCpp 오프 소스 프로젝트를 대상으로 오류 탐지에 활용될 수 있는 모델 학습 데이터를 제공합니다. 이 데이터셋은 프로그램의 동적 특성을 분석하여 스펙트럼 기반 (SBFL: Spectrum-Based Fault Localization) 및 변기 기반 (MBFL: Mutation-Based Fault Localization) 특징 데이터를 포함하고 있습니다.


## 2. JsonCpp 프로젝트 규모 요약
* 소스 코드 파일 개수: 8개
* 함수 개수: 363개
* 소스 코드 라인 개수: 약 4000줄


## 3. 데이터셋 구조

### 3.1 디렉토리 구조
* ``buggy_code_file_per_bug_version/:`` 각 버그 버전에 대한 버그가 있는 소스 코드 파일
* ``buggy_line_key_per_bug_version/``: 각 버그 버전의 버기 라인을 식별하는 고유 키 값
* ``bug_version_mutation_info.csv``: 각 버그 버전에 생성된 인공 버그의 변형 정보
* ``document.md``: 데이터셋의 상세 내용을 담은 문서
* ``FL_features_per_bug_version/``: 버그 버전 별로 SBFL과 MBFL 특징 정보를 포함한 학습 데이터 **(학습 데이터로 사용)**
* ``postprocessed_coverage_per_bug_version/``: 각 버그 버전의 테스트 케이스들의 커버리지 정보
* ``test_case_info_per_bug_version/``: 각 버그 버전 별로 사용된 테스트 케이스 분류 정보 (통과(pass), 실패(fail), 우연히 통과한(coincidentally correct) 테스트 케이스)

    ```
    fl_dataset-240416-v1/
        ├── buggy_code_file_per_bug_version
        ├── buggy_line_key_per_bug_version
        ├── bug_version_mutation_info.csv
        ├── document.md
        ├── FL_features_per_bug_version
        ├── postprocessed_coverage_per_bug_version
        └── test_case_info_per_bug_version
    ```

### 3.2 데이터셋 사이즈
* zip 파일 사이즈: 16,665,913 바이트

## 4. 버그 버전 정보
* 버그 개수
    유형 | 개수
    --- | ---
    실제 버그 | 3개
    인공 버그 | 162개
    총 버그 | 165개

* 실제 버그 (총 3개)
    버기 버전 | 출처 | 소스 코드 파일  | buggy line # | bug type
    --- | --- | --- | --- | ---
    bug1 | [github issue #1121](https://github.com/open-source-parsers/jsoncpp/issues/1121) | json_reader.cpp | 467 | assertion failure
    bug2 | [ossfuzz #18147](https://bugs.chromium.org/p/oss-fuzz/issues/detail?id=18147&q=jsoncpp&can=1&sort=-summary) | json_reader.cpp |  1279 | heap overflow
    bug3 | [ossfuzz #21916](https://bugs.chromium.org/p/oss-fuzz/issues/detail?id=21916&q=jsoncpp&can=1) | json_reader.cpp | 1628 | integer overflow

* 인공 버그 (총 3개)
    * ``bug_version_mutation_info.csv`` 파일에서 각 버그 버전 별로 인공적으로 생성된 버그(변형) 정보를 확인 할 수 있습니다.


## 5. 검증된 데이터와 검증 방법
* ``FL_features_per_bug_version/`` 디렉토리: 버그 버전 별 오류 탐지 데이터셋
    * 각 CSV 파일은 ``bug`` 열의 값이 ``1``인 행은 유일하게 한 하나만 존재하는지 검증합니다.
    * 스펙트럼 기반 특징 데이터 (``ep``, ``ef``, ``np``, ``nf``)의 합계가 실패(failing) 및 통과(passing) 테스트 케이스의 총수와 일치하는지 검증합니다. 버기 라인을 실행하였으나 우연히 통과하는 테스트 케이스는 제외합니다.
* ``buggy_code_file_per_bug_version/`` 디렉토리: 버그 버전 별 소스 코드 파일
    * 인공적으로 생성된 버그(변형)가 각 버그 버전의 소스 코드 파일에 지정된 위치에 올바르게 삽입되었는지 검증합니다.
* ``test_case_info_per_bug_version/`` 디렉토리: 각 버그 버전 별 실패한 테스트 케이스 정보
    * 각 버그 버전 별 실패(failing) 테스트 케이스가 해당 버그에서 버그가 있는 코드 라인을 실행하였는지 검증합니다.


## 6. 모델 학습용 데이터셋 특징 (총 16개 열)
### 6.1 각 라인 별 고유 키 (``key`` 열):
* 이 열은 ``<소스 코드 파일>#<함수명>#<라인 번호>`` 형식으로 각 소스 코드 라인의 고유 식별자를 기록합니다.

### 6.2 버기 라인 여부 (``bug`` 열):
* ``bug`` 열의 값이 ``1``이면 해당 라인은 버기 라인임을 나타냅니다.
* ``bug`` 열의 값이 ``0``이면 해당 라인은 정상 라인임을 나타냅니다.

### 6.3 스펙트럼 기반 특징 (SBFL, 총 4개 열):
* ``ep``: 해당 라인을 실행하고 통과한(pass)한 테스트 케이스의 개수
* ``ef``: 해당 라인을 실행하고 실패한(fail)한 테스트 케이스의 개수
* ``np``: 해당 라인을 실행하지 않고 통과한(pass)한 테스트 케이스의 개수
* ``nf``: 해당 라인을 실행하지 않고 실패한(fail)한 테스트 케이스의 개수

### 6.4 변이 기반 특징 (MBFL, 총 10개 열):
* **Metallaxis**
    * ``met_1``: $\max_{m \in \text{mut}_\text{killed}(s)} (kill(m))$
    * ``met_2``: $\max_{m \in \text{mut}_\text{killed}(s)} \frac{1}{\sqrt{kill(m)}}$
    * ``met_3``: $\max_{m \in \text{mut}_\text{killed}(s)} \frac{1}{\sqrt{kill(m) + notkill(m)}}$
    * ``met_4``: $\max_{m \in \text{mut}_\text{killed}(s)} \frac{kill(m)}{\sqrt{{kill(m)}({kill(m)}+{notkill(m)})}}$

        수식 추가 설명:
        * $\text{mut}_\text{killed}(s)$: 라인 $s$에 생성된 변형들 중 죽은 변형들의 개수
        * $\text{kill}(m)$: 변형 $m$을 죽인 테스트 케이스들의 개수
        * $\text{notkill}(m)$: 변형 $m$을 죽이지 못한 테스트 케이스들의 개수

* **MUSE**
    * ``muse_1``: $\frac{1}{{|\text{mut}(s)| + 1}}$
    * ``muse_2``: $\sum_{m \in \text{mut}(s)} |f_P(s) \cap p_m|$
    * ``muse_3``: $\sum_{m \in \text{mut}(s)} |p_P(s) \cap f_m|$
    * ``muse_4``: $\frac{1}{{(|\text{mut}(s)|+1)(f2p+1)}} \times \sum_{m \in \text{mut}(s)} \left( |f_P(s) \cap p_m| \right)$
    * ``muse_5``: $\frac{1}{{(|\text{mut}(s)|+1)(p2f+1)}} \times \sum_{m \in \text{mut}(s)} \left( |p_P(s) \cap f_m| \right)$
    * ``muse_6``: $\frac{1}{{(|\text{mut}(s)|+1)(f2p+1)}} \times \sum_{m \in \text{mut}(s)} \left( |f_P(s) \cap p_m| \right) - \frac{1}{{(|\text{mut}(s)|+1)(p2f+1)}} \times \sum_{m \in \text{mut}(s)} \left( |p_P(s) \cap f_m| \right)$

        수식 추가 설명:
        - $\text{mut}(s)$: 라인 $s$에 생성된 변형들의 집합
        - $f_P(s) (\text{or } p_P(s))$: 대상 프로그램 $P$에서 라인 $s$를 실행하고 fail (or pass)하는 테스트 케이스들의 집합
        - $f_m (\text{or }p_m)$: 변형 $m$에 대해 fail (or pass)하는 테스트 케이스들의 집합
        - $f2p (\text{or }p2f)$: 대상 프로그램 $P$의 모든 변형들에 대해서 fail에서 pass (or pass에서 fail)로 바뀐 테스트 케이스들의 개수