# Esusu-api
This is an Esusu group savings implementation.
Basically what i do here is a minimal setup which allow user 
* to register on the platform.
* Create a group savings and become the admin
* add member to group
* invite members through mail.
* as a member view all groups and pick a one to join
* make a contribution to a group, basically the group admin fixes the contribution amount, so a contribution is just a simple api call with one parametre providing you are an existing member

## Run
There are practically two ways to run this project.
* running it in a container : The easy and fast way
* running locally : a little installation will be needed

### Dockerize 
 The project can be run on containers, the webserver nginx will serve the application through uwsgi. 
 the project uses makefile for build, so make will have to be installed , in a Unix system that will be already installed
 but on a windows system am not sure.

```Make
    make build-and-contain
```
this will create the configuration files and logfiles in directory `/data/esusu/` so please do give it permissions.

If you only want to build the docker image alone :
```Make
    make build
```

### Run locally

am hoping virtual env an python3 is installed on the machine.

clone the project inside the environment : 

` git clone git@github.com:horlahlekhon/Esusu-api.git`

create a postgresql database with the `postgres` user, you can use other user and other database name, but just for convenience of not having to modify the config file you can just stick with what i have here.

`createdb -U postgres esusu_api`

The project is built with Make and am hoping `Make` is installed if on unix , but on other non unix os am not sure.

there is a make target that installs and test and also run the project. so after creating the database , run:

 `make`

to test :
`make test`

to run locally :
`make run`




after running go to  : localhost:8000/docs/  to view the documentations.








