# jsoncpp build script with code coverage instrumentation and intermediate files (--save-temps)
cmake \
    -DCMAKE_EXPORT_COMPILE_COMMANDS=ON \
    -DCMAKE_CXX_COMPILER=/usr/bin/clang++-13 \
    -DCMAKE_CXX_FLAGS="-O0 -fprofile-arcs -ftest-coverage -g -fno-omit-frame-pointer -gline-tables-only -DFUZZING_BUILD_MODE_UNSAFE_FOR_PRODUCTION --save-temps" \
    -DBUILD_SHARED_LIBS=OFF -G "Unix Makefiles" ../