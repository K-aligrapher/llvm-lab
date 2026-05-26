program test
  integer :: i, n
  integer, dimension(10) :: A, B
  integer :: sum

  n = 10

  do i = 1, n
    A(i) = B(i)
  end do

  do i = 2, n
    A(i) = A(i-1)
  end do

  sum = 0
  do i = 1, n
    sum = sum + A(i)
  end do

end program

