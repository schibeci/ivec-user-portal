#!/bin/sh

#
# Its a sample script, tested only to the point of running manage.py runserver_plus
#
# You need to have python dev header files installed for mx.DateTime to install

VPYTHON_DIR='mypython'
VIRTUALENV='virtualenv-1.6.1'
VIRTUALENV_TARBALL='virtualenv-1.6.1.tar.gz'

# only install if we dont already exist
if [ ! -d $VPYTHON_DIR ]
then
    echo -e '\n\nNo virtual python dir, lets create one\n\n'

    # only install virtual env if its not hanging around
    if [ ! -d $VIRTUALENV ]
    then
        echo -e '\n\nNo virtual env, creating\n\n'
  
        # only download the tarball if needed
        if [ ! -f $VIRTUALENV_TARBALL ]
        then
            wget http://pypi.python.org/packages/source/v/virtualenv/$VIRTUALENV_TARBALL
        fi

        # build virtualenv
        tar zxvf $VIRTUALENV_TARBALL
        cd $VIRTUALENV
        python setup.py build
        cd ..

    fi
       
    # create a virtual python in the current directory
    python $VIRTUALENV/build/lib*/virtualenv.py --no-site-packages $VPYTHON_DIR

    # we use fab for deployments
    ./$VPYTHON_DIR/bin/easy_install fabric

    # install all the eggs in this app
    ./$VPYTHON_DIR/bin/easy_install eggs/*

    # now we are going to eggify app settings, so we can run it locally
    # we need to jump through a few legacy hoops to make this happen

    if [ ! -d tmp ]
    then
        mkdir tmp
    fi
    cd tmp
    rm -rf ccgapps-settings ccgbuild
    svn export svn+ssh://ccg.murdoch.edu.au/store/techsvn/ccg/ccgapps-settings
    svn export svn+ssh://ccg.murdoch.edu.au/store/techsvn/ccg/ccgbuild
    # the directory has the wrong name, so create a sym link with the name we need
    ln -s ccgapps-settings appsettings
    # the setup.py is at the wrong level
    mv appsettings/setup.py .
    ../$VPYTHON_DIR/bin/python setup.py bdist_egg
    cd ccgbuild
    ../../$VPYTHON_DIR/bin/python setup.py bdist_egg
    cd ..
    ../$VPYTHON_DIR/bin/easy_install dist/*.egg
    ../$VPYTHON_DIR/bin/easy_install ccgbuild/dist/*.egg
    rm -rf appsettings ccgapps-settings ccgbuild
    cd ..

    # hack activate to set some environment we need
    echo "PROJECT_DIRECTORY=`pwd`;" >>  $VPYTHON_DIR/bin/activate
    echo "export PROJECT_DIRECTORY " >>  $VPYTHON_DIR/bin/activate

fi

echo -e "\n\n What just happened?\n\n"
echo " * Python has been installed into $VPYTHON_DIR"
echo " * eggs from the eggs in this project have been installed"
echo " * fabric is also installed"
echo " * and ccgapps-settings & ccgbuild"


# tell the (l)user how to activate this python install
echo -e "\n\nTo activate this python install, type the following at the prompt:\n\nsource $VPYTHON_DIR/bin/activate\n"
echo -e "To exit your virtual python, simply type 'deactivate' at the shell prompt\n\n"
