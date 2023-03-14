@rem taskarg: ${file}
@Echo off
SETLOCAL EnableDelayedExpansion

SET THIS_FOLDER=%~dp0

SET _NAME=%~2

echo %_NAME%

SET _RAW_TYPUS=%~3

if NOT DEFINED _RAW_TYPUS (
    SET _TYPUS=-D
)

if "%_RAW_TYPUS%"=="onedir" (
    SET _TYPUS=-D
)

if "%_RAW_TYPUS%"=="onefile" (
    SET _TYPUS=-F
)



rem -n %_NAME% ^
rem --upx-exclude vcruntime140.dll ^
rem --upx-exclude ucrtbase.dll ^


rem --upx-dir "D:\Dropbox\hobby\Modding\Ressources\python\upx\upx-3.96-win64" ^
rem --upx-exclude "vcruntime140.dll" ^

call %THIS_FOLDER%..\.venv\Scripts\activate
set INPATH=%~dp1
set INFILE=%~nx1
set INFILEBASE=%~n1
pushd %THIS_FOLDER%\..

IF EXIST pyinstaller_output_%_NAME% (
    RD /S /Q pyinstaller_output_%_NAME%
)

mkdir pyinstaller_output_%_NAME%

set PYTHONOPTIMIZE=1
pyinstaller --clean --noconfirm --log-level=INFO ^
%_TYPUS% ^
--upx-dir D:\Dropbox\hobby\Modding\Ressources\python\upx\upx-3.96-win64 ^
-i D:\Dropbox\hobby\Modding\Ressources\Icons\Personal_Icons\broca_progs_logo.ico ^
--distpath pyinstaller_output_%_NAME%/dist ^
--workpath pyinstaller_output_%_NAME%/work ^
%INPATH%%INFILE%

if "%_TYPUS%"=="-D" (
    cd pyinstaller_output_%_NAME%\dist\
    call 7z.exe a -tZip %_NAME%.zip %_NAME%\ -mx9
)