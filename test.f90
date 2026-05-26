program test
  implicit none

  integer :: i
  integer :: n
  integer :: sum

  integer, dimension(10) :: A
  integer, dimension(10) :: B

  n = 10

  ! ==========================================
  ! Loop 1 : Parallelizable
  ! Independent iterations
  ! ==========================================

  do i = 1, n
     A(i) = B(i)
  end do


  ! ==========================================
  ! Loop 2 : Not safe
  ! Loop-carried dependency
  ! ==========================================

  do i = 2, n
     A(i) = A(i-1)
  end do


  ! ==========================================
  ! Loop 3 : Reduction-like loop
  ! ==========================================

  sum = 0

  do i = 1, n
     sum = sum + A(i)
  end do

end program test
