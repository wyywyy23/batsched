#!/usr/bin/env python3
import itertools
import json
import glob
import unittest

from helper import *

def test_basic_algo_no_param(platform, workload, basic_algo_no_param):
    test_name = f'{basic_algo_no_param}-{platform.name}-{workload.name}'
    output_dir, robin_filename, _, _ = init_instance(test_name)

    batcmd = gen_batsim_cmd(platform.filename, workload.filename, output_dir, "")
    instance = RobinInstance(output_dir=output_dir,
        batcmd=batcmd,
        schedcmd=f"batsched -v '{basic_algo_no_param}'",
        simulation_timeout=30, ready_timeout=5,
        success_timeout=10, failure_timeout=0
    )

    instance.to_file(robin_filename)
    ret = run_robin(robin_filename)
    assert ret.returncode == 0

def test_easy_bf_plot_llh(platform, workload):
    algo = 'easy_bf_plot_liquid_load_horizon'
    test_name = f'{algo}-{platform.name}-{workload.name}'
    output_dir, robin_filename, _, schedconf_filename = init_instance(test_name)

    batcmd = gen_batsim_cmd(platform.filename, workload.filename, output_dir, "--energy")

    schedconf_content = {
        "trace_output_filename": f'{output_dir}/batsched_llh.trace'
    }
    write_file(schedconf_filename, json.dumps(schedconf_content))

    instance = RobinInstance(output_dir=output_dir,
        batcmd=batcmd,
        schedcmd=f"batsched -v '{algo}' --variant_options_filepath '{schedconf_filename}'",
        simulation_timeout=30, ready_timeout=5,
        success_timeout=10, failure_timeout=0
    )

    instance.to_file(robin_filename)
    ret = run_robin(robin_filename)
    assert ret.returncode == 0

def test_redis(platform, workload, one_basic_algo, redis_enabled):
    test_name = f'{one_basic_algo}-{platform.name}-{workload.name}-{redis_enabled}'
    output_dir, robin_filename, batconf_filename, _ = init_instance(test_name)

    batcmd = gen_batsim_cmd(platform.filename, workload.filename, output_dir,
        f"--config-file '{batconf_filename}'")

    batconf_content = {
        "redis": {
            "enabled": redis_enabled
        }
    }
    write_file(batconf_filename, json.dumps(batconf_content))

    instance = RobinInstance(output_dir=output_dir,
        batcmd=batcmd,
        schedcmd=f"batsched -v '{one_basic_algo}'",
        simulation_timeout=30, ready_timeout=5,
        success_timeout=10, failure_timeout=0
    )

    instance.to_file(robin_filename)
    ret = run_robin(robin_filename)
    assert ret.returncode == 0

def energy_model_instance():
    return {
        "power_sleep":9.75,
        "power_idle":95,
        "energy_switch_on":19030,
        "power_compute":190.738,
        "energy_switch_off":620,
        "time_switch_off":6.1,
        "pstate_sleep":13,
        "pstate_compute":0,
        "time_switch_on":152
    }

def test_inertial_shutdown(platform, workload,
    monitoring_period,
    allow_future_switches,
    upper_llh_threshold ,
    inertial_function,
    idle_time_to_sedate,
    sedate_idle_on_classical_events):
    algo = 'energy_bf_monitoring_inertial'
    test_name = f'{algo}-{platform.name}-{workload.name}-{inertial_function}-{idle_time_to_sedate}-{sedate_idle_on_classical_events}'
    output_dir, robin_filename, _, schedconf_filename = init_instance(test_name)

    batcmd = gen_batsim_cmd(platform.filename, workload.filename, output_dir, "--energy")

    schedconf_content = {
        "output_dir": output_dir,
        "monitoring_period": monitoring_period,
        "trace_output_filename": f'{output_dir}/batsched_llh.trace',
        "allow_future_switches": allow_future_switches,
        "upper_llh_threshold": upper_llh_threshold,
        "inertial_alteration": inertial_function,
        "idle_time_to_sedate": idle_time_to_sedate,
        "sedate_idle_on_classical_events": sedate_idle_on_classical_events
    }
    schedconf_content = dict(schedconf_content, **energy_model_instance())
    write_file(schedconf_filename, json.dumps(schedconf_content))

    instance = RobinInstance(output_dir=output_dir,
        batcmd=batcmd,
        schedcmd=f"batsched -v '{algo}' --variant_options_filepath '{schedconf_filename}'",
        simulation_timeout=30, ready_timeout=5,
        success_timeout=10, failure_timeout=0
    )

    instance.to_file(robin_filename)
    ret = run_robin(robin_filename)
    assert ret.returncode == 0
