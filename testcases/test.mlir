module attributes {dlti.dl_spec = #dlti.dl_spec<!llvm.ptr<270> = dense<32> : vector<4xi64>, !llvm.ptr<271> = dense<32> : vector<4xi64>, !llvm.ptr<272> = dense<64> : vector<4xi64>, i64 = dense<64> : vector<2xi64>, i128 = dense<128> : vector<2xi64>, f80 = dense<128> : vector<2xi64>, !llvm.ptr = dense<64> : vector<4xi64>, i1 = dense<8> : vector<2xi64>, i8 = dense<8> : vector<2xi64>, i16 = dense<16> : vector<2xi64>, i32 = dense<32> : vector<2xi64>, f16 = dense<16> : vector<2xi64>, f64 = dense<64> : vector<2xi64>, f128 = dense<128> : vector<2xi64>, "dlti.endianness" = "little", "dlti.mangling_mode" = "e", "dlti.legal_int_widths" = array<i32: 8, 16, 32, 64>, "dlti.stack_alignment" = 128 : i64>, fir.defaultkind = "a1c4d8i4l4r4", fir.kindmap = "", fir.relocation_model = 1 : i32, llvm.data_layout = "e-m:e-p270:32:32-p271:32:32-p272:64:64-i64:64-i128:128-f80:128-n8:16:32:64-S128", llvm.ident = "flang version 23.0.0 (https://github.com/llvm/llvm-project.git d24ebe3f00b35c14b64c06d88451c7556ccbc016)", llvm.target_triple = "x86_64-unknown-linux-gnu"} {
  func.func @_QQmain() attributes {fir.bindc_name = "TEST"} {
    %c0_i32 = arith.constant 0 : i32
    %c2_i32 = arith.constant 2 : i32
    %c1 = arith.constant 1 : index
    %c1_i32 = arith.constant 1 : i32
    %c10_i32 = arith.constant 10 : i32
    %c10 = arith.constant 10 : index
    %0 = fir.dummy_scope : !fir.dscope
    %1 = fir.address_of(@_QFEa) : !fir.ref<!fir.array<10xi32>>
    %2 = fir.shape %c10 : (index) -> !fir.shape<1>
    %3 = fir.declare %1(%2) {uniq_name = "_QFEa"} : (!fir.ref<!fir.array<10xi32>>, !fir.shape<1>) -> !fir.ref<!fir.array<10xi32>>
    %4 = fir.address_of(@_QFEb) : !fir.ref<!fir.array<10xi32>>
    %5 = fir.shape %c10 : (index) -> !fir.shape<1>
    %6 = fir.declare %4(%5) {uniq_name = "_QFEb"} : (!fir.ref<!fir.array<10xi32>>, !fir.shape<1>) -> !fir.ref<!fir.array<10xi32>>
    %7 = fir.alloca i32 {bindc_name = "i", uniq_name = "_QFEi"}
    %8 = fir.declare %7 {uniq_name = "_QFEi"} : (!fir.ref<i32>) -> !fir.ref<i32>
    %9 = fir.alloca i32 {bindc_name = "n", uniq_name = "_QFEn"}
    %10 = fir.declare %9 {uniq_name = "_QFEn"} : (!fir.ref<i32>) -> !fir.ref<i32>
    %11 = fir.alloca i32 {bindc_name = "sum", uniq_name = "_QFEsum"}
    %12 = fir.declare %11 {uniq_name = "_QFEsum"} : (!fir.ref<i32>) -> !fir.ref<i32>
    fir.store %c10_i32 to %10 : !fir.ref<i32>
    %13 = fir.convert %c1_i32 : (i32) -> index
    %14 = fir.load %10 : !fir.ref<i32>
    %15 = fir.convert %14 : (i32) -> index
    %16 = fir.convert %13 : (index) -> i32
    %17 = fir.do_loop %arg0 = %13 to %15 step %c1 iter_args(%arg1 = %16) -> (i32) {
      fir.store %arg1 to %8 : !fir.ref<i32>
      %28 = fir.load %8 : !fir.ref<i32>
      %29 = fir.convert %28 : (i32) -> i64
      %30 = fir.array_coor %6(%5) %29 : (!fir.ref<!fir.array<10xi32>>, !fir.shape<1>, i64) -> !fir.ref<i32>
      %31 = fir.load %30 : !fir.ref<i32>
      %32 = fir.load %8 : !fir.ref<i32>
      %33 = fir.convert %32 : (i32) -> i64
      %34 = fir.array_coor %3(%2) %33 : (!fir.ref<!fir.array<10xi32>>, !fir.shape<1>, i64) -> !fir.ref<i32>
      fir.store %31 to %34 : !fir.ref<i32>
      %35 = fir.convert %c1 : (index) -> i32
      %36 = fir.load %8 : !fir.ref<i32>
      %37 = arith.addi %36, %35 overflow<nsw> : i32
      fir.result %37 : i32
    }
    fir.store %17 to %8 : !fir.ref<i32>
    %18 = fir.convert %c2_i32 : (i32) -> index
    %19 = fir.load %10 : !fir.ref<i32>
    %20 = fir.convert %19 : (i32) -> index
    %21 = fir.convert %18 : (index) -> i32
    %22 = fir.do_loop %arg0 = %18 to %20 step %c1 iter_args(%arg1 = %21) -> (i32) {
      fir.store %arg1 to %8 : !fir.ref<i32>
      %28 = fir.load %8 : !fir.ref<i32>
      %29 = arith.subi %28, %c1_i32 overflow<nsw> : i32
      %30 = fir.convert %29 : (i32) -> i64
      %31 = fir.array_coor %3(%2) %30 : (!fir.ref<!fir.array<10xi32>>, !fir.shape<1>, i64) -> !fir.ref<i32>
      %32 = fir.load %31 : !fir.ref<i32>
      %33 = fir.load %8 : !fir.ref<i32>
      %34 = fir.convert %33 : (i32) -> i64
      %35 = fir.array_coor %3(%2) %34 : (!fir.ref<!fir.array<10xi32>>, !fir.shape<1>, i64) -> !fir.ref<i32>
      fir.store %32 to %35 : !fir.ref<i32>
      %36 = fir.convert %c1 : (index) -> i32
      %37 = fir.load %8 : !fir.ref<i32>
      %38 = arith.addi %37, %36 overflow<nsw> : i32
      fir.result %38 : i32
    }
    fir.store %22 to %8 : !fir.ref<i32>
    fir.store %c0_i32 to %12 : !fir.ref<i32>
    %23 = fir.convert %c1_i32 : (i32) -> index
    %24 = fir.load %10 : !fir.ref<i32>
    %25 = fir.convert %24 : (i32) -> index
    %26 = fir.convert %23 : (index) -> i32
    %27 = fir.do_loop %arg0 = %23 to %25 step %c1 iter_args(%arg1 = %26) -> (i32) {
      fir.store %arg1 to %8 : !fir.ref<i32>
      %28 = fir.load %12 : !fir.ref<i32>
      %29 = fir.load %8 : !fir.ref<i32>
      %30 = fir.convert %29 : (i32) -> i64
      %31 = fir.array_coor %3(%2) %30 : (!fir.ref<!fir.array<10xi32>>, !fir.shape<1>, i64) -> !fir.ref<i32>
      %32 = fir.load %31 : !fir.ref<i32>
      %33 = arith.addi %28, %32 : i32
      fir.store %33 to %12 : !fir.ref<i32>
      %34 = fir.convert %c1 : (index) -> i32
      %35 = fir.load %8 : !fir.ref<i32>
      %36 = arith.addi %35, %34 overflow<nsw> : i32
      fir.result %36 : i32
    }
    fir.store %27 to %8 : !fir.ref<i32>
    return
  }
  fir.global internal @_QFEa : !fir.array<10xi32> {
    %0 = fir.zero_bits !fir.array<10xi32>
    fir.has_value %0 : !fir.array<10xi32>
  }
  fir.global internal @_QFEb : !fir.array<10xi32> {
    %0 = fir.zero_bits !fir.array<10xi32>
    fir.has_value %0 : !fir.array<10xi32>
  }
  func.func private @_FortranAProgramStart(i32, !llvm.ptr, !llvm.ptr, !llvm.ptr)
  func.func private @_FortranAProgramEndStatement()
  func.func @main(%arg0: i32, %arg1: !llvm.ptr, %arg2: !llvm.ptr) -> i32 {
    %c0_i32 = arith.constant 0 : i32
    %0 = fir.zero_bits !fir.ref<tuple<i32, !fir.ref<!fir.array<0xtuple<!fir.ref<i8>, !fir.ref<i8>>>>>>
    fir.call @_FortranAProgramStart(%arg0, %arg1, %arg2, %0) fastmath<contract> : (i32, !llvm.ptr, !llvm.ptr, !fir.ref<tuple<i32, !fir.ref<!fir.array<0xtuple<!fir.ref<i8>, !fir.ref<i8>>>>>>) -> ()
    fir.call @_QQmain() fastmath<contract> : () -> ()
    fir.call @_FortranAProgramEndStatement() fastmath<contract> : () -> ()
    return %c0_i32 : i32
  }
}
