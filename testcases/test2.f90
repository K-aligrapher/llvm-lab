program test
  implicit none
  integer :: i, n
  integer, dimension(10) :: A, B
  integer :: sum

  n = 10

  ! Initialize B (just for completeness)
  do i = 1, n
    B(i) = i
  end do

  ! PARALLELIZABLE LOOP
  !$omp parallel do private(i)
  do i = 1, n
    A(i) = B(i)
  end do
  !$omp end parallel do

  ! NON-PARALLELIZABLE LOOP (has dependency)
  do i = 2, n
    A(i) = A(i-1)
  end do

  ! Reduction (can also be parallelized safely)
  sum = 0
  !$omp parallel do reduction(+:sum) private(i)
  do i = 1, n
    sum = sum + A(i)
  end do
  !$omp end parallel do

end program
