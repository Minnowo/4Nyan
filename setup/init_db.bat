


if NOT EXIST "../backend/postgres/bin/pg_ctl.exe" (
    goto end
)

cd ../backend/postgres/bin/

@REM set the data folder in the bin directory 
pg_ctl.exe --pgdata="data" init



:end