# Mini Developer Suite

This is a small webapp to manage git repositories and projects. It is written
in python using the flask microframework. You may compare it to GitLab and Github,
it's supposed to do similar things, just be smaller and easier to setup/use.

## Core features

* repository creation
* permission management
* SSH Key management
* issue tracker
* small wiki system

## Setup instructions

Configure the webapp by copying the file `config.py.example` to `config.py` and
editing the preferences. Then run the following commands to initialize a
virtual environment, the database, and run the test server.

    make setup
    make kill
    make run

If you want to use it within an apache server using mod_wsgi, use the provided
wsgi script in a virtual host.

## License (GPLv3+)

    Copyright (C) 2013

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program. If not, see <http://www.gnu.org/licenses/>.

Some files inside this repository are not originally part of the project, these
are distributed under their respective licenses. These files include the
Twitter Bootstrap and JQuery files. These files contain their own copyright
notice at the beginning of the file.
