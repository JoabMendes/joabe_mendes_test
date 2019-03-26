## Question B

In my solution for question B I first verified if the boolean comparision of the native `str` class  was able to
compare version numbers correctly. Which it demonstrated to be true:

![str default comparison](https://i.imgur.com/EpK3zXw.png)

From that I was able to extract version numbers from strings with a regular expression: `([\d.]+)`.
That expression will return a version number even in an alphanumeric string, if it matches the pattern.

![regular expression match](https://i.imgur.com/JcC16Iz.png)

After some parameters validation I was able to compare version numbers just with:

```python
    if version_a_value > version_b_value:
        return 1
    elif version_a_value < version_b_value:
        return -1
    else:
        return 0
```

My solution is implemented in `version_utils.is_version_gt(version_a, version_b)` and the tests can be found in 
`test.TestVersionUtils.test_is_version_gt`

To execute the tests for question B run:

```bash
$ ./run_test.sh
```