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
    -p - mysql root password\n\
\n\
Docker example:
    \$ docker ps - to list all running containers
    \$ docker ps -a - to list all existing containers
    \$ docker kill [name] - to stop container
    \$ docker logs [name] - to see container logs
"
}

while getopts 'hsrn:p:' flag; do
  case "${flag}" in
    h) print_usage
       exit 1 ;;
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

    docker start -i $name & 
    exit 0;
fi;

if $r_flag; then
    if [[ $name = '' || $password = '' ]]; then
        print_usage;
        exit 1;
    fi;

    docker run --name $name -e MYSQL_ROOT_PASSWORD=$password -e LANG=C.UTF-8 -p 3306:3306 -d mysql/mysql-server:latest
    exit 0;
fi;

print_usage
exit 1;
