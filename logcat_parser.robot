*** Settings ***
Library          ${CURDIR}/LogcatParser.py
Documentation    Measures the response time when switching to different audio sources.
...
...              Usage: pipenv run robot -v input_file:XXX -v output_file:xxx -v min_percentage
...                                       -v max_lifespan logcat_parser.robot

Test Setup       SETUP_LOGCAT_PARSER
Test Teardown    TEARDOWN_LOGCAT_PARSER

*** Variables ***
${input_file}    logcat_applications.txt
${output_file}    output.yml
${min_percentage}    75
${max_lifespan}    30

*** Keywords ***
SETUP_LOGCAT_PARSER
    ${verdict}  ${comment} =    LogcatParser.setup   ${input_file}
    Should Be True    ${verdict}    ${comment}

TEARDOWN_LOGCAT_PARSER
    ${verdict}  ${comment} =    LogcatParser.teardown   ${max_lifespan}    ${min_percentage}
    Should Be True    ${verdict}    ${comment}

*** Test Cases ***
LOGCAT_PARSER
    ${verdict}  ${comment} =    LogcatParser.run    ${output_file}
    Should Be True    ${verdict}    ${comment}
