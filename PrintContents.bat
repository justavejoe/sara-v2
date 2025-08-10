@ECHO OFF
REM ==================================================================================
REM This script reads a list of file and directory paths from "Directory.txt".
REM 
REM - If the path is a directory, it iterates through all files in that directory
REM   and its subdirectories, logging the name and content of each file.
REM - If the path is a file, it logs its name and content directly.
REM - All output is saved to the file specified in OUTPUT_FILE.
REM ==================================================================================

SETLOCAL ENABLEDELAYEDEXPANSION

REM Define the input file containing the list of directories and files.
SET "LIST_FILE=Directory.txt"
REM Define the output file where all content will be saved.
SET "OUTPUT_FILE=FileContents.txt"

REM Check if the list file exists.
IF NOT EXIST "%LIST_FILE%" (
    ECHO ERROR: The file '%LIST_FILE%' was not found.
    ECHO Please make sure the file is in the same directory as this script.
    PAUSE
    EXIT /B 1
)

REM Initialize or clear the output file and add a timestamp.
ECHO Log generated on %DATE% at %TIME% > "%OUTPUT_FILE%"
ECHO. >> "%OUTPUT_FILE%"

ECHO Starting to process paths from %LIST_FILE%...
ECHO Output will be saved to %OUTPUT_FILE%
ECHO.

REM Loop through each line in the Directory.txt file.
FOR /F "usebackq tokens=*" %%A IN ("%LIST_FILE%") DO (
    ECHO Processing path: "%%A"
    ECHO ================================================================= >> "%OUTPUT_FILE%"
    ECHO Processing path: "%%A" >> "%OUTPUT_FILE%"
    ECHO ================================================================= >> "%OUTPUT_FILE%"
    ECHO. >> "%OUTPUT_FILE%"

    REM Check if the item is a directory by seeing if a ".\" can be appended.
    IF EXIST "%%A\" (
        ECHO "%%A" is a directory. Logging contents of files within...
        ECHO "%%A" is a directory. Printing contents of files within... >> "%OUTPUT_FILE%"
        ECHO. >> "%OUTPUT_FILE%"
        REM Loop through all files in the specified directory and its subdirectories.
        FOR /R "%%A" %%B IN (*.*) DO (
            ECHO   - Logging file: "%%B"
            ECHO --- File: "%%B" --- >> "%OUTPUT_FILE%"
            TYPE "%%B" >> "%OUTPUT_FILE%"
            ECHO. >> "%OUTPUT_FILE%"
            ECHO --- End of File: "%%B" --- >> "%OUTPUT_FILE%"
            ECHO. >> "%OUTPUT_FILE%"
        )
    ) ELSE (
        REM If it's not a directory, check if it's a file.
        IF EXIST "%%A" (
            ECHO "%%A" is a file. Logging its content...
            ECHO "%%A" is a file. Printing its content... >> "%OUTPUT_FILE%"
            ECHO. >> "%OUTPUT_FILE%"
            ECHO --- File: "%%A" --- >> "%OUTPUT_FILE%"
            TYPE "%%A" >> "%OUTPUT_FILE%"
            ECHO. >> "%OUTPUT_FILE%"
            ECHO --- End of File: "%%A" --- >> "%OUTPUT_FILE%"
            ECHO. >> "%OUTPUT_FILE%"
        ) ELSE (
            ECHO WARNING: "%%A" is not a valid file or directory. Skipping.
            ECHO WARNING: "%%A" is not a valid file or directory. Skipping. >> "%OUTPUT_FILE%"
            ECHO. >> "%OUTPUT_FILE%"
        )
    )
)

ECHO.
ECHO =================================================================
ECHO All paths have been processed. Output saved to "%OUTPUT_FILE%".
ECHO =================================================================
PAUSE
ENDLOCAL
