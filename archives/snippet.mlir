module attributes {dlti.dl_spec = #dlti.dl_spec<!llvm.ptr<270> = dense<32> : vector<4xi64>, !llvm.ptr<271> = dense<32> : vector<4xi64>, !llvm.ptr<272> = dense<64> : vector<4xi64>, i64 = dense<64> : vector<2xi64>, i128 = dense<128> : vector<2xi64>, f80 = dense<128> : vector<2xi64>, !llvm.ptr = dense<64> : vector<4xi64>, i1 = dense<8> : vector<2xi64>, i8 = dense<8> : vector<2xi64>, i16 = dense<16> : vector<2xi64>, i32 = dense<32> : vector<2xi64>, f16 = dense<16> : vector<2xi64>, f64 = dense<64> : vector<2xi64>, f128 = dense<128> : vector<2xi64>, "dlti.endianness" = "little", "dlti.mangling_mode" = "e", "dlti.legal_int_widths" = array<i32: 8, 16, 32, 64>, "dlti.stack_alignment" = 128 : i64>, fir.defaultkind = "a1c4d8i4l4r4", fir.kindmap = "", fir.relocation_model = 1 : i32, llvm.data_layout = "e-m:e-p270:32:32-p271:32:32-p272:64:64-i64:64-i128:128-f80:128-n8:16:32:64-S128", llvm.ident = "flang version 23.0.0 (https://github.com/llvm/llvm-project.git d24ebe3f00b35c14b64c06d88451c7556ccbc016)", llvm.target_triple = "x86_64-unknown-linux-gnu"} {
  func.func @_QQmain() attributes {fir.bindc_name = "TEST"} {
    %c2_i32 = arith.constant 2 : i32
    %c1 = arith.constant 1 : index
    %c10_i32 = arith.constant 10 : i32
    %c1_i32 = arith.constant 1 : i32
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
    %9 = fir.convert %c1_i32 : (i32) -> index
    %10 = fir.convert %c10_i32 : (i32) -> index
    %11 = fir.convert %9 : (index) -> i32
    %12 = fir.do_loop %arg0 = %9 to %10 step %c1 iter_args(%arg1 = %11) -> (i32) {
      fir.store %arg1 to %8 : !fir.ref<i32>
      %17 = fir.load %8 : !fir.ref<i32>
      %18 = fir.convert %17 : (i32) -> i64
      %19 = fir.array_coor %6(%5) %18 : (!fir.ref<!fir.array<10xi32>>, !fir.shape<1>, i64) -> !fir.ref<i32>
      %20 = fir.load %19 : !fir.ref<i32>
      %21 = fir.load %8 : !fir.ref<i32>
      %22 = fir.convert %21 : (i32) -> i64
      %23 = fir.array_coor %3(%2) %22 : (!fir.ref<!fir.array<10xi32>>, !fir.shape<1>, i64) -> !fir.ref<i32>
      fir.store %20 to %23 : !fir.ref<i32>
      %24 = fir.convert %c1 : (index) -> i32
      %25 = fir.load %8 : !fir.ref<i32>
      %26 = arith.addi %25, %24 overflow<nsw> : i32
      fir.result %26 : i32
    }
    fir.store %12 to %8 : !fir.ref<i32>
    %13 = fir.convert %c2_i32 : (i32) -> index
    %14 = fir.convert %c10_i32 : (i32) -> index
    %15 = fir.convert %13 : (index) -> i32
    %16 = fir.do_loop %arg0 = %13 to %14 step %c1 iter_args(%arg1 = %15) -> (i32) {
      fir.store %arg1 to %8 : !fir.ref<i32>
      %17 = fir.load %8 : !fir.ref<i32>
      %18 = arith.subi %17, %c1_i32 overflow<nsw> : i32
      %19 = fir.convert %18 : (i32) -> i64
      %20 = fir.array_coor %3(%2) %19 : (!fir.ref<!fir.array<10xi32>>, !fir.shape<1>, i64) -> !fir.ref<i32>
      %21 = fir.load %20 : !fir.ref<i32>
      %22 = fir.load %8 : !fir.ref<i32>
      %23 = fir.convert %22 : (i32) -> i64
      %24 = fir.array_coor %3(%2) %23 : (!fir.ref<!fir.array<10xi32>>, !fir.shape<1>, i64) -> !fir.ref<i32>
      fir.store %21 to %24 : !fir.ref<i32>
      %25 = fir.convert %c1 : (index) -> i32
      %26 = fir.load %8 : !fir.ref<i32>
      %27 = arith.addi %26, %25 overflow<nsw> : i32
      fir.result %27 : i32
    }
    fir.store %16 to %8 : !fir.ref<i32>
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
