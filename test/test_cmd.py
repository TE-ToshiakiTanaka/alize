from nose.tools import with_setup, raises, ok_, eq_, timed
from alize import cmd
from alize.exception import *

def setup():
    pass

def teardown():
    pass

@with_setup(setup, teardown)
def test_cmd_run_success_01():
    result = cmd.run("ls")
    eq_(result[0], 0)

@with_setup(setup, teardown)
def test_cmd_run_success_02():
    result = cmd.run("ls", debug=True)
    eq_(result[0], 0)

@with_setup(setup, teardown)
def test_cmd_run_bg_success_01():
    try:
        result = cmd.run_bg("ls")
        ok_(True)
    except: ok_(False)

@with_setup(setup, teardown)
@timed(1.2)
def test_cmd_run_bg_success_02():
    try:
        result = cmd.run_bg("sleep 2")
        ok_(True)
    except: ok_(False)

@with_setup(setup, teardown)
def test_cmd_run_bg_success_01():
    try:
        result = cmd.run_bg("ls", debug=True)
        ok_(True)
    except: ok_(False)


@with_setup(setup, teardown)
def test_cmd_run_failed_01():
    result = cmd.run('ls -la | wc -l')
    eq_(result[0], 2)

@with_setup(setup, teardown)
@raises(RunError)
def test_cmd_run_failed_02():
    result = cmd.run("hoge")
    eq_(result[0], 1)

@with_setup(setup, teardown)
def test_cmd_run_bg_failed_01():
    try:
        result = cmd.run_bg("ls -la | wc -l")
        ok_(False)
    except: ok_(True)


@with_setup(setup, teardown)
@timed(2.2)
def test_cmd_run_sleep_success():
    result = cmd.run("sleep 2", timeout=5)
    eq_(result[0], 0)

@with_setup(setup, teardown)
@raises(TimeoutError)
def test_cmd_run_sleep_timeout_01():
    result = cmd.run("sleep 10", timeout=5)
    eq_(result[0], 0)

@with_setup(setup, teardown)
@timed(5.2)
def test_cmd_run_sleep_timeout_02():
    try:
        result = cmd.run("sleep 10", timeout=5)
    except TimeoutError as e:
        ok_(True)
