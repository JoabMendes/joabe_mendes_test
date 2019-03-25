## Question A


Considering two lines a(x, y) and b (x, y). They only overlap if `b.x <= a.y and b.x >= a.x` 
or if `a.x <= b.y and a.x >= b.x` whether one line's start isn't between the start and end of the other line.


A solution is implemented in `math_utils.overlap(line_a, line_b)` and the test can be found on 
`test.TestMathUtils.test_overlap`

To execute the tests for question A run:

```bash
$ ./run_test.sh
```