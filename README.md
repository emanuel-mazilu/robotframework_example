# robotframework_example

## To prepare enviroment:
```
pip3 install pipenv
pipenv install
```
or

```
pip3 install robotframework
```

## Usage:
```
python3 LogcatParser.py -f logcat_applications.txt

```
or

```
pipenv run robot -v input_file:xxx -v output_file:xxx -v min_percentage -v max_lifespan logcat_parser.robot

```
or

```
python3 -m robot logcat_parser.robot

```

