from automates.apps.automates.execute_driver import execute_gromet_experiment_json


def test_execute_sir_simple_mock():
    input_json = {
        "command": "simulate-gsl",
        "definition": {"type": "gromet-fn", "source": '{"name": "SimpleSIR"}'},
        "start": 0,
        "end": 120.0,
        "step": 30.0,
        "domain_parameter": "P:sir.in.dt",
        "parameters": {
            "P:sir.in.beta": 0.5,
            "P:sir.in.S": 100000,
            "P:sir.in.I": 1,
            "P:sir.in.R": 0,
            "P:sir.in.gamma": 0.07,
        },
        "outputs": [
            "P:sir.out.S",
            "P:sir.out.I",
            "P:sir.out.R",
        ],
    }
    result = execute_gromet_experiment_json(input_json)

    expected = {
        "result": {
            "domain_parameter": [0, 30, 60, 90, 120],
            "values": {
                "P:sir.out.I": [
                    13.899850001499987,
                    193.17455602717965,
                    2678.622276802565,
                    35981.04345749553,
                    273225.5469052609,
                ],
                "P:sir.out.R": [
                    2.1,
                    31.289685003149977,
                    436.9562526602273,
                    6062.063033945615,
                    81622.25429468622,
                ],
                "P:sir.out.S": [
                    99985.0001499985,
                    99776.53575896967,
                    96885.4214705372,
                    57957.893508558845,
                    -254846.80119994713,
                ],
            },
        },
        "status": "success",
        "code": 200,
    }

    assert expected == result


def test_execute_chime_sir_mock():
    input_json = {
        "command": "simulate-gsl",
        "definition": {"type": "gromet-fn", "source": '{"name": "CHIME-SIR"}'},
        "start": 0,
        "end": 120.0,
        "step": 30,
        "domain_parameter": "J:main.n_days",
        "parameters": {
            "J:main.i_day": 17.0,
            "J:main.N_p": 3,
            "J:main.infections_days": 14.0,
            "J:main.relative_contact_rate": 0.05,
            "J:main.s_n": 200,
            "J:main.i_n": 1,
            "J:main.r_n": 1,
        },
        "outputs": ["P:main.out.S", "P:main.out.I", "P:main.out.E", "P:main.out.R"],
    }
    result = execute_gromet_experiment_json(input_json)

    expected = {
        "result": {
            "domain_parameter": [0, 30, 60, 90, 120],
            "values": {
                "P:main.out.E": [0.0, 0.0, 0.0, 0.0, 0.0],
                "P:main.out.I": [
                    0.0,
                    0.8933233135653156,
                    0.7806198884453974,
                    0.6712711762750359,
                    0.5693715755370689,
                ],
                "P:main.out.R": [
                    0.0,
                    2.965680650912271,
                    4.763081925816063,
                    6.3215644582752715,
                    7.652866183157096,
                ],
                "P:main.out.S": [
                    0.0,
                    198.14099603552242,
                    196.45629818573855,
                    195.00716436544968,
                    193.77776224130582,
                ],
            },
        },
        "status": "success",
        "code": 200,
    }

    assert result == expected
