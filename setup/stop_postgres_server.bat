


if NOT EXIST "../backend/postgres/bin/pg_ctl.exe" (
    goto end
)

cd ../backend/postgres/bin/

pg_ctl.exe --pgdata="data" stop

:end