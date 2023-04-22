#!/bin/bash 

s_flag='false'
r_flag='false'
name=''
password=''

print_usage() {
  printf \
"\nThis script helps you to create or/and run docker mysql container. \n\
Usage:\n\
  -s - run existing container\n\
      example: ./database_start.sh -s -n example\n\
  -r - create new container\n\
      example: ./database_start.sh -r -n example -p 1234\n\
  \n\
  -n - name of the containter\n\
  -p - mysql root password\
"
}

while getopts 'srn:p:' flag; do
  case "${flag}" in
    s) s_flag='true' ;;
    r) r_flag='true' ;;
    n) name="${OPTARG}" ;;
    p) password="${OPTARG}" ;;
    *) print_usage
       exit 1 ;;
  esac
done

if $s_flag; then
    if [[ $name = '' ]]; then
        print_usage;
        exit 1;
    fi;

    docker start -i $name;
    exit 0;
fi;

if $r_flag; then
    if [[ $name = '' || $password = '' ]]; then
        print_usage;
        exit 1;
    fi;

    docker run --name $name -e MYSQL_ROOT_PASSWORD=$password -e LANG=C.UTF-8 -d mysql/mysql-server:5.7
    exit 0;
fi;
